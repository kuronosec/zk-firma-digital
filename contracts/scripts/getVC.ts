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

  // const addresses = addressesJson.amoyAddresses;
  const addresses = addressesJson.blockdagTestnetAddresses;

  const owner = (await ethers.getSigners())[0];
  const ownerAddress = await owner.getAddress();

  const userId = ownerAddress;

  const ZKFirmaDigitalCredentialIssuer = await ethers.getContractAt(
    'ZKFirmaDigitalCredentialIssuer',
    addresses.ZKFirmaDigitalCredentialIssuer,
  );

  try {
    // Get list of credentials
    const credentialIds: BigNumberish[] = await ZKFirmaDigitalCredentialIssuer.getUserCredentialIds(
      userId
    );
    const formattedIds = credentialIds.map((id) => id.toString());
    console.log("User Credential IDs:", formattedIds);
    // Call the getUserCredentialIds function to retrieve the credentials for the user
    const credential = await ZKFirmaDigitalCredentialIssuer.getCredential(
      userId, 
      1
    );
    console.log(credential);
    // Display the result
    // Destructure the result
    const credentialData = credential[0];  // INonMerklizedIssuer.CredentialData struct
    const uintArray = credential[1];       // uint256[8] array
    const subjectFields = credential[2];   // INonMerklizedIssuer.SubjectField[] array

    // Format the result as JSON
    const jsonResult = {
      credentialData: {
        credentialId: credentialData.id.toString(),
        context: credentialData.context.toString(),
        type: credentialData._type.toString(),
        issuanceDate: credentialData.issuanceDate.toString(),
      },
      uintArray: uintArray.map((num) => num.toString())
    };

    // Print the result as JSON
    console.log(JSON.stringify(jsonResult, null, 2));
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
