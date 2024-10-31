from web3 import Web3
import json
import os
import time
import asyncio

class EthereumUtils:
    def __init__(self):
        # Replace with your provider project URL or local node URL
        provider_url = "https://rpc-amoy.polygon.technology/"
        self.w3 = Web3(Web3.HTTPProvider(provider_url))
    
        # Load the private key from environment variables
        self.private_key = os.getenv("ETHEREUM_ADDRESS_PRIVATE_KEY")
        if self.private_key is None:
            raise ValueError(
                "Private key not found. Set ETHEREUM_ADDRESS_PRIVATE_KEY in your environment."
            )

        # Get the sender's address from the private key
        account = self.w3.eth.account.from_key(self.private_key)
        self.sender_address = account.address

        self.w3.eth.default_account = self.sender_address

        self.user_id = self.sender_address

        if self.w3.is_connected():
            print("Connected to the Polygon Amoy testing network")
        else:
            print("Failed to connect")
        
        self.medical_certificate_issuer_contract = None
        self.firma_digital_credential_issuer_contract = None

    def load_contracts(self):
        # Contract address (replace with the actual address of your contract)
        medical_certificate_issuer = "0xb0EEA758Cd916E67Df4B402f548586B2298Ba62e"
        firma_digital_credential_issuer = "0x40ec4B22a70c0f0D68C6EFd7feB0f5Dca38224e3"

        medical_certificate_issuer_abi = None
        firma_digital_credential_issuer_abi = None

        # Load the ABIs from the JSON files
        with open("../contracts/artifacts/src/MedicalCertificateIssuer.sol/MedicalCertificateIssuer.json", "r") as abi_file:
            medical_certificate_issuer_abi = json.load(abi_file)
        with open("../contracts/artifacts/src/ZKFirmaDigitalCredentialIssuer.sol/ZKFirmaDigitalCredentialIssuer.json", "r") as abi_file:
            firma_digital_credential_issuer_abi = json.load(abi_file)

        # Load the contract
        self.medical_certificate_issuer_contract = self.w3.eth.contract(
            address=medical_certificate_issuer,
            abi=medical_certificate_issuer_abi["abi"]
        )
        self.firma_digital_credential_issuer_contract = self.w3.eth.contract(
            address=firma_digital_credential_issuer,
            abi=firma_digital_credential_issuer_abi["abi"]
        )

        print("Constracts loaded...")


    def create_verifiable_credential(self, verifiable_credential_path):
        # Load the offline verifiable credential
        with open(verifiable_credential_path, "r") as json_file:
            verifiable_credential = json.load(json_file)
        # Call the function and get the results
        try:
            proof = self.pack_groth16_proof(verifiable_credential["proof"]["signatureValue"]["proof"])
            # The order of the public data in the credential is the following
            # 0 - PublicKeyHash (Goverment public key hash)
            # 1 - Nullifier
            # 2 - Reveal Age above 18
            # 3 - NullifierSeed
            # 4 - SignalHash
            transaction = self.firma_digital_credential_issuer_contract.functions.issueCredential(
                int(Web3.to_checksum_address(self.user_id), 16),
                int(verifiable_credential["proof"]["signatureValue"]["public"][3]),
                int(verifiable_credential["proof"]["signatureValue"]["public"][1]),
                int(Web3.to_checksum_address(self.user_id), 16),
                [int(verifiable_credential["proof"]["signatureValue"]["public"][2])],
                proof
            ).build_transaction({
                'from': self.sender_address,
                'nonce': self.w3.eth.get_transaction_count(self.sender_address),
                'gas': 2000000,
                'gasPrice': self.w3.to_wei('50', 'gwei'),
                'chainId': 80002
            })

            # Sign the transaction with the private key
            signed_tx = self.w3.eth.account.sign_transaction(transaction, self.private_key)

            # Send the signed transaction
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)

            # Print transaction hash
            print(f"Transaction sent! Hash: {tx_hash.hex()}")

            # Wait for the transaction receipt to confirm it was successful
            tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            if tx_receipt.status == 1:
                print("Contract call succeeded!")
            else:
                print("Contract call failed.")

        except Exception as e:
            print("Error calling contract function:", e)

    def get_credentials(self):
        # Call the function and get the results
        try:
            credentials = self.firma_digital_credential_issuer_contract.functions.getUserCredentialIds(
                int(Web3.to_checksum_address(self.user_id), 16)
            ).call()

            print(credentials)

            credential_data, uint_array, subject_fields = self.firma_digital_credential_issuer_contract.functions.getCredential(
                int(Web3.to_checksum_address(self.user_id), 16),
                credentials[0]
            ).call()

            print(credential_data)
            print(uint_array)
            print(subject_fields)
            return credentials
        except Exception as e:
            print("Error calling contract function:", e)

    def create_medical_credential_request(self, encrypted_request_id, revocation_nonce):
        # Call the function and get the results
        try:
            transaction = self.medical_certificate_issuer_contract.functions.requestMedicalCertificate(
                int(Web3.to_checksum_address(self.user_id), 16),
                encrypted_request_id,
                revocation_nonce
            ).build_transaction({
                'from': self.sender_address,
                'nonce': self.w3.eth.get_transaction_count(self.sender_address),
                'gas': 2000000,
                'gasPrice': self.w3.to_wei('50', 'gwei'),
                'chainId': 80002
            })

            # Sign the transaction with the private key
            signed_tx = self.w3.eth.account.sign_transaction(transaction, self.private_key)

            # Send the signed transaction
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)

            # Print transaction hash
            print(f"Transaction sent! Hash: {tx_hash.hex()}")

            # Wait for the transaction receipt to confirm it was successful
            tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            if tx_receipt.status == 1:
                print("Contract call succeeded!")
            else:
                print("Contract call failed.")
        except Exception as e:
            print("Error calling contract function:", e)

    def get_medical_certificate_requests(self):
        # Check for new medical request from the users
        while True:
            try:
                print("Getting user request of medical certificates")        
                number_requests = self.medical_certificate_issuer_contract.functions.getUserRequestCount(
                    int(Web3.to_checksum_address(self.user_id), 16)
                ).call()

                print("number_requests:" +str(number_requests))

                if int(number_requests) > 0:
                    user_request_item = self.medical_certificate_issuer_contract.functions.getUserRequest(
                        int(Web3.to_checksum_address(self.user_id), 16),
                        0
                    ).call()
                    return user_request_item
                time.sleep(600)
            except Exception as e:
                print("Error calling contract function:", e)

    def get_medical_certificate_document(self):
        # Call the function and get the results
        try:
            print("Getting created medical certificates")
            medical_certificates = self.medical_certificate_issuer_contract.functions.getGovernmentReponseCount(
                int(Web3.to_checksum_address(self.user_id), 16)
            ).call()

            print(medical_certificates)

            if int(medical_certificates) > 0:
                medical_certificate = self.medical_certificate_issuer_contract.functions.getGovernmentReponse(
                    int(Web3.to_checksum_address(self.user_id), 16),
                    0
                ).call()
                return medical_certificate
            else:
                return None
        except Exception as e:
            print("Error calling contract function:", e)

    def respond_medical_certificate_request(self, ipfs_hash, aes_key, revocation_nonce):
        # Call the function and get the results
        try:
            transaction = self.medical_certificate_issuer_contract.functions.respondMedicalCertificateRequest(
                int(Web3.to_checksum_address(self.user_id), 16),
                ipfs_hash,
                aes_key,
                revocation_nonce
            ).build_transaction({
                'from': self.sender_address,
                'nonce': self.w3.eth.get_transaction_count(self.sender_address),
                'gas': 2000000,
                'gasPrice': self.w3.to_wei('50', 'gwei'),
                'chainId': 80002
            })

            # Sign the transaction with the private key
            signed_tx = self.w3.eth.account.sign_transaction(transaction, self.private_key)

            # Send the signed transaction
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)

            # Print transaction hash
            print(f"Transaction sent! Hash: {tx_hash.hex()}")

            # Wait for the transaction receipt to confirm it was successful
            tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            if tx_receipt.status == 1:
                print("Contract call succeeded!")
            else:
                print("Contract call failed.")
        except Exception as e:
            print("Error calling contract function:", e)

    def pack_groth16_proof(self, groth16_proof):
        return [
            int(groth16_proof["pi_a"][0]),
            int(groth16_proof["pi_a"][1]),
            int(groth16_proof["pi_b"][0][1]),
            int(groth16_proof["pi_b"][0][0]),
            int(groth16_proof["pi_b"][1][1]),
            int(groth16_proof["pi_b"][1][0]),
            int(groth16_proof["pi_c"][0]),
            int(groth16_proof["pi_c"][1]),
        ]