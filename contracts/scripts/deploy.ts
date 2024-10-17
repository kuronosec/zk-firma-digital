import '@nomiclabs/hardhat-ethers'
import { ethers } from 'hardhat'

const publicKeyHash = "15100764808137121660160871414130376377652473835020058565951744372715764457760";

async function main() {
  const verifier = await ethers.deployContract('Verifier')
  await verifier.waitForDeployment()

  const _verifierAddress = await verifier.getAddress()

  console.log(`Verifier contract deployed to ${_verifierAddress}`)

  const ZKFirmaDigital = await ethers.deployContract('ZKFirmaDigital', [
    _verifierAddress,
    publicKeyHash,
  ])

  await ZKFirmaDigital.waitForDeployment()
  const _ZKFirmaDigitalAddress = await ZKFirmaDigital.getAddress()

  console.log(`ZKFirmaDigital contract deployed to ${_ZKFirmaDigitalAddress}`)

  const ZKFirmaDigitalVote = await ethers.deployContract('ZKFirmaDigitalVote', [
    "Aprueba usted un aumento del 50% de presupuesto para la ciencia en el pais?",
    ["0", "1"],
    _ZKFirmaDigitalAddress,
  ])

  await ZKFirmaDigitalVote.waitForDeployment()

  console.log(
    `ZKFirmaDigitalVote contract deployed to ${await ZKFirmaDigitalVote.getAddress()}`,
  )
}

main().catch(error => {
  console.error(error)
  process.exitCode = 1
})