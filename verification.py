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
        validator = CertificateValidator(end_entity_cert, validation_context=context)

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
                # print(cert['tbs_certificate'])
            return (True, info)
        except errors.PathValidationError as error:
            print("Certificate signature is not valid!"+" "+error)
            return (False, None)
