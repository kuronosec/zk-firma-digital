pragma circom 2.1.9;

include "circomlib/circuits/poseidon.circom";
include "../helpers/constants.circom";


/// @title Nullifier
/// @notice Computes the nullifier for an Aadhaar identity
/// @input photo The photo of the user with SHA padding
/// @output nullifier = hash(nullifierSeed, hash(photo[0:15]), hash(photo[16:31]))
template Nullifier() {
    signal input nullifierSeed;

    signal output out <== nullifierSeed;
}
