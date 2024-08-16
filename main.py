#!/home/kurono/miniconda3/envs/firma/bin/python

import sys
import os

from os import listdir
from os.path import isfile, join
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

from certificate import Certificate
from verification import Verification
from signature import Signature

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.certificate_path = "./tmp"
        self.file_to_sign = ""

        self.setWindowTitle("Zero Knowledge - Firma Digital")
        self.setGeometry(100, 100, 600, 400)

        # Create a QTabWidget
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # Add tabs
        self.verification_tab = self.create_verification_tab()
        self.signing_tab = self.create_signing_tab()
        self.tabs.addTab(self.verification_tab, "Verificación de certificados")
        self.tabs.addTab(self.signing_tab, "Firma de archivos")

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
        self.get_certificate_button = QPushButton("Obtener certificados Firma Digital")
        self.get_certificate_button.clicked.connect(self.on_submit_get_certificate)
        self.verification_layout.addWidget(self.get_certificate_button)

        # Create the "Verificar certificados Firma Digital" button
        self.verify_button = QPushButton("Verificar certificados Firma Digital")
        self.verify_button.clicked.connect(self.on_submit_verify_certificate)

        if os.path.exists(self.certificate_path):
            self.verification_layout.addWidget(self.verify_button)

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

    def on_submit_get_certificate(self):
        # Get the certificates from the card
        password = self.password_field.text()
        certificate = Certificate(password)
        certificate_text = certificate.get_certificates()
        QMessageBox.information(self, "Certificados", f"{certificate_text}")
        # If the certificates were stored in disk then provide the option
        # to verify them
        if os.path.exists(self.certificate_path):
            self.verification_layout.addWidget(self.verify_button)

    def on_submit_verify_certificate(self):
        # Verify the stored certificates using the Goverment chain of trust
        password = self.password_field.text()
        verification = Verification(password)
        files = [file for file in listdir(self.certificate_path) if isfile(join(self.certificate_path, file))]
        for file in files:
            file = join(self.certificate_path, file)
            (valid, info) = verification.verify_certificate(file)
            if valid:
                QMessageBox.information(self, "Validación", f"{info}\n\n Firma de certificado válida!!!")
            else:
                QMessageBox.information(self, "Validación", f"{info}\n\n Firma de certificado inválida!!!")

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

if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())
