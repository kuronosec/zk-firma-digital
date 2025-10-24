// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import {Initializable} from "@openzeppelin/contracts-upgradeable/proxy/utils/Initializable.sol";
import {ContextUpgradeable} from "@openzeppelin/contracts-upgradeable/utils/ContextUpgradeable.sol";

abstract contract SenderBlacklistManager is Initializable, ContextUpgradeable {
    mapping(address => bool) internal senderBlacklist;
    address[] private senderBlacklistAccounts;
    mapping(address => bool) private isSenderBlacklistTracked;

    event SenderBlacklistUpdated(address indexed account, bool isBlacklisted);

    function __SenderBlacklistManager_init(address[] memory initialBlacklist) internal onlyInitializing {
        for (uint256 i = 0; i < initialBlacklist.length; ++i) {
            _setSenderBlacklistStatus(initialBlacklist[i], true);
        }
    }

    function isSenderBlacklisted(address account) public view returns (bool) {
        return senderBlacklist[account];
    }

    function getSenderBlacklist() public view returns (address[] memory) {
        uint256 length = senderBlacklistAccounts.length;
        uint256 count;

        for (uint256 i = 0; i < length; ++i) {
            if (senderBlacklist[senderBlacklistAccounts[i]]) {
                unchecked {
                    ++count;
                }
            }
        }

        address[] memory blacklist_ = new address[](count);
        uint256 index;

        for (uint256 i = 0; i < length; ++i) {
            address account = senderBlacklistAccounts[i];
            if (senderBlacklist[account]) {
                blacklist_[index] = account;
                unchecked {
                    ++index;
                }
            }
        }

        return blacklist_;
    }

    function _setSenderBlacklistStatus(address account, bool status) internal {
        require(account != address(0), "SenderBlacklist: zero address");

        if (senderBlacklist[account] == status) {
            return;
        }

        senderBlacklist[account] = status;

        if (status && !isSenderBlacklistTracked[account]) {
            isSenderBlacklistTracked[account] = true;
            senderBlacklistAccounts.push(account);
        }

        emit SenderBlacklistUpdated(account, status);
    }
}
