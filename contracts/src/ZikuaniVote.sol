// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

// ZK Firma Digital imports
import '../interfaces/IZikuaniVote.sol';
import '../interfaces/IZKFirmaDigitalCredentialIssuer.sol';
import './ZikuaniVoteBase.sol';

// ZK Passport imports
import {IPoseidonSMT} from "@rarimo/passport-contracts/interfaces/state/IPoseidonSMT.sol";
import {PublicSignalsBuilder} from "@rarimo/passport-contracts/sdk/lib/PublicSignalsBuilder.sol";
import {AQueryProofExecutor} from "@rarimo/passport-contracts/sdk/AQueryProofExecutor.sol";

contract ZikuaniVote is ZikuaniVoteBase, AQueryProofExecutor {
    // Credenctial issuer for ZK Firma Digital
    address public ZKFirmaDigitalCredentialIssuerAddr;
    
    // Bitmask for ZK passport
    uint256 selector;

    // PublicSignalsBuilder is a library for building public signals
    using PublicSignalsBuilder for uint256;

    uint256 public constant IDENTITY_LIMIT = type(uint32).max;

    // Salt for event_data
    address public erc1155;

    // Constructor to initialize proposals
    function __ZikuaniVote_init(
        VoteParams memory _voteParams,
        address _credentialIssuerAddr,
        address _registrationSMT,
        address _verifier,
        uint256 _selector
    ) external initializer {
        __ZikuaniVoteBase_init(_voteParams);
        __AQueryProofExecutor_init(_registrationSMT, _verifier);

        ZKFirmaDigitalCredentialIssuerAddr = _credentialIssuerAddr;
        erc1155 = _registrationSMT;

        // Store selector bitmask used by the verifier circuit
        // Must match the selector used when generating the proof off-chain
        selector = _selector;
    }

    /// @dev Register a vote in the contract.
    /// @param proposalIndex: Index of the proposal you want to vote for.
    /// @param nullifierSeed: Nullifier Seed used while generating the proof.
    /// @param nullifier: Nullifier for the user's ZK Firma Digital data.
    /// @param signal: signal used while generating the proof, should be equal to msg.sender.
    /// @param revealArray: Array of the values used to reveal data, if value is 1 data is revealed, not if 0.
    /// @param groth16Proof: SNARK Groth16 proof.
    function voteForProposal(
        uint256 proposalIndex,
        uint nullifierSeed,
        uint nullifier,
        uint signal,
        uint[1] calldata revealArray, 
        uint[8] calldata groth16Proof
    ) public {
        uint256 userId = addressToUint256(msg.sender);
        require(
            proposalIndex < proposals.length,
            '[ZKFirmaDigitalVote]: Invalid proposal index'
        );
        require(
            userId == signal,
            '[ZKFirmaDigitalVote]: Wrong user signal sent'
        );
        require(
            voteParams.voteScope == nullifierSeed,
            '[ZKFirmaDigitalVote]: Wrong nullifierSeed, you must generate proof with the right seed'
        );
        // Check that user hasn't already voted
        require(
            !checkVoted(nullifier),
            '[ZKFirmaDigitalVote]: User has already voted'
        );

        // Issue credential for this voting campaign
        IZKFirmaDigitalCredentialIssuer(
            ZKFirmaDigitalCredentialIssuerAddr
            ).issueCredential(
                userId,
                nullifierSeed,
                nullifier,
                signal,
                revealArray,
                groth16Proof
        );

        proposals[proposalIndex].voteCount++;
        hasVoted[nullifier] = true;

        emit Voted(msg.sender, proposalIndex);
    }

    function _beforeVerify(bytes32, uint256, bytes memory _userPayload) internal view override {
        (uint256 proposalIndex, UserData memory _userData) = abi.decode(
            _userPayload,
            (uint256, UserData)
        );

        require(
            proposalIndex < proposals.length,
            '[ZikuaniVote]: Invalid proposal index'
        );
        // Check that user hasn't already voted
        require(
            !checkVoted(_userData.nullifier),
            '[ZikuaniVote]: User has already voted'
        );
        // Check for a predefined list of countires to be able to vote
        require(
            _validateCitizenship(voteParams.citizenshipWhitelist, _userData.citizenship),
            "Voting: citizenship is not whitelisted"
        );
    }

    function _afterVerify(bytes32, uint256, bytes memory _userPayload) internal override {
        (uint256 proposalIndex, UserData memory _userData) = abi.decode(
            _userPayload,
            (uint256, UserData)
        );

        proposals[proposalIndex].voteCount++;
        hasVoted[_userData.nullifier] = true;

        emit Voted(msg.sender, proposalIndex);
    }

    function _buildPublicSignals(bytes32, uint256 _currentDate, bytes memory _userPayload)
        internal view override returns (uint256) {
        (uint256 proposalIndex, UserData memory _userData) = abi.decode(
            _userPayload,
            (uint256, UserData)
        );

        // Limit of time for creation of identity
        uint256 _identityCreationTimestampUpperBound = 
            voteParams.identityCreationTimestampUpperBound -
            IPoseidonSMT(getRegistrationSMT()).ROOT_VALIDITY();
        uint256 identityCounterUpperBound = IDENTITY_LIMIT;

        // Limit of number of identities created
        if (_userData.identityCreationTimestamp > 0) {
            _identityCreationTimestampUpperBound = _userData.identityCreationTimestamp;
            identityCounterUpperBound = voteParams.identityCounterUpperBound;
        }

        uint256 builder = PublicSignalsBuilder.newPublicSignalsBuilder(
            selector,
            _userData.nullifier
        );
        builder.withCurrentDate(_currentDate, 1 days);
        builder.withEventIdAndData(
            voteParams.voteScope,
            uint256(uint248(uint256(keccak256(abi.encode(msg.sender, erc1155)))))
        );
        builder.withCitizenship(_userData.citizenship);
        builder.withTimestampLowerboundAndUpperbound(0,
            _identityCreationTimestampUpperBound);
        builder.withIdentityCounterLowerbound(0,
            identityCounterUpperBound);
        builder.withCitizenshipMask(_userData.citizenship);

        return builder;
    }
}
