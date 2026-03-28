import os
from cryptography.fernet import Fernet
from dotenv import load_dotenv

load_dotenv()

FERNET_KEY = os.getenv("FERNET_KEY")
if not FERNET_KEY:
    raise ValueError("FERNET_KEY not found in environment variables.")

cipher_suite = Fernet(FERNET_KEY.encode('utf-8'))

def encrypt_data(data: str) -> str:
    """Encrypts string data using AES-256 (Fernet)."""
    if not data:
        return data
    return cipher_suite.encrypt(data.encode('utf-8')).decode('utf-8')

def decrypt_data(encrypted_data: str) -> str:
    """Decrypts AES-256 (Fernet) encrypted string data."""
    if not encrypted_data:
        return encrypted_data
    return cipher_suite.decrypt(encrypted_data.encode('utf-8')).decode('utf-8')
