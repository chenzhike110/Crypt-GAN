import base64
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
 
if __name__ == '__main__':
    data = b'I am fine Thank you'
    password = b'fuck' #16,24,32位长的密码
    password = add_to_16(password)
    encrypt_data = encrypt(data, password)
    encrypt_data = base64.b64encode(encrypt_data)
    print ('encrypt_data:', encrypt_data)
 
 
    encrypt_data = base64.b64decode(encrypt_data)
    decrypt_data = decrypt(encrypt_data, password)
    print ('decrypt_data:', decrypt_data.decode('utf8'))