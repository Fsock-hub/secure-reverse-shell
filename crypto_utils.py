import os
try:
    from cryptography.fernet import Fernet
except:
    os.system('python -m pip install cryptography')
    from cryptography.fernet import Fernet
    
def generate_key():
    return Fernet.generate_key()

def encrypt_message(key, message: str) -> bytes:
    f = Fernet(key)
    return f.encrypt(message.encode())

def decrypt_message(key, token: bytes) -> str:
    f = Fernet(key)
    return f.decrypt(token).decode()
