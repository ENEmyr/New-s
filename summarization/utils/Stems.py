from corpus import thai_stems

LANGUAGE_SUPPORT = [
    'th'
]

def get_stem(word:str, lang:str='th') -> str:
    if not lang in LANGUAGE_SUPPORT:
        return word
    if lang == 'th':
        #THAI_STEM_PAIR_INDEX = {}
        #THAI_WORD_PAIR_STEM_INDEX = {}
        #stem_index = 0
        for element in thai_stems():
            tmp = element.split(',')
            stem = tmp[0]
            words = tmp[1:]
            words[0] = words[0][1:]
            words[len(words)-1] = words[len(words)-1][:-1]
            if word in words:
                return stem
    return word
            #tmp = element.split(',')
            #stem = tmp[0]
            #tmp[1] = tmp[1][1:]
            #tmp[len(tmp)-1] = tmp[len(tmp)-1][:-1]
            #THAI_STEM_PAIR_INDEX[index_stem] = stem
            #for word in tmp[1:]:
            #    THAI_WORD_PAIR_STEM_INDEX[word] = stem_index
            #stem_index += 1

__all__ = [
    'get_stem'
]