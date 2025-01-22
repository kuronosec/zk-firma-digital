#!python

# Import the required libraries
import os
import json
import datetime
import logging
import jwt
import webbrowser
from urllib.parse import urlencode

# We will use the PyQt6 to provide a grafical interface for the user
from PyQt6.QtWidgets import ( QMainWindow,
                              QWidget,
                              QVBoxLayout,
                              QLineEdit,
                              QPushButton,
                              QMessageBox,
                              QTabWidget,
                              QLabel)

# Import our own libraries
from certificate import Certificate
from verification import Verification
from signature import Signature
from configuration import Configuration
from circom import Circom


class AuthenticationWindow(QMainWindow):
    def __init__(self, _token):
        super().__init__()

        self.token = _token
        self.config = Configuration()
        if not os.path.exists(self.config.output_dir):
            os.makedirs(self.config.output_dir)

        self.setWindowTitle("Zero Knowledge - Firma Digital")
        self.setGeometry(600, 400, 700, 400)

        # Create a QTabWidget
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # Add tabs
        self.verification_tab = self.create_verification_tab()
        self.tabs.addTab(self.verification_tab, self.tr("Validación de autenticación"))

    def create_verification_tab(self):
        # Create the first tab's content
        verification_tab = QWidget(self)

        # Create a vertical layout
        self.verification_layout = QVBoxLayout()
        # Verify the JWT token
        self.payload = self.verify_kyc_jwt_token(self.token)

        # Create a user verification label QLabel
        user_id = self.payload['user_id']
        first_message = self.tr('Autenticarse como usuario')
        second_message = self.tr('Por favor verifique que sea correcto.')
        self.verification_label = QLabel(
            f"{first_message}: {user_id}. {second_message}"
        )
        self.verification_layout.addWidget(self.verification_label)

        # Create the password field
        self.password_field = QLineEdit()
        self.password_field.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_field.setPlaceholderText(self.tr("Introduzca el PIN de su tarjeta"))
        self.verification_layout.addWidget(self.password_field)

        # Create the "Obtener certificados Firma Digital" button
        self.generate_credential_button = QPushButton(self.tr("Validar autenticación de usuario."))
        self.generate_credential_button.clicked.connect(self.on_submit_generate_credential)
        self.generate_credential_button.setStyleSheet("background-color : green")
        self.verification_layout.addWidget(self.generate_credential_button)

        # Set the layout for the central widget
        verification_tab.setLayout(self.verification_layout)
        return verification_tab

    def on_submit_generate_credential(self):
        if not self.payload:
            # Redirect back to the browser with failure status
            return_url = "https://app.sakundi.io/confirm-authorize"
            webbrowser.open(return_url)
            return

        user_id = self.payload['user_id']

        self.generate_credential_button.setEnabled(False)
        self.generate_credential_button.setStyleSheet("background-color : gray")
        # Get the certificates from the card
        password = self.password_field.text()
        certificate = Certificate(password)
        (valid, info) = certificate.get_certificates()
        QMessageBox.information(self, self.tr("Certificados"), f"{info}")
        if not valid:
            self.generate_credential_button.setEnabled(True)
            self.generate_credential_button.setStyleSheet("background-color : green")
            return
        # If the certificates were stored in disk then provide the option
        # to verify them
        if not os.path.exists(self.config.certificate_path):
            QMessageBox.information(self, self.tr("Certificado"), self.tr("No se pudo obtener el certificado"))
            self.generate_credential_button.setEnabled(True)
            self.generate_credential_button.setStyleSheet("background-color : green")
            return
        # Verify the stored certificates using the Goverment chain of trust
        password = self.password_field.text()
        if not user_id.startswith('0x'):
            signal_hash = '0x' + bytes(user_id, 'utf-8').hex()
        else:
            signal_hash = user_id
        verification = Verification(
            password,
            signal_hash
        )

        (valid, info) = verification.verify_certificate(self.config.certificate_path)
        if not valid:
            first_message = self.tr('Firma de certificado inválida!!!')
            QMessageBox.information(self, self.tr("Validación"), f"{info}\n\n {first_message}")
        else:
            first_message = self.tr('Firma de certificado válida!!!')
            QMessageBox.information(self, self.tr("Validación"), f"{info}\n\n {first_message}")
            try:
                circom = Circom()
                circom.generate_witness()
                circom.prove()
                circom.verify()
            except Exception as error:
                message = self.tr("Hubo un error al crear la credencial verificable")
                QMessageBox.information(self, "Circom", message)
                logging.error(message+" "+str(error), exc_info=True)
                self.generate_credential_button.setEnabled(True)
                self.generate_credential_button.setStyleSheet("background-color : green")
                return

            # Create credential
            public_input_data = None
            proof_data = None

            with open(self.config.public_signals_file, 'r') as json_file:
                public_input_data = json.load(json_file)

            with open(self.config.proof_file, 'r') as json_file:
                proof_data = json.load(json_file)

            # Structure json credential data
            verifiable_credential = self.verifiable_credential_template()
            verifiable_credential["proof"]["signatureValue"]["public"] = public_input_data
            verifiable_credential["proof"]["signatureValue"]["proof"] = proof_data

            # Convert the JSON data to a string and URL-encode it
            json_str = json.dumps(verifiable_credential)

            QMessageBox.information(self, self.tr("Validación de identidad exitosa"),
                                    self.tr("La validación de identidad fue exitosa."))

            # Dictionary of parameters to include in the URL
            params = {
                'user_id': self.payload['user_id'],
                'client_id': self.payload['auth_data']['client_id'],
                'redirect_uri': self.payload['auth_data']['redirect_uri'],
                'verifiable_credential': json_str
            }

            # Create credential and store it in a file for the user to utilize
            with open(self.config.credential_file, 'w', encoding='utf-8') as json_file:
                json.dump(verifiable_credential,
                          json_file,
                          ensure_ascii=False,
                          indent=4,
                          default=str)

            # Encode the parameters and append them to the base URL
            query_string = urlencode(params)

            # Redirect back to the browser with success status
            return_url = f"https://app.sakundi.io/confirm-authorize?{query_string}"
            webbrowser.open(return_url)
        self.generate_credential_button.setEnabled(True)
        self.generate_credential_button.setStyleSheet("background-color : green")
        self.close()

    def verifiable_credential_template(self):
        verifiable_credential = {
            "@context": [
                "https://www.w3.org/ns/credentials/v2",
                "https://w3id.org/citizenship/v2"
            ],
            "type": [
                "VerifiableCredential",
                "ResidentCardCredential"
            ],
            "name": "Resident Card",
            "issuer": "http://fdi.sinpe.fi.cr/repositorio/CA%20SINPE%20-%20PERSONA%20FISICA%20v2(2).crt",
            "validFrom": datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
            "validUntil": datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
            "credentialSubject": {
                "type": [
                "Person",
                "Resident"
                ],
                "ResidentCard": {
                "type": "ResidentCard",
                "age": 99
                }
            },
            "proof": {
                "type": "RsaSignature2018",
                "created": datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
                "verificationMethod": "http://fdi.sinpe.fi.cr/repositorio/CA%20SINPE%20-%20PERSONA%20FISICA%20v2(2).crt",
                "proofPurpose": "authentication",
                "signatureValue": {
                    
                }
            }
        }
        return verifiable_credential

    def verify_kyc_jwt_token(self, token):
        """
        Verifies the JWT token using the public key.
        """
        # Load the public key from a file
        with open(self.config.JWT_cert_path, "r") as f:
            public_key = f.read()

        try:
            payload = jwt.decode(token, public_key, algorithms=["RS256"])
            return payload
        except jwt.ExpiredSignatureError:
            logging.error("Token has expired.", exc_info=True)
            return None
        except jwt.InvalidTokenError:
            logging.error("Invalid token.", exc_info=True)
            return None
