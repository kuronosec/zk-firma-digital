// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import {Initializable} from "@openzeppelin/contracts-upgradeable/proxy/utils/Initializable.sol";
import {ContextUpgradeable} from "@openzeppelin/contracts-upgradeable/utils/ContextUpgradeable.sol";

abstract contract DestinationRegistry is Initializable, ContextUpgradeable {
    mapping(address => bool) internal destinationWhitelist;
    mapping(address => bool) internal destinationBanlist;
    mapping(address => bool) internal pendingDestinations;

    address[] private destinationWhitelistAccounts;
    mapping(address => bool) private isDestinationWhitelistTracked;
    address[] private pendingDestinationAccounts;
    mapping(address => bool) private isPendingDestinationTracked;

    event DestinationWhitelistUpdated(address indexed account, bool isAllowed);
    event DestinationRegistrationRequested(address indexed account);
    event DestinationRegistrationApproved(address indexed account);
    event DestinationRegistrationRejected(address indexed account, bool banned);
    event DestinationRevoked(address indexed account, bool banned);
    event DestinationBanStatusUpdated(address indexed account, bool banned);

    function __DestinationRegistry_init(address[] memory initialWhitelist) internal onlyInitializing {
        for (uint256 i = 0; i < initialWhitelist.length; ++i) {
            _whitelistDestination(initialWhitelist[i]);
        }
    }

    function registerDestination() public {
        address account = _msgSender();

        require(!destinationBanlist[account], "DestinationRegistry: destination banned");
        require(!destinationWhitelist[account], "DestinationRegistry: already whitelisted");
        require(!pendingDestinations[account], "DestinationRegistry: request pending");

        pendingDestinations[account] = true;

        if (!isPendingDestinationTracked[account]) {
            isPendingDestinationTracked[account] = true;
            pendingDestinationAccounts.push(account);
        }

        emit DestinationRegistrationRequested(account);
    }

    function _approveDestination(address account) internal {
        require(account != address(0), "DestinationRegistry: zero address");
        require(pendingDestinations[account], "DestinationRegistry: no pending request");

        pendingDestinations[account] = false;
        if (destinationBanlist[account]) {
            destinationBanlist[account] = false;
            emit DestinationBanStatusUpdated(account, false);
        }

        _whitelistDestination(account);

        emit DestinationRegistrationApproved(account);
    }

    function _rejectDestination(address account, bool ban) internal {
        require(account != address(0), "DestinationRegistry: zero address");
        require(pendingDestinations[account], "DestinationRegistry: no pending request");

        pendingDestinations[account] = false;
        if (ban) {
            destinationBanlist[account] = true;
            emit DestinationBanStatusUpdated(account, true);
        }

        emit DestinationRegistrationRejected(account, ban);
    }

    function _revokeDestination(address account, bool ban) internal {
        require(account != address(0), "DestinationRegistry: zero address");
        require(destinationWhitelist[account], "DestinationRegistry: not whitelisted");

        _removeDestination(account);

        pendingDestinations[account] = false;

        if (ban) {
            destinationBanlist[account] = true;
            emit DestinationBanStatusUpdated(account, true);
        }

        emit DestinationRevoked(account, ban);
    }

    function _setDestinationBanStatus(address account, bool banned) internal {
        require(account != address(0), "DestinationRegistry: zero address");

        if (banned) {
            pendingDestinations[account] = false;
            if (destinationWhitelist[account]) {
                _removeDestination(account);
                emit DestinationRevoked(account, true);
            }
        }

        destinationBanlist[account] = banned;
        emit DestinationBanStatusUpdated(account, banned);
    }

    function isDestinationWhitelisted(address account) public view returns (bool) {
        return destinationWhitelist[account];
    }

    function isDestinationBanned(address account) public view returns (bool) {
        return destinationBanlist[account];
    }

    function hasPendingDestination(address account) public view returns (bool) {
        return pendingDestinations[account];
    }

    function getDestinationWhitelist() public view returns (address[] memory) {
        uint256 length = destinationWhitelistAccounts.length;
        uint256 count;

        for (uint256 i = 0; i < length; ++i) {
            if (destinationWhitelist[destinationWhitelistAccounts[i]]) {
                unchecked {
                    ++count;
                }
            }
        }

        address[] memory whitelist_ = new address[](count);
        uint256 index;

        for (uint256 i = 0; i < length; ++i) {
            address account = destinationWhitelistAccounts[i];
            if (destinationWhitelist[account]) {
                whitelist_[index] = account;
                unchecked {
                    ++index;
                }
            }
        }

        return whitelist_;
    }

    function getPendingDestinations() public view returns (address[] memory) {
        uint256 length = pendingDestinationAccounts.length;
        uint256 count;

        for (uint256 i = 0; i < length; ++i) {
            if (pendingDestinations[pendingDestinationAccounts[i]]) {
                unchecked {
                    ++count;
                }
            }
        }

        address[] memory pending_ = new address[](count);
        uint256 index;

        for (uint256 i = 0; i < length; ++i) {
            address account = pendingDestinationAccounts[i];
            if (pendingDestinations[account]) {
                pending_[index] = account;
                unchecked {
                    ++index;
                }
            }
        }

        return pending_;
    }

    function _whitelistDestination(address account) internal {
        require(account != address(0), "DestinationRegistry: zero address");

        if (!destinationWhitelist[account]) {
            destinationWhitelist[account] = true;
            emit DestinationWhitelistUpdated(account, true);
        }

        if (!isDestinationWhitelistTracked[account]) {
            isDestinationWhitelistTracked[account] = true;
            destinationWhitelistAccounts.push(account);
        }
    }

    function _removeDestination(address account) internal {
        require(account != address(0), "DestinationRegistry: zero address");

        if (destinationWhitelist[account]) {
            destinationWhitelist[account] = false;
            emit DestinationWhitelistUpdated(account, false);
        }
    }
}
