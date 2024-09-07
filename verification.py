import base64
import json

from utils import splitToWords, preprocess_message_for_sha256
from asn1crypto import pem
from certvalidator import CertificateValidator, ValidationContext, errors

class Verification:
    def __init__(self, pin):
        self.pin = pin
        self.root_CA_path = './CA-certificates/certificado-cadena-confianza.pem'

    def verify_certificate(self, user_certificate_path):
        trust_roots = []
        with open(self.root_CA_path, 'rb') as f:
            for _, _, der_bytes in pem.unarmor(f.read(), multiple=True):
                trust_roots.append(der_bytes)

        with open(user_certificate_path, 'rb') as f:
            end_entity_cert = f.read()

        context = ValidationContext(trust_roots=trust_roots)

        try:
            validator = CertificateValidator(end_entity_cert, validation_context=context)
            path = validator.validate_usage(set(['digital_signature']))
            for cert in path:
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
                byte_array, qr_data_padded_length = preprocess_message_for_sha256(list(tbs_bytes),
                                                                                  maxDataLength)

                # Get the public key info
                public_key_info = cert['tbs_certificate']['subject_public_key_info']
                public_key_bytes = public_key_info['public_key'].native
                modulus = public_key_bytes['modulus']

                # Get signature
                signature_bytes = cert['signature_value'].native
                # Convert the signature to a big integer
                signature_int = int(signature_bytes.hex(), 16)
                # Print the big integer in chunks
                signature_str = splitToWords(signature_int, 121, 17)
                public_key_str = splitToWords(modulus, 121, 17)

                if signature_str is not None:
                    json_data = {
                         "qrDataPadded": byte_array,
                         "qrDataPaddedLength": qr_data_padded_length,
                         "signature": signature_str,
                         "pubKey": public_key_str,
                         "nullifierSeed": "12345678",
                         "signalHash": "10010552857485068401460384516712912466659718519570795790728634837432493097374",
                         "revealAgeAbove18": "1"
                    }
                    json_data = json.dumps(json_data, indent=4)
                    with open('./aux/input.json', 'w') as json_file:
                        json_file.write(json_data)
                else:
                    print("Number does not fit")
            return (True, info)
        except errors.PathValidationError as error:
            print("Certificate signature is not valid!"+" "+error)
            return (False, None)
