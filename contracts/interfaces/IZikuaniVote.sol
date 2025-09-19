// SPDX-License-Identifier: GPL-3.0
pragma solidity ^0.8.20;

interface IZikuaniVote {

    struct Proposal {
        string description;
        uint256 voteCount;
    }

    struct UserData {
        uint256 nullifier;
        uint256 citizenship;
        uint256 identityCreationTimestamp;
    }

    struct VoteParams {
        string votingQuestion;
        string[] proposalDescriptions;
        uint256 identityCreationTimestampUpperBound;
        uint256[] citizenshipWhitelist;
        uint256 birthDateLowerbound;
        uint256 expirationDateLowerBound;
        uint256 identityCounterUpperBound;
        // A random number to use as nullifier seed.
        // We need a different number for each vote contract to avoid double voting
        uint64 voteScope;
    }

    event Voted(address indexed _from, uint256 indexed _propositionIndex);
}
