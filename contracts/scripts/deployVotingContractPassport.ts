import '@nomiclabs/hardhat-ethers'
import '@openzeppelin/hardhat-upgrades'
import { ethers, upgrades } from 'hardhat'

async function main() {

  const verifierAddress = "0x5E49605FDC07F853b3f03b51e687A04e89B29cdF";
  const registrationSMTAddress = "0x85e46721ED2eC04cc9Dfd02C385307cDa0133c32";
  
  // Example timestamp upper bound (e.g., current time + 1 month)
  const identityCreationTimestampUpperBound = Math.floor(Date.now() / 1000) + 30 * 24 * 60 * 60;

  // Citizen whitelist example: ["CRI", "COL"]
  const citizenshipWhitelist = [0x435249, 0x434f4c];

  // Example birth date lower bound (e.g., 18 years ago)
  const birthDateLowerbound = Math.floor(Date.now() / 1000) - 18 * 365 * 24 * 60 * 60;

  // Example expiration date lower bound (e.g., must expire after 2026)
  const expirationDateLowerBound = Math.floor(new Date("2026-01-01").getTime() / 1000);

  const identityCounterUpperBound = 1;

  const voteScope = Math.floor(Math.random() * 100000);

  const voteParams = {
    votingQuestion: 
      "¿Está usted de acuerdo con que se apruebe la LEY DE MERCADO DE CRIPTOACTIVOS en Costa Rica?",
    proposalDescriptions: 
      ["Sí, estoy de acuerdo.", "No, no estoy de acuerdo."],
    identityCreationTimestampUpperBound,
    citizenshipWhitelist,
    birthDateLowerbound,
    expirationDateLowerBound,
    identityCounterUpperBound,
    voteScope
  };

  console.log("Vote params: ", JSON.stringify(voteParams, null, 2));

  console.log(`verifier contract deployed to ${verifierAddress}`);

  const ZKPassportVoteContract = await ethers.getContractFactory("ZKPassportVote");

  const zkPassportVoteProxy = await upgrades.deployProxy(
    ZKPassportVoteContract,
    [
      voteParams,
      registrationSMTAddress,
      verifierAddress,
      // Selector bitmask must match the one used when building the proof
      // 2593 decimal == 0xA21
      2593,
    ],
    { initializer: "__ZKPassportVote_init" }
  );

  await zkPassportVoteProxy.waitForDeployment();

  console.log(`ZKPassportVote proxy deployed at ${await zkPassportVoteProxy.getAddress()}`);
}

main().catch(error => {
  console.error(error);
  process.exitCode = 1;
})
