from ethereum_utils import EthereumUtils
from encryption import Encryption
from ethereum_utils import EthereumUtils
from pinata import upload_to_pinata, download_from_pinata

# This is a bacth process that checks for user on-chain requests
# And sends medical certificates through Pinata
if __name__ == "__main__":
    # Create object to communcate to the blockchain
    # In this case its Polygon
    eth_utils = EthereumUtils()

    # Load smart constracts we will be calling:
    # - MedicalCertificateIssuer
    # - ZKFirmaDigitalCredentialIssuer
    eth_utils.load_contracts()

    # Check if there is a new request
    user_request_item = eth_utils.get_medical_certificate_requests()
    # print(user_request_item)

    # Initialize utlities to decrytp and encrypt data with RSA and AES
    encryption = Encryption("./CA-certificates/public_testing_key.pem",
                 private_key_path='./CA-certificates/private_testing_key.pem')

    # For PoC purposes we are going to use the same key
    # pair for users and goverment
    public_key = encryption.load_public_key()
    private_key = encryption.load_private_key()

    # Decrypt the user request
    user_id = int(encryption.decrypt(user_request_item[1], private_key))

    print("Request user medical certificate: "+str(user_id))
    # Encrypt the PDF content with AES and save the output
    # For the moment just lock for the pdf name in a directory
    # TODO: do it in a sensible way
    input_pdf_path = "../assets/"+str(user_id)+"-medical-certificate.pdf"
    output_pdf_path = "../assets/encrypted_output.pdf"

    # Encrypt the certificate and return the AES key to send to the blockchain
    encrypted_aes_key = encryption.encrypt_pdf_content(
        public_key,
        input_pdf_path,
        output_pdf_path
    )

    # Print encrypted AES key for storage/transmission alongside the encrypted file
    # print("Encrypted AES Key:", encrypted_aes_key)

    # Publish the encrypted file to a private Pinata location
    # Get the ipfa has to send to the user
    ipfs_hash = upload_to_pinata(output_pdf_path)

    # Encrypt the ipfs hash as well
    encrypted_ipfs_hash = encryption.encrypt(ipfs_hash, public_key)

    # Now create the medical certificate response
    # The goverment send to the blockchain
    # The encrypted ipfs hash
    # The encrypted aes key
    # And the revocation nonce to remove the current user request
    eth_utils.respond_medical_certificate_request(
        encrypted_ipfs_hash,
        encrypted_aes_key
    )