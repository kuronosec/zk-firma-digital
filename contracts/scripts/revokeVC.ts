/* eslint-disable @typescript-eslint/no-var-requires */

// This script is used to verify proof against deployed contract.
// Assume proof was generated using production public key.

import '@nomiclabs/hardhat-ethers'
import { ethers } from 'hardhat'
import * as os from "os"
import * as path from "path"

type BigNumberish = string | bigint

async function main() {
  const addressesJson = require(
    `../deployed-contracts/ethereum.json`,
  )

  const addresses = addressesJson.amoyAddresses;

  const ZKFirmaDigitalCredentialIssuer = await ethers.getContractAt(
    'ZKFirmaDigitalCredentialIssuer',
    addresses.ZKFirmaDigitalCredentialIssuer,
  );

  const revoke_nonce = 3;

  try {
    // Call the revokeClaimAndTransit function to retrieve the credentials for the user
    console.log(await ZKFirmaDigitalCredentialIssuer.revokeClaimAndTransit(
      revoke_nonce
    ));
  } catch (error) {
    // Catch and log the error

    // Display a user-friendly message
    console.error("Error during method call:");

    // If there's a revert reason, log it
    if (error.message) {
      console.error("Error message:", error.message);
    }

    // If there's additional low-level error data, display it
    if (error.data) {
      console.error("Error data:", error.data);
    }

    // Log the full error object for deeper debugging
    console.error(error);
  }
}

// We recommend this pattern to be able to use async/await everywhere
// and properly handle errors.
main().catch(error => {
  console.error(error)
  process.exitCode = 1
})
