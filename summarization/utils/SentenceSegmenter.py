from typing import Union, List
from thai_segmenter import sentence_segment as sent_seg

def sentence_segment(document:str, remove_newline:bool = True, with_tag:bool = False) -> Union[List[dict], List[str]]:
    if with_tag:
        return sent_seg(document)
    else:
        if remove_newline:
            return [sent.content.replace('\n', ' ') for sent in sent_seg(document)]
        else:
            return [sent.content for sent in sent_seg(document)]