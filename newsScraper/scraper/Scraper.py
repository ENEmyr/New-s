import collections, re, random, requests
from bs4 import BeautifulSoup
from typing import List, Tuple, Union
from abc import ABC, abstractmethod

class ScrapeData(dict):
    def __init__(self, iterable:dict = {}):
        super().__init__(iterable)
    
    @property
    def legal_key(self) -> List[str]:
        """Legal key of scraper data dictionary
        
        Returns
        -------
        List[str]
            list of legal key
        """        
        LEGAL_KEY_LIST = [
            "title",
            "imageUrl",
            "content",
            "publisher",
            "author",
            "language",
            "tags",
            "category",
            "publishAt",
            "sourceUrl"
        ]
        return LEGAL_KEY_LIST

    def __validate_iso8601(self, dt_str:str) -> bool:
        """Validate an ISO8601 format from given datetime string
        
        Parameters
        ----------
        dt_str : str
            datetime string
        
        Returns
        -------
        bool
            validate result
        """        
        matcher = re.compile(r'^(-?(?:[1-9][0-9]*)?[0-9]{4})-(1[0-2]|0[1-9])-(3[01]|0[1-9]|[12][0-9])T(2[0-3]|[01][0-9]):([0-5][0-9]):([0-5][0-9])(\.[0-9]+)?(Z|[+-](?:2[0-3]|[01][0-9]):[0-5][0-9])?$').match
        try:
            if matcher(dt_str) is not None:
                return True
            else:
                return False
        except:
            return False

    def __setitem__(self, key, value):
        if key in self.legal_key:
            if key == 'publishAt':
                if not self.__validate_iso8601(value):
                    raise ValueError('Illegal datetime format')
            elif key == 'tags' and not isinstance(value, list):
                raise ValueError('Illegal tags type')
            elif key == 'language' and not isinstance(value, list):
                raise ValueError('Illegal language type')
            return super().__setitem__(key, value)
        else:
            raise ValueError('Illegal key')

class Scraper(ABC):
    ''' Abstract class for scraper '''
    def __init__(self, max_trace_limit:int):
        """Constructor of Scraper class
        
        Parameters
        ----------
        max_trace_limit : int
            max number of limit that used in order to trace a news from news source
        """        
        self._scraped_data = ScrapeData({
            "title":"",
            "imageUrl":"",
            "content":"",
            "author":"",
            "publisher":"",
            "language": [],
            "tags": [],
            "category": "",
            "publishAt": "",
            "sourceUrl": ""
        })
        self.__urls = [],
        self.__MAX_TRACE_LIMIT = max_trace_limit
        self.__HEADERS_LIST = [
            'Mozilla/5.0 (Windows; U; Windows NT 6.1; x64; fr; rv:1.9.2.13) Gecko/20101203 Firebird/3.6.13',
            'Mozilla/5.0 (compatible, MSIE 11, Windows NT 6.3; Trident/7.0; rv:11.0) like Gecko',
            'Mozilla/5.0 (Windows; U; Windows NT 6.1; rv:2.2) Gecko/20110201',
            'Opera/9.80 (X11; Linux i686; Ubuntu/14.10) Presto/2.12.388 Version/12.16',
            'Mozilla/5.0 (Windows NT 5.2; RW; rv:7.0a1) Gecko/20091211 SeaMonkey/9.23a1pre'
        ]

    @property
    def PASS_STATUS(self) -> List[int]:
        """Status code of response successfully
        
        Returns
        -------
        List[int]
            list of successfully status code
        """        
        return [200, 204]
    
    @property
    def HEADER_LIST(self) -> List[str]:
        """Header of request
        
        Returns
        -------
        List[str]
            list of request header 
        """        
        return self.__HEADERS_LIST

    @property
    def PROXY_URL(self) -> str:
        """Url to find a proxy list
        
        Returns
        -------
        str
            url of proxy collector website
        """        
        return 'https://free-proxy-list.net/'

    @property
    def MAX_TRACE_LIMIT(self) -> int:
        """Maximum trace limit
        
        Returns
        -------
        int
            maximum number of urls in trace process
        """        
        return self.__MAX_TRACE_LIMIT

    @property
    @abstractmethod
    def base_url(self) -> str:
        """Base url of request Api
        
        Returns
        -------
        str
            base url of request Api
        """        
        pass
    
    @property
    def urls(self) -> List[str]:
        """View queue of news url
        
        Returns
        -------
        List[str]
            list of news url that used to scrape a news data
        """        
        return self.__urls.copy()

    @urls.setter
    def urls(self, new_urls:List[str]) -> None:
        """Set new url list to urls
        
        Parameters
        ----------
        urls : List[str]
            list of news url
        
        Raises
        ------
        ValueError
            error when given urls is not a list of string
        """        
        if isinstance(new_urls, list):
            if all([isinstance(x, str) for x in new_urls]) or len(new_urls) == 0:
                self.__urls = new_urls
            else:
                raise ValueError('Invalid urls')
        else:
            raise ValueError('Invalid urls')
    
    @abstractmethod
    def trace(self, limit:int = 0, checkpoint:str = '') -> Tuple[List[str], str]:
        """Trace all news urls since given checkpoint until reach the given limit
        
        Parameters
        ----------
        limit : int, optional
            trace limit 0 is mean as much as possible, by default 0
        checkpoint : str, optional
            the checkpoint of latest trace can be a date-time format or news id, by default ''
        
        Returns
        -------
        Tuple[List[str], str]
            list of traced news urls and latest news id
        """        
        limit = self.MAX_TRACE_LIMIT if limit == 0 else limit

    @abstractmethod
    def _filter(self, data:Union[dict, str]) -> dict:
        """Filter a raw scraped data and give the clean one after processed
        
        Parameters
        ----------
        data : Union[dict, str]
            raw scraped data
        
        Returns
        -------
        dict
            filtered scraped data
        """        
        pass

    @abstractmethod
    def scrape(self, urls:Union[str, List[str]] = None) -> List[dict]:
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

    def random_header(self) -> dict:
        """Random a heder that use for change request header
        
        Returns
        -------
        dict
            A dictionary contains User-Agent
        """        
        return {'User-Agent': random.choice(self.__HEADERS_LIST)}
    
    def get_proxies(self) -> List[str]:
        """Get a list of proxies that can be use for change request proxy
        
        Returns
        -------
        List[str]
            A list of proxies
        """        
        res = requests.get(self.PROXY_URL)
        soup = BeautifulSoup(res.text, 'lxml')
        table = soup.find('table',id='proxylisttable')
        list_tr = table.find_all('tr')
        list_td = [elem.find_all('td') for elem in list_tr]
        list_td = list(filter(None, list_td))
        list_ip = [elem[0].text for elem in list_td]
        list_ports = [elem[1].text for elem in list_td]
        list_proxies = [':'.join(elem) for elem in list(zip(list_ip, list_ports))]
        return list_proxies               