import fs from 'fs';
import path from 'path';
import { deployPoseidons } from './utils/deploy-poseidons.util';
import { StateDeployHelper } from './utils/StateDeployHelper';
import { ethers } from 'hardhat';
import { ZKFirmaDigitalCredentialIssuerDeployHelper } from './utils/ZKFirmaDigitalCredentialIssuerDeployHelper';
const pathOutputJson = path.join(__dirname, './deploy_output_test.json');

async function main() {
  // const stateAddress = '0x624ce98D2d27b20b8f8d521723Df8fC4db71D79D'; // current iden3 state smart contract on main
  // const stateAddress = '0x134b1be34911e39a8397ec6289782989729807a4'; // current iden3 state smart contract on mumbai
  // const stateAddress = '0x1a4cC30f2aA0377b0c3bc9848766D90cb4404124'; // current iden3 state smart contract on amoy
  const stateAddress = '0x769671b481BA59414733BA95fe8aD2731d6652E6'; // current iden3 state smart contract on blockdag-testnet

  const owner = (await ethers.getSigners())[0];
  const [poseidon2Elements, poseidon3Elements, poseidon4Elements] = await deployPoseidons(
    owner,
    [2, 3, 4]
  );
  const stDeployHelper = await StateDeployHelper.initialize([owner], true);
  const smtLib = await stDeployHelper.deploySmtLib(
    await poseidon2Elements.getAddress(),
    await poseidon3Elements.getAddress()
  );

  const credentialIssuerDeployer =
    await ZKFirmaDigitalCredentialIssuerDeployHelper.initialize([owner], true);
  
  const contracts = await credentialIssuerDeployer.deployCredentialIssuer(
    smtLib,
    poseidon3Elements,
    poseidon4Elements,
    stateAddress
  );

  const credentialIssuer = contracts.ZKFirmaDigitalCredentialIssuer;

  const outputJson = {
    state: stateAddress,
    smtLib: await smtLib.getAddress(),
    credentialIssuer: await credentialIssuer.getAddress(),
    poseidon2: await poseidon2Elements.getAddress(),
    poseidon3: await poseidon3Elements.getAddress(),
    poseidon4: await poseidon4Elements.getAddress(),
    network: process.env.HARDHAT_NETWORK
  };
  fs.writeFileSync(pathOutputJson, JSON.stringify(outputJson, null, 1));
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
