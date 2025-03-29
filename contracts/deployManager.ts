// contracts/scripts/deployManager.ts
import fs from 'fs';
import path from 'path';
import { ethers } from 'hardhat';
import { Contract } from 'ethers';
import { deployPoseidons } from './utils/deploy-poseidons.util';
import { StateDeployHelper } from './utils/StateDeployHelper';
import { ZKFirmaDigitalCredentialIssuerDeployHelper } from './utils/ZKFirmaDigitalCredentialIssuerDeployHelper';

interface DeployedContracts {
  state?: string;
  smtLib?: string;
  credentialIssuer?: string;
  poseidon2?: string;
  poseidon3?: string;
  poseidon4?: string;
  network: string;
}

export class DeploymentManager {
  private deploymentPath: string;
  private deployedContracts: DeployedContracts;

  constructor(network: string) {
    this.deploymentPath = path.join(__dirname, './deploy_output_test.json');
    this.deployedContracts = this.loadDeployment();
    this.deployedContracts.network = network;
  }

  private loadDeployment(): DeployedContracts {
    try {
      if (fs.existsSync(this.deploymentPath)) {
        return JSON.parse(fs.readFileSync(this.deploymentPath, 'utf8'));
      }
    } catch (error) {
      console.log('No existing deployment found or error reading file');
    }
    return { network: '' };
  }

  private saveDeployment() {
    fs.writeFileSync(this.deploymentPath, JSON.stringify(this.deployedContracts, null, 1));
  }

  private async verifyContract(address: string): Promise<boolean> {
    try {
      const code = await ethers.provider.getCode(address);
      return code !== '0x';
    } catch {
      return false;
    }
  }

  async deployPoseidons() {
    const owner = (await ethers.getSigners())[0];
    let shouldDeploy = false;

    // Check if any Poseidon contracts need to be redeployed
    if (this.deployedContracts.poseidon2) {
      const isValid = await this.verifyContract(this.deployedContracts.poseidon2);
      shouldDeploy = !isValid;
    } else {
      shouldDeploy = true;
    }

    if (shouldDeploy) {
      console.log('Deploying Poseidon contracts...');
      const [poseidon2Elements, poseidon3Elements, poseidon4Elements] = await deployPoseidons(
        owner,
        [2, 3, 4]
      );

      this.deployedContracts.poseidon2 = await poseidon2Elements.getAddress();
      this.deployedContracts.poseidon3 = await poseidon3Elements.getAddress();
      this.deployedContracts.poseidon4 = await poseidon4Elements.getAddress();
      this.saveDeployment();

      return { poseidon2Elements, poseidon3Elements, poseidon4Elements };
    } else {
      console.log('Reusing existing Poseidon contracts');
      return {
        poseidon2Elements: await ethers.getContractAt('PoseidonUnit2L', this.deployedContracts.poseidon2!),
        poseidon3Elements: await ethers.getContractAt('PoseidonUnit3L', this.deployedContracts.poseidon3!),
        poseidon4Elements: await ethers.getContractAt('PoseidonUnit4L', this.deployedContracts.poseidon4!)
      };
    }
  }

  async deploySmtLib(stDeployHelper: StateDeployHelper, poseidon2Address: string, poseidon3Address: string) {
    if (this.deployedContracts.smtLib) {
      const isValid = await this.verifyContract(this.deployedContracts.smtLib);
      if (isValid) {
        console.log('Reusing existing SmtLib contract');
        return await ethers.getContractAt('SmtLib', this.deployedContracts.smtLib);
      }
    }

    console.log('Deploying SmtLib contract...');
    const smtLib = await stDeployHelper.deploySmtLib(poseidon2Address, poseidon3Address);
    this.deployedContracts.smtLib = await smtLib.getAddress();
    this.saveDeployment();
    return smtLib;
  }

  async deployCredentialIssuer(
    credentialIssuerDeployer: ZKFirmaDigitalCredentialIssuerDeployHelper,
    smtLib: Contract,
    poseidon3Elements: Contract,
    poseidon4Elements: Contract,
    stateContractAddress: string
  ) {
    if (this.deployedContracts.credentialIssuer) {
      const isValid = await this.verifyContract(this.deployedContracts.credentialIssuer);
      if (isValid) {
        console.log('Reusing existing CredentialIssuer contract');
        return {
          ZKFirmaDigitalCredentialIssuer: await ethers.getContractAt(
            'ZKFirmaDigitalCredentialIssuer',
            this.deployedContracts.credentialIssuer
          )
        };
      }
    }

    console.log('Deploying CredentialIssuer contract...');
    const contracts = await credentialIssuerDeployer.deployCredentialIssuer(
      smtLib,
      poseidon3Elements,
      poseidon4Elements,
      stateContractAddress
    );

    const credentialIssuer = contracts.ZKFirmaDigitalCredentialIssuer;
    this.deployedContracts.credentialIssuer = await credentialIssuer.getAddress();
    this.saveDeployment();
    return contracts;
  }
}

// Export deployment helper function
export async function deployIncrementally(stateAddress: string = '') {
  const networkName = process.env.HARDHAT_NETWORK || 'localhost';
  const deployManager = new DeploymentManager(networkName);

  const owner = (await ethers.getSigners())[0];
  
  // Deploy Poseidon contracts if needed
  const { poseidon2Elements, poseidon3Elements, poseidon4Elements } = await deployManager.deployPoseidons();

  // Deploy SmtLib if needed
  const stDeployHelper = await StateDeployHelper.initialize([owner], true);
  const smtLib = await deployManager.deploySmtLib(
    stDeployHelper,
    await poseidon2Elements.getAddress(),
    await poseidon3Elements.getAddress()
  );

  // Deploy CredentialIssuer if needed
  const credentialIssuerDeployer = await ZKFirmaDigitalCredentialIssuerDeployHelper.initialize([owner], true);
  const contracts = await deployManager.deployCredentialIssuer(
    credentialIssuerDeployer,
    smtLib,
    poseidon3Elements,
    poseidon4Elements,
    stateAddress
  );

  return contracts;
}