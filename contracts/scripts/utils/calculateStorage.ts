import { keccak256 } from "@ethersproject/keccak256";
import { ethers } from "ethers";

const inputString = "zkfirmadigital.storage.ZKFirmaDigitalCredentialIssuer";
const urlLD =
  "https://raw.githubusercontent.com/kuronosec/zk-firma-digital/main/assets/zk-firma-digital.jsonld";
const schemaType = "ZKFirmaDigital";

const getStorageHash = (inputStr: string) => {
  // Step 1: Compute keccak256 hash of the string "polygonid.storage.BalanceCredentialIssuer"
  const hash1 = keccak256(ethers.toUtf8Bytes(inputStr));

  // Step 2: Interpret the result as a uint256 and subtract 1
  const uint256Value = BigInt(hash1) - BigInt(1);

  // Step 3: ABI-encode the resulting uint256 value
  const coder = new ethers.AbiCoder();
  const encodedValue = coder.encode(["uint256"], [uint256Value.toString()]);

  // Step 4: Compute the keccak256 hash of the ABI-encoded value
  const hash2 = keccak256(encodedValue);

  // Step 5: Perform a bitwise AND operation with the inverse of bytes32(uint256(0xff))
  const mask = BigInt(
    "0xffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff00"
  );
  const result = BigInt(hash2) & mask;

  console.log("Result: ", "0x" + result.toString(16).padStart(64, "0"));

  //0xb775a0063b8bb6b7d39c4f74d1ce330eaeeb81ff68db2df91398ea2d7dc23900;
};

getStorageHash(inputString);