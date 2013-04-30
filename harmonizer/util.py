'''
Defines common functions to be used by harmonizer classes
'''

import re

def normalize_word(word, schemes):
    normalized_word = word.strip()

    if "NORM_ALIFS" in schemes:
        normalize_word = (normalize_word.replace("|", "A")
                                        .replace(">", "A")
                                        .replace("&", "A")
                                        .replace("<", "A"))
    if "NORM_YAA" in schemes:
        normalize_word = normalize_word.replace("Y", "y")

    if "REMOVE_DIACRITICS" in schemes:
        normalize_word = (normalize_word.replace("F", "")
                                        .replace("N", "")
                                        .replace("K", "")
                                        .replace("a", "")
                                        .replace("u", "")
                                        .replace("i", "")
                                        .replace("~", "")
                                        .replace("o", "")
                                        .replace("{", ""))

    if "REMOVE_WORD_SENSE" in schemes:
        # Remove (\_\d) suffix from lemmas
        normalized_word = re.sub(r"_\d$", "", normalized_word)
    return normalized_word