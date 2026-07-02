pragma circom 2.1.9;

include "circomlib/circuits/smt/smtverifier.circom";
include "circomlib/circuits/poseidon.circom";
include "circomlib/circuits/bitify.circom";

/*
 * Proves that `address` is NOT present in the OFAC sanctions blacklist,
 * represented as a Sparse Merkle Tree (SMT) with root `ofacRoot`.
 *
 * The SMT key for each blacklisted address is Poseidon(addressLo, addressHi),
 * which distributes keys uniformly across the field — keeping proof paths
 * short regardless of address patterns.
 *
 * The address is split into two 128-bit limbs (addressLo, addressHi) instead
 * of a single field element because the BN254 scalar field is ~254 bits —
 * too small to safely hold a raw 256-bit value (e.g. a Stellar ed25519
 * public key) without risking modular wraparound. Two 128-bit limbs cover
 * any address up to 256 bits — Ethereum (160 bits), Stellar (256 bits), or
 * other chains — with no network-specific assumptions.
 *
 * nLevels = 20 supports up to 2^20 (~1M) blacklisted entries.
 * The OFAC SDN crypto address list has ~15k entries as of 2025.
 */
template NotInOFACBlacklist(nLevels) {
    // ── Public inputs ─────────────────────────────────────────────────────
    signal input ofacRoot;    // SMT root of the OFAC blacklist, published on-chain
    signal input addressHash; // Poseidon(addressLo, addressHi);

    // ── Private inputs ────────────────────────────────────────────────────
    signal input addressLo;          // Low 128 bits of the user's address (never revealed)
    signal input addressHi;          // High 128 bits of the user's address (never revealed)
    signal input siblings[nLevels];  // SMT sibling hashes along the proof path
    signal input oldKey;             // Neighboring leaf key (non-membership witness)
    signal input oldValue;           // Neighboring leaf value
    signal input isOld0;             // 1 if the neighbor is an empty leaf

    // Range-check each limb to exactly 128 bits so every address has a single
    // canonical (addressLo, addressHi) encoding, matching how the off-chain
    // SMT and the bound Firma proof split the same address.
    component loBits = Num2Bits(128);
    loBits.in <== addressLo;
    component hiBits = Num2Bits(128);
    hiBits.in <== addressHi;

    // Constrain addressHash = Poseidon(addressLo, addressHi).
    // This proves the prover knows the preimage of the public addressHash,
    // and makes addressHash the canonical SMT key for uniform distribution.
    component hasher = Poseidon(2);
    hasher.inputs[0] <== addressLo;
    hasher.inputs[1] <== addressHi;
    hasher.out === addressHash;

    // Prove addressHash is NOT a key in the OFAC blacklist SMT (fnc=1 → non-inclusion).
    component verifier = SMTVerifier(nLevels);
    verifier.enabled  <== 1;
    verifier.root     <== ofacRoot;
    verifier.key      <== addressHash;
    verifier.value    <== 0;
    verifier.fnc      <== 1;
    verifier.oldKey   <== oldKey;
    verifier.oldValue <== oldValue;
    verifier.isOld0   <== isOld0;
    for (var i = 0; i < nLevels; i++) {
        verifier.siblings[i] <== siblings[i];
    }
}

component main { public [ofacRoot, addressHash] } = NotInOFACBlacklist(20);
