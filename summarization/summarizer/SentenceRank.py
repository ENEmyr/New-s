from typing import List, Tuple, Union
from summarization.summarizer.Summarizer import Summarizer

class SentenceRank(Summarizer):
    ''' Extractive text summarization from sentence ranking algorithm '''
    def __init__(self, compression_rate:float = 0.65, lang:str = 'th'):
        """Contructor of SentenceRank class
        
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
        n_sentences = self.n_extract_sents(len(weighted_sentences))
        extractive_sentences_index = list(map(lambda tup: tup[0], weighted_sentences[:n_sentences]))
        extractive_setences = [self._sentences[index] for index in extractive_sentences_index]
        if merge:
            return self.merge_sentences(extractive_setences)
        return extractive_setences

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
        words_freq = self.words_frequency(sentences, normalize='double_k', k=0.3, allow_unknown=True)
        weighted_sentences = []
        sentence_ref_index = 0
        for each_sent in words_freq:
            tf_vector = self._sentence_to_tf_vector(each_sent)
            idf_vector = self._sentence_to_idf_vector(each_sent)
            weighted_sent = self._weighted_sentence(tf_vector, idf_vector)
            if sentence_ref_index > 0:
                # insert most weight to top list
                index = 0
                for index in range(sentence_ref_index-1, -1, -1):
                    if weighted_sentences[index][1] > weighted_sent:
                        break
                if index != sentence_ref_index-1:
                    weighted_sentences.insert(index+1, (sentence_ref_index, weighted_sent))
                    sentence_ref_index += 1
                    continue
                elif index == 0 and weighted_sentences[0][1] < weighted_sent: # Special case index == 0
                    weighted_sentences.insert(0, (sentence_ref_index, weighted_sent))
                    sentence_ref_index += 1
                    continue
            weighted_sentences.append((sentence_ref_index, weighted_sent))
            sentence_ref_index += 1
        return self._extract_importance_sentences(weighted_sentences[1:], merge_sentences)