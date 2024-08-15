import PyKCS11
import json
import hashlib
import base64

# Path to your PKCS#11 library
PKCS11_LIB = "/usr/lib/x64-athena/libASEP11.so"

# Load the PKCS#11 library
pkcs11 = PyKCS11.PyKCS11Lib()
pkcs11.load(PKCS11_LIB)

# Open a session with the token
slots = pkcs11.getSlotList(tokenPresent=True)
if not slots:
    raise Exception("No token found")
slot = slots[0]
session = pkcs11.openSession(slot, PyKCS11.CKF_SERIAL_SESSION | PyKCS11.CKF_RW_SESSION)

# Login with your PIN
session.login("65810")

# Find the private key object
private_key = session.findObjects([(PyKCS11.CKA_CLASS, PyKCS11.CKO_PRIVATE_KEY)])[0]

# Load the JSON data
json_file_path = "./tmp/data.json"
with open(json_file_path, "r") as f:
    json_data = f.read()

# Canonicalize and hash the JSON data (using SHA-256)
hashed_data = hashlib.sha256(json_data.encode('utf-8')).digest()

# Sign the hash using the private key
mechanism = PyKCS11.Mechanism(PyKCS11.CKM_SHA256_RSA_PKCS, None)
signature = session.sign(private_key, hashed_data, mechanism)

# Base64 encode the signature
signature_base64 = base64.b64encode(bytearray(signature)).decode('utf-8')

# Print or store the signature
print("Signature (Base64):", signature_base64)

# Optionally, add the signature back into the JSON data
signed_json = json.loads(json_data)
signed_json['signature'] = signature_base64

# Save the signed JSON to a new file
signed_json_file_path = "./tmp/signed_data.json"
with open(signed_json_file_path, "w") as f:
    json.dump(signed_json, f, indent=4)

# Logout and close the session
session.logout()
session.closeSession()
