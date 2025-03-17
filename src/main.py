#!python

# Import the required libraries
import sys
import os
import json
import datetime
import logging
import shutil
from urllib.parse import urlparse, parse_qs

# We will use the PyQt6 to provide a grafical interface for the user
# TODO: test that it works on Windows
from PyQt6.QtWidgets import ( QApplication,
                              QMainWindow,
                              QWidget,
                              QVBoxLayout,
                              QLineEdit,
                              QPushButton,
                              QMessageBox,
                              QTabWidget,
                              QLabel,
                              QFileDialog )
from PyQt6.QtCore import QTranslator

# Import our own libraries
from certificate import Certificate
from verification import Verification
from signature import Signature
from configuration import Configuration
from circom import Circom
from authentication_window import AuthenticationWindow


def clear_saved_state():
    state_path = os.path.expanduser(
        r"~/Library/Saved Application State/io.sakundi.zk-firma-digital.savedState/")
    logging.info("Clearing saved application state.")
    if os.path.exists(state_path):
        try:
            shutil.rmtree(state_path)
            logging.info("Cleared saved application state.")
        except Exception as e:
            logging.info("Failed to clear saved state:", e)

clear_saved_state()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.config = Configuration()
        if not os.path.exists(self.config.output_dir):
            os.makedirs(self.config.output_dir)
        self.file_to_sign = ""

        # Create a QLabel
        self.file_label = QLabel()
        # HTML link to the local file
        self.file_label.setText(f'<a href="file:///{self.config.credential_file}">{self.tr("Haga click aquí para ver el archivo de credencial generado</a>")}')

        # Allow the QLabel to open external links
        self.file_label.setOpenExternalLinks(True)

        self.setWindowTitle("Zero Knowledge - Firma Digital")
        self.setGeometry(600, 400, 700, 400)

        # Create a QTabWidget
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # Add tabs
        self.verification_tab = self.create_verification_tab()
        self.signing_tab = self.create_signing_tab()
        self.tabs.addTab(self.verification_tab, self.tr("Creación de credencial ZK"))
        # self.tabs.addTab(self.signing_tab, self.tr("Firma de credenciales verificables")

    def create_verification_tab(self):
        # Create the first tab's content
        verification_tab = QWidget(self)

        # Create a vertical layout
        self.verification_layout = QVBoxLayout()

        # Create the password field
        self.password_field = QLineEdit()
        self.password_field.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_field.setPlaceholderText(self.tr("Introduzca el PIN de su tarjeta"))
        self.verification_layout.addWidget(self.password_field)

        # Create the "Obtener certificados Firma Digital" button
        self.generate_credential_button = QPushButton(self.tr("Generar credencial JSON"))
        self.generate_credential_button.clicked.connect(self.on_submit_generate_credential)
        self.generate_credential_button.setStyleSheet("background-color : green")
        self.verification_layout.addWidget(self.generate_credential_button)

        # Set the layout for the central widget
        verification_tab.setLayout(self.verification_layout)
        return verification_tab

    def create_signing_tab(self):
        # Create the signature tab's content
        self.signature_tab = QWidget()
        self.signature_layout = QVBoxLayout()
        self.signature_layout.addWidget(QLabel(self.tr("Firmar archivo JSON")))

        # Create the password field
        self.password_field_sign = QLineEdit()
        self.password_field_sign.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_field_sign.setPlaceholderText(self.tr("Introduzca el PIN de su tarjeta"))
        self.signature_layout.addWidget(self.password_field_sign)

        # Create a button to open the file dialog
        button_browser = QPushButton(self.tr("Escoger archivo a firmar"))
        button_browser.clicked.connect(self.browse_files)
        self.signature_layout.addWidget(button_browser)

        # Label to display the selected file
        self.browser_label = QLabel(self.tr("Selected file: None"))
        self.signature_layout.addWidget(self.browser_label)
        self.signature_tab.setLayout(self.signature_layout)

        # Create a button to sign the file
        button_sign = QPushButton(self.tr("Firmar archivo"))
        button_sign.clicked.connect(self.sign_files)
        self.signature_layout.addWidget(button_sign)

        return self.signature_tab

    def on_submit_generate_credential(self):
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
        ethereum_address = os.getenv(
            "ETHEREUM_ADDRESS",
            '0x' + bytes("user", 'utf-8').hex()
        )
        verification = Verification(password, signal_hash=ethereum_address)

        (valid, info) = verification.verify_certificate(self.config.certificate_path)
        if not valid:
            QMessageBox.information(self, self.tr("Validación"), f"{info}\n\n {self.tr('Firma de certificado inválida!!!')}")
        else:
            QMessageBox.information(self, self.tr("Validación"), f"{info}\n\n {self.tr('Firma de certificado válida!!!')}")
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

            # Create credential and store it in a file for the user to utilize
            with open(self.config.credential_file, 'w', encoding='utf-8') as json_file:
                json.dump(verifiable_credential,
                          json_file,
                          ensure_ascii=False,
                          indent=4,
                          default=str)

            self.verification_layout.addWidget(self.file_label)

            QMessageBox.information(self, self.tr("Creación de credencial válida"),
                                    self.tr("Encontrar credencial verificable en el enlace."))
        self.generate_credential_button.setEnabled(True)
        self.generate_credential_button.setStyleSheet("background-color : green")
    
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

    def browse_files(self):
        # Open a file dialog and select a file
        file_name, _ = QFileDialog.getOpenFileName(self,
                                                   self.tr("Open File"),
                                                   "",
                                                   "JSON Files (*.json)")

        if file_name:
            self.browser_label.setText(f"Selected file: {file_name}")
            self.file_to_sign = file_name
        else:
            self.browser_label.setText(self.tr("No file selected"))

    # This code is not being used at the moment
    # Do we really need it?
    def sign_files(self):
        # Sign selected file
        password = self.password_field_sign.text()
        if self.file_to_sign:
            signature = Signature(password)
            signature.load_library()
            file_name = os.path.basename(self.file_to_sign)
            file_only_path = os.path.dirname(self.file_to_sign)
            signed_name = file_only_path+"/"+"signed-"+file_name
            info = signature.sign_file(self.file_to_sign)
            QMessageBox.information(self, self.tr("Firma de archivo JSON"),
                                    f"{info}\n\nArchivo JSON firmado:\n\n {signed_name}")
            self.browser_label.setText(f"Archivo JSON firmado: {signed_name}")
        else:
            self.browser_label.setText(self.tr("No file selected"))

def load_language(language_code):
    config = Configuration()
    try:
        translator = QTranslator()
        if translator.load(
            os.path.join( config.installation_path,
                        f"translations_{language_code}.qm")
        ):
            logging.info(f"Loaded language: translations_{language_code}.qm")
            return translator
        else:
            logging.info(f"Could not load language: translations_{language_code}.qm")
            return None
    except Exception:
        logging.error(
                "Error Loading Language.",
                exc_info=True
            )

# Main entry point for our app
if __name__ == "__main__":

    logging.info("Starting ZK-Firma-Digital")
    language_code = "es"
    translator = load_language(language_code)

    if len(sys.argv) > 1:
        uri = sys.argv[1]

        # Parse the URI
        parsed_uri = urlparse(uri)
        action = parsed_uri.path.strip("/")
        params = parse_qs(parsed_uri.query)

        # Extract the JWT token from the URI
        token = params.get("token", [None])[0]

        if parsed_uri.netloc == "authentication" and token:
            app = QApplication(sys.argv)
            app.installTranslator(translator)
            window = AuthenticationWindow(token)
            window.show()

            code = app.exec()
            clear_saved_state()
            sys.exit(code)
        else:
            logging.error(
                "Invalid KYC request or missing parameters.",
                exc_info=True
            )
    else:
        app = QApplication(sys.argv)
        app.installTranslator(translator)
        window = MainWindow()
        window.show()

        code = app.exec()
        clear_saved_state()
        sys.exit(code)