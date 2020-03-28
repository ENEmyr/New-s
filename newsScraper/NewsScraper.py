import re
from types import SimpleNamespace
from typing import List, Union, Tuple
from newsScraper.scraper.SanookScraper import SanookScraper
from newsScraper.scraper.Scraper import Scraper

class NewsScraper(Scraper):
    ''' NewsScraper Adapter Class '''
    
    def __init__(self, max_trace_limit:int = 10):
        """Constructor of Scraper class
        
        Parameters
        ----------
        max_trace_limit : int
            max number of limit that used in order to trace a news from news source
        """        
        super().__init__(max_trace_limit)
        self.__scraper = {
            "sanook": SanookScraper(max_trace_limit)
        }
        self.__PUBLISHER_NAME = {}
        self.__PUBLISHERS = {}
        for key in self.__scraper.keys():
            self.__PUBLISHER_NAME[key.upper()] = key
            self.__PUBLISHERS[key] = True
        self.__PUBLISHER_NAME = SimpleNamespace(**self.__PUBLISHER_NAME) # Use for access element in dict with .
    
    @property
    def PUBLISHER_NAME(self) -> str:
        """Use for refer to publisher name

        Available publisher are:

            - PUBLISHER_NAME.SANOOK
        
        Returns
        -------
        dict
            dictionary that use to collect publisher name
        """        
        return self.__PUBLISHER_NAME

    def set_publisher(self, *args:Tuple[str]) -> None:
        """Use to set up publisher targets to scrape a news

        Parameters
        ----------
        *args : Tuple[str]
            tuple of publisher name that available in PUBLISHER_NAME
        """        
        for key in self.__PUBLISHERS:
            if key in args:
                self.__PUBLISHERS[key] = True
            else:
                self.__PUBLISHERS[key] = False
    
    @property
    def base_url(self) -> dict:
        """Base urls of all request Api
        
        Returns
        -------
        dict
            dictionary of all base urls where key is publisher name and value is url of request Api
        """        
        base_urls = {}
        for key in self.__scraper:
            if self.__PUBLISHERS[key]:
                base_urls[key] = self.__scraper[key].base_url
        return base_urls

    def trace(self, limit:int = 0, checkpoint:dict = {}) -> List[str]:
        """Trace all news urls from all publisher since given checkpoint until reach the given limit
        
        Parameters
        ----------
        limit : int, optional
            trace limit 0 is mean as much as possible, by default 0
        checkpoint : dict, optional
            dictionary in pair of PUBLISHER_NAME and checkpoint, where checkpoint is mean the latest trace that can be a date-time format or news id, by default {}
        
        Returns
        -------
        List[str]
            list of traced news urls

        Raises
        ------
        ValueError
            error when some key of checkpoint that use to identify publisher not found in publisher list
        """     
        if not all([x in self.__scraper.keys() for x in checkpoint]):
            raise ValueError("Invalid Key of checkpoint")
        limit = self.MAX_TRACE_LIMIT if limit == 0 else limit
        traced_urls = []
        for key in self.__scraper:
            if self.__PUBLISHERS[key]:
                cp = "" if not key in checkpoint else checkpoint[key]
                urls = self.__scraper[key].trace(limit=self.MAX_TRACE_LIMIT, checkpoint=cp)
                traced_urls += urls
        self.urls = traced_urls
        return traced_urls
    
    def _filter(self, data:str) -> str:
        """Identify publisher from given url
        
        Parameters
        ----------
        data : str
            url that need to identify publisher name
        
        Returns
        -------
        str
            publisher name that's the part of __scraper.keys()
        """        
        sanook_matcher = re.compile(r'^(http://|https://|https://www\.|http://www\.)sanook\.com/news/[0-9]{7}(/|)$').match
        if bool(sanook_matcher(data)):
            return self.PUBLISHER_NAME.SANOOK
        return ''
    
    def scrape(self, urls:Union[str, List[str]]=None) -> List[dict]:
        """Scrape a news data from given url
        
        Parameters
        ----------
        urls : Union[str, List[str]], optional
            news url or list of news urls or None when the trace method has called before this method, by default None
        
        Returns
        -------
        List[dict]
            list of news data 
        """        
        if urls == None and len(self.urls) == 0:
            return []
        elif isinstance(urls, str):
            urls = [urls]
        elif isinstance(urls, list):
            urls = urls
        else:
            urls = self.urls
        scraped_list = []
        for url in urls:
            publisher_name = self._filter(url)
            if bool(publisher_name):
                scraped_data = self.__scraper[publisher_name].scrape(url)
                if len(scraped_data) >= 0:
                    scraped_list.append(scraped_data[0])
        return scraped_list