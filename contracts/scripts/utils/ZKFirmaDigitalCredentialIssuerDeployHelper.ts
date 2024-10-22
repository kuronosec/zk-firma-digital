import { ethers, upgrades, artifacts } from 'hardhat';
import { Contract } from 'ethers';
import { SignerWithAddress } from '@nomicfoundation/hardhat-ethers/signers';
import { deployClaimBuilder, deployIdentityLib } from './deploy-utils';

export class ZKFirmaDigitalCredentialIssuerDeployHelper {
  constructor(
    private signers: SignerWithAddress[],
    private readonly enableLogging: boolean = false
  ) {}

  static async initialize(
    signers: SignerWithAddress[] | null = null,
    enableLogging = false
  ): Promise<ZKFirmaDigitalCredentialIssuerDeployHelper> {
    let sgrs;
    if (signers === null) {
      sgrs = await ethers.getSigners();
    } else {
      sgrs = signers;
    }
    return new ZKFirmaDigitalCredentialIssuerDeployHelper(sgrs, enableLogging);
  }

  async deployCredentialIssuer(
    smtLib: Contract,
    poseidon3: Contract,
    poseidon4: Contract,
    stateContractAddress: string
  ): Promise<{
    ZKFirmaDigitalCredentialIssuer: Contract;
  }> {
    const owner = this.signers[0];

    this.log('======== Credential issuer: deploy started ========');

    const cb = await deployClaimBuilder(true);
    const il = await deployIdentityLib(
      await smtLib.getAddress(),
      await poseidon3.getAddress(),
      await poseidon4.getAddress(),
      true
    );

    this.log('======== Credential issuer: deploy ZK Firma Digital verifier contracts ========');
    const Verifier = await ethers.getContractFactory('Verifier');
    const verifier = await Verifier.deploy();

    const _verifierAddress = await verifier.getAddress();

    const pubkeyHashBigInt = BigInt("15100764808137121660160871414130376377652473835020058565951744372715764457760").toString();

    const ZKFirmaDigitalContract = await ethers.getContractFactory('ZKFirmaDigital');
    const ZKFirmaDigitalVerifier = await ZKFirmaDigitalContract.deploy(
      _verifierAddress,
      pubkeyHashBigInt
    );

    const _ZKFirmaDigitalAddress = await ZKFirmaDigitalVerifier.getAddress();

    const credentialIssuerFactory = await ethers.getContractFactory(
      'ZKFirmaDigitalCredentialIssuer',
      {
        libraries: {
          ClaimBuilder: await cb.getAddress(),
          IdentityLib: await il.getAddress(),
          PoseidonUnit4L: await poseidon4.getAddress()
        }
      }
    );

    // this.log(artifacts.getArtifactPaths());

    const ZKFirmaDigitalCredentialIssuer = await upgrades.deployProxy(
      credentialIssuerFactory,
      [stateContractAddress, _ZKFirmaDigitalAddress],
      {
        unsafeAllow: ['external-library-linking', 'struct-definition', 'state-variable-assignment'],
        initializer: 'initialize(address,address)'
      }
    );

    await ZKFirmaDigitalCredentialIssuer.waitForDeployment();

    this.log(
      `credentialIssuer contract deployed to address ${await ZKFirmaDigitalCredentialIssuer.getAddress()} from ${await owner.getAddress()}`
    );

    this.log('======== Credential issuer: deploy completed ========');

    return {
      ZKFirmaDigitalCredentialIssuer
    };
  }

  private log(...args): void {
    this.enableLogging && console.log(args);
  }
}
