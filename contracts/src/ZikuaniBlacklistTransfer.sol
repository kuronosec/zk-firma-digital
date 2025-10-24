// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import {Strings} from "@openzeppelin/contracts/utils/Strings.sol";
import {OwnableUpgradeable} from "@openzeppelin/contracts-upgradeable/access/OwnableUpgradeable.sol";

import {AQueryProofExecutor} from "@rarimo/passport-contracts/sdk/AQueryProofExecutor.sol";
import {IPoseidonSMT} from "@rarimo/passport-contracts/interfaces/state/IPoseidonSMT.sol";
import {PublicSignalsBuilder} from "@rarimo/passport-contracts/sdk/lib/PublicSignalsBuilder.sol";

import {SenderBlacklistManager} from "./base/SenderBlacklistManager.sol";
import {DestinationRegistry} from "./base/DestinationRegistry.sol";
import {NationalityWhitelistManager} from "./base/NationalityWhitelistManager.sol";

/// @title ZikuaniBlacklistTransfer
/// @notice Executes a value transfer after validating a ZK Passport proof,
///         ensuring the caller is not blacklisted and belongs to an allowed nationality.
contract ZikuaniBlacklistTransfer is
    OwnableUpgradeable,
    SenderBlacklistManager,
    DestinationRegistry,
    NationalityWhitelistManager,
    AQueryProofExecutor
{
    using Strings for uint256;
    using PublicSignalsBuilder for uint256;

    struct TransferParams {
        uint256 identityCreationTimestampUpperBound;
        uint256 identityCounterUpperBound;
        uint256 birthDateLowerbound;
        uint256 birthDateUpperbound;
        uint256 expirationDateLowerBound;
        uint256 expirationDateUpperBound;
        uint64 transferScope;
    }

    struct TransferPayload {
        address payable destination;
        UserData userData;
    }

    struct TransferContext {
        address payable destination;
        address sender;
        uint256 amount;
        bool initialized;
    }

    struct UserData {
        uint256 nullifier;
        uint256 nationality;
        uint256 identityCreationTimestamp;
    }

    uint256 private constant IDENTITY_LIMIT = type(uint32).max;

    TransferParams public transferParams;
    uint256 public selector;

    mapping(uint256 => bool) public nullifierUsed;

    TransferContext private activeTransfer;

    event TransferExecuted(
        address indexed sender,
        address indexed destination,
        uint256 amount,
        uint256 nationality,
        uint256 nullifier
    );

    function initialize(
        TransferParams memory params_,
        uint256[] memory nationalityWhitelist_,
        address[] memory senderBlacklist_,
        address[] memory destinationWhitelist_,
        address registrationSMT_,
        address verifier_,
        uint256 selector_
    ) external initializer {
        __Ownable_init(_msgSender());
        __SenderBlacklistManager_init(senderBlacklist_);
        __DestinationRegistry_init(destinationWhitelist_);
        __NationalityWhitelistManager_init(nationalityWhitelist_);
        __AQueryProofExecutor_init(registrationSMT_, verifier_);

        transferParams = params_;
        selector = selector_;
    }

    /// @notice Adds or removes a sender from the blacklist.
    function setSenderBlacklistStatus(address account, bool status) external onlyOwner {
        _setSenderBlacklistStatus(account, status);
    }

    /// @notice Approves a pending destination registration.
    function approveDestination(address account) external onlyOwner {
        _approveDestination(account);
    }

    /// @notice Rejects a pending destination registration.
    function rejectDestination(address account, bool ban) external onlyOwner {
        _rejectDestination(account, ban);
    }

    /// @notice Revokes an approved destination and optionally bans it.
    function revokeDestination(address account, bool ban) external onlyOwner {
        _revokeDestination(account, ban);
    }

    /// @notice Directly sets the ban status for a destination.
    function setDestinationBanStatus(address account, bool banned) external onlyOwner {
        _setDestinationBanStatus(account, banned);
    }

    /// @notice Replaces the nationality whitelist.
    function updateNationalityWhitelist(uint256[] calldata whitelist_) external onlyOwner {
        _replaceNationalityWhitelist(whitelist_);
    }

    /// @notice Withdraws ETH from the contract.
    /// @param recipient Address receiving the funds.
    /// @param amount Amount to withdraw.
    function withdraw(address payable recipient, uint256 amount) external onlyOwner {
        require(recipient != address(0), "ZikuaniBlacklistTransfer: recipient is zero");
        require(amount <= address(this).balance, "ZikuaniBlacklistTransfer: insufficient balance");

        (bool success_, ) = recipient.call{value: amount}("");
        require(success_, "ZikuaniBlacklistTransfer: withdraw failed");
    }

    /// @dev Allows the contract to receive ETH.
    receive() external payable {}

    /// @notice Executes a compliant transfer by validating a ZK proof and forwarding the provided funds.
    /// @param registrationRoot_ The registration Merkle root used when generating the proof.
    /// @param currentDate_ Current date encoded as yyMMdd.
    /// @param userPayload_ Encoded `TransferPayload` data containing the destination and user proof data.
    /// @param zkPoints_ Groth16 proof points.
    function executeTransfer(
        bytes32 registrationRoot_,
        uint256 currentDate_,
        bytes memory userPayload_,
        ProofPoints calldata zkPoints_
    ) external payable {
        require(msg.value > 0, "ZikuaniBlacklistTransfer: zero transfer amount");
        require(!activeTransfer.initialized, "ZikuaniBlacklistTransfer: transfer in progress");

        TransferPayload memory payload_ = abi.decode(userPayload_, (TransferPayload));
        require(
            isDestinationWhitelisted(payload_.destination),
            "ZikuaniBlacklistTransfer: destination not whitelisted"
        );

        activeTransfer = TransferContext({
            destination: payload_.destination,
            sender: msg.sender,
            amount: msg.value,
            initialized: true
        });

        _executeWithCircomProof(registrationRoot_, currentDate_, userPayload_, zkPoints_);

        delete activeTransfer;
    }

    function _beforeVerify(
        bytes32,
        uint256,
        bytes memory userPayload_
    ) internal view override {
        require(activeTransfer.initialized, "ZikuaniBlacklistTransfer: missing transfer context");
        require(activeTransfer.sender == msg.sender, "ZikuaniBlacklistTransfer: sender mismatch");

        require(!isSenderBlacklisted(msg.sender), "ZikuaniBlacklistTransfer: sender blacklisted");

        TransferPayload memory payload_ = abi.decode(userPayload_, (TransferPayload));
        UserData memory userData_ = payload_.userData;

        require(
            payload_.destination == activeTransfer.destination,
            "ZikuaniBlacklistTransfer: destination mismatch"
        );
        require(payload_.destination != address(0), "ZikuaniBlacklistTransfer: destination is zero");
        require(activeTransfer.amount == msg.value, "ZikuaniBlacklistTransfer: amount mismatch");

        require(
            !_isNullifierUsed(userData_.nullifier),
            "ZikuaniBlacklistTransfer: proof already used"
        );
        require(
            isNationalityAllowed(userData_.nationality),
            "ZikuaniBlacklistTransfer: nationality not allowed"
        );
        require(
            isDestinationWhitelisted(activeTransfer.destination),
            "ZikuaniBlacklistTransfer: destination not whitelisted"
        );
        require(
            !isDestinationBanned(activeTransfer.destination),
            "ZikuaniBlacklistTransfer: destination banned"
        );
    }

    function _afterVerify(
        bytes32,
        uint256,
        bytes memory userPayload_
    ) internal override {
        require(activeTransfer.initialized, "ZikuaniBlacklistTransfer: missing transfer context");

        TransferPayload memory payload_ = abi.decode(userPayload_, (TransferPayload));
        UserData memory userData_ = payload_.userData;

        nullifierUsed[userData_.nullifier] = true;

        address payable destination_ = activeTransfer.destination;
        uint256 amount_ = activeTransfer.amount;
        address sender_ = activeTransfer.sender;

        activeTransfer.initialized = false;
        activeTransfer.amount = 0;
        activeTransfer.sender = address(0);
        activeTransfer.destination = payable(address(0));

        require(isDestinationWhitelisted(destination_), "ZikuaniBlacklistTransfer: destination revoked");
        require(!isDestinationBanned(destination_), "ZikuaniBlacklistTransfer: destination banned");
        require(amount_ > 0, "ZikuaniBlacklistTransfer: amount is zero");

        (bool success_, ) = destination_.call{value: amount_}("");
        require(success_, "ZikuaniBlacklistTransfer: transfer failed");

        emit TransferExecuted(
            sender_,
            destination_,
            amount_,
            userData_.nationality,
            userData_.nullifier
        );
    }

    function _buildPublicSignals(
        bytes32,
        uint256 currentDate_,
        bytes memory userPayload_
    ) internal view override returns (uint256) {
        require(activeTransfer.initialized, "ZikuaniBlacklistTransfer: missing transfer context");

        TransferPayload memory payload_ = abi.decode(userPayload_, (TransferPayload));
        UserData memory userData_ = payload_.userData;

        uint256 identityCounterUpperBound_ = IDENTITY_LIMIT;
        uint256 identityCreationTimestampUpperBound_ = transferParams.identityCreationTimestampUpperBound;

        uint256 rootValidity_ = IPoseidonSMT(getRegistrationSMT()).ROOT_VALIDITY();
        if (identityCreationTimestampUpperBound_ > rootValidity_) {
            identityCreationTimestampUpperBound_ -= rootValidity_;
        } else if (identityCreationTimestampUpperBound_ != 0) {
            identityCreationTimestampUpperBound_ = 0;
        }

        if (userData_.identityCreationTimestamp > 0) {
            identityCreationTimestampUpperBound_ = userData_.identityCreationTimestamp;
            if (transferParams.identityCounterUpperBound != 0) {
                identityCounterUpperBound_ = transferParams.identityCounterUpperBound;
            }
        } else if (transferParams.identityCounterUpperBound != 0) {
            identityCounterUpperBound_ = transferParams.identityCounterUpperBound;
        }

        uint256 builder_ = PublicSignalsBuilder.newPublicSignalsBuilder(
            selector,
            userData_.nullifier
        );

        builder_.withCurrentDate(currentDate_, 1 days);
        builder_.withEventIdAndData(
            transferParams.transferScope,
            uint256(
                uint248(
                    uint256(
                        keccak256(
                            abi.encode(
                                msg.sender,
                                activeTransfer.destination,
                                activeTransfer.amount
                            )
                        )
                    )
                )
            )
        );
        builder_.withNationality(userData_.nationality);
        builder_.withCitizenship(userData_.nationality);
        builder_.withTimestampLowerboundAndUpperbound(0, identityCreationTimestampUpperBound_);
        builder_.withIdentityCounterLowerbound(0, identityCounterUpperBound_);
        builder_.withCitizenshipMask(userData_.nationality);

        if (
            transferParams.birthDateLowerbound != 0 ||
            transferParams.birthDateUpperbound != 0
        ) {
            builder_.withBirthDateLowerboundAndUpperbound(
                transferParams.birthDateLowerbound,
                transferParams.birthDateUpperbound
            );
        }

        if (
            transferParams.expirationDateLowerBound != 0 ||
            transferParams.expirationDateUpperBound != 0
        ) {
            builder_.withExpirationDateLowerboundAndUpperbound(
                transferParams.expirationDateLowerBound,
                transferParams.expirationDateUpperBound
            );
        }

        return builder_;
    }

    function _isNullifierUsed(uint256 nullifier_) internal view returns (bool) {
        return nullifierUsed[nullifier_];
    }

    function _executeWithCircomProof(
        bytes32 registrationRoot_,
        uint256 currentDate_,
        bytes memory userPayload_,
        ProofPoints calldata zkPoints_
    ) internal {
        _beforeVerify(registrationRoot_, currentDate_, userPayload_);

        uint256 builder_ = _buildPublicSignals(registrationRoot_, currentDate_, userPayload_);
        builder_.withIdStateRoot(registrationRoot_);

        uint256[] memory publicSignals_ = PublicSignalsBuilder.buildAsUintArray(builder_);

        if (!_verifyCircomProofInternal(zkPoints_, publicSignals_)) {
            revert InvalidCircomProof(publicSignals_, zkPoints_);
        }

        _afterVerify(registrationRoot_, currentDate_, userPayload_);
    }

    function _verifyCircomProofInternal(
        ProofPoints calldata zkPoints_,
        uint256[] memory pubSignals_
    ) internal view returns (bool) {
        string memory funcSign_ = string(
            abi.encodePacked(
                "verifyProof(uint256[2],uint256[2][2],uint256[2],uint256[",
                pubSignals_.length.toString(),
                "])"
            )
        );

        (bool success_, bytes memory returnData_) = getVerifier().staticcall(
            abi.encodePacked(
                abi.encodeWithSignature(funcSign_, zkPoints_.a, zkPoints_.b, zkPoints_.c),
                pubSignals_
            )
        );

        if (!success_) revert FailedToCallVerifyProof();

        return abi.decode(returnData_, (bool));
    }

}
