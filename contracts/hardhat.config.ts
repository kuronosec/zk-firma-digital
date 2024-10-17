import { HardhatUserConfig } from "hardhat/config";
import "@nomicfoundation/hardhat-toolbox";
import "hardhat-dependency-compiler";

const config: HardhatUserConfig = {
  solidity: "0.8.19",
  paths: {
    sources: "./src", 
    artifacts: "./src",
    cache: "./src",
    tests: "./src"
  }
};

export default config;
