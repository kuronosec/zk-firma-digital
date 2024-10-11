# ZK-Firma-Digital

## Overview

ZK Firma Digital is a zero-knowledge protocol that allows Costa Rican Firma Digital card 
owners to prove their identity in a privacy preserving way. It provides a set of tools
to generate and verify proofs, authenticate users and verify proofs off/on-chain.

The project aims to develop a zero-knowledge proof infrastructure solution for enhancing
Costa Rica's digital identity system. Our goal is to strengthen citizen privacy by minimizing
data collection, enabling individuals to access a wide range of valuable services without
disclosing sensitive information.

## Rationale

The Costa Rican government offers an advanced digital identity system (Firma Digital) that allows residents or entities to sign documents with a digital identity validated by the central bank as CA and authenticate themselves on various public or private websites and services.
However, there is a significant privacy concern related to sensitive data in Costa Rica. A small amount of identity information, such as a national ID number or car plate number, can lead to extensive data collection. Private companies can use this kind of data to harvest citizen data, for instance, by calling and offering them products or services without any previous request or permission. This fact is exceptionally relevant now that big corporations harvest indiscriminate user data to train AI models. Even worse, criminals are collecting this same data to perform identity theft and fraud, sometimes even making fraudulent calls from the jails.

Our project aims to address these privacy issues by developing a zero-knowledge proof infrastructure using blockchain technology and ZK circuits. This solution will enable citizens to verify their identity and provide specific information without revealing actual personal details. By minimizing the distribution of sensitive data across various institutions and companies, we can significantly reduce the risk of data theft. Additionally, this system can authenticate users for diverse services, ensuring they are real individuals and not bots, without requiring sensitive information such as email addresses or phone numbers.

## Potential use cases

* Anonymous authentication
* Descentralized anonymous voting
* Anonymous proof of humanity
* Health data privacy
* Know Your Customer
* Privacy-Preserving Verification
* Anti-Sybil Mechanisms
* DAO Governance
* Quadratic Funding (QF)
* Wallet Recovery
* And many more

## Installation

**On Linux:**

To install the software and be able to generate proofs from your Firma Digital card, please follow these steps:
* Download the installer and the zkey file:
```bash
    wget http://app.sakundi.io:9090/zk-firma-digital_0.2_amd64.deb
    wget http://app.sakundi.io:9090/firma-verifier.zkey
```
* Verify the sha256 hash sum for both files:
```bash
sha256sum zk-firma-digital_0.2_amd64.deb
sha256sum firma-verifier.zkey
```
This should be equal to:
```bash
8608d4330daace89c1573432eddd556b5dfb2608bb24cab0e4a68c2956eddff0  zk-firma-digital_0.2_amd64.deb
91ad03aa0e33430d29361ae450f01d7a4992e068a7d6dddf954886fc4205aa21  firma-verifier.zkey
```
* If the hash sums are correct, then install the zk-firma-digital Debian package:
```bash
    sudo dpkg -i zk-firma-digital_0.2_amd64.deb
```
* Then, move the firma-verifier.zkey to the required directory:
```bash
    sudo mv firma-verifier.zkey /usr/share/zk-firma-digital/zk-artifacts/
```
* Finally, to run the program, introduce your smart card in a USB slot and execute the following command:

```bash
    /usr/share/zk-firma-digital/zk-firma-digital.bin
```

**On Windows:**

Please follow these steps:

* Download the installer from this address, for instance using the browser:
```bash
    http://app.sakundi.io:9090/zk-firma-digital.exe
```
In this case, the installer includes the zkey, which makes it a bit heavy.

* Verify the sha256 hash sum:
```bash
certutil -hashfile C:\file\path\zk-firma-digital.exe SHA256
```
This should be equal to:
```bash
333e488fa8f9a7219c2c1ab738974cdb47ced6d5197cfaedf976b36e661a2ee1  ./zk-firma-digital.exe
```
* If the hash sums is correct, then just run the zk-firma-digital installer.

Before being able to run the app, you need a couple of dependencies:
* Install Nodejs, that you can find in this link:
```bash
    https://nodejs.org/en/download/prebuilt-installer
```
* After Installing Nodejs, run the following command to install Snarkjs:

```bash
    npm install -g snarkjs@latest
```

## Build

If you want to build the current installer, execute the following command:

```bash
./builder/build_linux.sh
```

## See it working
When you generate a Zk credential from your Firma Digital, which is a JSON file, you can test it by authenticating in this PoC website:

* http://app.sakundi.io:8080/

You can find the source code here: https://github.com/kuronosec/zk-firma-web

Also you can find an example of the built verifiable credential here: https://github.com/kuronosec/zk-firma-digital/blob/main/src/examples/residence-credential.json

## Warning

This project is still in the proof-of-concept phase and under heavy development and therefore still not recommended for production environments.
