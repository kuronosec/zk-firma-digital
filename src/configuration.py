import os
import platform

from pathlib import Path

# Get the OS type
os_type = platform.system()

class Configuration:
    def __init__(self, type="runtime") -> None:
        # Define OS specific paths
        # Check what operation system we re running on
        if os_type == 'Windows':
            self.installation_path = Path('C:/Program Files/zk-firma-digital')
        elif os_type == "Linux":
            self.installation_path = Path('/usr/share/zk-firma-digital')
        elif os_type == "Darwin":
            self.installation_path = Path('/usr/local/zk-firma-digital')
        else:
            print("Unknown operating system")

        self.user_path = os.path.join(Path.home(), Path('.zk-firma-digital/'))

        self.credentials_path = os.path.join(self.user_path, Path('credentials/'))
        self.credential_file = os.path.join(self.credentials_path, Path('credential.json'))

        self.certificate_path = os.path.join(self.credentials_path, Path('certificado.cert'))
        self.zk_artifacts_path = os.path.join(self.installation_path, Path('zk-artifacts/'))

        self.root_CA_path = os.path.join(self.installation_path,
                                         Path('CA-certificates/certificado-cadena-confianza.pem'))
        self.JWT_cert_path = os.path.join(self.installation_path,
                                         Path('CA-certificates/JWT_public_key.pem'))
        self.credentials_path = self.credentials_path

        self.spinner_path = os.path.join(self.installation_path, 'spinner.gif')

        # Define where to find the diferent components
        # of thew compilation process
        if type == "compile":
            self.build_path = Path("../build/")
            self.output_dir = self.build_path
            self.js_dir = os.path.join(self.build_path, Path('firma-verifier_js/'))
        elif type == "runtime":
            self.build_path = Path("build/")
            self.output_dir = os.path.join(self.user_path, self.build_path)
            self.js_dir = os.path.join(self.zk_artifacts_path, Path('firma-verifier_js/'))
        # Files for proof and verification
        self.vkey_file = os.path.join(self.zk_artifacts_path, Path('vkey.json'))
        self.wasm = os.path.join(self.js_dir, Path('firma-verifier.wasm'))

        self.input_file = os.path.join(self.credentials_path, Path('input.json'))
        self.witness = os.path.join(self.credentials_path, Path('witness.wtns'))
        self.zkey_file = os.path.join(self.zk_artifacts_path, Path('firma-verifier.zkey'))
        self.output_file = os.path.join(self.output_dir, Path('vkey.json'))
        self.public_signals_file = os.path.join(self.output_dir, Path('public.json'))
        self.proof_file = os.path.join(self.output_dir, Path('proof.json'))

        # Files for ceremony and setup
        self.r1cs = os.path.join(self.output_dir, Path('firma-verifier.r1cs'))
        self.sym_file = os.path.join(self.output_dir, Path('firma-verifier.sym'))
        self.ptau_file = os.path.join(self.output_dir, Path('firma-verifier-final.ptau'))
        self.circ_file = Path('../circuits/firma-verifier.circom')
        self.node_module_dir = Path('../circuits/node_modules/')