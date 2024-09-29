# ZK-Firma-Digital

## Overview

ZK Firma Digital is a zero-knowledge protocol that allows Costa Rican Firma Digital card 
owners to prove their identity in a privacy preserving way. It provides a set of tools
to generate and verify proofs, authenticate users and verify proofs off/on-chain.

## Installation

To install the software and be able to generate proofs from your Firma Digital card, please follow these steps:
* Download the installer (Initially only for Linux Debian) and the zkey file:
```bash
    wget http://app.sakundi.io:8080/zk-firma-digital_0.1_amd64.deb
    wget wget http://app.sakundi.io:8080/firma-verifier.zkey
```
* Verify the sha256 hash sum for both files:
```bash
sha256sum zk-firma-digital_0.1_amd64.deb
sha256sum firma-verifier.zkey
```
This should be equal to:
```bash
e785cbe5deb0fcebae53f6f1ff025531884ec630923db4b322040ffdff657d77  zk-firma-digital_0.1_amd64.deb
91ad03aa0e33430d29361ae450f01d7a4992e068a7d6dddf954886fc4205aa21  firma-verifier.zkey
```
* If the hash sums are correct, then install the zk-firma-digital Debian package:
```bash
    sudo dpkg -i zk-firma-digital_0.1_amd64.deb
```
* Then, move the firma-verifier.zkey to the required directory:
```bash
    sudo mv firma-verifier.zkey /usr/share/zk-firma-digital/zk-artifacts/
```
* Finally, to run the program, introduce your smart card in a USB slot and execute the following command:

```bash
    /usr/share/zk-firma-digital/zk-firma-digital.bin
```

## Build

If you want to build the current installer, execute the following command:

```bash
./builder/build_linux.sh
```
