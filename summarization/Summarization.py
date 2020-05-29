from summarization.summarizer import TextRank, SentenceRank

def summarize(document:str, compression_rate:float = 0.60, lang:str = 'th', algorithm:str = 'text_rank') -> str:
    """Summarize given document according to define algorithm
    
    Parameters
    ----------
    document : str
        a document that need to be summarize
    compression_rate : float, optional
        compression rate that used to calculate number of extractive sentences, the value must be in range [0, 1], by default 0.60
    lang : str, optional
        language of document that need to be summarize, by default 'th'
    algorithm : str, optional
        summarization algorithm, can be 'text_rank' or 'sentence_rank, by default 'text_rank'
    
    Returns
    -------
    str
        summarized document
    
    Raises
    ------
    ValueError
        summarizer did not support language that given through lang parameter
    ValueError
        a document is not be a string type
    ValueError
        can't find summarize algorithm
    """    
    LANGUAGE_SUPPORT = ['th']
    ALGORITHM_SUPPORT = ['sentence_rank', 'text_rank']
    if not lang in LANGUAGE_SUPPORT:
        raise ValueError("Unsupport language")
    if type(document) != str:
        raise ValueError("Document must be string")
    if not algorithm in ALGORITHM_SUPPORT:
        raise ValueError("Can't find summarize algorithm")
    compression_rate = compression_rate if compression_rate >= 0 and compression_rate <= 1 else 0.60
    if algorithm == 'sentence_rank':
        summarizer = SentenceRank(compression_rate, lang)
    else:
        summarizer = TextRank(compression_rate, lang)
    try:
        summarized = summarizer.summarize(document, merge_sentences=True)
    except:
        print('Error occur while summrizing...')
        summarized = document
    return summarized