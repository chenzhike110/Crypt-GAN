import enchant
from .utils import NON_ALPHABET, error

class Validator:

    def __init__(self, lang='en_US', threshold=50):
        if threshold not in range(0, 101):
            error("threshold must be between 0 and 100")
        self.lang = lang
        self.percentage_success = threshold
        self.d = enchant.Dict(lang)

    def is_valid(self, text):
        """Checks if relevant words in `text` are written in `lang`"""
        words = NON_ALPHABET.split(text)
        total = len(words)
        count = 0
        i = 0
        for word in words:
            count += 1
            length = len(word)
            if length == 0:
                i += 1
            elif length > 1:
                testWord = word.lower()
                valid = self.d.check(testWord)
                if valid:
                    i += 1
            progress = round(100 * (i/total))
            if length > 1 and progress >= self.percentage_success:
                return True
            max_progress = round(100 * ((i + total - count)/total))
            if max_progress < self.percentage_success:
                return False
        return False
