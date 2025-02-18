// SPDX-License-Identifier: GPL-3.0
pragma solidity 0.8.20;

import {Ownable2StepUpgradeable} from '@openzeppelin/contracts-upgradeable/access/Ownable2StepUpgradeable.sol';
import {ClaimBuilder} from '@iden3/contracts/lib/ClaimBuilder.sol';
import {IdentityLib} from '@iden3/contracts/lib/IdentityLib.sol';
import {INonMerklizedIssuer} from '@iden3/contracts/interfaces/INonMerklizedIssuer.sol';
import {NonMerklizedIssuerBase} from '@iden3/contracts/lib/NonMerklizedIssuerBase.sol';
import {PrimitiveTypeUtils} from '@iden3/contracts/lib/PrimitiveTypeUtils.sol';
import {PoseidonUnit4L} from '@iden3/contracts/lib/Poseidon.sol';
import {IZKFirmaDigital} from '../interfaces/IZKFirmaDigital.sol';

/**
 * @dev Example of decentralized credential issuer.
 * This issuer issue non-merklized credentials decentralized.
 */
contract ZKFirmaDigitalCredentialIssuer is NonMerklizedIssuerBase, Ownable2StepUpgradeable {
    using IdentityLib for IdentityLib.Data;
    address public ZKFirmaDigitalVerifierAddr;
    uint256 public constant contractNullifierSeed = 253091582028213;

    /// @custom:storage-location erc7201:polygonid.storage.CredentialIssuer
    struct CredentialIssuerStorage {
        // countOfIssuedClaims count of issued claims for incrementing id and revocation nonce for new claims
        uint64 countOfIssuedClaims;
        // claim store
        mapping(uint256 => uint256[]) userClaims;
        mapping(uint256 => ClaimItem) idToClaim;
        mapping(uint256 => uint256) nullifierToUser;
        // this mapping is used to store credential subject fields
        // to escape additional copy in issueCredential function
        // since "Copying of type struct OnchainNonMerklizedIdentityBase.SubjectField memory[] memory to storage not yet supported."
        mapping(uint256 => INonMerklizedIssuer.SubjectField[]) idToCredentialSubject;
    }

    // keccak256(abi.encode(uint256(keccak256("zkfirmadigital.storage.ZKFirmaDigitalCredentialIssuer")) - 1)) & ~bytes32(uint256(0xff))
    bytes32 private constant CredentialIssuerStorageLocation =
        0x1786bc6ebe7251c5adf29bd410fbc6767c8f7e53055a55569c691b703559e900;

    function _getCredentialIssuerStorage()
        private
        pure
        returns (CredentialIssuerStorage storage $)
    {
        assembly {
            $.slot := CredentialIssuerStorageLocation
        }
    }

    /**
     * @dev Version of contract
     */
    string public constant VERSION = '1.0.0';

    // jsonldSchemaHash hash of jsonld schema.
    // More about schema: https://devs.polygonid.com/docs/issuer-node/issuer-node-api/claim/apis/#get-claims
    uint256 private constant jsonldSchemaHash = 78462520673154254320111203189905;
    string private constant jsonSchema =
        'https://raw.githubusercontent.com/kuronosec/zk-firma-digital/main/assets/zk-firma-digital.json';
    string private constant jsonldSchema =
        'https://raw.githubusercontent.com/kuronosec/zk-firma-digital/main/assets/zk-firma-digital.jsonld';

    struct ClaimItem {
        uint256 id;
        uint64 issuanceDate;
        uint256[8] claim;
    }

    function initialize(address _stateContractAddr, address _verifierAddr) public initializer {
        require(ZKFirmaDigitalVerifierAddr == address(0), "Already initialized");
        ZKFirmaDigitalVerifierAddr = _verifierAddr;
        super.initialize(_stateContractAddr);
        __Ownable_init(_msgSender());
    }

    /**
     * @dev Get user's id list of credentials
     * @param _userId - user id
     * @return array of credential ids
     */
    function getUserCredentialIds(uint256 _userId) external view returns (uint256[] memory) {
        CredentialIssuerStorage storage $ = _getCredentialIssuerStorage();
        return $.userClaims[_userId];
    }

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
        override
        returns (
            INonMerklizedIssuer.CredentialData memory,
            uint256[8] memory,
            INonMerklizedIssuer.SubjectField[] memory
        )
    {
        CredentialIssuerStorage storage $ = _getCredentialIssuerStorage();

        string[] memory jsonLDContextUrls = new string[](2);
        jsonLDContextUrls[0] = jsonldSchema;
        jsonLDContextUrls[1] = 'https://schema.iden3.io/core/jsonld/displayMethod.jsonld';

        ClaimItem memory claimItem = $.idToClaim[_credentialId];
        INonMerklizedIssuer.CredentialData memory credentialData = INonMerklizedIssuer
            .CredentialData({
                id: claimItem.id,
                context: jsonLDContextUrls,
                _type: 'ZKFirmaDigitalCredential',
                issuanceDate: claimItem.issuanceDate,
                credentialSchema: INonMerklizedIssuer.CredentialSchema({
                    id: jsonSchema,
                    _type: 'JsonSchema2023'
                }),
                displayMethod: INonMerklizedIssuer.DisplayMethod({
                    id: 'https://raw.githubusercontent.com/kuronosec/zk-firma-digital/main/assets/zk-firma-digital-display-method.json',
                    _type: 'Iden3BasicDisplayMethodV1'
                })
            });
        return (credentialData, claimItem.claim, $.idToCredentialSubject[_credentialId]);
    }

    /**
     * @dev Revoke claim using it's revocationNonce
     * @param _revocationNonce  - revocation nonce
     */
    function revokeClaimAndTransit(uint64 _revocationNonce) public onlyOwner {
        _getIdentityBaseStorage().identity.revokeClaim(_revocationNonce);
        _getIdentityBaseStorage().identity.transitState();
    }

    /**
     * @dev Issue credential based on ZK Firma Digital Proof.
     * @param nullifierSeed: Nullifier Seed used while generating the proof.
     * @param nullifier: Nullifier for the user's Firma Digital data, used as user id for which the claim is issued.
     * @param signal: signal used while generating the proof, should be equal to msg.sender.
     * @param revealArray: Array of the values used to reveal data, if value is 1 data is revealed, not if 0.
     * @param groth16Proof: SNARK Groth16 proof.
     */
    function issueCredential(
        uint _userId,
        uint64 nullifierSeed,
        uint nullifier,
        uint signal,
        uint[1] calldata revealArray, 
        uint[8] calldata groth16Proof) public {
        CredentialIssuerStorage storage $ = _getCredentialIssuerStorage();
        // Check if the nullifier has already been used
        _checkPreviousClaims(_userId, nullifier);

        // Check ZK Firma Digital Proof
        _validateProof(nullifierSeed, nullifier, signal, revealArray, groth16Proof);

        uint64 expirationDate = convertTime(block.timestamp + 30 days);
        uint256 random_nonce = generateNonce();

        ClaimBuilder.ClaimData memory claimData = ClaimBuilder.ClaimData({
            // metadata
            schemaHash: jsonldSchemaHash,
            idPosition: ClaimBuilder.ID_POSITION_INDEX,
            expirable: true,
            updatable: false,
            merklizedRootPosition: 0,
            version: 0,
            id: _userId,
            revocationNonce: nullifierSeed,
            expirationDate: expirationDate,
            // data
            merklizedRoot: 0,
            indexDataSlotA: random_nonce,
            indexDataSlotB: revealArray[0],
            valueDataSlotA: revealArray[0],
            valueDataSlotB: revealArray[0]
        });
        uint256[8] memory claim = ClaimBuilder.build(claimData);

        uint256 hashIndex = PoseidonUnit4L.poseidon([claim[0], claim[1], claim[2], claim[3]]);
        uint256 hashValue = PoseidonUnit4L.poseidon([claim[4], claim[5], claim[6], claim[7]]);

        ClaimItem memory claimToSave = ClaimItem({
            id: nullifierSeed,
            issuanceDate: convertTime(block.timestamp),
            claim: claim
        });

        $.idToCredentialSubject[nullifierSeed].push(
            INonMerklizedIssuer.SubjectField({key: 'ageAbove18', value: revealArray[0], rawValue: ''})
        );
        $.idToCredentialSubject[nullifierSeed].push(
            INonMerklizedIssuer.SubjectField({key: 'citizen', value: revealArray[0], rawValue: ''})
        );
        $.idToCredentialSubject[nullifierSeed].push(
            INonMerklizedIssuer.SubjectField({key: 'organization', value: revealArray[0], rawValue: ''})
        );
        $.idToCredentialSubject[nullifierSeed].push(
            INonMerklizedIssuer.SubjectField({key: 'randomNonce', value: random_nonce, rawValue: ''})
        );

        $.nullifierToUser[nullifier] = _userId;
        addClaimHashAndTransit(hashIndex, hashValue);
        saveClaim(nullifierSeed, _userId, claimToSave);
    }

    // saveClaim save a claim to storage
    function saveClaim(uint64 _nullifierSeed, uint256 _userId, ClaimItem memory _claim) private {
        CredentialIssuerStorage storage $ = _getCredentialIssuerStorage();

        $.userClaims[_userId].push(_nullifierSeed);
        $.idToClaim[_nullifierSeed] = _claim;
        $.countOfIssuedClaims++;
    }

    // addClaimHashAndTransit add a claim to the identity and transit state
    function addClaimHashAndTransit(uint256 hashIndex, uint256 hashValue) private {
        _getIdentityBaseStorage().identity.addClaimHash(hashIndex, hashValue);
        _getIdentityBaseStorage().identity.transitState();
    }

    function convertTime(uint256 timestamp) private pure returns (uint64) {
        require(timestamp <= type(uint64).max, 'Timestamp exceeds uint64 range');
        return uint64(timestamp);
    }

    /// @dev Check if the timestamp is more recent than (current time - 3 hours)
    /// @param timestamp: msg.sender address.
    /// @return bool
    function isLessThan3HoursAgo(uint timestamp) public view returns (bool) {
        return true;
    }

    /// @dev Convert an address to uint256, used to check against signal.
    /// @param _addr: msg.sender address.
    /// @return Address msg.sender's address in uint256
    function addressToUint256(address _addr) private pure returns (uint256) {
        return uint256(uint160(_addr));
    }

    /// @dev Generate a random nonce for the credentials to be unique.
    /// @return Nonce random nonce
    function generateNonce() public view returns (uint256) {
        uint256 nonce = uint256(
            keccak256(
                abi.encodePacked(
                    block.timestamp,  // Current block timestamp
                    block.difficulty, // Current block difficulty
                    msg.sender        // Address of the sender
                )
            )
        );
        uint256 mask = (1 << 253) - 1; // Mask with 253 bits set to 1, to have SNARK friendly nonce 
        return nonce & mask;
    }

    function _validateProof(
        uint nullifierSeed,
        uint nullifier,
        uint signal,
        uint[1] calldata revealArray,
        uint[8] calldata groth16Proof) internal view {
        require(
            IZKFirmaDigital(ZKFirmaDigitalVerifierAddr).verifyZKFirmaDigitalProof(
                nullifierSeed,
                nullifier,
                signal,
                revealArray,
                groth16Proof
            ),
            '[ZKFirmaDigitalCredentialIssuer]: The proof sent is not valid.'
        );
    }

    function _checkPreviousClaims(uint _userId, uint nullifier) internal view {
        CredentialIssuerStorage storage $ = _getCredentialIssuerStorage();
        
        uint256 userNullifier = $.nullifierToUser[nullifier];
        if (userNullifier != 0) {
            uint256[] memory previousClaims = $.userClaims[_userId];

            if (previousClaims.length > 0) {
                // Get the latest claim ID from the array
                uint256 latestClaimId = previousClaims[previousClaims.length - 1];
                ClaimItem memory latestClaim = $.idToClaim[latestClaimId];

                require(
                    block.timestamp >= latestClaim.claim[4],
                    "[ZKFirmaDigitalCredentialIssuer]: Previous claim not expired."
                );
            }
        }
    }
}
