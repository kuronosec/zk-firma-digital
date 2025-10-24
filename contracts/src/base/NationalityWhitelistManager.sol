// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import {Initializable} from "@openzeppelin/contracts-upgradeable/proxy/utils/Initializable.sol";
import {ContextUpgradeable} from "@openzeppelin/contracts-upgradeable/utils/ContextUpgradeable.sol";

abstract contract NationalityWhitelistManager is Initializable, ContextUpgradeable {
    uint256[] internal nationalityWhitelist;
    mapping(uint256 => bool) internal isNationalityWhitelisted;

    event NationalityWhitelistUpdated(uint256 indexed nationality, bool allowed);

    function __NationalityWhitelistManager_init(uint256[] memory whitelist_) internal onlyInitializing {
        _replaceNationalityWhitelist(whitelist_);
    }

    function getNationalityWhitelist() public view returns (uint256[] memory) {
        return nationalityWhitelist;
    }

    function isNationalityAllowed(uint256 nationality_) public view returns (bool) {
        if (nationalityWhitelist.length == 0) {
            return true;
        }

        return isNationalityWhitelisted[nationality_];
    }

    function _replaceNationalityWhitelist(uint256[] memory whitelist_) internal {
        _clearNationalityWhitelist();

        for (uint256 i = 0; i < whitelist_.length; ++i) {
            uint256 nationality_ = whitelist_[i];
            if (!isNationalityWhitelisted[nationality_]) {
                isNationalityWhitelisted[nationality_] = true;
                nationalityWhitelist.push(nationality_);
                emit NationalityWhitelistUpdated(nationality_, true);
            }
        }
    }

    function _clearNationalityWhitelist() internal {
        for (uint256 i = 0; i < nationalityWhitelist.length; ++i) {
            uint256 nationality_ = nationalityWhitelist[i];
            if (isNationalityWhitelisted[nationality_]) {
                isNationalityWhitelisted[nationality_] = false;
                emit NationalityWhitelistUpdated(nationality_, false);
            }
        }

        delete nationalityWhitelist;
    }
}
