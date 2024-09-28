# ZK-Firma-Digital

## Overview

ZK Firma Digital is a zero-knowledge protocol that allows Costa Rican Firma Digital card 
owners to prove their identity in a privacy preserving way. It provides a set of tools
to generate and verify proofs, authenticate users and verify proofs off/on-chain.

## Installation

To install the software and be able to generate proofs from your Firma Digital card, please follow these steps:
* Download the installer (Initially only for Linux Debian) and necessary files:
```bash
    * wget http://app.sakundi.io:8080/zk-firma-digital_0.1_amd64.deb
    * wget http://app.sakundi.io:8080/zk-firma-digital_0.1_amd64.deb.sha256.txt
    * wget wget http://app.sakundi.io:8080/firma-verifier.zkey
    * wget http://app.sakundi.io:8080/firma-verifier.zkey.sha256.txt
```
* Verify the sha256 hash sum for both files.
* If the hash sum is correct, then install zk-firma-digital:
```bash
    * sudo dpkg -i release/zk-firma-digital_0.1_amd64.deb
```
* Move the firma-verifier.zkey to the required directory:
```bash
    sudo mv firma-verifier.zkey /usr/share/zk-firma-digital/zk-artifacts/
```
* Finally, to run the program, introduce your smart card in a USB slot and execute the following command:

```bash
/usr/share/zk-firma-digital/zk-firma-digital.bin
```
