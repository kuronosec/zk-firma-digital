import { HardhatUserConfig } from "hardhat/config";
import "@nomicfoundation/hardhat-toolbox";
import "hardhat-dependency-compiler";

const privateKey = process.env.ETHEREUM_ADDRESS_PRIVATE_KEY || '1';

const config: HardhatUserConfig = {
  solidity: "0.8.19",
  paths: {
    sources: "./src", 
    artifacts: "./src",
    cache: "./src",
    tests: "./src"
  },
  networks: {
    localhost: {
      // This is just a hardhat testing address, do not reuse in productionq
      url: "http://127.0.0.1:8545",
      accounts: [privateKey]
    }
  }
};

export default config;
