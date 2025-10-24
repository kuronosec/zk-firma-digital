import { ethers, upgrades } from 'hardhat';
import fs from 'fs';
import path from 'path';

type DeployConfig = {
  identityCreationTimestampUpperBound: bigint;
  identityCounterUpperBound: bigint;
  birthDateLowerbound: bigint;
  birthDateUpperbound: bigint;
  expirationDateLowerBound: bigint;
  expirationDateUpperBound: bigint;
  transferScope: bigint;
  selector: bigint;
  nationalityWhitelist: bigint[];
  senderBlacklist: string[];
  destinationWhitelist: string[];
  registrationSMT: string;
  verifier: string;
};

async function main() {
  const [deployer] = await ethers.getSigners();

  const configPath = path.join(__dirname, 'deploy_blacklist_transfer_config.json');
  if (!fs.existsSync(configPath)) {
    throw new Error(`Missing deployment config at ${configPath}`);
  }

  const config: DeployConfig = JSON.parse(fs.readFileSync(configPath, 'utf8'));

  console.log('Deploying ZikuaniBlacklistTransfer with account:', deployer.address);

  const Transfer = await ethers.getContractFactory('ZikuaniBlacklistTransfer');

  const transferParams = {
    identityCreationTimestampUpperBound: config.identityCreationTimestampUpperBound,
    identityCounterUpperBound: config.identityCounterUpperBound,
    birthDateLowerbound: config.birthDateLowerbound,
    birthDateUpperbound: config.birthDateUpperbound,
    expirationDateLowerBound: config.expirationDateLowerBound,
    expirationDateUpperBound: config.expirationDateUpperBound,
    transferScope: config.transferScope,
  };

  const contract = await upgrades.deployProxy(
    Transfer,
    [
      transferParams,
      config.nationalityWhitelist,
      config.senderBlacklist,
      config.destinationWhitelist,
      config.registrationSMT,
      config.verifier,
      config.selector,
    ],
    {
      initializer: 'initialize',
    }
  );

  await contract.waitForDeployment();

  const address = await contract.getAddress();
  console.log(`ZikuaniBlacklistTransfer deployed at ${address}`);

  const outputPath = path.join(__dirname, 'deploy_blacklist_transfer_output.json');
  fs.writeFileSync(
    outputPath,
    JSON.stringify(
      {
        contract: address,
        network: process.env.HARDHAT_NETWORK,
        deployer: deployer.address,
      },
      null,
      2
    )
  );

  console.log(`Deployment details written to ${outputPath}`);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
