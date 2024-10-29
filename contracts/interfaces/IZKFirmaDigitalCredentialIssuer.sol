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
}
