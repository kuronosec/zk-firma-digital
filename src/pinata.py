import requests
import os

# Pinata API credentials
PINATA_API_KEY = os.getenv("PINATA_API_KEY")
PINATA_SECRET_API_KEY = os.getenv("PINATA_SECRET_API_KEY")

# Upload the encrypted file to Pinata
def upload_to_pinata(encrypted_file_path):
    url = "https://api.pinata.cloud/pinning/pinFileToIPFS"

    # Headers with API keys
    headers = {
        "pinata_api_key": PINATA_API_KEY,
        "pinata_secret_api_key": PINATA_SECRET_API_KEY
    }

    # Open the encrypted file in binary mode
    with open(encrypted_file_path, "rb") as file:
        files = {"file": file}

        # Send a POST request to Pinata to pin the file to IPFS
        response = requests.post(url, headers=headers, files=files)

    # Check the response
    if response.status_code == 200:
        ipfs_hash = response.json()["IpfsHash"]
        print("File uploaded successfully to IPFS!")
        print("IPFS Hash:", ipfs_hash)
        return ipfs_hash
    else:
        print("Failed to upload file:", response.text)
        return None

def download_from_pinata(ipfs_hash, output_file_path):

    # URL to access the file via IPFS (using Pinata's public gateway)
    ipfs_url = f"https://gateway.pinata.cloud/ipfs/{ipfs_hash}"
    print("ipfs_url: "+ipfs_url)

    response = requests.get(ipfs_url, stream=True)
    
    if response.status_code == 200:
        with open(output_file_path, "wb") as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        print("File downloaded successfully:", output_file_path)
    else:
        print("Failed to retrieve file:", response.status_code)