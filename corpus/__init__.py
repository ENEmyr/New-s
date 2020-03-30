from typing import FrozenSet
from pythainlp.corpus import thai_female_names, thai_male_names, thai_negations, thai_words, thai_stopwords, thai_syllables

STEM_FILE_PATH = './corpus/ThaiWordStemming.csv'

def thai_stems() -> FrozenSet:
    try:
        stems = open(STEM_FILE_PATH, 'r', encoding='utf-8-sig').read().splitlines()[1:]
        return frozenset(stems)
    except FileNotFoundError:
        return frozenset()

__all__ = [
    "thai_stems",
    "thai_female_names",
    "thai_male_names",
    "thai_negations",
    "thai_words",
    "thai_stopwords",
    "thai_syllables"
]