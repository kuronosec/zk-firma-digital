"use strict";

/**
 * End-to-end example: build the OFAC SMT, generate a non-membership proof,
 * and verify it locally with snarkjs.
 *
 * Prerequisites (run once):
 *   circom ofac-blacklist.circom --r1cs --wasm --sym -o build/
 *   snarkjs groth16 setup build/ofac-blacklist.r1cs pot12_final.ptau build/ofac-blacklist_0.zkey
 *   snarkjs zkey contribute build/ofac-blacklist_0.zkey build/ofac-blacklist_final.zkey
 *   snarkjs zkey export verificationkey build/ofac-blacklist_final.zkey build/verification_key.json
 */

const snarkjs = require("snarkjs");
const { buildOFACTree, generateProofInputs } = require("./generate-inputs");

// Sample OFAC list — replace with the full list fetched from your data source.
// Addresses can be from any network (Ethereum, Stellar, ...) as long as they
// fit in 256 bits — see splitAddress() in generate-inputs.js.
const OFAC_ADDRESSES = [
    "0xd882cfc20f52f2599d84b8e8d58c7fb62cfe344b",
    "0x901bb9583b24d97e995513c6778dc6888ab6870e",
    "0xa7e5d5a720f06526557c513402f2e6b5fa20b008",
].map(BigInt);

// The address to check — this stays private in the proof
const USER_ADDRESS = BigInt("0x1234567890abcdef1234567890abcdef12345678");

async function main() {
    console.log("Building OFAC Sparse Merkle Tree...");
    const { tree, poseidon } = await buildOFACTree(OFAC_ADDRESSES);
    console.log("SMT root:", tree.root.toString());

    console.log(`\nGenerating non-membership proof for ${USER_ADDRESS.toString(16)}...`);
    const inputs = await generateProofInputs(tree, poseidon, USER_ADDRESS);
    console.log("Circuit inputs ready.");
    console.log("  addressHash:", inputs.addressHash.toString());
    console.log("  ofacRoot:   ", inputs.ofacRoot.toString());

    console.log("\nGenerating Groth16 proof...");
    const { proof, publicSignals } = await snarkjs.groth16.fullProve(
        inputs,
        "build/ofac-blacklist_js/ofac-blacklist.wasm",
        "build/ofac-blacklist_final.zkey"
    );

    console.log("Proof generated.");
    console.log("Public signals:", publicSignals);

    const vKey = require("../../build/verification_key.json");
    const valid = await snarkjs.groth16.verify(vKey, publicSignals, proof);
    console.log("\nProof valid:", valid);

    /*
     * On-chain: the Solidity verifier receives (proof, publicSignals) and checks:
     *   1. proof is valid against the verification key
     *   2. publicSignals[0] (ofacRoot) matches the on-chain published root
     *   3. publicSignals[1] (addressHash) matches the Zikuani Firma proof's signalHash
     */
}

main().catch(console.error);
