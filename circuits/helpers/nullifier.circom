pragma circom 2.1.9;

include "circomlib/circuits/poseidon.circom";

/// @title Nullifier
/// @notice Computes the nullifier
template Nullifier(n, k) {
    signal input nullifierSeed;
    signal input signature[k];

    signal output out;

    // Calculate Poseidon hash of the signature
    var poseidonInputSize = k \ 2;
    if (k % 2 == 1) {
        poseidonInputSize++;
    }
    assert(poseidonInputSize <= 16);

    signal signatureHasherInput[poseidonInputSize];
    for (var i = 0; i < poseidonInputSize; i++) {
        if (i == poseidonInputSize - 1 && k % 2 == 1) {
            signatureHasherInput[i] <== signature[i * 2];
        } else {
            signatureHasherInput[i] <== signature[i * 2] + (1 << n) * signature[i * 2 + 1];
        }
    }
    component signatureHasher = Poseidon(poseidonInputSize);
    signatureHasher.inputs <== signatureHasherInput;

    out <== Poseidon(2)([nullifierSeed, signatureHasher.out]);
}
