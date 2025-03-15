from setuptools import setup
import os

APP = ['main.py']
# List additional files and folders to be bundled inside your .app.
DATA_FILES = []

OPTIONS = {
    'argv_emulation': True,
    'includes': [
        'asn1crypto',
        'certvalidator',
        'PyJWT',
        'PyKCS11',
        'PyQt6',
        'PyQt6_sip',
        'oscrypto',
        'web3',
        'jaraco.text',
        'jwt',
        'Crypto',
        'Crypto.Hash',
        'Crypto.Hash.keccak',
        'eth_hash'
    ],
    'excludes': ['typing_extensions', 'packaging'],
    'packages': [
        'asn1crypto',
        'certvalidator',
        'PyKCS11',
        'PyQt6',
        'oscrypto',
        'web3',
        'cryptography',
        'jwt',
        'Crypto',
        'eth_hash'
    ],
    'plist': {
        'CFBundleDisplayName': 'zk-firma-digital',
        'CFBundleExecutable': 'zk-firma-digital',
        'CFBundleIconFile': 'icon-windowed.icns',
        'CFBundleIdentifier': 'zk-firma-digital',
        'CFBundleInfoDictionaryVersion': '6.0',
        'CFBundleName': 'zk-firma-digital',
        'CFBundlePackageType': 'APPL',
        'CFBundleShortVersionString': '0.6.2',
        'NSHighResolutionCapable': 'true',
        'CFBundleDisplayName': 'zk-firma-digital',
        'CFBundleName': 'zk-firma-digital',
        'CFBundleIdentifier': 'io.sakundi.zk-firma-digital',
        'CFBundleURLTypes': [
            {
                'CFBundleURLName': 'io.sakundi.zk-firma-digital',
                'CFBundleURLSchemes': ['zk-firma-digital']
            }
        ],
        # Add the required PyRuntimeLocations key:
        'PyRuntimeLocations': [
            "@executable_path/../Frameworks/Python.framework/Versions/3.12/Python",
            "~"
        ],
    },
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
