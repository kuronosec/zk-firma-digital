"use strict";

/**
 * Generates an OFAC non-membership Groth16 proof for a single address, in
 * the same `{ proof, public }` JSON shape used throughout this project
 * (see zikuani-stellar/example-proof.json) — so it can be dropped straight
 * into `SOROBAN_OFAC_PROOF_FILE` for the zikuani-stellar web app, or fed to
 * `identity_gate::verify_identity` directly.
 *
 * Counterpart to helpers/prove.js, but parameterized by address and
 * scriptable instead of a fixed end-to-end demo.
 *
 * Usage:
 *   node helpers/prove-ofac.js <address> [outputFile]
 *
 *   <address>    A Stellar "G..." StrKey, a "0x..." EVM address, or a raw
 *                decimal/hex BigInt literal.
 *   [outputFile] Where to write the proof JSON. Defaults to stdout.
 *
 * Prerequisites: same circuit build artifacts as helpers/prove.js
 * (build/ofac-blacklist_js/ofac-blacklist.wasm, build/ofac-blacklist_final.zkey).
 *
 * IMPORTANT: this still sources the blacklist from FAKE_OFAC_ADDRESSES
 * (see ofac-addresses.fake.js) since this repo has no real OFAC SDN crypto
 * address feed wired in yet. Swap `OFAC_ADDRESSES` for the real list before
 * relying on this for anything beyond local testing.
 *
 * Also note: the resulting `ofacRoot` (logged to stderr) is only a valid
 * public signal if it matches whatever root `identity_gate` currently
 * accepts (set via `initialize` / `set_ofac_root`). Rebuilding the tree from
 * a different address list produces a different root.
 */

const fs = require("fs");
const snarkjs = require("snarkjs");
const { buildOFACTree, generateProofInputs } = require("./generate-inputs");
const { FAKE_OFAC_ADDRESSES } = require("./ofac-addresses.fake");
const { stellarAddressToBigInt } = require("./stellar");

const OFAC_ADDRESSES = FAKE_OFAC_ADDRESSES;

function parseAddressArg(arg) {
    if (/^G[A-Z2-7]{55}$/.test(arg)) {
        return stellarAddressToBigInt(arg);
    }
    if (arg.startsWith("0x") || arg.startsWith("0X")) {
        return BigInt(arg);
    }
    return BigInt(arg);
}

// Generation only -- this does not locally verify the proof it produces.
// Verification is the on-chain verifier contract's job (identity_gate /
// ofac_verifier), not the prover's.
async function proveOfacNonMembership(addressBigInt) {
    const { tree, poseidon } = await buildOFACTree(OFAC_ADDRESSES);
    const inputs = await generateProofInputs(tree, poseidon, addressBigInt);

    const { proof, publicSignals } = await snarkjs.groth16.fullProve(
        inputs,
        "build/ofac-blacklist_js/ofac-blacklist.wasm",
        "build/ofac-blacklist_final.zkey"
    );

    return { proof, public: publicSignals, ofacRoot: inputs.ofacRoot, addressHash: inputs.addressHash };
}

async function main() {
    const [addressArg, outputFile] = process.argv.slice(2);
    if (!addressArg) {
        console.error("Usage: node helpers/prove-ofac.js <address> [outputFile]");
        process.exit(1);
    }

    const addressBigInt = parseAddressArg(addressArg);
    const { proof, public: publicSignals, ofacRoot, addressHash } = await proveOfacNonMembership(addressBigInt);

    console.error("ofacRoot:   ", ofacRoot.toString());
    console.error("addressHash:", addressHash.toString());

    const output = JSON.stringify({ public: publicSignals, proof }, null, 2);
    if (outputFile) {
        fs.writeFileSync(outputFile, output);
        console.error(`Proof written to ${outputFile}`);
    } else {
        process.stdout.write(output + "\n");
    }
}

module.exports = { proveOfacNonMembership, parseAddressArg };

if (require.main === module) {
    // snarkjs/ffjavascript's field-arithmetic WASM bindings leave worker
    // threads running that never let the event loop drain on their own, so
    // exit explicitly once the actual work (proof generation + output) is done.
    main()
        .then(() => process.exit(0))
        .catch((err) => {
            console.error(err);
            process.exit(1);
        });
}
