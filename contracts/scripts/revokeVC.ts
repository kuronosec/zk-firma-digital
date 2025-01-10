/* eslint-disable @typescript-eslint/no-var-requires */

// This script is used to verify proof against deployed contract.
// Assume proof was generated using production public key.

import '@nomiclabs/hardhat-ethers'
import { Groth16Proof } from 'snarkjs'
import { ethers } from 'hardhat'
import * as os from "os"
import * as path from "path"

type BigNumberish = string | bigint

async function main() {
  // Get the home directory
  const homeDirectory: string = os.homedir();
  // Construct a file path inside the home directory
  const VCFilePath: string = path.join(homeDirectory, ".zk-firma-digital/credentials/credential.json");
  // Assumes credential is created in below path
  // The order of the public data in the credential is the following
  // 0 - PublicKeyHash (Goverment public key hash)
  // 1 - Nullifier
  // 2 - Reveal Age above 18
  // 3 - NullifierSeed
  // 4 - SignalHash
  const verifiableCredential = require(VCFilePath)

  const addressesJson = require(
    `../deployed-contracts/ethereum.json`,
  )

  const addresses = addressesJson.amoyAddresses;

  const owner = (await ethers.getSigners())[0];
  const ownerAddress = await owner.getAddress();

  const userId = ownerAddress;
  const nullifierSeed = verifiableCredential.proof.signatureValue.public[3];
  const nullifier = verifiableCredential.proof.signatureValue.public[1];
  // Signal used when generating proof
  const signal = process.env.ETHEREUM_ADDRESS || '1';
  // For the moment this is assumed always the case that age > 18
  const revealArray = [verifiableCredential.proof.signatureValue.public[2]];
  // Get proof from credential
  const proof = verifiableCredential.proof.signatureValue.proof;

  const ZKFirmaDigitalCredentialIssuer = await ethers.getContractAt(
    'ZKFirmaDigitalCredentialIssuer',
    addresses.ZKFirmaDigitalCredentialIssuer,
  );

  try {
    // Call the revokeClaimAndTransit function to retrieve the credentials for the user
    console.log(await ZKFirmaDigitalCredentialIssuer.revokeClaimAndTransit(
      0
    ));
  } catch (error) {
    // Catch and log the error

    // Display a user-friendly message
    console.error("Error during proxy deployment:");

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
