/* eslint-disable @typescript-eslint/no-var-requires */

// This script is used to verify proof against deployed contract.
// Assume proof was generated using production public key.

import '@nomiclabs/hardhat-ethers'
import { Groth16Proof } from 'snarkjs'
import { ethers } from 'hardhat'

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
  // Assumes credential is created in below path
  // The order of the public data in the credential is the following
  // 0 - PublicKeyHash (Goverment public key hash)
  // 1 - Nullifier
  // 2 - Reveal Age above 18
  // 3 - NullifierSeed
  // 4 - SignalHash
  const verifiableCredential = require('../../build/example-credential/credential.json')

  const { ZKFirmaDigital } = require(
    `../deployed-contracts/ethereum.json`,
  ).localPublicKey

  const nullifierSeed = verifiableCredential.proof.signatureValue.public[3]
  const nullifier = verifiableCredential.proof.signatureValue.public[1]
  // Signal used when generating proof
  const signal = process.env.ETHEREUM_ADDRESS || '1';
  // For the moment this is assumed always the case that age > 18
  const revealArray = [verifiableCredential.proof.signatureValue.public[2]]
  // Get proof from credential
  const proof = verifiableCredential.proof.signatureValue.proof

  const ZKFirmaDigitalVerifier = await ethers.getContractAt(
    'ZKFirmaDigital',
    ZKFirmaDigital,
  )

  const address = await ZKFirmaDigitalVerifier.getAddress()
  // console.log(`ZKFirmaDigital : ${address}`)
  // console.log(`nullifierSeed : ${nullifierSeed}`)
  // console.log(`nullifier : ${nullifier}`)
  // console.log(`proof : ${packGroth16Proof(proof)}`)

  console.log(
    await ZKFirmaDigitalVerifier.verifyZKFirmaDigitalProof(
      nullifierSeed,
      nullifier,
      signal,
      revealArray,
      packGroth16Proof(proof),
    ),
  )
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
