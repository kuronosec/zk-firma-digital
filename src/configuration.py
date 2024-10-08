import os

from pathlib import Path

class Configuration:
    def __init__(self) -> None:
        # Define OS specific paths
        # Check what operation system we re running on
        if os.name == 'nt':
            self.installation_path = Path('C:/Program Files/zk-firma-digital')
        # Linux
        else:
            self.installation_path = Path('/usr/share/zk-firma-digital')

        self.user_path = os.path.join(Path.home(), Path('.zk-firma-digital/'))
        self.build_path = Path("build/")

        self.credentials_path = os.path.join(self.user_path, Path('credentials/'))
        self.credential_file = os.path.join(self.credentials_path, Path('credential.json'))

        self.certificate_path = os.path.join(self.credentials_path, Path('certificado.cert'))
        self.zk_artifacts_path = os.path.join(self.installation_path, Path('zk-artifacts/'))

        self.root_CA_path = os.path.join(self.installation_path, Path('CA-certificates/certificado-cadena-confianza.pem'))
        self.output_dir = os.path.join(self.user_path, self.build_path)
        self.credentials_path = self.credentials_path

        # Define where to find the diferent components
        # of thew compilation process

        # Files for proof and verification
        self.js_dir = os.path.join(self.zk_artifacts_path, Path('firma-verifier_js/'))
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
        self.circ_file = '../circuits/firma-verifier.circom'

