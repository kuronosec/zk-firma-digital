#!python

# Import the necessary libraries
import os.path

from zkpy.circuit import Circuit, GROTH, PLONK, FFLONK
from zkpy.ptau import PTau
from configuration import Configuration

# This class provides utilitis to compile the circom circuts
# fot the Firma Digital
class Circom():
    def __init__(self) -> None:
        # Define variables
        self.config = Configuration()

        # Create comilation object
        print("Open circuit")
        self.circuit = Circuit(circ_file=self.config.circ_file,
                        output_dir=self.config.output_dir,
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
        print("Compile circuit")
        self.circuit.compile()
        self.circuit.check_circ_compiled()
        print("Get info")
        self.circuit.get_info()

    # Start the Power of Tau ceremony
    # TODO: allow contributions
    def power_of_tau(self) -> None:
        print("Power of Tau ceremony")
        if(not os.path.isfile(self.config.ptau_file)):
            print("start()")
            self.ptau.start(curve='bn128', constraints='23')
            print("contribute()")
            self.ptau.contribute()
            print("beacon()")
            self.ptau.beacon()
            print("prep_phase2()")
            self.ptau.prep_phase2()

    # Create the input from the user in a way snarks undertands it
    def generate_witness(self) -> None:
        if(not os.path.isfile(self.config.witness)):
            print("circuit.gen_witness")
            self.circuit.gen_witness(self.config.input_file)

    # Setup the keys based on the ceremony
    def setup(self) -> None:
        if(not os.path.isfile(self.config.output_file)):
            print("setup")
            self.circuit.setup(GROTH, self.ptau)

    # Calculate the ZK proof based on the circuit and the key
    def prove(self) -> None:
        print("prove")
        self.circuit.prove(GROTH)
        print("export_vkey")
        self.circuit.export_vkey(zkey_file=self.config.zkey_file,
                            output_file=self.config.output_file)

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
    circom = Circom()
    circom.compile_circuit()
    circom.power_of_tau()
    circom.setup()