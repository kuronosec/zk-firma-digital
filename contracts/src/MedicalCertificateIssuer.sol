// SPDX-License-Identifier: GPL-3.0
pragma solidity 0.8.20;

import {IZKFirmaDigitalCredentialIssuer} from '../interfaces/IZKFirmaDigitalCredentialIssuer.sol';
import {INonMerklizedIssuer} from '@iden3/contracts/interfaces/INonMerklizedIssuer.sol';

contract MedicalCertificateIssuer {
    address public ZKFirmaDigitalCredentialIssuerAddr;
    address public governmentAddr;

    struct UserRequestItem {
        uint256 userId;
        bytes requestNumber;
    }

    struct GovernmentReponseItem {
        uint256 userId;
        bytes ipfsHash;
        bytes aesKey;
    }

    mapping(uint256 => UserRequestItem[]) private userRequests;
    mapping(uint256 => GovernmentReponseItem[]) private governmentReponses;

    // Event emitted when new data is added
    event UserRequestAdded(uint256 _userId);
    event GovernmentReponsetAdded(uint256 _userId);

    constructor(
        address _credentialIssuerAddr,
        address _governmentAddr) {
        require(
            ZKFirmaDigitalCredentialIssuerAddr == address(0),
            "Already initialized."
        );
        ZKFirmaDigitalCredentialIssuerAddr = _credentialIssuerAddr;
        governmentAddr = _governmentAddr;
    }

    function requestMedicalCertificate(
        uint256 _userId,
        bytes calldata _requestNumber) public {
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

        // TODO: what to do with the VC data?
        (credentialData, proof, subjectFields) = credentialIssuer.getCredential(
            _userId,
            credentialIds[0]
        );

        userRequests[_userId].push(
            UserRequestItem({
                userId: _userId,
                requestNumber: _requestNumber
            })
        );
        emit UserRequestAdded(_userId);
    }

    function getUserRequest(uint256 _userId, uint index) external view returns (UserRequestItem memory) {
        require(index < userRequests[_userId].length, "Index out of bounds");
        return userRequests[_userId][index];
    }

    function getUserRequestCount(uint256 _userId) external view returns (uint) {
        return userRequests[_userId].length;
    }

    function deleteUserRequest(uint256 _userId, uint index) external {
        uint lastIndex = userRequests[_userId].length - 1;
        require(index <= lastIndex, "Index out of bounds");

        // Swap and delete to maintain array integrity
        if (index != lastIndex) {
            userRequests[_userId][index] = userRequests[_userId][lastIndex];
        }

        // Remove the last element
        userRequests[_userId].pop();
    }

    function respondMedicalCertificateRequest(
        uint256 _userId,
        bytes calldata _ipfsHash,
        bytes calldata _aesKey) public {
        require(
            msg.sender == governmentAddr,
            "[MedicalCertificateIssuer]: Only government address can use this function."
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

        // TODO: what to do with the VC data?
        (credentialData, proof, subjectFields) = credentialIssuer.getCredential(
            _userId,
            credentialIds[0]
        );

        governmentReponses[_userId].push(
            GovernmentReponseItem({
                userId: _userId,
                ipfsHash: _ipfsHash,
                aesKey: _aesKey
            })
        );

        this.deleteUserRequest(_userId, 0);
        emit GovernmentReponsetAdded(_userId);
    }

    function getGovernmentReponse(uint256 _userId, uint index) external view returns (GovernmentReponseItem memory) {
        require(index < governmentReponses[_userId].length, "Index out of bounds");
        return governmentReponses[_userId][index];
    }

    function getGovernmentReponseCount(uint256 _userId) external view returns (uint) {
        return governmentReponses[_userId].length;
    }

    function deleteGovernmentReponse(uint256 _userId, uint index) external {
        require(
            msg.sender == governmentAddr,
            "[MedicalCertificateIssuer]: Only government address can use this function."
        );
        
        uint lastIndex = governmentReponses[_userId].length - 1;
        require(index <= lastIndex, "Index out of bounds");

        // Swap and delete to maintain array integrity
        if (index != lastIndex) {
            governmentReponses[_userId][index] = governmentReponses[_userId][lastIndex];
        }

        // Remove the last element
        governmentReponses[_userId].pop();
    }
}
