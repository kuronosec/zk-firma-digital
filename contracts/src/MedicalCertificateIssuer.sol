// SPDX-License-Identifier: GPL-3.0
pragma solidity 0.8.20;

import {IZKFirmaDigitalCredentialIssuer} from '../interfaces/IZKFirmaDigitalCredentialIssuer.sol';
import {INonMerklizedIssuer} from '@iden3/contracts/interfaces/INonMerklizedIssuer.sol';

contract MedicalCertificateIssuer {
    address public ZKFirmaDigitalCredentialIssuerAddr;
    uint256 public constant storedNullifierSeed = 253091582028213;

    mapping(uint256 => bytes[]) private userRequest;

    // Event emitted when new data is added
    event UserRequestAdded(uint256 _userId, uint indexed dataIndex, bytes data);

    constructor(address _credentialIssuerAddr) {
        require(
            ZKFirmaDigitalCredentialIssuerAddr == address(0),
            "Already initialized."
        );
        ZKFirmaDigitalCredentialIssuerAddr = _credentialIssuerAddr;
    }

    function requestMedicalCertificate(
        uint256 _userId,
        bytes calldata _userRequest) public {
        require(
            _userId == uint256(uint160(msg.sender)),
            "[MedicalCertificateIssuer]: User ID has to be the transaction sender address"
        );

        INonMerklizedIssuer.CredentialData memory credentialData;
        uint256[8] memory proof;
        INonMerklizedIssuer.SubjectField[] memory subjectFields;

        IZKFirmaDigitalCredentialIssuer credentialIssuer = IZKFirmaDigitalCredentialIssuer(
            ZKFirmaDigitalCredentialIssuerAddr
        );
        uint256[] memory credentialIds = credentialIssuer.getUserCredentialIds(_userId);

        require(
            credentialIds.length > 0,
            "No credentials available, create one first."
        );

        (credentialData, proof, subjectFields) = credentialIssuer.getCredential(
            _userId,
            credentialIds[0]
        );

        userRequest[_userId].push(_userRequest);
        emit UserRequestAdded(_userId, userRequest[_userId].length - 1, _userRequest);
    }

    function getUserRequest(uint256 _userId, uint index) external view returns (bytes memory) {
        require(index < userRequest[_userId].length, "Index out of bounds");
        return userRequest[_userId][index];
    }

    function getUserRequestCount(uint256 _userId) external view returns (uint) {
        return userRequest[_userId].length;
    }

    function deleteUserRequest(uint256 _userId, uint index) external {
        uint lastIndex = userRequest[_userId].length - 1;
        require(index <= lastIndex, "Index out of bounds");

        // Swap and delete to maintain array integrity
        if (index != lastIndex) {
            userRequest[_userId][index] = userRequest[_userId][lastIndex];
        }
        
        // Remove the last element
        userRequest[_userId].pop();
    }
}
