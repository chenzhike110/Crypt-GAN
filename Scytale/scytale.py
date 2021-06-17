from Utils.utils import *
from Utils.validator import Validator
import numpy as np
import math

FILL_CHARACTER = ' '

def key_to_matrix_bounds(text, key):
    rows = key
    cols = math.ceil(len(text)/rows)
    return (rows, cols)

def scytale(text, rows, cols, textline):
    """Encrypts/Decrypts a `text` using the scytale transposition cipher with specified `key`"""
    m = np.array(list(text.ljust(rows*cols, FILL_CHARACTER))).reshape((rows, cols))
    result = ''.join([''.join(row) for row in m.transpose()]).strip()
    if textline!= None:
        textline.append(f'Text to cipher: "{text}" ({len(text)})')
        textline.append(np.array2string(m))
        textline.append(f"Result size: {len(result)}")
    return result

def cipher(text, key, textline):
    bounds = key_to_matrix_bounds(text, key)
    rows = bounds[0]
    cols = bounds[1]
    if textline!= None:
        textline.append(f"Testing matrix: {rows}x{cols}")
    return scytale(text, rows, cols, textline)

def test(text, rows, cols, textline):
    validator = Validator()
    dimensions = (rows, cols)
    if dimensions in testedKeys:
        return FAILED
    testedKeys.add(dimensions)
    decrypt = scytale(text, rows, cols, textline)
    textline.append(f"Testing matrix: {rows}x{cols}       ")
    textline.append(f'Testing decrypted text:\n"{decrypt}"')
    if validator.is_valid(decrypt):
        return ((rows, cols), decrypt)
    return FAILED

def testKeys(text, keys, terminal):
    for k in keys:
        bounds = key_to_matrix_bounds(text,k)
        rows = bounds[0]
        cols = bounds[1]
        decrypted = test(text, rows, cols, terminal)
        if decrypted == FAILED:
            decrypted = test(text, cols, rows, terminal)
            if decrypted != FAILED:
                return decrypted
        else:
            return decrypted
    return FAILED

def crack(text, textline=True):
    """Cracks the text that must be encrypted with the scytale cipher"""
    global testedKeys
    testedKeys = set()
    size = len(text)
    textline.append(f'Text to crack: "{text}" ({size})')
    divs = list(divisors(size))
    decrypted = testKeys(text, divs, textline)
    if decrypted == FAILED:
        keys = [x for x in range(2, size) if x not in divs]
        decrypted = testKeys(text, keys, textline)
    if decrypted != FAILED:
        return decrypted
    return FAILED

# if __name__ == "__main__":
#     set_args()

#     validator = Validator(args.lang, args.threshold, args.debug, args.beep)
#     text = read(args.text)
#     size = len(text)

#     if args.key is not None:
#         if args.key not in range(1, size + 1):
#             error(f"key must be between 1 and {size}")
#         print(cipher(text))
#     else:
#         crack(text)
