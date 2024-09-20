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

# Find the public key object (assuming it's a RSA public key)
public_key = session.findObjects([(PyKCS11.CKA_CLASS, PyKCS11.CKO_PUBLIC_KEY)])[0]

# Load the signed JSON data
signed_json_file_path = "../build/signed_data.json"
with open(signed_json_file_path, "r") as f:
    signed_json = json.load(f)

# Extract the signature and the original data
signature_base64 = signed_json.pop('signature')  # Remove the signature from the JSON data
signature = base64.b64decode(signature_base64)  # Decode the signature from Base64

# Recompute the hash of the original data (SHA-256)
json_data_str = json.dumps(signed_json, separators=(',', ':'), sort_keys=True)  # Canonicalize the JSON
hashed_data = hashlib.sha256(json_data_str.encode('utf-8')).digest()

# Verify the signature using the public key
mechanism = PyKCS11.Mechanism(PyKCS11.CKM_SHA256_RSA_PKCS, None)
try:
    session.verify(public_key, hashed_data, signature, mechanism)
    print("Signature is valid.")
except PyKCS11.PyKCS11Error:
    print("Signature verification failed.")

# Logout and close the session
session.logout()
session.closeSession()
