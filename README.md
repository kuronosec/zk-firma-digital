# ZK Firma Digital

## Overview

ZK Firma Digital is a zero-knowledge protocol that allows Costa Rican Firma Digital card 
owners to prove their identity in a privacy preserving way. It provides a set of tools
to generate and verify proofs, authenticate users and verify proofs off/on-chain.

The project aims to develop a zero-knowledge proof infrastructure solution for enhancing
Costa Rica's digital identity system. Our goal is to strengthen citizen privacy by minimizing
data collection, enabling individuals to access a wide range of valuable services without
disclosing sensitive information.

Documentation: [https://docs.sakundi.io/](https://docs.sakundi.io/)

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

**On Windows:**

Please follow these steps:

* Download the installer by clicking the following link:

[Windows Installer](https://app.sakundi.io:9090/zk-firma-digital-0.5.exe)

* Verify the sha256 hash sum:
```bash
certutil -hashfile "C:\file\path\zk-firma-digital-0.5.exe" SHA256
```
This should be equal to:
```bash
a12d82222533d546b0364a2589ced1ecc024ce49d89881ad94b48c4f2e2b4c61  zk-firma-digital-0.5.exe
```
* If the hash sums is correct, then just run the zk-firma-digital installer.

The Windows installer includes a couple of Javascript dependencies, Nodejs and Snarkjs. The installer also
includes the zkey necessary for generating valid ZK proofs, which makes it a bit heavy.

* Finally, to run the program, introduce your smart card in a USB slot and execute the following command:

```bash
    "C:\Program Files\zk-firma-digital\zk-firma-digital.exe"
```
Or just look for ```Zk Firma Digital``` in the app search.

**On Linux (At moment only Debian):**

To install the software and be able to generate proofs from your Firma Digital card, please follow these steps:
* Download the installer package:
```bash
    wget https://app.sakundi.io:9090/zk-firma-digital_0.5_amd64.deb
```
* Verify the sha256 hash sum:
```bash
sha256sum zk-firma-digital_0.5_amd64.deb
```
This should be equal to:
```bash
f7924230256b432a755746f7e86455f292f4e2659acc1f46e6db09c08c04b407  zk-firma-digital_0.5_amd64.deb
```
* If the hash sums is correct, then install the zk-firma-digital Debian package:
```bash
    sudo dpkg -i zk-firma-digital_0.5_amd64.deb
```
* Finally, to run the program, introduce your smart card in a USB slot and execute the following command:

```bash
    /usr/share/zk-firma-digital/zk-firma-digital.bin
```
Or just look for the app in the search bar.

## Build

**On Linux:**

If you want to build the current installer, execute the following commands:

```bash
git clone https://github.com/kuronosec/zk-firma-digital
cd zk-firma-digital
./builder/build_linux.sh
```

**On Windows:**

Some tooling is needed to build the project in Windows. First of all install [Cygwin](https://cygwin.com/install.html) to be able to use a Linux like development environment. Then, using the Cygwin console run the following commands:

```bash
git clone https://github.com/kuronosec/zk-firma-digital
cd zk-firma-digital
./builder/build_windows.sh
```

## See it working
When you generate a Zk credential from your Firma Digital, which is a JSON file, you can test it by authenticating in this PoC website:

* http://app.sakundi.io:8080/

You can find the source code here: https://github.com/kuronosec/zk-firma-web

Also you can find an example of the built verifiable credential here: https://github.com/kuronosec/zk-firma-digital/blob/main/src/examples/residence-credential.json
