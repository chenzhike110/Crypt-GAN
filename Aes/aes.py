from Utils.utils import read, read_file, error
from os.path import splitext as split_extension
from Crypto import Random
from Crypto.Cipher import AES

MODES = {
    "ECB": AES.MODE_ECB,
    "CBC": AES.MODE_CBC,
    "CFB": AES.MODE_CFB,
    "OFB": AES.MODE_OFB,
    "OPENPGP": AES.MODE_OPENPGP
}

def pad(s):
    return s + b"\0" * (AES.block_size - len(s) % AES.block_size)

def encrypt(message, key):
    message = pad(message)
    if OP_MODE == MODES["ECB"]:
        cipher = AES.new(key, OP_MODE)
        iv = ''
    else:
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(key, OP_MODE, iv)
    return iv + cipher.encrypt(message)

def decrypt(ciphertext, key):
    if OP_MODE == MODES["ECB"]:
        cipher = AES.new(key, OP_MODE)
    else:
        iv = ciphertext[:AES.block_size]
        cipher = AES.new(key, OP_MODE, iv)
    plaintext = cipher.decrypt(ciphertext[AES.block_size:])
    return plaintext.rstrip(b"\0")

def encrypt_file(file_name, key):
    fo = open(file_name, 'rb')
    plaintext = fo.read()
    enc = encrypt(plaintext, key)
    fo = open(file_name + ".enc", 'wb')
    fo.write(enc)

def decrypt_file(file_name, key):
    fo = open(file_name, 'rb')
    ciphertext = fo.read()
    dec = decrypt(ciphertext, key)
    fo = open(split_extension(file_name)[0], 'wb')
    fo.write(dec)

def write(file_name, text):
    open(file_name, 'wb').write(text)

def is_valid_key(key):
    size = len(key) * 8
    return size % 128 == 0 or size % 192 == 0 or size % 256 == 0

if __name__ == "__main__":
    set_args()

    OP_MODE = MODES["CBC"]
    if args.mode:
        args.mode = args.mode.upper()
        if args.mode not in MODES:
            error(args.mode + " is not a valid mode")
        OP_MODE = MODES[args.mode]

    try:
        text = read_file(args.infile, binary=True) if args.infile else read(args.text, binary=True)

        if args.keyfile is not None:
            args.key = read_file(args.keyfile, binary=True)
        key = args.key
        if key is None:
            error("Must specify AES key")
        if not is_valid_key(key):
            error(key + " (size " + str(len(key) * 8) + " bits) is not a valid AES key")
    except FileNotFoundError as e:
        error(e)

    try:
        result = decrypt(text, key) if args.decrypt else encrypt(text, key)
    except ValueError as e:
        error(e)

    if args.outfile:
        write(args.outfile, result)
    else:
        print(result)
