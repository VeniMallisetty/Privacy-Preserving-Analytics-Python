from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
import base64

# Function to generate RSA key pair
def generate_key_pair():
    key = RSA.generate(2048)
    private_key = key.export_key()
    public_key = key.publickey().export_key()
    return private_key, public_key

# Function to encrypt data
def encrypt_data(data, public_key):
    key = RSA.import_key(public_key)
    cipher_rsa = PKCS1_OAEP.new(key)
    encrypted_data = cipher_rsa.encrypt(data.encode())
    return base64.b64encode(encrypted_data).decode()

# Function to decrypt data
def decrypt_data(encrypted_data, private_key):
    key = RSA.import_key(private_key)
    cipher_rsa = PKCS1_OAEP.new(key)
    decrypted_data = cipher_rsa.decrypt(base64.b64decode(encrypted_data.encode()))
    return decrypted_data.decode()
