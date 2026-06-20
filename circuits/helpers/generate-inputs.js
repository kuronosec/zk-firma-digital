"use strict";

const { buildPoseidon, newMemEmptyTrie } = require("circomlibjs");

const N_LEVELS = 20;
const LIMB_BITS = 128n;
const LIMB_MASK = (1n << LIMB_BITS) - 1n;

/**
 * Splits an address (as a BigInt, up to 256 bits) into two 128-bit limbs.
 * Two limbs avoid the modular wraparound risk of stuffing a raw 256-bit
 * value (e.g. a Stellar ed25519 public key) into a single ~254-bit field
 * element, while still covering shorter addresses like Ethereum's 160 bits.
 *
 * @param {bigint} addressBigInt
 * @returns {{ addressLo: bigint, addressHi: bigint }}
 */
function splitAddress(addressBigInt) {
    return {
        addressLo: addressBigInt & LIMB_MASK,
        addressHi: addressBigInt >> LIMB_BITS,
    };
}

/**
 * Builds a Sparse Merkle Tree from a list of OFAC-sanctioned addresses.
 *
 * Keys are Poseidon(addressLo, addressHi) to distribute them uniformly
 * across the field, keeping proof paths short and matching what the
 * circuit expects.
 *
 * @param {bigint[]} blacklistedAddresses  Addresses as BigInts (any network, up to 256 bits)
 * @returns {{ tree, root: BigInt, poseidon }}
 */
async function buildOFACTree(blacklistedAddresses) {
    const poseidon = await buildPoseidon();
    const tree = await newMemEmptyTrie();

    for (const addr of blacklistedAddresses) {
        const { addressLo, addressHi } = splitAddress(addr);
        const key = poseidon([addressLo, addressHi]);
        await tree.insert(key, 1n);
    }

    return { tree, root: tree.root, poseidon };
}

/**
 * Generates the circuit inputs to prove `address` is NOT in the OFAC SMT.
 * Throws if the address IS found in the tree.
 *
 * @param {object} tree          SMT instance from buildOFACTree
 * @param {object} poseidon      Poseidon hasher from buildOFACTree
 * @param {bigint} addressBigInt Address to check, as a BigInt (any network, up to 256 bits)
 * @returns {object} Inputs ready for snarkjs.groth16.fullProve
 */
async function generateProofInputs(tree, poseidon, addressBigInt) {
    const F = poseidon.F;
    const { addressLo, addressHi } = splitAddress(addressBigInt);
    const addressHash = poseidon([addressLo, addressHi]);

    const res = await tree.find(addressHash);

    if (res.found) {
        throw new Error(`Address ${addressBigInt} IS in the OFAC blacklist — proof refused`);
    }

    // poseidon()/tree.find() return values in the field's internal (non-BigInt)
    // representation; snarkjs needs plain BigInts for circuit inputs.
    const siblings = (res.siblings ?? []).map(s => F.toObject(s));
    while (siblings.length < N_LEVELS) siblings.push(0n);

    return {
        ofacRoot:    F.toObject(tree.root),
        addressHash: F.toObject(addressHash),
        addressLo:   addressLo,
        addressHi:   addressHi,
        siblings:    siblings,
        oldKey:      res.notFoundKey   !== undefined ? F.toObject(res.notFoundKey)   : 0n,
        oldValue:    res.notFoundValue !== undefined ? F.toObject(res.notFoundValue) : 0n,
        isOld0:      res.isOld0 ? 1n : 0n,
    };
}

module.exports = { buildOFACTree, generateProofInputs, splitAddress, N_LEVELS };
