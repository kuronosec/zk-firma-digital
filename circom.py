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
# circuit.gen_witness("./example_circuits/input.json")
# circuit.setup(PLONK, ptau)
# circuit.prove(PLONK)
# circuit.export_vkey()
# circuit.verify(PLONK, vkey_file="vkey.json", public_file="public.json", proof_file="proof.json")

print("Power of Tau ceremony")
ptau = PTau(ptau_file="466b3077-c267-42ec-9a9a-e0e7cfa6cb04.ptau",
                       working_dir="./circuits/build/")
ptau.start()
ptau.contribute()
ptau.beacon()
ptau.prep_phase2()
