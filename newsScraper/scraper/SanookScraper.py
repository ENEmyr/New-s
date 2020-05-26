import requests
import re
from bs4 import BeautifulSoup
from datetime import datetime
from typing import List, Union, Tuple, Set
from newsScraper.scraper.Scraper import Scraper
from itertools import cycle

class SanookScraper(Scraper):
    ''' News scraper for sanook '''
    def __init__(self, max_trace_limit:int = 100):
        super().__init__(max_trace_limit)
        self.__NEWS_SITE = 'https://www.sanook.com/news/'
        self.__proxies_pool = cycle(self.get_proxies())
    
    @property
    def base_url(self) -> str:
        """Base url of request Api
        
        Returns
        -------
        str
            https://graph.sanook.com
        """        
        return "https://graph.sanook.com"

    def trace(self, limit:int = 0, checkpoint:List[str] = []) -> Tuple[Set[str], str]:
        """Trace all news urls since given checkpoint until reach the given limit
        
        Parameters
        ----------
        limit : int, optional
            trace limit 0 is mean as much as possible, by default 0
        checkpoint : List[str], optional
            news id that represent the latest trace, by default []
        
        Returns
        -------
        Tuple[Set[str], str]
            list of traced news urls and latest news id

        Raises
        ------
        Exception 'Call Sanook Api failed'
            Occur when got bad status code from api or failed when tried to decode a response as json
        """        
        latest_news_ids = []
        limit = self.MAX_TRACE_LIMIT if limit == 0 else limit
        qparam_operationName = 'getArchiveEntries'
        qparam_variables = '{"oppaChannel":"news","oppaCategorySlugs":[],"channels":["news"],"notInCategoryIds":[{"channel":"news","ids":[]}],"orderBy":{"field":"CREATED_AT","direction":"DESC"},"first":'+str(limit)+',"offset":0,"after":"Y3Vyc29yOjE5"}'
        qparam_extensions = '{"persistedQuery":{"version":1,"sha256Hash":"f754ffc68eb4683990679d0154c39cb90b63d628"}}'
        qparams = {
            'operationName':qparam_operationName,
            'variables': qparam_variables,
            'extensions': qparam_extensions
            }
        response = requests.get(self.base_url, params=qparams, headers=self.random_header(), proxies={"http": next(self.__proxies_pool)})
        if response.status_code not in self.PASS_STATUS:
            raise Exception('Call Sanook api failed.')
        try:
            data = response.json()
        except:
            raise Exception('Call Sanook api failed.')
        try:
            edges = data['data']['entries']['edges']
        except:
            print(data)
        traced_urls = []
        for edge in edges:
            node = edge['node']
            if len(checkpoint) > 0 and node['id'] in checkpoint:
                break
            else:
                url = f"{self.__NEWS_SITE}{node['id']}"
                latest_news_ids.append(node['id'])
                traced_urls.append(url)
        self.urls = traced_urls
        return traced_urls, set(latest_news_ids)
    
    def _filter(self, data:dict) -> dict:
        """Filter a raw scraped data and give the clean one after processed
        
        Parameters
        ----------
        data : dict
            raw scraped data
        
        Returns
        -------
        dict
            filtered scraped data
        """        
        data = data['data']['entry']
        if len(data['body']) > 1:
            # News content mostly will not be too long
            return {}
        sanook_url = f"{self.__NEWS_SITE}{data['id']}"
        dt_raw = data['createdAtdatetime'].split(' ')
        year, month, day = dt_raw[0].split('-')
        hour, minute = dt_raw[1].split(':')
        year, month, day, hour, minute = int(year), int(month), int(day), int(hour), int(minute)
        dt_isoformat = datetime(year, month, day, hour, minute).isoformat('T')+'Z' # create datetime according to RFC3339 format
        content = BeautifulSoup(data['body'][0], features='html.parser').getText() # clean html tag with beautiful soup
        
        self._scraped_data['title'] = data['title'] or 'Untitled'
        self._scraped_data['imageUrl'] = data['thumbnail'] or 'Undefined'
        self._scraped_data['content'] = content
        self._scraped_data['publisher'] = 'Sanook'
        self._scraped_data['language'] = ['th']
        self._scraped_data['tags'] = data['tags'] or []
        self._scraped_data['publishAt'] = dt_isoformat
        self._scraped_data['sourceUrl'] = sanook_url
        try:
            self._scraped_data['category'] = data['primaryCategory']['name'] or 'Undefined'
        except:
            self._scraped_data['category'] = 'Undefined'
        try:
            self._scraped_data['author'] = data['author']['name'] or data['author']['realName'] or 'Sanook'
        except:
            self._scraped_data['author'] = 'Sanook'
        return self._scraped_data
    
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
        
        Raises
        ------
        ValueError
            error when have no url in urls or hasn't call trace method before
        """        
        if urls == None and len(self.urls) == 0:
            return []
        elif isinstance(urls, str):
            urls = [urls]
        elif isinstance(urls, list):
            urls = urls
        else:
            urls = self.urls
        filtered_list = []
        qparam_operationName = 'getEntryWithGallery'
        qparam_extensions = '{"persistedQuery":{"version":1,"sha256Hash":"2d493971ae139330de9de1c8e8494561d27b2d11"}}'
        for url in urls:
            url_matcher = re.compile(r'^(http://|https://|https://www\.|http://www\.)sanook\.com/news/[0-9]{7}(/|)$').match
            id_matcher = re.compile(r'[0-9]{7}').search
            if bool(url_matcher(url)):
                id = id_matcher(url).group()
            else:
                raise ValueError('Invalid url')
            qparam_variables = '{"id":"'+str(id)+'","channel":"news","relatedLimit":5,"relatedGalleryFirst":6,"oppaChannel":"news","oppaCategorySlugs":[]}'
            qparams = {
                'operationName':qparam_operationName,
                'variables': qparam_variables,
                'extensions': qparam_extensions
                }
            response = requests.get(self.base_url, params=qparams, headers=self.random_header(), proxies={"http": next(self.__proxies_pool)})
            if response.status_code not in self.PASS_STATUS:
                continue
            else:
                try:
                    filtered_data = self._filter(response.json())
                except ValueError as err:
                    continue
                if bool(filtered_data) :
                    tmp_dict = dict(filtered_data) # for some reason if not do this filtered_data will point to old memory address
                    filtered_list.append(tmp_dict)
        return filtered_list