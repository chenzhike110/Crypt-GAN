from Utils.validator import *
from Utils.utils import FAILED, MODULE, ENGLISH_IC, MIN_ENGLISH_IC, MAX_SCORE, error, flatten, flatmap, read, clean, memoize, shift_by
from Utils import utils 
import Caesar.caesar as caesar
import math

validator = Validator()

KEY_LENGTH_THRESHOLD = 100
TEST_2_MAX_TEXT_LENGTH = 32

def vigenere(text, key, decrypt):
    shifts = [ord(k) - ord('a') for k in key.lower()]
    i = 0
    key_length = len(key)
    def do_shift(char):
        nonlocal i
        if char.isalpha():
            shift = shifts[i] if not decrypt else MODULE - shifts[i]
            i = (i + 1) % key_length
            return shift_by(char, shift)
        return char
    return ''.join(map(do_shift, text))

def useful_divisors(terms):
    threshold = KEY_LENGTH_THRESHOLD
    return flatmap(lambda n: list(utils.divisors(n, threshold))[1:], terms)

def caesar_crack(text):
    (decryptedKey, decryptedText) = caesar.crack(text)
    if decryptedKey is not None:
        key = chr(decryptedKey + ord('A'))
        return (key, decryptedText)
    return FAILED

def friedman(text, frequencies=None):
    kp = ENGLISH_IC
    kr = MIN_ENGLISH_IC
    ko = utils.coincidence_index(text, frequencies)
    return (ko, math.ceil((kp - kr)/(ko - kr)))

def kasiki(text):
    clean_text = utils.clean(text)
    min_length = 2 if (len(clean_text) < TEST_2_MAX_TEXT_LENGTH) else 3
    seqSpacings = utils.find_sequence_duplicates(clean_text, min_length)
    divisors = useful_divisors(flatten(list(seqSpacings.values())))
    divisorsCount = utils.repetitions(divisors)
    return [x[0] for x in divisorsCount if x[0] <= KEY_LENGTH_THRESHOLD]

def subgroup(text, n, key_length):
    clean_text = utils.clean(text)
    i = n - 1
    letters = []
    while i < len(clean_text):
        letters.append(clean_text[i])
        i += key_length
    return ''.join(letters)

def test(text, key_length, textline):
    textline.append(f"Testing key length {key_length}")
    groups = []
    for n in range(1, key_length + 1):
        groups.append(subgroup(text, n, key_length))
    a = ord('A')
    key = ""
    for n, group in enumerate(groups):
        coef = utils.coincidence_index(group)
        textline.append(f"Subgroup {n + 1} (IC: {coef})\n{group}")
        best_subkey = ('A', 0)
        for i in range(MODULE):
            shift = (MODULE - i)%MODULE
            decrypt = caesar.caesar(group, shift)
            frequencies = utils.most_frequent_chars(decrypt)
            score = utils.match_score(''.join(map(lambda x: x[0], frequencies)))
            subkey = chr(a + i)
            textline.append(f"Testing subkey '{subkey}' with match score {round(100 * (score/MAX_SCORE))}%")
            if best_subkey[1] < score:
                best_subkey = (subkey, score)
        textline.append(f"Best subkey is '{best_subkey[0]}' with match score {round(100 * (best_subkey[1]/MAX_SCORE))}%")
        key += best_subkey[0]
    decrypt = vigenere(text, key, True)
    return (key, decrypt) if validator.is_valid(decrypt) else FAILED

def crack(text, textline):
    clean_text = utils.clean(text)
    frequencies = utils.most_frequent_chars(clean_text)
    textline.append(f"Frequencies: {frequencies}")
    (coef, key_avg) = friedman(clean_text, frequencies)
    textline.append(f"Text IC (Index of Coincidence): {coef}")
    PERMITTED_ERROR = 0.3 * (ENGLISH_IC - MIN_ENGLISH_IC)
    if coef >= ENGLISH_IC - PERMITTED_ERROR:
        textline.append(f"IC suggests that the text is encrypted with monoalphabetic cipher")
        tryCaesar = caesar_crack(text)
        if tryCaesar != FAILED:
            return tryCaesar
    if key_avg > 0 and key_avg <= KEY_LENGTH_THRESHOLD:
        textline.append(f"Friedman test suggests a key length of {key_avg}")
        decrypted = test(text, key_avg, textline)
        if decrypted != FAILED:
            return decrypted
    textline.append("Kasiki examination")
    key_lengths = kasiki(text)
    if key_avg in key_lengths:
        key_lengths.remove(key_avg)
    textline.append("Kasiki possible key lengths (sorted by probability):")
    textline.append(str(key_lengths))
    for key_length in key_lengths:
        decrypted = test(text, key_length, textline)
        if decrypted != FAILED:
            return decrypted
    return FAILED
