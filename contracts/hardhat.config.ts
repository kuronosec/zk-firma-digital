import { HardhatUserConfig } from "hardhat/config";
import "@nomicfoundation/hardhat-toolbox";
import "hardhat-dependency-compiler";
import "@openzeppelin/hardhat-upgrades";
import '@nomicfoundation/hardhat-verify';

const privateKey = process.env.ETHEREUM_ADDRESS_PRIVATE_KEY || '1';
const amoyRpcUrl = process.env.POLYGON_AMOY_RPC_URL || "https://rpc-amoy.polygon.technology/";
const polygonRpcUrl = process.env.POLYGON_MAINNET_RPC_URL || "https://polygon-rpc.com";

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
      chainId: 80002,
      url: amoyRpcUrl,
      accounts: [privateKey]
    },
    polygon: {
      chainId: 137,
      url: polygonRpcUrl,
      accounts: [privateKey]
    },
  }
};

export default config;
