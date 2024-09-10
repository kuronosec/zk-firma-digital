from zkpy.circuit import Circuit, GROTH, PLONK, FFLONK
from zkpy.ptau import PTau

print("Open circuit")
circuit = Circuit(circ_file="./circuits/firma-verifier.circom",
                  output_dir="./circuits/build",
                  js_dir="./circuits/build/firma-verifier_js")
print("Compile circuit")
print(circuit.compile())
print(circuit.check_circ_compiled())
print("Get info")
print(circuit.get_info())
# print("Print constraints")
# print(circuit.print_constraints())

print("Power of Tau ceremony")
ptau = PTau(ptau_file="./circuits/build/46be33b5-3a8b-48a8-be69-01ade9154593.ptau",
                       working_dir="./")
ptau.start()
ptau.contribute()
ptau.beacon()
ptau.prep_phase2()

circuit.gen_witness("./tmp/input.json")
circuit.setup(PLONK, ptau)
circuit.prove(PLONK)
circuit.export_vkey()
circuit.verify(PLONK, vkey_file="vkey.json",
               public_file="public.json",
               proof_file="proof.json")
