
from cryptography.fernet import Fernet

    
def generate_key():
    return Fernet.generate_key()

def encrypt_message(key, message: bytes) -> bytes:
    f = Fernet(key)
    return f.encrypt(message)

def decrypt_message(key, token: bytes) -> bytes:
    f = Fernet(key)
    return f.decrypt(token)
