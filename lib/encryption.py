from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP

def generate_keys():
    # Generate a new RSA key pair
    key = RSA.generate(2048)

    # Extract the private and public keys from the key pair
    private_key = key.export_key()
    public_key = key.publickey().export_key()

    return public_key, private_key

def encrypt(private_key: str, data: str) -> str:
    cipher = PKCS1_OAEP.new(RSA.import_key(private_key))
    return cipher.encrypt(data.encode())

def decrypt(private_key: str, encrypted_data: str) -> str:
    cipher = PKCS1_OAEP.new(RSA.import_key(private_key))
    return cipher.decrypt(encrypted_data.encode())
