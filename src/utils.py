import re
import struct
import logging
import os
import traceback
from web3 import Web3
import hashlib

from pathlib import Path

from poseidon_bn254_t3_constants import C as POSEIDON_C, M as POSEIDON_M

STELLAR_ADDRESS_PATTERN = re.compile(r'^G[A-Z2-7]{55}$')

# Minimal Stellar StrKey codec (SEP-0023) for ed25519 public keys ("G..."
# addresses), ported from zikuani-stellar's prover/helpers (and circuits/
# helpers/stellar.js before that) so this app has no extra runtime
# dependency for it. Layout: 1 version byte (0x30) + 32-byte raw ed25519
# public key + 2-byte CRC16/XMODEM checksum, all base32-encoded (RFC 4648,
# no padding) -> 56 characters starting with "G".
_STELLAR_BASE32_ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ234567"
_ED25519_PUBLIC_KEY_VERSION_BYTE = 6 << 3  # 0x30

def _base32_decode(value):
    bits = 0
    acc = 0
    out = bytearray()
    for ch in value:
        idx = _STELLAR_BASE32_ALPHABET.find(ch)
        if idx == -1:
            continue
        acc = (acc << 5) | idx
        bits += 5
        if bits >= 8:
            bits -= 8
            out.append((acc >> bits) & 0xff)
    return bytes(out)

def _crc16_xmodem(data):
    crc = 0x0000
    for byte in data:
        crc ^= byte << 8
        for _ in range(8):
            if crc & 0x8000:
                crc = ((crc << 1) ^ 0x1021) & 0xffff
            else:
                crc = (crc << 1) & 0xffff
    return crc

def decode_stellar_address(g_address):
    full = _base32_decode(g_address)
    if len(full) != 35:
        raise ValueError("invalid StrKey length")
    if full[0] != _ED25519_PUBLIC_KEY_VERSION_BYTE:
        raise ValueError("not an ed25519 public key StrKey (unexpected version byte)")
    payload = full[0:33]
    crc_given = full[33] | (full[34] << 8)
    if crc_given != _crc16_xmodem(payload):
        raise ValueError("bad StrKey checksum")
    return full[1:33]

def stellar_address_to_bigint(g_address):
    return int.from_bytes(decode_stellar_address(g_address), byteorder='big')

# Poseidon hash (BN254 scalar field, t=3 i.e. 2 inputs), ported from
# circomlibjs's poseidon_reference.js using the exact same published
# constants (see poseidon_bn254_t3_constants.py) -- produces bit-identical
# output to circomlibjs's buildPoseidon() for the same inputs, verified
# against known test vectors.
_BN254_FR_MODULUS = 21888242871839275222246405745257275088548364400416034343698204186575808495617
_POSEIDON_N_ROUNDS_F = 8
_POSEIDON_N_ROUNDS_P = 57  # N_ROUNDS_P[t-2] for t=3
_POSEIDON_T = 3

def _pow5(a):
    a2 = (a * a) % _BN254_FR_MODULUS
    a4 = (a2 * a2) % _BN254_FR_MODULUS
    return (a4 * a) % _BN254_FR_MODULUS

def poseidon2(in0, in1):
    p = _BN254_FR_MODULUS
    t = _POSEIDON_T
    state = [0, in0 % p, in1 % p]
    for r in range(_POSEIDON_N_ROUNDS_F + _POSEIDON_N_ROUNDS_P):
        state = [(state[i] + POSEIDON_C[r * t + i]) % p for i in range(t)]
        if r < _POSEIDON_N_ROUNDS_F // 2 or r >= _POSEIDON_N_ROUNDS_F // 2 + _POSEIDON_N_ROUNDS_P:
            state = [_pow5(a) for a in state]
        else:
            state[0] = _pow5(state[0])
        state = [
            sum(POSEIDON_M[i][j] * state[j] for j in range(t)) % p
            for i in range(t)
        ]
    return state[0]

# Splits an address (as an int, up to 256 bits) into two 128-bit limbs --
# matches splitAddress() in zikuani-stellar's prover/helpers/generate-inputs.js.
_LIMB_BITS = 128
_LIMB_MASK = (1 << _LIMB_BITS) - 1

def split_address(address_int):
    return address_int & _LIMB_MASK, address_int >> _LIMB_BITS

# Some utility libraries to process the input data as the
# Circom circuit requires
def splitToWords(number, wordsize, number_element):
  t = number
  words = []
  base_two = 2

  for i in range(number_element):
    words.append(str(t % pow(base_two, wordsize)))
    t = t // pow(base_two, wordsize)

  if (t != 0):
    raise ValueError(f"Number {number} does not fit in {wordsize * number_element} bits")

  return words

def preprocess_message_for_sha256(message: bytearray, max_len: int) -> bytearray:
    # Step 1: Calculate the original message length in bits
    original_bit_len = len(message) * 8

    # Step 2: Add the '1' bit, represented as 0x80 in hexadecimal (10000000 in binary)
    message.append(0x80)

    # Step 3: Add padding of zeros (bytes of 0x00) until message length is congruent to 448 mod 512
    # 448 mod 512 because we need 64 bits for the length at the end (512 - 64 = 448)
    while (len(message) * 8) % 512 != 448:
        message.append(0x00)

    # Step 4: Append the original length of the message as a 64-bit big-endian integer
    message += struct.pack('>Q', original_bit_len)

    # Step 5: If the final message length exceeds max_len, pad it with zeroes to max_len
    message_len = len(message)
    if message_len > max_len:
        print(message_len)
        raise ValueError("Message length exceeds the maximum length")
    elif message_len < max_len:
        message += bytearray(max_len - len(message))

    return message, message_len

# Helper function to zero pad a message to 32 bytes
def zero_pad(message, length):
    return message.rjust(length * 2, '0')

# Hash function using keccak256
def hash_message(message):
    # Convert the message to a hex string if it's not already
    if isinstance(message, (int, bytes)):
        # If it's an int or bigint, convert to hex
        message = hex(message)
    elif isinstance(message, str):
        # Ensure the message is hex formatted
        if not message.startswith('0x'):
            raise ValueError("String message should be in hex format.")
    else:
        raise TypeError("Message must be an int, str (hex format), or bytes.")

    # Pad message to 32 bytes (64 hex characters)
    message = zero_pad(message[2:], 32)  # Remove the '0x' prefix and pad

    # Compute keccak256 hash of the message
    message_hash = Web3.keccak(hexstr=message)

    # Convert to int and shift right by 3 bits
    result = int.from_bytes(message_hash, byteorder='big') >> 3

    # Return the result as a string
    return str(result)

def is_stellar_address(value):
    return bool(STELLAR_ADDRESS_PATTERN.match(value))

# Hash function for Stellar addresses: Poseidon(addressLo, addressHi), the
# same address-binding hash the Stellar-side OFAC non-membership circuit
# (ofac-blacklist.circom, in the zikuani-stellar repo's prover/) embeds as
# its public `addressHash` output. This is deliberately a *different* hash
# family/encoding than hash_message()'s keccak256 -- that one matches the
# EVM verifying contracts' on-chain `_hash(signal)` recomputation, which
# expects keccak256 over the raw EVM address. Stellar's identity_gate
# contract has no such on-chain recomputation step, so this just needs to
# match whatever the OFAC proof for the same address already produces.
#
# Implemented entirely in Python (poseidon2/split_address/
# stellar_address_to_bigint above) so this app needs no extra runtime
# dependency (no Node, no bundled JS/node_modules) -- verified to produce
# bit-identical output to circomlibjs's buildPoseidon() for the same inputs.
def compute_stellar_signal_hash(address):
    address_int = stellar_address_to_bigint(address)
    address_lo, address_hi = split_address(address_int)
    return str(poseidon2(address_lo, address_hi))

# Create a logs directory if it doesn't exist (cross-platform)
user_path = os.path.join(Path.home(), Path('.zk-firma-digital/'))
log_directory = os.path.join(user_path, "logs")
os.makedirs(log_directory, exist_ok=True)

# Define the path to the log file
log_file = os.path.join(log_directory, "app.log")

# Configure the logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(log_file, encoding="utf-8")
    ]
)
