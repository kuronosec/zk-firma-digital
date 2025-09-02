// SPDX-License-Identifier: GPL-3.0
pragma solidity ^0.8.20;

// For upgradeable contracts
import {Initializable} from "@openzeppelin/contracts-upgradeable/proxy/utils/Initializable.sol";

import '../interfaces/IZKFirmaDigitalCredentialIssuer.sol';
import '../interfaces/IZikuaniVote.sol';

abstract contract ZikuaniVoteBase is IZikuaniVote, Initializable {
    // List of proposals
    Proposal[] public proposals;

    // Voting parameters
    VoteParams public voteParams;

    // Mapping to track if a userNullifier has already voted
    mapping(uint256 => bool) public hasVoted;

    // Initializer to setup common voting params (must be called during initialization)
    function __ZikuaniVoteBase_init(
        VoteParams memory _voteParams
    ) internal onlyInitializing {
        // General parameters
        voteParams.votingQuestion = _voteParams.votingQuestion;
        voteParams.voteScope = _voteParams.voteScope;
        for (uint256 i = 0; i < _voteParams.proposalDescriptions.length; i++) {
            proposals.push(Proposal(_voteParams.proposalDescriptions[i], 0));
        }

        // ZK passport related parameters
        voteParams.identityCreationTimestampUpperBound = 
            _voteParams.identityCreationTimestampUpperBound;
        voteParams.citizenshipWhitelist = _voteParams.citizenshipWhitelist;
        voteParams.birthDateLowerbound = _voteParams.birthDateLowerbound;
        voteParams.expirationDateLowerBound = _voteParams.expirationDateLowerBound;
        voteParams.identityCounterUpperBound = _voteParams.identityCounterUpperBound;
    }

    /// @dev Convert an address to uint256, used to check against signal.
    /// @param _addr: msg.sender address.
    /// @return Address msg.sender's address in uint256
    function addressToUint256(address _addr) internal pure returns (uint256) {
        return uint256(uint160(_addr));
    }

    // Function to get the total number of proposals
    function getProposalCount() public view returns (uint256) {
        return proposals.length;
    }

    // Function to get proposal information by index
    function getProposal(
        uint256 proposalIndex
    ) public view returns (string memory, uint256) {
        require(
            proposalIndex < proposals.length,
            '[ZKFirmaDigitalVote]: Invalid proposal index'
        );

        Proposal memory proposal = proposals[proposalIndex];
        return (proposal.description, proposal.voteCount);
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
