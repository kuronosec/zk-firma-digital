/* eslint-disable @typescript-eslint/no-var-requires */

// This script is used to verify proof against deployed contract.
// Assume proof was generated using production public key.

import '@nomiclabs/hardhat-ethers'
import { Groth16Proof } from 'snarkjs'
import { ethers } from 'hardhat'
import * as os from "os"
import * as path from "path"

type BigNumberish = string | bigint

export type PackedGroth16Proof = [
  BigNumberish,
  BigNumberish,
  BigNumberish,
  BigNumberish,
  BigNumberish,
  BigNumberish,
  BigNumberish,
  BigNumberish
]

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

  // const userId = ownerAddress;
  const userId = BigInt('26591510467413365423581463608483105278265869749887044347635609912909668609');
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
    console.log(
      await ZKFirmaDigitalCredentialIssuer.issueCredential(
        userId,
        nullifierSeed,
        nullifier,
        signal,
        revealArray,
        packGroth16Proof(proof),
      ),
    )
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

/**
 * Packs a proof into a format compatible with ZKFirmaDigital.sol contract.
 * @param originalProof The proof generated with SnarkJS.
 * @returns The proof compatible with Semaphore.
 */
function packGroth16Proof(
  groth16Proof: Groth16Proof
): PackedGroth16Proof {
  return [
    groth16Proof.pi_a[0],
    groth16Proof.pi_a[1],
    groth16Proof.pi_b[0][1],
    groth16Proof.pi_b[0][0],
    groth16Proof.pi_b[1][1],
    groth16Proof.pi_b[1][0],
    groth16Proof.pi_c[0],
    groth16Proof.pi_c[1],
  ]
}

// We recommend this pattern to be able to use async/await everywhere
// and properly handle errors.
main().catch(error => {
  console.error(error)
  process.exitCode = 1
})
