// SPDX-License-Identifier: GPL-3.0
pragma solidity ^0.8.19;

import {INonMerklizedIssuer} from '@iden3/contracts/interfaces/INonMerklizedIssuer.sol';

interface IZKFirmaDigitalCredentialIssuer {
   /**
     * @dev Get user's id list of credentials
     * @param _userId - user id
     * @return array of credential ids
     */
    function getUserCredentialIds(uint256 _userId) external view returns (uint256[] memory);

    /**
     * @dev Get credential by id
     * @param _userId - user id
     * @param _credentialId - credential id
     * @return credential data
     */
    function getCredential(
        uint256 _userId,
        uint256 _credentialId
    )
        external
        view
        returns (
            INonMerklizedIssuer.CredentialData memory,
            uint256[8] memory,
            INonMerklizedIssuer.SubjectField[] memory
        );

    /**
     * @dev Revoke claim using it's revocationNonce
     * @param _revocationNonce  - revocation nonce
     */
    function revokeClaimAndTransit(uint64 _revocationNonce) external;

        /**
     * @dev Issue credential based on ZK Firma Digital Proof.
     * @param _userId: user identification this credential is assigned to
     * @param nullifierSeed: Nullifier Seed used while generating the proof.
     * @param nullifier: Nullifier for the user's Firma Digital data, used as user id for which the claim is issued.
     * @param signal: signal used while generating the proof, should be equal to msg.sender.
     * @param revealArray: Array of the values used to reveal data, if value is 1 data is revealed, not if 0.
     * @param groth16Proof: SNARK Groth16 proof.
     */
    function issueCredential(
        uint _userId,
        uint nullifierSeed,
        uint nullifier,
        uint signal,
        uint[1] calldata revealArray,
        uint[8] calldata groth16Proof) external;
}
