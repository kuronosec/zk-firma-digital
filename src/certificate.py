# Import necessary libraries
import pprint
import os

from asn1crypto import pem, x509
from PyKCS11 import *
from configuration import Configuration

# This class interacts with the Smart Card and extracts the autentication certificate
class Certificate:
    def __init__(self, pin):
        """
            Initialize stuff
        """
        self.config = Configuration()
        self.user_path = self.config.user_path
        self.credentials_path = self.config.credentials_path
        self.pin = pin

        # Check what operation system we re running on
        # TODO: Windows
        if os.name == 'nt':
            self.library_path = 'todo'
        # Linux
        else:
            self.library_path = '/usr/lib/x64-athena/libASEP11.so'

    def get_certificates(self):
        """
        Try to read the smart card to get the stored public certificates
        """
        pkcs11 = PyKCS11Lib()
        try:
            pkcs11.load(self.library_path)
        except PyKCS11Error as error:
            message = "Hubo un error al cargar la libreria de la smart card"
            print(message+" "+str(error))
            return False, message

        session = None

        try:
            session = pkcs11.openSession(0, CKF_SERIAL_SESSION | CKF_RW_SESSION)
            session.login(self.pin)
        except PyKCS11Error as error:
            message = """Hubo un error al leer la tarjeta,\
                         por favor verifique que esta conectada correctamente\
                         y que ingreso el pin correcto."""
            print(message+" "+str(error))
            return False, message

        result = []
        certs = session.findObjects([(CKA_CLASS, CKO_CERTIFICATE)])

        # Extract the certificates to be used later
        for cert in certs:
            cka_value, cka_id = session.getAttributeValue(cert, [CKA_VALUE, CKA_ID])
            cert_der = bytes(cka_value)
            cert = x509.Certificate.load(cert_der)
            common_name = cert.native["tbs_certificate"]["subject"]["common_name"]
            if "AUTENTICACION" in common_name:
                result.append(common_name)

                if not os.path.exists(self.credentials_path):
                    os.makedirs(self.credentials_path)

                # cert is an instance of x509.Certificate
                with open(self.config.certificate_path, 'wb') as f:
                    pprint.pprint(cert.native["tbs_certificate"]["subject"])
                    der_bytes = cert.dump()
                    pem_bytes = pem.armor('CERTIFICATE', der_bytes)
                    f.write(pem_bytes)

        return True, result
