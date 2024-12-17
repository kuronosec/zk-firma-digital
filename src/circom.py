#!python

# Import the necessary libraries
import os

from zkpy.circuit import Circuit, GROTH, PLONK, FFLONK
from zkpy.ptau import PTau
from configuration import Configuration

# This class provides utilitis to compile the circom circuts
# fot the Firma Digital
class Circom():
    def __init__(self, _type="runtime") -> None:
        # Define variables
        self.config = Configuration(type=_type)

        # Create comilation object
        print("Open circuit")
        self.circuit = Circuit(circ_file=self.config.circ_file,
                        output_dir=str(self.config.output_dir),
                        node_module_dir=self.config.node_module_dir,
                        js_dir=self.config.js_dir,
                        r1cs=self.config.r1cs,
                        sym_file=self.config.sym_file,
                        wasm=self.config.wasm,
                        witness=self.config.witness,
                        zkey=self.config.zkey_file)

        # Create Power Of Tau ceremony object
        # Refs: https://eprint.iacr.org/2022/1592.pdf
        self.ptau = PTau(ptau_file=self.config.ptau_file,
                        working_dir="./")

    # Actually compile or circom code
    def compile_circuit(self) -> None:
        if not self.circuit.check_circ_compiled():
            print("Compile circuit")
            if not os.path.exists(self.config.output_dir):
                os.makedirs(self.config.output_dir)
            self.circuit.compile()
            print("Get info")
            self.circuit.get_info()
        else:
            print("Circuit already compiled.")

    # Start the Power of Tau ceremony
    # TODO: allow contributions
    def power_of_tau(self) -> None:
        if(not os.path.isfile(self.config.ptau_file)):
            print("Power of Tau ceremony")
            print("start()")
            self.ptau.start(curve='bn128', constraints='23')
            print("contribute()")
            self.ptau.contribute()
            print("beacon()")
            self.ptau.beacon()
            print("prep_phase2()")
            self.ptau.prep_phase2()
        else:
            print("power_of_tau already done")

    # Create the input from the user in a way snarks undertands it
    def generate_witness(self) -> None:
        print("circuit.gen_witness")
        self.circuit.gen_witness(
            self.config.input_file,
            output_file=self.config.witness)

    # Setup the keys based on the ceremony
    def setup(self) -> None:
        if(not os.path.isfile(self.config.output_file)):
            print("setup")
            self.circuit.setup(GROTH, self.ptau)
        else:
            print("Setup already done")

    # Calculate the ZK proof based on the circuit and the key
    def prove(self) -> None:
        print("prove")
        self.circuit.prove(GROTH)

    def export_vkey(self) -> None:
        if not os.path.isfile(self.config.output_file):
            print("export_vkey")
            self.circuit.export_vkey(
                zkey_file=str(self.config.output_dir)+'/firma-verifier.zkey',
                output_file=self.config.output_file
            )
        else:
            print("export_vkey already done")

    # Verify that the created user ZK proof is valida for the circuit
    # i.e. the users posses a Firma Digital but we don't any information
    # about it
    def verify(self) -> None:
        if(os.path.isfile(self.config.vkey_file)
        and os.path.isfile(self.config.public_signals_file)
        and os.path.isfile(self.config.proof_file)):
            print("verify")
            self.circuit.verify(GROTH, vkey_file=self.config.vkey_file,
                        public_file=self.config.public_signals_file,
                        proof_file=self.config.proof_file)

# Runs the full compilation process
if __name__ == "__main__":
    circom = Circom(_type="compile")
    circom.compile_circuit()
    circom.power_of_tau()
    circom.setup()
    circom.export_vkey()