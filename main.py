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
                              QMessageBox )
from certificate import Certificate
from verification import Verification

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.certificate_path = "./tmp"

        self.setWindowTitle("Zero Knowledge - Firma Digital")
        self.setGeometry(100, 100, 300, 200)

        # Create a main widget
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        # Create a vertical layout
        self.layout = QVBoxLayout()

        # Create the password field
        self.password_field = QLineEdit()
        self.password_field.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_field.setPlaceholderText("Introduzca el PIN de su tarjeta")
        self.layout.addWidget(self.password_field)

        # Create the "Obtener certificados Firma Digital" button
        self.get_certificate_button = QPushButton("Obtener certificados Firma Digital")
        self.get_certificate_button.clicked.connect(self.on_submit_get_certificate)
        self.layout.addWidget(self.get_certificate_button)

        # Create the "Verificar certificados Firma Digital" button
        self.verifiy_button = QPushButton("Verificar certificados Firma Digital")
        self.verifiy_button.clicked.connect(self.on_submit_verify_certificate)

        if os.path.exists(self.certificate_path):
            self.layout.addWidget(self.verifiy_button)

        # Set the layout for the central widget
        central_widget.setLayout(self.layout)

    def on_submit_get_certificate(self):
        # Get the certificates from the card
        password = self.password_field.text()
        certificate = Certificate(password)
        certificate_text = certificate.get_certificates()
        QMessageBox.information(self, "Certificados", f"{certificate_text}")
        # If the certificates were stored in disk then provide the option
        # to verify them
        if os.path.exists(self.certificate_path):
            self.layout.addWidget(self.verifiy_button)

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

# Create the application
app = QApplication(sys.argv)

# Create and show the main window
window = MainWindow()
window.show()

# Run the application event loop
sys.exit(app.exec())
