from typing import List
from pythainlp import word_tokenize as tokenize

def word_tokenize(document:str) -> List[str]:
    return tokenize(document)