import os.path

from zkpy.circuit import Circuit, GROTH, PLONK, FFLONK
from zkpy.ptau import PTau

circ_file="./circuits/firma-verifier.circom"

output_dir="./circuits/build/"

js_dir=output_dir+"firma-verifier_js"
r1cs=output_dir+"firma-verifier.r1cs"
sym_file=output_dir+"firma-verifier.sym"
wasm=output_dir+"firma-verifier_js/firma-verifier.wasm"
witness=output_dir+"witness.wtns"
zkey=output_dir+"firma-verifier-final.zkey"
ptau_file=output_dir+"firma-verifier-final.ptau"
input_file="./tmp/input.json"
zkey_file=output_dir+"firma-verifier.zkey"
output_file=output_dir+"vkey.json"
vkey_file=output_dir+"vkey.json"
public_file=output_dir+"public.json"
proof_file=output_dir+"proof.json"


print("Open circuit")
circuit = Circuit(circ_file=circ_file,
                output_dir=output_dir,
                js_dir=js_dir,
                r1cs=r1cs,
                sym_file=sym_file,
                wasm=wasm,
                witness=witness,
                zkey=zkey)

print("Compile circuit")
print(circuit.compile())
print(circuit.check_circ_compiled())
print("Get info")
print(circuit.get_info())

print("Power of Tau ceremony")
ptau = PTau(ptau_file=ptau_file,
                working_dir="./")

if(not os.path.isfile(ptau_file)):
    print("start()")
    ptau.start(curve='bn128', constraints='23')
    print("contribute()")
    ptau.contribute()
    print("beacon()")
    ptau.beacon()
    print("prep_phase2()")
    ptau.prep_phase2()

if(not os.path.isfile(input_file)):
    print("circuit.gen_witness")
    circuit.gen_witness(input_file)

if(not os.path.isfile(output_file)):
    print("setup")
    circuit.setup(GROTH, ptau)
    print("prove")
    circuit.prove(GROTH)
    print("export_vkey")
    circuit.export_vkey(zkey_file=zkey_file,
                        output_file=output_file)

if(os.path.isfile(vkey_file)
   and os.path.isfile(public_file)
   and os.path.isfile(proof_file)):
    print("verify")
    circuit.verify(GROTH, vkey_file=vkey_file,
                public_file=public_file,
                proof_file=proof_file)
