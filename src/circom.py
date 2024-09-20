#!python

import os.path

from zkpy.circuit import Circuit, GROTH, PLONK, FFLONK
from zkpy.ptau import PTau

class Circom():
    def __init__(self) -> None:
        # define variables
        self.circ_file="../circuits/firma-verifier.circom"

        self.output_dir="../build/"

        self.js_dir=self.output_dir+"firma-verifier_js"
        self.r1cs=self.output_dir+"firma-verifier.r1cs"
        self.sym_file=self.output_dir+"firma-verifier.sym"
        self.wasm=self.output_dir+"firma-verifier.wasm"
        self.witness=self.output_dir+"witness.wtns"
        self.zkey=self.output_dir+"firma-verifier.zkey"
        self.ptau_file=self.output_dir+"firma-verifier-final.ptau"
        self.input_file="../build/input.json"
        self.zkey_file=self.output_dir+"firma-verifier.zkey"
        self.output_file=self.output_dir+"vkey.json"
        self.vkey_file=self.output_dir+"vkey.json"
        self.public_file=self.output_dir+"public.json"
        self.proof_file=self.output_dir+"proof.json"

        print("Open circuit")
        self.circuit = Circuit(circ_file=self.circ_file,
                        output_dir=self.output_dir,
                        js_dir=self.js_dir,
                        r1cs=self.r1cs,
                        sym_file=self.sym_file,
                        wasm=self.wasm,
                        witness=self.witness,
                        zkey=self.zkey)

        self.ptau = PTau(ptau_file=self.ptau_file,
                        working_dir="./")

    def compile_circuit(self) -> None:
        print("Compile circuit")
        self.circuit.compile()
        self.circuit.check_circ_compiled()
        print("Get info")
        self.circuit.get_info()

    def power_of_tau(self) -> None:
        print("Power of Tau ceremony")
        if(not os.path.isfile(self.ptau_file)):
            print("start()")
            self.ptau.start(curve='bn128', constraints='23')
            print("contribute()")
            self.ptau.contribute()
            print("beacon()")
            self.ptau.beacon()
            print("prep_phase2()")
            self.ptau.prep_phase2()

    def generate_witness(self) -> None:
        if(not os.path.isfile(self.witness)):
            print("circuit.gen_witness")
            self.circuit.gen_witness(self.input_file)

    def setup(self) -> None:
        if(not os.path.isfile(self.output_file)):
            print("setup")
            self.circuit.setup(GROTH, self.ptau)

    def prove(self) -> None:
        print("prove")
        self.circuit.prove(GROTH)
        print("export_vkey")
        self.circuit.export_vkey(zkey_file=self.zkey_file,
                            output_file=self.output_file)

    def verify(self) -> None:
        if(os.path.isfile(self.vkey_file)
        and os.path.isfile(self.public_file)
        and os.path.isfile(self.proof_file)):
            print("verify")
            self.circuit.verify(GROTH, vkey_file=self.vkey_file,
                        public_file=self.public_file,
                        proof_file=self.proof_file)

if __name__ == "__main__":
    circom = Circom()
    circom.compile_circuit()
    circom.power_of_tau()
    circom.setup()