from typing import List, Tuple, Union
from summarization.summarizer.Summarizer import Summarizer
from gensim.summarization import summarize as textrank_summarize

class TextRank(Summarizer):
    ''' Extractive text summarization from TextRank algorithm'''
    def __init__(self, compression_rate:float = 0.65, lang:str = 'th'):
        """Contructor of TextRank class
        
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
        super().__init__(compression_rate=compression_rate, lang=lang)

    def _extract_importance_sentences(self, weighted_sentences:List[Tuple[int, float]], merge:bool = False) -> Union[List[str], str]:
        """Extract importance sentences from list of sentence, the number of extractive sentences is calculate from given compression_rate
        
        Parameters
        ----------
        weighted_sentences : List[Tuple[int, float]]
            a list of weighted sentences that is the result of summarize process
        merge : bool, optional
            a flag that determine whether or not to merge a list of sentences into string, by default False
        
        Returns
        -------
        Union[List[str], str]
            list of sentences or string of merged sentences
        """        
        pass

    def summarize(self, document:str, merge_sentences:bool = False) -> Union[List[str], str]:
        """Summarize given document
        
        Parameters
        ----------
        document : str
            a document that need to be summarize
        merge_sentences : bool, optional
            a flag that determine whether or not to merge a list of sentences into string, by default False
        
        Returns
        -------
        Union[List[str], str]
            list of sentence or string of merged sentences
        """        
        sentences = self.sentence_segment(document)
        merged_sentences = self.merge_sentences(sentences)
        return textrank_summarize(merged_sentences, 1-self.compression_rate)