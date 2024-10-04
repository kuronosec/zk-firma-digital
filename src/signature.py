# Import required libraries
import json
import hashlib
import base64
import os
import datetime
import binascii

from PyKCS11 import *

# This class helps us to check the Firma Digital certificate signature
# before even trying to create a ZK proof based on it
class Signature():
    def __init__(self, pin):
        """
            Initialize stuff
        """
        self.pin = pin

        # Check what operation system we re running on
        # TODO: make it work on windows
        if os.name == 'nt':
            self.library_path = 'todo'
        else:
            self.library_path = '/usr/lib/x64-athena/libASEP11.so'

    def load_library(self):
        """
        Try to read the smart card to get the stored public certificates
        """
        self.pkcs11 = PyKCS11Lib()
        try:
            self.pkcs11.load(self.library_path)
        except PyKCS11Error as error:
            message = "Hubo un error al cargar la libreria de la smart card"
            print(message+" "+str(error))
            return message

    def sign_file(self, file_path):
        # Open a session with the token
        slots = self.pkcs11.getSlotList(tokenPresent=True)
        if not slots:
            raise Exception("No token found")

        slot = slots[0]

        session = None

        try:
            session = self.pkcs11.openSession(slot, PyKCS11.CKF_SERIAL_SESSION | PyKCS11.CKF_RW_SESSION)

            # Login with your PIN
            session.login(self.pin)

            # Find the private key object
            private_key = session.findObjects([(PyKCS11.CKA_CLASS, PyKCS11.CKO_PRIVATE_KEY)])[0]

            # Load the JSON data
            json_file_path = file_path

            with open(json_file_path, "r") as f:
                verifiable_credential_data = f.read()

            # Canonicalize and hash the JSON data (using SHA-256)
            hashed_data = hashlib.sha256(verifiable_credential_data.encode('utf-8')).digest()

            # Sign the hash using the private key
            mechanism = PyKCS11.Mechanism(PyKCS11.CKM_SHA256_RSA_PKCS, None)
            signature = session.sign(private_key, hashed_data, mechanism)

            # Base64 encode the signature
            signature_value = binascii.hexlify(bytearray(signature))

            # Add the signature back into the JSON data
            verifiable_credential_signed_json = json.loads(verifiable_credential_data)
            verifiable_credential_signed_json['proof'] = {
                "type": "RsaSignature2018",
                "created": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                "proofPurpose": "assertionMethod",
                "verificationMethod": "https://example.com/keys/1",
                "signatureValue": signature_value
            }

            # Create the Verifiable Presentation
            verifiable_presentation_signed_json = {
                "@context": ["https://www.w3.org/2018/credentials/v1"],
                "type": ["VerifiablePresentation"],
                "verifiableCredential": [verifiable_credential_signed_json],
                "holder": "did:example:holder",
                "proof": {
                    "type": "RsaSignature2018",
                    "created": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                    "proofPurpose": "authentication",
                    "verificationMethod": "https://example.com/keys/holder-key",
                    "signatureValue": signature_value
                }
            }

            # Save the signed JSON to a new file
            file_name = os.path.basename(file_path)
            file_only_path = os.path.dirname(file_path)
            verifiable_credential_signed_json_file_path = file_only_path+"/"+"signed-"+file_name
            verifiable_presentation_signed_json_file_path = file_only_path+"/"+"signed-vp-"+file_name

            with open(verifiable_credential_signed_json_file_path, "w") as f:
                json.dump(verifiable_credential_signed_json, f, indent=4, default=str)

            with open(verifiable_presentation_signed_json_file_path, "w") as f:
                json.dump(verifiable_presentation_signed_json, f, indent=4, default=str)

            # Logout and close the session
            session.logout()
            session.closeSession()
        except PyKCS11Error as error:
            message = """Hubo un error al leer la tarjeta,\
                         por favor verifique que esta conectada correctamente\
                         y que ingreso el pin correcto."""
            print(message+" "+str(error))
            return message
        return "Se firmó el archivo correctamente!"
