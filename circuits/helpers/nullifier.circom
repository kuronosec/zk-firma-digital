pragma circom 2.1.9;

include "circomlib/circuits/poseidon.circom";

/// @title Nullifier
/// @notice Computes the nullifier
template Nullifier() {
    signal input nullifierSeed;

    signal output out <== nullifierSeed;
}
