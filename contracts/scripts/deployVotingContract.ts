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
    "¿Está usted de acuerdo con que se apruebe la LEY DE MERCADO DE CRIPTOACTIVOS en Costa Rica?",
    ["Sí, estoy de acuerdo.", "No, no estoy de acuerdo."],
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