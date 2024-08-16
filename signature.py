import json
import hashlib
import base64
import os

from PyKCS11 import *

class Signature():
    def __init__(self, pin):
        """
            Initialize stuff
        """
        self.pin = pin

        # Check what operation system we re running on
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
                json_data = f.read()

            # Canonicalize and hash the JSON data (using SHA-256)
            hashed_data = hashlib.sha256(json_data.encode('utf-8')).digest()

            # Sign the hash using the private key
            mechanism = PyKCS11.Mechanism(PyKCS11.CKM_SHA256_RSA_PKCS, None)
            signature = session.sign(private_key, hashed_data, mechanism)

            # Base64 encode the signature
            signature_base64 = base64.b64encode(bytearray(signature)).decode('utf-8')

            # Add the signature back into the JSON data
            signed_json = json.loads(json_data)
            signed_json['signature'] = signature_base64

            # Save the signed JSON to a new file
            file_name = os.path.basename(file_path)
            file_only_path = os.path.dirname(file_path)
            signed_json_file_path = file_only_path+"/"+"signed-"+file_name

            with open(signed_json_file_path, "w") as f:
                json.dump(signed_json, f, indent=4)

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
