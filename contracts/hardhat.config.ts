import { HardhatUserConfig } from "hardhat/config";
import "@nomicfoundation/hardhat-toolbox";
import "hardhat-dependency-compiler";
import "@openzeppelin/hardhat-upgrades";
import '@nomicfoundation/hardhat-verify';

const privateKey = process.env.ETHEREUM_ADDRESS_PRIVATE_KEY || '1';

const config: HardhatUserConfig = {
  solidity: {
    compilers: [
      {
        version: '0.8.20'
      },
      {
        version: '0.8.16'
      },
      {
        version: '0.8.28'
      },
    ]
  },
  paths: {
    sources: "./src"
  },
  networks: {
    localhost: {
      // This is just a hardhat testing address, do not reuse in productionq
      url: "http://127.0.0.1:8545",
      accounts: [privateKey]
    },
    amoy: {
      // This is just a hardhat testing address, do not reuse in productionq
      url: "https://rpc-amoy.polygon.technology/",
      accounts: [privateKey]
    },
    "blockdag-testnet": {
      chainId: 1043,
      // A custom rpc node was used to deploy the contracts on blockdag testnet
      // This is not the official rpc node for blockdag testnet
      // You may use this one:  https://test-rpc.primordial.bdagscan.com/
      // url: "http://65.21.121.242:18545",
      url: "https://rpc.primordial.bdagscan.com/",
      accounts: [privateKey],
      // ledgerAccounts: [`${process.env.LEDGER_ACCOUNT}`],
      gasPrice: 1_000_000_000, // 1 gwei in wei,
    },
  }
};

export default config;
