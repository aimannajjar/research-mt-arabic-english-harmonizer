'''
Defines common functions to be used by harmonizer classes
'''

def normalize_word(word):
    # Normalizes Alif forms and removes diacritics
    return (word.strip().replace("|", "A")
                        .replace(">", "A")
                        .replace("&", "A")
                        .replace("<", "A")
                        .replace("Y", "y")
                        .replace("F", "")
                        .replace("N", "")
                        .replace("K", "")
                        .replace("a", "")
                        .replace("u", "")
                        .replace("i", "")
                        .replace("~", "")
                        .replace("o", "")
                        .replace("{", ""))
