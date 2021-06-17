from Crypto.Cipher import AES
from Crypto import Random

def pad(s):
    return s + b"\0" * (AES.block_size - len(s) % AES.block_size)

def add_to_16(text):
    while len(text) % 16 != 0:
        text += b'\0'
    return (text)

def encrypt(message, key):
    message = pad(message)
    iv = Random.new().read(AES.block_size)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    return iv + cipher.encrypt(message)

def decrypt(ciphertext, key):
    iv = ciphertext[:AES.block_size]
    cipher = AES.new(key, AES.MODE_CBC, iv)
    plaintext = cipher.decrypt(ciphertext[AES.block_size:])
    return plaintext.rstrip(b"\0")