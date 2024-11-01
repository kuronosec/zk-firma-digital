#!python

# Import the required libraries
import sys
import os
import json
import datetime
import utils
import logging

from os import listdir
from os.path import isfile, join
from pathlib import Path

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
from PyQt6.QtCore import QTimer, Qt, QTranslator
from PyQt6.QtGui import QCursor

# Import our own libraries
from certificate import Certificate
from verification import Verification
from signature import Signature
from encryption import Encryption
from ethereum_utils import EthereumUtils
from configuration import Configuration
from circom import Circom
from pinata import download_from_pinata

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
        self.file_label.setText(
            self.tr(f'<a href="file:///{self.config.credential_file}">Haga click aquí para ver el archivo de credencial generado</a>')
        )

        # Allow the QLabel to open external links
        self.file_label.setOpenExternalLinks(True)

        self.setWindowTitle(self.tr("Zero Knowledge - Firma Digital"))
        self.setGeometry(600, 400, 1000, 400)

        # Create a QTabWidget
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # Add tabs
        self.verification_tab = self.create_verification_tab()
        self.signing_tab = self.create_signing_tab()
        self.certificate_request_tab = self.create_certificate_request_tab()
        self.medical_certificate_tab = self.create_medical_certificate_tab()

        self.tabs.addTab(self.verification_tab, self.tr("Creación de credencial ZK"))
        self.tabs.addTab(self.signing_tab, self.tr("Firma de credenciales verificables"))
        self.tabs.addTab(self.certificate_request_tab, self.tr("Solicitar certificado médico"))
        self.tabs.addTab(self.medical_certificate_tab, self.tr("Ver certificados médicos"))

        self.eth_utils = EthereumUtils()
        self.eth_utils.load_contracts()

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
        self.generate_credential_button.clicked.connect(
            self.on_submit_generate_credential
        )
        self.generate_credential_button.setStyleSheet(self.tr("background-color : green"))
        self.verification_layout.addWidget(self.generate_credential_button)

        # Set the layout for the central widget
        verification_tab.setLayout(self.verification_layout)
        self.verification_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)

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
        self.signature_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        self.signature_tab.setLayout(self.signature_layout)

        # Create a button to sign the file
        button_sign = QPushButton(self.tr("Firmar archivo"))
        button_sign.clicked.connect(self.sign_files)
        self.signature_layout.addWidget(button_sign)

        return self.signature_tab

    def create_certificate_request_tab(self):
        # Create the encryption tab's content
        self.certificate_request_tab = QWidget()
        self.certificate_request_layout = QVBoxLayout()
        self.certificate_request_layout.addWidget(QLabel(self.tr("Solicite un certificado médico")))

        # Create the user id field
        self.id_number_field = QLineEdit()
        self.id_number_field.setPlaceholderText(self.tr("Introduzca su número de cédula"))
        self.certificate_request_layout.addWidget(self.id_number_field)
        self.certificate_request_tab.setLayout(self.certificate_request_layout)
        self.certificate_request_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        # Create a button to sign the file
        self.create_request_button = QPushButton(self.tr("Enviar solicitud"))
        self.create_request_button.setStyleSheet("background-color : green")
        self.create_request_button.clicked.connect(self.send_medical_request)
        self.certificate_request_layout.addWidget(self.create_request_button)

        return self.certificate_request_tab

    def create_medical_certificate_tab(self):
        # Create the medical certificate tab's content
        self.medical_certificate_tab = QWidget()
        self.medical_certificate_layout = QVBoxLayout()
        self.medical_certificate_layout.addWidget(QLabel(self.tr("Descarge su certificados médico")))

        self.message_label = QLabel(self.tr("Buscando certificados..."))
        self.message_label.setStyleSheet("background-color : green")
        self.message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.medical_certificate_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.medical_certificate_layout.addWidget(self.message_label)
        self.medical_certificate_tab.setLayout(self.medical_certificate_layout)

        # Timer to check for resource availability every 60 seconds
        self.check_timer = QTimer(self)
        self.check_timer.timeout.connect(self.check_resource)
        self.check_timer.start(60000)  # Check every 60 seconds

        return self.medical_certificate_tab

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
            QMessageBox.information(self, self.tr("Certificado"),
                                    self.tr("No se pudo obtener el certificado"))
            self.generate_credential_button.setEnabled(True)
            self.generate_credential_button.setStyleSheet("background-color : green")
            return
        # Verify the stored certificates using the Goverment chain of trust
        password = self.password_field.text()
        verification = Verification(password)

        (valid, info) = verification.verify_certificate(self.config.certificate_path)
        if not valid:
            QMessageBox.information(
                self, 
                self.tr("Validación"),
                self.tr(f"{info}\n\n Firma de certificado inválida!!!"))
        else:
            QMessageBox.information(
                self,
                self.tr("Validación"),
                self.tr(f"{info}\n\n Firma de certificado válida!!!")
            )
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

            QMessageBox.information(
                self,
                self.tr("Creación de credencial válida"),
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
                                                   "Open File",
                                                   "",
                                                   "JSON Files (*.json)")

        if file_name:
            self.browser_label.setText(self.tr(f"Selected file: {file_name}"))
            self.file_to_sign = file_name
        else:
            self.browser_label.setText(self.tr("No file selected"))

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
            QMessageBox.information(
                self,
                self.tr("Firma de archivo JSON"),
                f"{info}\n\nArchivo JSON firmado:\n\n {signed_name}"
            )
            self.browser_label.setText(self.tr(f"Archivo JSON firmado: {signed_name}"))
        else:
            self.browser_label.setText(
                self.tr("No file selected")
            )

    def send_medical_request(self):
        self.create_request_button.setEnabled(False)
        self.create_request_button.setStyleSheet("background-color : gray")
        # Sign certificate request number
        id_number = self.id_number_field.text()

        # Check number not empty
        if id_number:
            # Inititialize encryption object and load public key
            encryption = Encryption("./CA-certificates/public_testing_key.pem")
            public_key = encryption.load_public_key()

            # Encrypt request id with govement's public key
            encrypted_id = encryption.encrypt(id_number, public_key)

            # Create on-chain (Polygon amoy) standard verifable credential
            self.eth_utils.create_verifiable_credential(
                self.config.credential_file
            )

            # Check for existing credentials
            credentials = self.eth_utils.get_credentials()

            # If credentials available, create medical certificate request
            self.eth_utils.create_medical_credential_request(
                encrypted_id
            )
            QMessageBox.information(self, self.tr("Petición de certificado"),
                                    self.tr(f"Petición de certificado enviada"))
        self.create_request_button.setEnabled(True)
        self.create_request_button.setStyleSheet("background-color : green")

    def check_resource(self):
        # Check if resource is available
        medical_certificate = self.eth_utils.get_medical_certificate_document()
        if medical_certificate != None:
            encryption = Encryption(
                "./CA-certificates/public_testing_key.pem",
                "./CA-certificates/private_testing_key.pem")
            private_key = encryption.load_private_key()

            # Take ipfs has encryption data and decrypt it
            ipfs_hash = encryption.decrypt(
                medical_certificate[1],
                private_key)

            # Convert the bytes to a string
            ipfs_hash_str = ipfs_hash.decode("utf-8") if isinstance(
                ipfs_hash,
                bytes
                ) else ipfs_hash

            download_from_pinata(
                ipfs_hash_str,
                os.path.join(self.config.user_path,
                             Path('documents/encrypted_output_pinata.pdf'))
            )

            aes_key = encryption.decrypt(
                medical_certificate[2],
                private_key)
            encryption.decrypt_pdf_content(
                os.path.join(self.config.user_path,
                             Path('documents/encrypted_output_pinata.pdf')),
                os.path.join(self.config.user_path,
                             Path('documents/medical-certificate.pdf')),
                aes_key)

            self.show_link(os.path.join(self.config.user_path,
                             Path('documents/medical-certificate.pdf')))
            self.eth_utils.revoke_verifiable_credential(0)

            self.check_timer.stop()  # Stop checking once the resource is found

    def show_link(self, medical_certificate_file):
        self.message_label.setText(
            self.tr(f'<a href="file:///{medical_certificate_file}">Haga click aquí para ver el archivo de certificado médico</a>'))
        self.message_label.setOpenExternalLinks(True)
        self.message_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextBrowserInteraction)
        self.message_label.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

def load_language(language_code):
    translator = QTranslator()
    if translator.load(f"translations_{language_code}.qm"):
        print(f"Loaded language: translations_{language_code}.qm")
        return translator
    else:
        print(f"Could not load language: translations_{language_code}.qm")
        return None

# Main entry point for our app
if __name__ == "__main__":
    try:
        app = QApplication(sys.argv)
        language_code = "en"
        translator = load_language(language_code)
        app.installTranslator(translator)

        window = MainWindow()
        window.show()

        sys.exit(app.exec())
    except Exception as error:
        message = "There was an error in the main app:"
        logging.error(message+" "+str(error), exc_info=True)