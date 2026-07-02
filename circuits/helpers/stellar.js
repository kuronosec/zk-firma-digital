"use strict";

/**
 * Minimal Stellar StrKey codec (SEP-0023) for ed25519 public keys ("G..." addresses).
 * Layout: 1 version byte (0x30) + 32-byte raw ed25519 public key + 2-byte CRC16/XMODEM
 * checksum, all base32-encoded (RFC 4648, no padding) -> 56 characters starting with "G".
 */

const ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ234567";
const ED25519_PUBLIC_KEY_VERSION_BYTE = 6 << 3; // 0x30

function base32Encode(buf) {
    let bits = 0, value = 0, output = "";
    for (const byte of buf) {
        value = (value << 8) | byte;
        bits += 8;
        while (bits >= 5) {
            output += ALPHABET[(value >>> (bits - 5)) & 31];
            bits -= 5;
        }
    }
    if (bits > 0) output += ALPHABET[(value << (5 - bits)) & 31];
    return output;
}

function base32Decode(str) {
    let bits = 0, value = 0;
    const bytes = [];
    for (const ch of str) {
        const idx = ALPHABET.indexOf(ch);
        if (idx === -1) continue;
        value = (value << 5) | idx;
        bits += 5;
        if (bits >= 8) {
            bytes.push((value >>> (bits - 8)) & 0xff);
            bits -= 8;
        }
    }
    return Buffer.from(bytes);
}

function crc16xmodem(buf) {
    let crc = 0x0000;
    for (const byte of buf) {
        crc ^= byte << 8;
        for (let i = 0; i < 8; i++) {
            crc = (crc & 0x8000) ? ((crc << 1) ^ 0x1021) & 0xffff : (crc << 1) & 0xffff;
        }
    }
    return crc;
}

/**
 * Encodes a 32-byte ed25519 public key as a Stellar "G..." StrKey address.
 * @param {Buffer} pubkey32
 * @returns {string}
 */
function encodeStellarAddress(pubkey32) {
    if (pubkey32.length !== 32) throw new Error("ed25519 public key must be 32 bytes");
    const payload = Buffer.concat([Buffer.from([ED25519_PUBLIC_KEY_VERSION_BYTE]), pubkey32]);
    const crc = crc16xmodem(payload);
    const crcBuf = Buffer.from([crc & 0xff, (crc >> 8) & 0xff]); // little-endian
    return base32Encode(Buffer.concat([payload, crcBuf]));
}

/**
 * Decodes a Stellar "G..." StrKey address into its raw 32-byte ed25519 public key.
 * @param {string} gAddress
 * @returns {Buffer}
 */
function decodeStellarAddress(gAddress) {
    const full = base32Decode(gAddress);
    if (full.length !== 35) throw new Error("invalid StrKey length");
    const versionByte = full[0];
    if (versionByte !== ED25519_PUBLIC_KEY_VERSION_BYTE) {
        throw new Error("not an ed25519 public key StrKey (unexpected version byte)");
    }
    const payload = full.slice(0, 33);
    const crcGiven = full[33] | (full[34] << 8);
    if (crcGiven !== crc16xmodem(payload)) throw new Error("bad StrKey checksum");
    return full.slice(1, 33);
}

/**
 * Decodes a Stellar "G..." address straight into the BigInt representation
 * used as the circuit's `address` value (see splitAddress() in generate-inputs.js).
 * @param {string} gAddress
 * @returns {bigint}
 */
function stellarAddressToBigInt(gAddress) {
    return BigInt("0x" + decodeStellarAddress(gAddress).toString("hex"));
}

module.exports = {
    encodeStellarAddress,
    decodeStellarAddress,
    stellarAddressToBigInt,
};
