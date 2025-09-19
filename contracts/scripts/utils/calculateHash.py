from web3 import Web3

# Example JSON-LD schema or string
jsonld_schema = """
{
  "@context": [
    {
      "@version": 1.1,
      "@protected": true,
      "id": "@id",
      "type": "@type",
      "ZKFirmaDigitalCredential": {
        "@id": "https://raw.githubusercontent.com/kuronosec/zk-firma-digital/main/assets/zk-firma-digital.jsonld#ZKFirmaDigital",
        "@context": {
          "@version": 1.1,
          "@protected": true,
          "id": "@id",
          "type": "@type",
          "vocab": "https://github.com/kuronosec/zk-firma-digital/main/assets/zk-firma-digital-vocab.md#",
          "iden3_serialization": "iden3:v1:slotIndexA=ageAbove18&slotValueB=randomNonce",
          "xsd": "http://www.w3.org/2001/XMLSchema#",
          "ageAbove18": {
            "@id": "vocab:ageAbove18",
            "@type": "xsd:positiveInteger"
          },
          "randomNonce": {
            "@id": "vocab:randomNonce",
            "@type": "xsd:positiveInteger"
          }
        }
      }
    }
  ]
}
"""

# Calculate keccak256 hash and convert to uint256
hash_bytes = Web3.keccak(text=jsonld_schema)
hash_uint256 = int.from_bytes(hash_bytes, byteorder="big")

print(f"Hash (uint256): {hash_uint256}")
