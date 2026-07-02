"use strict";

/**
 * End-to-end example: build the OFAC SMT, generate a non-membership proof,
 * and verify it locally with snarkjs. Covers both outcomes:
 *   1. A clean address NOT in the list -> proof generates and verifies.
 *   2. An address that IS in the list -> generateProofInputs throws,
 *      before a proof can even be attempted.
 *
 * Prerequisites (run once):
 *   circom ofac-blacklist.circom --r1cs --wasm --sym -o build/
 *   snarkjs groth16 setup build/ofac-blacklist.r1cs pot13_final.ptau build/ofac-blacklist_0.zkey
 *   snarkjs zkey contribute build/ofac-blacklist_0.zkey build/ofac-blacklist_final.zkey
 *   snarkjs zkey export verificationkey build/ofac-blacklist_final.zkey build/verification_key.json
 */

const snarkjs = require("snarkjs");
const { buildOFACTree, generateProofInputs } = require("./generate-inputs");
const { FAKE_OFAC_ADDRESSES } = require("./ofac-addresses.fake");

// Sample OFAC list — replace with the full list fetched from your data source.
// FAKE_OFAC_ADDRESSES mixes Ethereum and Stellar addresses to exercise both
// limb sizes — see splitAddress() in generate-inputs.js.
const OFAC_ADDRESSES = FAKE_OFAC_ADDRESSES;

// The address to check — this stays private in the proof. Not in OFAC_ADDRESSES.
const CLEAN_ADDRESS = BigInt("0x1234567890abcdef1234567890abcdef12345678");

async function main() {
    console.log(`Building OFAC Sparse Merkle Tree from ${OFAC_ADDRESSES.length} addresses...`);
    const { tree, poseidon } = await buildOFACTree(OFAC_ADDRESSES);
    console.log("SMT root:", poseidon.F.toObject(tree.root).toString());

    // ── Positive case: clean address ─────────────────────────────────────
    console.log(`\n[positive] Generating non-membership proof for ${CLEAN_ADDRESS.toString(16)}...`);
    const inputs = await generateProofInputs(tree, poseidon, CLEAN_ADDRESS);
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

    const vKey = require("../build/verification_key.json");
    const valid = await snarkjs.groth16.verify(vKey, publicSignals, proof);
    console.log("[positive] Proof valid:", valid);
    if (!valid) throw new Error("[positive] expected a valid proof for a clean address");

    /*
     * On-chain: the Solidity verifier receives (proof, publicSignals) and checks:
     *   1. proof is valid against the verification key
     *   2. publicSignals[0] (ofacRoot) matches the on-chain published root
     *   3. publicSignals[1] (addressHash) matches the Zikuani Firma proof's signalHash
     */

    // ── Negative case: a sanctioned address ──────────────────────────────
    const sanctioned = OFAC_ADDRESSES[0];
    console.log(`\n[negative] Attempting to prove non-membership for a blacklisted address (${sanctioned.toString(16)})...`);
    try {
        await generateProofInputs(tree, poseidon, sanctioned);
        throw new Error("[negative] expected generateProofInputs to throw, but it did not");
    } catch (err) {
        console.log("[negative] Correctly refused:", err.message);
    }

    console.log("\nAll checks passed.");
}

main().catch((err) => {
    console.error(err);
    process.exit(1);
});
