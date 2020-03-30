from typing import FrozenSet
from corpus import thai_stopwords

LANGUAGES_SUPPORT = [
    'th'
]

def stopwords(lang:str = 'th') -> FrozenSet:
    if lang in LANGUAGES_SUPPORT:
        if lang == 'th':
            return thai_stopwords()
    else:
        return frozenset()