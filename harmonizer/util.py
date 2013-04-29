'''
Defines common functions to be used by harmonizer classes
'''

import re

def normalize_word(word):
    # Normalize Alif forms and remove diacritics
    normalized_word = (word.strip().replace("|", "A")
                                    .replace(">", "A")
                                    .replace("&", "A")
                                    .replace("<", "A")
                                    .replace("Y", "y"))
                                    # .replace("F", "")
                                    # .replace("N", "")
                                    # .replace("K", "")
                                    # .replace("a", "")
                                    # .replace("u", "")
                                    # .replace("i", "")
                                    # .replace("~", "")
                                    # .replace("o", "")
                                    # .replace("{", ""))

    # Remove (\_\d) suffix from lemmas
    normalized_word = re.sub(r"_\d$", "", normalized_word)
    return normalized_word