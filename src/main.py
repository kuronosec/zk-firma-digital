#!python

# IMport the required libraries
import sys
import os
import json
import datetime
import utils
import logging

from os import listdir
from os.path import isfile, join

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

# Import our own libraries
from certificate import Certificate
from verification import Verification
from signature import Signature
from configuration import Configuration
from circom import Circom

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
        self.file_label.setText(f'<a href="file:///{self.config.credential_file}">Haga click aquí para ver el archivo de credencial generado</a>')

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
        self.tabs.addTab(self.verification_tab, "Creación de credencial ZK")
        self.tabs.addTab(self.signing_tab, "Firma de credenciales verificables")

    def create_verification_tab(self):
        # Create the first tab's content
        verification_tab = QWidget(self)

        # Create a vertical layout
        self.verification_layout = QVBoxLayout()

        # Create the password field
        self.password_field = QLineEdit()
        self.password_field.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_field.setPlaceholderText("Introduzca el PIN de su tarjeta")
        self.verification_layout.addWidget(self.password_field)

        # Create the "Obtener certificados Firma Digital" button
        self.generate_credential_button = QPushButton("Generar credencial JSON")
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
        self.signature_layout.addWidget(QLabel("Firmar archivo JSON"))

        # Create the password field
        self.password_field_sign = QLineEdit()
        self.password_field_sign.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_field_sign.setPlaceholderText("Introduzca el PIN de su tarjeta")
        self.signature_layout.addWidget(self.password_field_sign)

        # Create a button to open the file dialog
        button_browser = QPushButton("Escoger archivo a firmar")
        button_browser.clicked.connect(self.browse_files)
        self.signature_layout.addWidget(button_browser)

        # Label to display the selected file
        self.browser_label = QLabel("Selected file: None")
        self.signature_layout.addWidget(self.browser_label)
        self.signature_tab.setLayout(self.signature_layout)

        # Create a button to sign the file
        button_sign = QPushButton("Firmar archivo")
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
        QMessageBox.information(self, "Certificados", f"{info}")
        if not valid:
            self.generate_credential_button.setEnabled(True)
            self.generate_credential_button.setStyleSheet("background-color : green")
            return
        # If the certificates were stored in disk then provide the option
        # to verify them
        if not os.path.exists(self.config.certificate_path):
            QMessageBox.information(self, "Certificado", "No se pudo obtener el certificado")
            self.generate_credential_button.setEnabled(True)
            self.generate_credential_button.setStyleSheet("background-color : green")
            return
        # Verify the stored certificates using the Goverment chain of trust
        password = self.password_field.text()
        verification = Verification(password)

        (valid, info) = verification.verify_certificate(self.config.certificate_path)
        if not valid:
            QMessageBox.information(self, "Validación", f"{info}\n\n Firma de certificado inválida!!!")
        else:
            QMessageBox.information(self, "Validación", f"{info}\n\n Firma de certificado válida!!!")
            try:
                circom = Circom()
                circom.generate_witness()
                circom.prove()
                circom.verify()
            except Exception as error:
                message ="Hubo un error al crear la credencial verificable"
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

            QMessageBox.information(self, "Creación de credencial válida",
                                    "Encontrar credencial verificable en el enlace.")
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
            self.browser_label.setText(f"Selected file: {file_name}")
            self.file_to_sign = file_name
        else:
            self.browser_label.setText("No file selected")

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
            QMessageBox.information(self, "Firma de archivo JSON",
                                    f"{info}\n\nArchivo JSON firmado:\n\n {signed_name}")
            self.browser_label.setText(f"Archivo JSON firmado: {signed_name}")
        else:
            self.browser_label.setText("No file selected")

# Main entry point for our app
if __name__ == "__main__":
    try:
        app = QApplication(sys.argv)

        window = MainWindow()
        window.show()

        sys.exit(app.exec())
    except Exception as error:
        message = "Hubo un error en la aplicacion:"
        logging.error(message+" "+str(error), exc_info=True)