from Utils import utils, validator

def caesar(text, shift):
    """Encrypts/Decrypts a `text` using the caesar substitution cipher with specified `shift` key"""
    if shift < 0 or shift > utils.MODULE:
        utils.error(f"key must be between 0 and {utils.MODULE}")
    return ''.join(map(lambda char: utils.shift_by(char, shift), text))

def crack(text, lineEdit=None):
    """Cracks the text that must be encrypted with the caesar cipher"""
    validator1 = validator.Validator()
    shifts = utils.reversed_shifts(utils.clean(text))
    for i, shift in enumerate(shifts):
        decrypt = caesar(text, shift)
        if lineEdit != None:
            lineEdit.append(f"Testing '{utils.FREQUENCY_ALPHABET[i]}' (ROT-{shift})")
            lineEdit.append(f'Testing decrypted text:\n"{decrypt}"')
        if validator1.is_valid(decrypt):
            encryptionKey = (utils.MODULE - shift)%utils.MODULE
            return (encryptionKey, decrypt)
    return utils.FAILED
