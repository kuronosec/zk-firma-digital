# Import the required libraries
import json
import os
import sys
import logging

from utils import splitToWords, preprocess_message_for_sha256, hash_message
from asn1crypto import pem, x509
from certvalidator import CertificateValidator, ValidationContext, errors
from configuration import Configuration
from signature import Signature

# This class helps to validate the certificate extracted from the smart card
# to see if it actually was signed by the goverment chain of trust
class Verification:
    def __init__(self, pin, signal_hash=None):
        self.pin = pin
        self.signal_hash = signal_hash
        self.config = Configuration()
        self.user_path = self.config.user_path
        self.credentials_path=self.config.credentials_path
        self.user_signature = Signature(pin)

        # We have a folder with the goverment certificates
        self.root_CA_path = self.config.root_CA_path

    # Actually carry our the signature verification process
    def verify_certificate(self, user_certificate_path):
        trust_roots = []
        # Load goverment chain of trust
        with open(self.root_CA_path, 'rb') as f:
            for _, _, der_bytes in pem.unarmor(f.read(), multiple=True):
                trust_roots.append(der_bytes)

        # Load user certificate
        with open(user_certificate_path, 'rb') as f:
            end_entity_cert = f.read()
            if pem.detect(end_entity_cert):
                _, _, end_entity_cert = pem.unarmor(end_entity_cert)
        
        root_cert = x509.Certificate.load(trust_roots[2])
        subject = root_cert.subject
        # Show certificate info
        info = "Datos del certificado Root:\n"
        for rdn in subject.chosen:
            for attr in rdn:
                info= info + f"{attr['type'].native}: {attr['value'].native}\n"
        
        user_cert = x509.Certificate.load(end_entity_cert)
        context = ValidationContext(trust_roots=trust_roots)

        # Finally proceed with the validation
        try:
            validator = CertificateValidator(end_entity_cert, validation_context=context)
            path = validator.validate_usage(set(['digital_signature']))
            info = self.get_certificate_info(user_cert, root_cert)
            return (True, info)
        except errors.PathValidationError as error:
            message = "Certificate signature is not valid!"
            logging.error(message+" "+str(error), exc_info=True)
            return (False, None)
 
    # Get info from the certificate
    def get_certificate_info(self, cert, root_cert):
        # Subject
        subject = cert.subject
        info = "Datos del certificado:\n"
        for rdn in subject.chosen:
            for attr in rdn:
                info= info + f"{attr['type'].native}: {attr['value'].native}\n"

        # Get to be signed data
        maxDataLength = 512 * 6
        tbs_certificate = cert['tbs_certificate']
        tbs_bytes = tbs_certificate.dump()
        byte_array, cert_data_padded_length = preprocess_message_for_sha256(list(tbs_bytes),
                                                                            maxDataLength)

        # Get the public key info from issuer
        public_key_info = root_cert['tbs_certificate']['subject_public_key_info']
        public_key_bytes = public_key_info['public_key'].native
        modulus = public_key_bytes['modulus']

        # Get signature
        signature_bytes = cert.signature
        # Convert the signature to a big integer
        signature_int = int.from_bytes(signature_bytes, byteorder='big')

        # Print the big integer in chunks
        signature_str = splitToWords(signature_int, 121, 17)
        public_key_str = splitToWords(modulus, 121, 17)
        # If the user wants to associate a string with
        # the verifiable credential (Ethereum addres, email, etc)
        signal_hash = None
        try:
            signal_hash = hash_message(self.signal_hash)
        except errors as error:
            logging.error(error, exc_info=True)

        # Nullifier seed
        nullifier_seed = int.from_bytes(os.urandom(4), sys.byteorder)
        self.user_signature.load_library()
        user_signature = self.user_signature.sign_data(tbs_bytes)
        # Convert the signature to a big integer
        user_signature_int = int.from_bytes(user_signature, byteorder='big')
        # Print the big integer in chunks
        user_signature_str = splitToWords(user_signature_int, 121, 17)

        if signature_str is not None:
            json_data = {
                    "certDataPadded": byte_array,
                    "certDataPaddedLength": cert_data_padded_length,
                    "signature": signature_str,
                    "pubKey": public_key_str,
                    "nullifierSeed": str(nullifier_seed),
                    "signalHash": signal_hash,
                    "revealAgeAbove18": "1",
                    "userSignature": user_signature_str
            }
            json_data = json.dumps(json_data, indent=4)
            with open(self.config.input_file, 'w') as json_file:
                json_file.write(json_data)
        else:
            logging.error("Number does not fit", exc_info=True)
        return info
