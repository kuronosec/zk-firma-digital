# ZK Firma Digital

## Overview

ZK Firma Digital is a zero-knowledge protocol that allows Costa Rican Firma Digital card 
owners to prove their identity in a privacy preserving way. It provides a set of tools
to generate and verify proofs, authenticate users and verify proofs off/on-chain.

The project aims to develop a zero-knowledge proof infrastructure solution for enhancing
Costa Rica's digital identity system. Our goal is to strengthen citizen privacy by minimizing
data collection, enabling individuals to access a wide range of valuable services without
disclosing sensitive information.

See the [documentation](https://docs.sakundi.io/) for more details.

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
* And many more!


## Hardware Requirements
To run ZK-Firma-Digital, ensure your system meets at least the following hardware requirements:

| **Component** | **Specification**          |
|---------------|-----------------------------|
| CPU           | 2 Cores + 2 Threads per Core |
| RAM           | 16 GB                        |

## Installation

### Windows

1. Download the installer:
[Windows Installer](https://app.sakundi.io:9090/zk-firma-digital-0.6.3.exe)

2. Verify the sha256 hash:
    ```bash
    certutil -hashfile "C:\file\path\zk-firma-digital-0.6.3.exe" SHA256
    ```
    The result should match:
    ```bash
    c116a271668e9e430116cd335f7bb4128d1af4d387ad7593330850932281cf07  zk-firma-digital-0.6.3.exe
    ```
3. Run the installer if the hash matches.

    Note: The Windows installer includes a couple of Javascript dependencies, Nodejs and Snarkjs. The installer also includes the zkey necessary for generating valid ZK proofs, which makes it a bit heavy.

4. Launch the program: 
    * Insert your smart card into a USB port.
    * Run: 
        ```bash
        "C:\Program Files\zk-firma-digital\zk-firma-digital.exe"
        ```
    * Alternatively, search for ZK Firma Digital in the Start menu.

### Linux (Debian)

1. Download the installer:
    ```bash
    wget https://app.sakundi.io:9090/zk-firma-digital_0.6.3_amd64.deb
    ```
2. Verify the sha256 hash:
    ```bash
    sha256sum zk-firma-digital_0.6.3_amd64.deb
    ```
    The result should match:
    ```bash
    8c8f38ceae2d6b99c07396156c7ea3ccb915e705360ba3cd8bbbe408574622c4  zk-firma-digital_0.6.3_amd64.deb
    ```
3. Install the Debian package:
    ```bash
    sudo dpkg -i zk-firma-digital_0.6.3_amd64.deb
    ```
4. Launch the program:
    * Insert your smart card into a USB port.
    * Run: 
        ```bash
        /usr/share/zk-firma-digital/zk-firma-digital.bin
        ```
    * Alternatively, search for the app in your application launcher.
  
### MacOS

1. Download the installer:
[MacOs Installer](https://app.sakundi.io:9090/zk-firma-digital.pkg)

2. Verify the sha256 hash:
    ```bash
    sha256sum zk-firma-digital.pkg
    ```
    The result should match:
    ```bash
    c671b84bcea6e6d4261947d2e612ead6db9f0b8ead99321333551172662d6a39  zk-firma-digital.pkg
    ```
3. Run the installer if the hash matches.

    Note: The MacOS installer includes a couple of Javascript dependencies, Nodejs and Snarkjs. The installer also includes the zkey necessary for generating valid ZK proofs, which makes it a bit heavy.

4. Launch the program: 
    * Insert your smart card into a USB port.
    * Run: 
        ```bash
        "open /Applications/zk-firma-digital.app/Contents/MacOS/zk-firma-digital"
        ```
    * Alternatively, search for ZK Firma Digital in the Finder menu.

## Build

### Linux

1. Clone the repository:
    ```bash
    git clone https://github.com/kuronosec/zk-firma-digital
    cd zk-firma-digital
    ```
2. Run the build script:
    ```bash
    ./builder/build_linux.sh
    ```

### Windows

1. Install the prerequisites:
    * [Git for Windows](https://gitforwindows.org/)
    * [Python 3.10+](https://www.python.org/downloads/)
    * Install PyInstaller:
        ```bash
        pip install pyinstaller
        ```
    * [Inno Setup](https://jrsoftware.org/)
    * Configure antivirus to exclude the build and release directories.

2. Clone the Repository:
    ```bash
    git clone https://github.com/kuronosec/zk-firma-digital.git
    cd zk-firma-digital
    ```
3. Run the build script:
    ```bash
    ./builder/build_windows.sh
    ```
4. Locate the output files:
    * Executable: `build` directory.
    * Installer: `release` directory.
5. Troubleshooting:
    * Antivirus or Security Issues: During the build process, your antivirus software (including Windows Defender) may flag the generated `.exe` file as a potential threat. This is a common issue with self-built executables. To resolve it:
        1. Add Exclusions: Configure your antivirus or security software to exclude the build and release directories.
            * For Windows Defender:
                1. Open **Windows Security**.
                2. Navigate to **Virus & threat protection**.
                3. Click on **Manage settings** under **Virus & threat protection settings**.
                4. Toggle **Real Time Protection** off temporarily (if necessary).
                5. Scroll down to **Exclusions** and click on **Add or remove exclusions**.
                6. Add the paths for both the `build` and `release` directories to the exclusion list.
        2. Validate the Executable: After adding exclusions, rerun the build process and verify that the executable runs without being flagged.
    * Missing Tools or Command Errors: If you encounter errors like `command not found` when running the build script, it may indicate missing tools or misconfigured system paths. Follow these steps:
        1. Review the build script for errors or missing dependencies.
        2. Consult the repository's issues page or documentation for additional support.

## See it working
To try the system with a decentralized voting system go to:

* Website: [https://voto.sakundi.io/vote](https://voto.sakundi.io/vote)

Other useful links:

* PoC source code: [GitHub Repository](https://github.com/kuronosec/zk-voto-digital)
* Example credential: [residence-credential.json](https://github.com/kuronosec/zk-firma-digital/blob/main/src/examples/residence-credential.json)
