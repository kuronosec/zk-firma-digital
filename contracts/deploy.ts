// contracts/scripts/deploy.ts
import { deployIncrementally } from './deployManager';

async function main() {
  // For amoy testnet
  const stateAddress = '0x1a4cC30f2aA0377b0c3bc9848766D90cb4404124';
  
  try {
    const contracts = await deployIncrementally(stateAddress);
    console.log('Deployment completed successfully');
    
    if (contracts.ZKFirmaDigitalCredentialIssuer) {
      console.log(
        `ZKFirmaDigitalCredentialIssuer deployed to: ${await contracts.ZKFirmaDigitalCredentialIssuer.getAddress()}`
      );
    }
  } catch (error) {
    console.error('Error during deployment:', error);
    process.exitCode = 1;
  }
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});