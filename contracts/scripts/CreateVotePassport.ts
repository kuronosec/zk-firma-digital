/* eslint-disable @typescript-eslint/no-var-requires */

// This script is used to verify proof against deployed contract.
// Assume proof was generated using production public key.

import '@nomiclabs/hardhat-ethers'
import { ethers } from 'hardhat'
import * as os from "os"
import * as path from "path"
import { ZkProof } from '@rarimo/zk-passport'
import { encodeAbiParameters, encodeFunctionData, parseAbiParameters, toHex } from 'viem'

function buildVoteArguments(proof: ZkProof, vote: bigint) {
  if (!proof.proof.piA.length || !proof.proof.piB.length || !proof.proof.piC.length) {
    throw new Error('Invalid proof structure')
  }

  const nullifier = BigInt(proof.pubSignals[0])
  const citizenship = BigInt(proof.pubSignals[6])
  const identityCreationTimestamp = BigInt(proof.pubSignals[15])

  const root = BigInt(proof.pubSignals[11])
  const currentDate = BigInt(proof.pubSignals[13])

  const a = [BigInt(proof.proof.piA[0]), BigInt(proof.proof.piA[1])] as const
  const b = [
    [BigInt(proof.proof.piB[0][1]), BigInt(proof.proof.piB[0][0])],
    [BigInt(proof.proof.piB[1][1]), BigInt(proof.proof.piB[1][0])],
  ] as const
  const c = [BigInt(proof.proof.piC[0]), BigInt(proof.proof.piC[1])] as const

  return {
    args: [
      toHex(root, { size: 32 }),
      currentDate,
      encodeAbiParameters(parseAbiParameters('uint256, (uint256, uint256, uint256)'), [
        vote as bigint,
        [nullifier, citizenship, identityCreationTimestamp],
      ]),
      { a, b, c },
    ] as const,
  }
}

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
  // 4 - Signal
  const verifiableCredential = require(VCFilePath)

  const addressesJson = require(
    `../deployed-contracts/ethereum.json`,
  )

  const addresses = addressesJson.blockdagTestnetAddresses;

  const owner = (await ethers.getSigners())[0];
  const ownerAddress = await owner.getAddress();

  const proof = verifiableCredential;
  // console.log(proof);

  const { args } = buildVoteArguments(proof, BigInt(1n));
  // Get proof from credential

  const ZikuaniVote = await ethers.getContractAt(
    'ZikuaniVote',
    addresses.ZikuaniVote,
  );

   // console.log("args: ", args);
   console.log("ownerAddress: ", ownerAddress);
   console.log("addresses.ZikuaniVote: ", addresses.ZikuaniVote);

  const [registrationRoot, currentDate, userPayload, zkPoints_] = args;

  try {
    console.log(
      await ZikuaniVote.voteParams(),
    )
    console.log("Get public signals");
    const chainSignals = await ZikuaniVote.getPublicSignals(registrationRoot, currentDate, userPayload);
    console.log('contract public signals:', chainSignals);
    // console.log('proof pubSignals:', proof.pubSignals);
    console.log(
      "proof pubSignals (hex):",
      proof.pubSignals.map((s: string) => "0x" + BigInt(s).toString(16))
    );
    console.log(
      await ZikuaniVote.execute(registrationRoot,
        currentDate,
        userPayload,
        zkPoints_),
    )
  } catch (error) {
    // Catch and log the error

    // Display a user-friendly message
    console.error("Error during Vote:");

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
