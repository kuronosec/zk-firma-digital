//SPDX-License-Identifier: Unlicense
pragma solidity ^0.8.19;

import '../interfaces/IZKFirmaDigitalGroth16Verifier.sol';
import '../interfaces/IZKFirmaDigital.sol';

contract ZKFirmaDigital is IZKFirmaDigital {
    address public verifier;
    uint256 public immutable storedPublicKeyHash;

    constructor(address _verifier, uint256 _pubkeyHash) {
        verifier = _verifier;
        storedPublicKeyHash = _pubkeyHash;
    }

    /// @dev Verifies the ZKFirmaDigital proof received.
    /// @param nullifierSeed: Nullifier Seed used to compute the nullifier.
    /// @param nullifier: Nullifier for the ZK Firma Digital user.
    /// @param signal: Signal committed while generating the proof.
    /// @param revealArray: Array of the values used to reveal data, if value is 1 data is revealed, not if 0.
    /// @param groth16Proof: SNARK Groth16 proof.
    /// @return Verified bool
    function verifyZKFirmaDigitalProof(
        uint nullifierSeed,
        uint nullifier,
        uint signal,
        uint[1] calldata revealArray,
        uint[8] calldata groth16Proof
    ) public view returns (bool) {
        uint signalHash = _hash(signal);
        return
            IZKFirmaDigitalGroth16Verifier(verifier).verifyProof(
                [groth16Proof[0], groth16Proof[1]],
                [
                    [groth16Proof[2], groth16Proof[3]],
                    [groth16Proof[4], groth16Proof[5]]
                ],
                [groth16Proof[6], groth16Proof[7]],
                [
                    storedPublicKeyHash,
                    nullifier,
                    // revealAgeAbove18
                    revealArray[0],
                    nullifierSeed,
                    signalHash
                ]
            );
    }

    /// @dev Creates a keccak256 hash of a message compatible with the SNARK scalar modulus.
    /// @param message: Message to be hashed.
    /// @return Message digest.
    function _hash(uint256 message) private pure returns (uint256) {
        return uint256(keccak256(abi.encodePacked(message))) >> 3;
    }
}
