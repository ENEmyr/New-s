import numpy as np
from corpus import thai_words
from abc import ABC, abstractmethod
from typing import List, Tuple, Union, NewType
from summarization.utils import sentence_segment as sent_seg
from summarization.utils import word_tokenize as tokenize
from summarization.utils import stopwords, get_stem

SentenceVector = NewType('SentenceVector', type(np.array([])))
TFVector = NewType('TFVector', type(np.array([])))
IDFVector = NewType('IDFVector', type(np.array([])))
WeightedWordVector = NewType('WeightedWordVector', type(np.array([])))

LANGUAGE_SUPPORT = [
    'th'
]

class Summarizer(ABC):
    ''' Abstract class for summarizer engine '''
    def __init__(self, compression_rate:float = 0.65, lang:str = 'th'):
        """Contructor of Summarizer class
        
        Parameters
        ----------
        compression_rate : float, optional
            compression rate that used to calculate number of extractive sentences, the value must be in range [0, 1], by default 0.65
        lang : str, optional
            language of document that need to be summarize, by default 'th'
        
        Raises
        ------
        Exception
            unsupport language
        """        
        if not lang in LANGUAGE_SUPPORT:
            raise Exception("Language not support")
        compression_rate = compression_rate if compression_rate <= 1 and compression_rate >= 0 else 0.65
        self.__ratio = 1 - compression_rate # raio of output sentences
        self.__document = ''
        self._sentences = []
        self.__lang = lang
        self.__total_sentences = 0
        self.__all_words = []
    
    def n_extract_sents(self, n_sents:int) -> int:
        """Get number of extractive sentences
        
        Parameters
        ----------
        n_sents : int
            total number of sentences
        
        Returns
        -------
        int
            number of extractive sentences
        """        
        return int(np.ceil(self.__ratio*n_sents))

    @property
    def compression_rate(self) -> float:
        """Get current compression rate
        
        Returns
        -------
        float
            compression rate
        """        
        return 1 - self.__ratio
    
    @compression_rate.setter
    def compression_rate(self, rate:float) -> None:
        """Set compression rate
        
        Parameters
        ----------
        rate : float
            compression rate, the value must be in range [0, 1]
        """        
        rate = rate if rate <= 1 and rate >= 0 else 0.65
        self.__ratio = 1 - rate

    def word_tokenize(self, document:str) -> List[str]:
        """Demarcate a given document into its component words
        
        Parameters
        ----------
        document : str
            document that need to be tokenize
        
        Returns
        -------
        List[str]
            a list of component words
        """        
        return tokenize(document)

    def stem(self, word:str) -> str:
        """Get a word stem of given word
        
        Parameters
        ----------
        word : str
            word that need to find its stem
        
        Returns
        -------
        str
            word stem or word
        """        
        return get_stem(word, self.__lang)

    def remove_stopwords(self, words:List[str], allow_unknown:bool = True) -> List[str]:
        """Remove words which have very little meaning or similar words from given list
        
        Parameters
        ----------
        words : List[str]
            a list of word
        allow_unknown : bool, optional
            a flag that determine whether or not to remove unknown word, by default False
        
        Returns
        -------
        List[str]
            a list of removed stopwords
        """        
        stopwords_set = stopwords(self.__lang)
        if allow_unknown:
            new_words = list(filter(lambda word: not word in stopwords_set, words))
        else:
            new_words = list(filter(lambda word: not word in stopwords_set, words))
            new_words = list(filter(lambda word: word in thai_words(), new_words))
        return new_words

    def sentence_segment(self, document:str, remove_newline:bool = True, with_tag:bool = False) -> Union[List[dict], List[str]]:
        """Split a document into sentences
        
        Parameters
        ----------
        document : str
            document that need to be split
        remove_newline : bool, optional
            a flag that determine whether or not to replace '\\n' to ' ', by default True
        with_tag : bool, optional
            a flag that determine whether or not to return a word tag as a result, by default False
        
        Returns
        -------
        Union[List[dict], List[str]]
            list of sentences or list of dictionary that contains segmented document and a list of word with its tag
        """        
        self._sentences = sent_seg(document, remove_newline, with_tag)
        return self._sentences.copy()
    
    def merge_sentences(self, sentences:List[str] = []) -> str:
        """Combine given list of sentences into a string
        
        Parameters
        ----------
        sentences : List[str], optional
            a list of sentences, by default []
        
        Returns
        -------
        str
            a string that combine every sentences and seprarate it with newline
        
        Raises
        ------
        ValueError
            can't find any sentences to merge
        """        
        if len(sentences) == 0 and len(self._sentences) == 0:
            raise ValueError('Sentences not found')
        merged = ''
        sentences = sentences if len(sentences) != 0 else self._sentences
        if type(sentences[0]) != str:
            for sent in sentences:
                merged += sent.content+'\n'
        else:
            for sent in sentences:
                merged += sent+'\n'
        return merged
    
    def __n_term_normalize(self, word_freq:int, normalize_factor:int) -> float:
        """Get normalize value of word
        
        Parameters
        ----------
        word_freq : int
            number of occurrences of a word
        normalize_factor : int
            a normalize factor
        
        Returns
        -------
        float
            normalized value
        """        
        return word_freq/normalize_factor

    def __double_normalize(self, word_freq:int, normalize_factor:int, k:float) -> float:
        """Get a value of double normalization k of word
        
        Parameters
        ----------
        word_freq : int
            number of occurrences of a word
        normalize_factor : int
            a normalize factor
        k : float
            constant k
        
        Returns
        -------
        float
            nomalized value
        """        
        return k + ((1-k) * word_freq/normalize_factor)
    
    def __log_normalize(self, word_freq:int, c:int = 1) -> float:
        """Get a value of log normalization
        
        Parameters
        ----------
        word_freq : int
            number of occurrences of a word
        c : int, optional
            constant c, by default 1
        
        Returns
        -------
        float
            normalized value
        """        
        return np.log(c+word_freq)

    def words_frequency(self, sentences:List[str] = None, normalize:str = '', k:float = 0.5, allow_unknown:bool = True) -> List[dict]:
        """Calculate a words frequency from a list of sentences
        
        Parameters
        ----------
        sentences : List[str], optional
            a list of sentences that represent a document, by default None
        normalize : str, optional
            normalize method consists of 'n_term', 'double_k', 'log', by default '' mean raw count
        k : float, optional
            a constant that use in double normalization K, by default 0.5
        allow_unknown : bool, optional
            a flag that determine whether or not to keep unknown word in a list of word frequency, by default True
        
        Returns
        -------
        List[dict]
            a list of dictionary that each element represented a pair of word and its frequency
            e.g. result
            [
                {
                    'ตัวอย่าง' : 1.0,
                    'รีเทิร์น' : 0.5,
                    'ลิสต์' : 1.0
                },
                {
                    'คำ' : 1.0,
                    'รีเทิร์น' : 0.5
                }
            ]
        
        Raises
        ------
        ValueError
            can't find any sentences
        """        
        available_normalize_method = [
            'n_term',
            'double_k',
            'log'
        ]
        sentences = sentences if bool(sentences) else self._sentences
        k = k if k <= 1 and k >= 0 else 0.5
        if not bool(sentences):
            raise ValueError('Sentences not found')
        words_freq = []
        for sent in sentences:
            words = self.word_tokenize(sent)
            words = self.remove_stopwords(words, allow_unknown)
            word_set = set(words)
            normalize_factor = 0
            sent_word_count = {}
            for word in word_set:
                count = words.count(word)
                sent_word_count[word] = count
                if normalize == '' or not normalize in available_normalize_method:
                    normalize_factor += count # use this factor in order to calculate normal tf
                else:
                    normalize_factor = max(normalize_factor, count) # use this factor in double normalize
            if normalize == 'double_k':
                sent_word_count = dict(map(
                    lambda item: (item[0], self.__double_normalize(item[1], normalize_factor, k)), 
                    sent_word_count.items())) # Double Normalization K
            elif normalize == 'log':
                sent_word_count = dict(map(
                    lambda item: (item[0], self.__log_normalize(item[1])), 
                    sent_word_count.items())) # Log normalization
            elif normalize == 'n_term':
                sent_word_count = dict(map(
                    lambda item: (item[0], self.__n_term_normalize(item[1], normalize_factor)), 
                    sent_word_count.items())) # Term frequency
            else:
                sent_word_count = dict(map(
                    lambda item: (item[0], item[1]), 
                    sent_word_count.items())) # Raw count
            words_freq.append(sent_word_count)
        if sentences == self._sentences:
            self.__all_words = ','.join(list(map(
                lambda x: ','.join(list(x.keys())), 
                words_freq))).split(',')
            self.__total_sentences = len(words_freq)
        return words_freq

    def _sentence_to_tf_vector(self, sentence:dict) -> TFVector:
        """Transform given sentence to TermFrequency vector
        
        Parameters
        ----------
        sentence : dict
            a single element in list that was generated from words_freqeuncy method that represent a single sentence
        
        Returns
        -------
        TFVector
            vector of TermFrequency
        """        
        return np.array(list(sentence.values()))
    
    def _sentence_to_idf_vector(self, sentence:dict) -> IDFVector:
        """Transform given sentence to InverseDocumentFrequency vector
        
        Parameters
        ----------
        sentence : dict
            a single element in list that was generated from words_frequency method that represent a single sentence
        
        Returns
        -------
        IDFVector
            vector of InverseDocumentFrequency
        
        Raises
        ------
        ValueError
            can't find any sentence
        """        
        if self.__total_sentences == 0 or len(self.__all_words) == 0:
            raise ValueError("Sentences required")
        words = list(sentence.keys())
        n_sent_vector = np.array(list(map(lambda word: self.__all_words.count(word), words))) # vector of no. of sentence that contain word i
        idf_smooth_vector = np.log(self.__total_sentences/(1+n_sent_vector))+1 #inverse document frequency smooth of sentence sent
        return idf_smooth_vector
    
    def _weighted_word_vector(self, tf_vector:TFVector, idf_vector:IDFVector) -> WeightedWordVector:
        """Assign weight to every words in given vector
        
        Parameters
        ----------
        tf_vector : TFVector
            vector of TermFrequency
        idf_vector : IDFVector
            vector of InverseDocumentFrequency
        
        Returns
        -------
        WeightedWordVector
            vector of weighted word
        """        
        return tf_vector*idf_vector
    
    def _weighted_sentence(self, tf_vector:TFVector, idf_vector:IDFVector) -> float:
        """Calculate a weight of sentence from a result of dot product between TermFrequency vector and InverseDocumentFrequency
        
        Parameters
        ----------
        tf_vector : TFVector
            vector of TermFrequency
        idf_vector : IDFVector
            vector of InverseDocumentFrequency
        
        Returns
        -------
        float
            sentence weight
        """        
        return tf_vector.dot(idf_vector)

    @abstractmethod
    def _extract_importance_sentences(self, weighted_sentences:List[Tuple[int, float]], merge:bool = False) -> Union[List[str], str]:
        pass

    @abstractmethod
    def summarize(self, document:str, merge_sentences:bool = False) -> Union[List[str], str]:
        pass