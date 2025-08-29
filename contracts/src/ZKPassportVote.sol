// SPDX-License-Identifier: MIT
pragma solidity 0.8.28;

import '../interfaces/IZKFirmaDigitalVote.sol';

import {IPoseidonSMT} from "@rarimo/passport-contracts/interfaces/state/IPoseidonSMT.sol";
import {PublicSignalsBuilder} from "@rarimo/passport-contracts/sdk/lib/PublicSignalsBuilder.sol";
import {AQueryProofExecutor} from "@rarimo/passport-contracts/sdk/AQueryProofExecutor.sol";
// For upgradeable contracts
import {Initializable} from "@openzeppelin/contracts-upgradeable/proxy/utils/Initializable.sol";

contract ZKPassportVote is Initializable, IZKFirmaDigitalVote, AQueryProofExecutor {
    // List of proposals
    Proposal[] public proposals;
    // Voting parameters
    VoteParams public voteParams;

    uint256 selector;

    // Mapping to track if a userNullifier has already voted
    mapping(uint256 => bool) public hasVoted;
    
    // PublicSignalsBuilder is a library for building public signals
    using PublicSignalsBuilder for uint256;

    uint256 public constant IDENTITY_LIMIT = type(uint32).max;

    // Constructor to initialize proposals
    function __ZKPassportVote_init(
        VoteParams memory _voteParams,
        address _registrationSMT,
        address _verifier
    ) external initializer {
        voteParams.votingQuestion = _voteParams.votingQuestion;
        voteParams.identityCreationTimestampUpperBound = 
            _voteParams.identityCreationTimestampUpperBound;
        voteParams.citizenshipWhitelist = _voteParams.citizenshipWhitelist;
        voteParams.birthDateLowerbound = _voteParams.birthDateLowerbound;
        voteParams.expirationDateLowerBound = _voteParams.expirationDateLowerBound;
        voteParams.identityCounterUpperBound = _voteParams.identityCounterUpperBound;

        for (uint256 i = 0; i < _voteParams.proposalDescriptions.length; i++) {
            proposals.push(Proposal(_voteParams.proposalDescriptions[i], 0));
        }
        voteParams.voteScope = _voteParams.voteScope;
        __AQueryProofExecutor_init(_registrationSMT, _verifier);
    }

    function _beforeVerify(bytes32, uint256, bytes memory _userPayload) internal view override {
        (uint256 proposalIndex, UserData memory _userData) = abi.decode(
            _userPayload,
            (uint256, UserData)
        );

        require(
            proposalIndex < proposals.length,
            '[ZKPassportVote]: Invalid proposal index'
        );
        // Check that user hasn't already voted
        require(
            !checkVoted(_userData.nullifier),
            '[ZKPassportVote]: User has already voted'
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
            uint256(uint248(uint256(keccak256(abi.encode(proposalIndex)))))
        );
        builder.withCitizenship(_userData.citizenship);
        builder.withTimestampLowerboundAndUpperbound(0,
            _identityCreationTimestampUpperBound);
        builder.withIdentityCounterLowerbound(0,
            identityCounterUpperBound);
        builder.withBirthDateLowerboundAndUpperbound(
            voteParams.birthDateLowerbound,
            PublicSignalsBuilder.ZERO_DATE
        );
        builder.withExpirationDateLowerboundAndUpperbound(
            voteParams.expirationDateLowerBound,
            PublicSignalsBuilder.ZERO_DATE
        );

        return builder;
    }

    // Function to get the total number of proposals
    function getProposalCount() public view returns (uint256) {
        return proposals.length;
    }

    // Function to get the total number of votes across all proposals
    function getTotalVotes() public view returns (uint256) {
        uint256 totalVotes = 0;
        uint256 proposalLength = proposals.length;
        for (uint256 i = 0; i < proposalLength; i++) {
            totalVotes += proposals[i].voteCount;
        }
        return totalVotes;
    }

    // Function to check if a user has already voted
    function checkVoted(uint256 _nullifier) public view returns (bool) {
        return hasVoted[_nullifier];
    }

    function _validateCitizenship(
        uint256[] memory whitelist_,
        uint256 elem_
    ) internal pure returns (bool) {
        if (whitelist_.length == 0) {
            return true;
        }

        for (uint256 i = 0; i < whitelist_.length; ++i) {
            if (whitelist_[i] == elem_) {
                return true;
            }
        }

        return false;
    }
}