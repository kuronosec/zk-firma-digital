 DIF hackathon 2024
 
 ## Inspiration

The Costa Rican government offers an advanced digital identity system (Firma Digital) that allows residents or entities to sign documents with a digital identity validated by the central bank as CA and authenticate themselves on various public or private websites and services. However, there is a significant privacy concern related to sensitive data in Costa Rica. A small amount of identity information, such as a national ID number or car plate number, can lead to extensive data collection. Private companies can use this kind of data to harvest citizen data, for instance, by calling and offering them products or services without any previous request or permission. This fact is exceptionally relevant now that big corporations harvest indiscriminate user data to train AI models. Even worse, criminals are collecting this same data to perform identity theft and fraud, sometimes even making fraudulent calls from the jails.

I also take inspiration from my own experience. Me and my family have already received
scam calls, from people that clearly have access to sensitive information about us.
This kind of data comes from companies or institutions that collect too much data
for use cases that do not require them. For instance, once, I had to send a complete
picture of my passport to a sports streaming app just to prove that I was older than
18 years. Not even KYC was necessary in that case. This kind of indiscriminate data
collection finally ends up in the hands of criminals for sale on the "dark web."

In the past, I was a contributor to Tails, the OS used by Snowden to reveal the NSA
massive espionage capabilities because I feel that a world without privacy is a
a world without freedom of expression and without democracy.

## What it does

The project aims to address these privacy issues by creating a zero-knowledge proof infrastructure using blockchain technology and ZK circuits. This solution will enable citizens to verify their identity and provide specific information without revealing actual personal details. By minimizing the distribution of sensitive data across various institutions and companies, we can significantly reduce the risk of data theft. Additionally, this system can authenticate users for diverse services, ensuring they are real individuals and not bots, without requiring sensitive information such as email addresses or phone numbers.

The project allows the Costa Rican Firma Digital holder to create off-chain Verifiable Credentials with Zero-Knowledge proofs. The VC can be used to prove that the person is a resident or citizen of the country without revealing any sensitive information. This is usefull in many use cases, as we will show later.

Using the Privado ID tools, our PoC also allows users to create non-merklized verifiable credentials in the Polygon network. The user can then use those on-chain VCs to request medical certificates to the "government." The "government" would check for VCs and medical credentials requests on-chain in our smart contract, and if they match and come from a real user (resident or citizen), then the "government" creates a medical certificate that corresponds to the user. Then, it is encrypted and uploaded as a private file to Pinata. The app allows the "government" to encrypt the file using AES and then encrypt the AES key using the user's RSA public key. The encrypted key and
the also encrypted IPFS hash are sent to the smart contract so the user can retrieve the file from Pinata. The used VCs are finally revoked from the smart contract, and the user can decrypt and visualize their medical certificate.

## How we built it

We took inspiration from the Anon Aadhaar project and ZK Passports. This kind of project permits us to connect the blockchain world to physical identity mechanisms that already work without revealing sensible information. This is especially useful in public blockchains such as Ethereum or Polygon, where uploaded data is easily visible to anyone.

In our case, we use the Costa Rican Firma Digital, a set of government-signed certificates that allows the user to prove identity and further sign arbitrary documents. This makes it even more powerful than the mentioned projects.

The PoC app is mainly built with Python. Since we use the Circom compiler tools to create Zero-Knowledge proofs, we also use Javascript. We have also created a Web GUI that allows the user to log in and see current VCs.

We have created smart contracts using the Solidity language for the on-chain Verifiable Credentials and medical certificate requests.

We use Pinata to store the encrypted medical certificates the cardholder requests and the government uploads.

## Challenges we ran into

Since we are using PSE tools such as Anon Aadhaar, which uses zero-knowledge proofs but is not compatible with W3C DID and VCs, it was difficult to integrate both technologies. Also, it was challenging to make sense of the compatibility requirement and how to prove that what we do fulfills W3C standards.

## Accomplishments that we're proud of

This is my first project using Circom and Zero-knowledge proofs in general.
Therefore, I am proud to have built a working PoC in such a short time that solves real privacy problems and can already be used in the real world.

Also, it was not my first time using verifiable credential technology, but I could expand my knowledge, allowing me to build better and more private applications in the future and, more importantly, bring ZK Firma Digital to be a solution that millions of people could use.

## What we learned

I have learned about several technologies for the first time, such as Circom and Zero-Knowledge proofs. I have learned to integrate such proofs on-chain and how to create DID and VC on-chain that can be used to solve real-world problems.

I have also used Pinata for the first time, allowing me to create a genuinely Web3 solution.

## What's next for ZK Firma Digital

We want to create products that solve real privacy problems in Costa Rica and beyond. We are confident that ZK Firma Digital will be fundamental to such efforts. There are many use cases where we could apply our technology, such as:

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


## Please provide a written description of how DIDs and VCs were used.

The Firma Digital card contains two X.509 certificates signed by the Costa Rican central bank on behalf of the government. One of the credentials is used for user authentication, and the other one contains a public/key pair to sign arbitrary documents with legal validity. 

We process the authentication certificate with Circom to create Zero-Knowledge proofs based on such certificates, which allows the users to prove their identity without revealing sensitive information.

We create off-chain Verifiable Credentials based on such ZK proofs that can be used for many use cases, such as anonymous authentication, Decentralized anonymous voting, anonymous proof of humanity, Health data privacy, Know Your Customer, Privacy-Preserving Verification, and Anti-Sybil Mechanisms.

The user can also generate on-chain non-merklized VCs using the Privado ID tools. For that, the user needs a Polygon address, which is used for the Descentralized Identity (DID). The VC issuer is a smart contract in Polygon (Amoy) called ZKFirmaDigitalCredentialIssuer. Its address creates the issuer's DID. Those on-chain VCs can be used for the same use cases mentioned above.

For the sake of this hackathon, we allow the users to utilize the VCs to request medical certificates from the government, which needs to be done in a privacy-preserving way. More details are given in the next section.

## Include a text description that should explain the features and functionality of your project.

Our PoC project includes a Python app that allows the user to extract the x.509 authentication certificate from the smart card using a secret PIN. The application checks that the certificate is valid and signed by the government private key.

Then, the certificate is processed by a custom-made Circom circuit that validates the certificate SHA256 checksum and the RSA signature. If everything is correct, the circuit generates a Zero-knowledge proof, demonstrating that the user is a holder of Firma Digital but without revealing sensitive identity information. The app embeds the proof in an off-chain verifiable credential that is not yet compatible with W3C standards.

The user can use such off-chain VCs and a Polygon blockchain address to generate on-chain non-merklized VCs using the Privado ID tools. We have developed a custom smart contract using Solidity that issues credentials in a decentralized form. The contract is called ZKFirmaDigitalCredentialIssuer. Those on-chain VCs are actually compatible with W3C standards. 

As an actual use case, the app allows users to request medical certificates from the "government" in a privacy-preserving way. Another smart contract called MedicalCertificateIssuer validates that VCs already exist for the user, and if that's the case, then the user can insert a new request. The request includes the user's ID number encrypted with the "government"'s RSA public key. The "government" needs to see the ID number to generate the medical certificate. It uses a batch process that checks the MedicalCertificateIssuer smart contract looking for new requests. We will explore private information retrieval technologies for this task in the future. 

When a new request arrives, the "government" prepares the medical certificate for the user. The batch process (also in Python) encrypts the file with a random AES key. Then, the encrypted file is uploaded to Pinata. The process also encrypts the random AES key with the user's public RSA key. Later, it uploads it to the smart contract with an encrypted IPFS hash corresponding to the file in Pinata. 

The app reviews the smart contract for new "government" responses that involve the user's DID. The user gets the encrypted AES key and the IPFS hash and decrypts them with their private RSA key. Once the data is decrypted, the user retrieves the medical certificate from Pinata. This fulfills the requirement for Identity-Based Access Controls For Private Files in Pinata. Finally, the app decrypts the file with the AES key and shows the medical certificate to the user (in PDF format).

We also provide a Web interface where the user can log in with the off-chain VC without providing any sensitive data. There, they can obtain a list of on-chain non-merklized credentials currently stored in the issuer smart contract that are still valid and have not expired.