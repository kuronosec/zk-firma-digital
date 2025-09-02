import '@nomiclabs/hardhat-ethers'
import '@openzeppelin/hardhat-upgrades'
import { ethers, upgrades } from 'hardhat'

async function main() {

  const addressesJson = require(
    `../deployed-contracts/ethereum.json`,
  );

  // const addresses = addressesJson.amoyAddresses;
  const addresses = addressesJson.blockdagTestnetAddresses;

  const ZKFirmaDigitalCredentialIssuer = addresses.ZKFirmaDigitalCredentialIssuer;
  const verifierAddress = addresses.TD3QueryProofVerifier;
  const registrationSMTAddress = addresses.RegistrationSMTReplicator;
  
  // Example timestamp upper bound (e.g., current time + 1 month)
  const identityCreationTimestampUpperBound = Math.floor(Date.now() / 1000) + 30 * 24 * 60 * 60;

  // Citizen whitelist example: ["CRI", "COL"]
  const citizenshipWhitelist = [0x435249, 0x434f4c];

  // Example birth date lower bound (e.g., 18 years ago)
  const birthDateLowerbound = Math.floor(Date.now() / 1000) - 18 * 365 * 24 * 60 * 60;

  // Example expiration date lower bound (e.g., must expire after 2026)
  const expirationDateLowerBound = Math.floor(new Date("2026-01-01").getTime() / 1000);

  const identityCounterUpperBound = 1;

  // const voteScope = Math.floor(Math.random() * 100000);
  // For testing purposes give the same constant value
  const voteScope = 75994;

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

  const ZikuaniVoteContract = await ethers.getContractFactory("ZikuaniVote");

  const ZikuaniVoteProxy = await upgrades.deployProxy(
    ZikuaniVoteContract,
    [
      voteParams,
      ZKFirmaDigitalCredentialIssuer,
      registrationSMTAddress,
      verifierAddress,
      // Selector bitmask must match the one used when building the proof
      // 2593 decimal == 0xA21
      2593,
    ],
    { initializer: "__ZikuaniVote_init" }
  );

  await ZikuaniVoteProxy.waitForDeployment();

  console.log(`ZikuaniVote proxy deployed at ${await ZikuaniVoteProxy.getAddress()}`);
}

main().catch(error => {
  console.error(error);
  process.exitCode = 1;
})
