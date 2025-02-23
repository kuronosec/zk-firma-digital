import '@nomiclabs/hardhat-ethers'
import { ethers } from 'hardhat'

async function main() {

  const addressesJson = require(
    `../deployed-contracts/ethereum.json`,
  );

  const addresses = addressesJson.amoyAddresses;

  const ZKFirmaDigitalCredentialIssuer = addresses.ZKFirmaDigitalCredentialIssuer;
  const voteScope = Math.floor(Math.random() * 100000);

  console.log(`ZKFirmaDigitalCredentialIssuer contract deployed to ${ZKFirmaDigitalCredentialIssuer}`);

  const ZKFirmaDigitalVote = await ethers.deployContract('ZKFirmaDigitalVote', [
    "Do you approve a 75% increment in the science and technology budget for this year in Costa Rica?",
    ["No, I do not approve an increment.", "Yes, I do approve an increment."],
    ZKFirmaDigitalCredentialIssuer,
    voteScope
  ]);

  await ZKFirmaDigitalVote.waitForDeployment()

  console.log(
    `ZKFirmaDigitalVote contract deployed to ${await ZKFirmaDigitalVote.getAddress()}`,
  );
}

main().catch(error => {
  console.error(error);
  process.exitCode = 1;
})