from ethereum_utils import EthereumUtils
from encryption import Encryption
from pinata import upload_to_pinata, download_from_pinata

# Main entry point for our app
if __name__ == "__main__":
    eth_utils = EthereumUtils()
    eth_utils.load_contracts()
    data = eth_utils.get_medical_certificate_requests()
    encryption = Encryption("./CA-certificates/public_testing_key.pem",
                 private_key_path='./CA-certificates/private_testing_key.pem')
    # For testing purpose we are going to use the same key
    # pair for user and goverment
    public_key = encryption.load_public_key()
    private_key = encryption.load_private_key()
    user_id = int(encryption.decrypt(data, private_key))
    print("Request user medical certificate: "+str(user_id))
    # Encrypt the PDF content with AES and save the output
    input_pdf_path = "../assets/"+str(user_id)+"-medical-certificate.pdf"
    output_pdf_path = "../assets/encrypted_output.pdf"
    encrypted_aes_key = encryption.encrypt_pdf_content(
        public_key,
        input_pdf_path,
        output_pdf_path
    )

    # Print encrypted AES key for storage/transmission alongside the encrypted file
    print("Encrypted AES Key:", encrypted_aes_key)
    aes_key = encryption.decrypt(encrypted_aes_key, private_key)
    print(aes_key)
    encryption.decrypt_pdf_content(
        output_pdf_path,
        "../assets/medical-certificate.pdf",
        aes_key)
    ipfs_hash = upload_to_pinata(output_pdf_path)
    download_from_pinata(
        ipfs_hash,
        "../assets/encrypted_output_pinata.pdf"
    )