import os

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding as sym_padding
from PyPDF2 import PdfReader, PdfWriter

class Encryption:
    def __init__(self, public_key_path, private_key_path=None):
        self.public_key_path = public_key_path
        self.private_key_path = private_key_path

    def load_public_key(self):
        # Load the public key from the PEM file
        public_key = None
        with open(self.public_key_path, "rb") as pem_file:
            public_key = serialization.load_pem_public_key(
                pem_file.read(),
                backend=default_backend()
            )
        return public_key
    
    def load_private_key(self):
        # Load the private key from the PEM file
        private_key = None
        with open(self.private_key_path, "rb") as pem_file:
            private_key = serialization.load_pem_private_key(
                pem_file.read(),
                password=None,
            )
        return private_key

    def encrypt(self, data, public_key):

        # Encrypt data with the public key
        encrypted_data = public_key.encrypt(
            data.encode("utf-8"),
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

        return encrypted_data
    
    def generate_testing_key_pair(self, path):
        # Generate private key
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )

        # Extract the public key from the private key
        public_key = private_key.public_key()

        # Save the private key to a PEM file
        with open(path+"private_testing_key.pem", "wb") as private_file:
            private_file.write(
                private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption()  # No password encryption for testing
                )
            )

        # Save the public key to a PEM file
        with open(path+"public_testing_key.pem", "wb") as public_file:
            public_file.write(
                public_key.public_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PublicFormat.SubjectPublicKeyInfo
                )
            )

    def decrypt(self, encrypted_data, private_key):
        # Decrypt the data
        try:
            decrypted_data = private_key.decrypt(
                encrypted_data,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            print("Decrypted Message:", decrypted_data)
            return decrypted_data
        except Exception as e:
            print("Decryption failed:", e)

    # Function to encrypt the PDF content with AES
    def encrypt_pdf_content(self, public_key, input_pdf_path, output_pdf_path):

        # AES Key Generation
        aes_key = os.urandom(32)  # AES-256 key (32 bytes)

        # Encrypt the AES key with RSA
        encrypted_aes_key = public_key.encrypt(
            aes_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

        # Read the PDF content
        reader = PdfReader(input_pdf_path)
        writer = PdfWriter()

        # Add all pages to the writer
        for page in reader.pages:
            writer.add_page(page)

        # Save the unencrypted PDF data to bytes
        pdf_data = bytearray()
        with open("temp_unencrypted.pdf", "wb") as temp_pdf:
            writer.write(temp_pdf)
        with open("temp_unencrypted.pdf", "rb") as temp_pdf:
            pdf_data.extend(temp_pdf.read())
        os.remove("temp_unencrypted.pdf")  # Clean up temporary file

        # Set up AES encryption in CBC mode
        iv = os.urandom(16)
        cipher = Cipher(algorithms.AES(aes_key), modes.CBC(iv), backend=default_backend())
        encryptor = cipher.encryptor()

        # Pad the data to a multiple of the AES block size (128 bits)
        padder = sym_padding.PKCS7(128).padder()
        padded_pdf_data = padder.update(pdf_data) + padder.finalize()

        # Encrypt the padded data
        encrypted_pdf_data = encryptor.update(padded_pdf_data) + encryptor.finalize()

        # Save the IV and encrypted content to output
        with open(output_pdf_path, "wb") as output_file:
            output_file.write(iv)                 # Save the IV (needed for decryption)
            output_file.write(encrypted_pdf_data)  # Save the encrypted PDF data

        print("PDF encrypted and saved as:", output_pdf_path)
        return encrypted_aes_key
    
    def decrypt_pdf_content(self, encrypted_pdf_path, decrypted_pdf_path, aes_key):
        # Read the IV and encrypted content from the file
        with open(encrypted_pdf_path, "rb") as file:
            iv = file.read(16)  # AES block size (128 bits or 16 bytes)
            encrypted_pdf_data = file.read()

        # Set up AES decryption in CBC mode with the given IV
        cipher = Cipher(algorithms.AES(aes_key), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()

        # Decrypt the data
        decrypted_padded_data = decryptor.update(encrypted_pdf_data) + decryptor.finalize()

        # Remove padding (PKCS7)
        unpadder = sym_padding.PKCS7(128).unpadder()
        decrypted_pdf_data = unpadder.update(decrypted_padded_data) + unpadder.finalize()

        # Write the decrypted data to a new PDF file
        with open(decrypted_pdf_path, "wb") as file:
            file.write(decrypted_pdf_data)

        print("Decrypted PDF saved as:", decrypted_pdf_path)


if __name__ == "__main__":
    encryption = Encryption("./CA-certificates/public_testing_key.pem")
    encryption.generate_testing_key_pair("./CA-certificates/")
    public_key = encryption.load_public_key()
    encryption.encrypt("110000000000", public_key)

