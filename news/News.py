import threading
import asyncio
import time
from typing import List, Tuple, Union, Dict
from apiConnector.ApiConnector import ApiConnector
from newsScraper.NewsScraper import NewsScraper
from summarization.Summarization import summarize

class News:
    ''' Main package that used to run automatic news summarization from online news source '''
    def __init__(
        self, 
        delay:float = 3600, 
        trace_limit:int = 12, 
        summarize_algorithm:str = 'text_rank',
        compression_rate:float = .6,
        checkpoints:dict = {}
        ) -> None:
        self.__delay = delay
        self.__trace_limit = trace_limit
        self.__summarize_algorithm = summarize_algorithm
        self.__compression_rate = compression_rate
        self.__news_scraper = NewsScraper(max_trace_limit=trace_limit)
        self.__checkpoints = checkpoints if bool(checkpoints) else {
            'sanook' : ''
        }
    
    async def __update_checkpoint(self, latest_news_ids:Dict[str, str]) -> None:
        for publisher in latest_news_ids:
            self.__checkpoints[publisher] = latest_news_ids[publisher]

    async def __auto_scrape(self, name=None, run_event=None):
        api_connector = ApiConnector()
        #while run_event.is_set():
        urls, latest_news_ids = self.__news_scraper.trace(limit=self.__trace_limit, checkpoint=self.__checkpoints)
        if latest_news_ids['sanook'] != self.__checkpoints['sanook']:
            scraped_news = self.__news_scraper.scrape()
            await self.__update_checkpoint(latest_news_ids)
            api_connector.setModel('raw')
            for news in scraped_news:
                status_code, status_text = await api_connector.post(news)
                if not status_code in api_connector.PASS_STATUS:
                    print("Bad status code at post raw news :", status_code)
                    continue
                else:
                    print("Raw news pushed.")
    
    async def __auto_summarize(self, name=None, run_event=None):
        failed_del_id = []
        raw_connector = ApiConnector()
        summarized_connector = ApiConnector()
        raw_connector.setModel('raw')
        summarized_connector.setModel('summarized')
        #while run_event.is_set():
        get_raw_params = {'limit':24}
        status_code, raw_news = await raw_connector.get(get_raw_params)
        if len(raw_news) != 0:
            for news in raw_news:
                if news['_id'] in failed_del_id:
                    continue
                del_id = news['_id']
                summarized_news = summarize(news['content'], self.__compression_rate, lang='th', algorithm='text_rank')
                news['content'] = summarized_news
                del(news['_id'])
                del(news['__v'])
                del(news['insertDt'])
                status_code, status_text = await summarized_connector.post(news)
                if not status_code in summarized_connector.PASS_STATUS:
                    print("Bad status code at post summarized news :", status_code)
                    continue
                else:
                    print("Summarized news pushed")
                status_code, status_text = await raw_connector.delete(del_id)
                time.sleep(5)
                if not status_code in raw_connector.PASS_STATUS:
                    print("Bad status code at del raw news :", status_code)
                    failed_del_id.append(del_id)
                else:
                    print("Delete raw news id {} completed".format(del_id))
        if len(failed_del_id) != 0:
            for i in range(0, len(failed_del_id)):
                status_code, status_text = await raw_connector.delete(failed_del_id[i])
                if not status_code in raw_connector.PASS_STATUS:
                    print("Bad status code at del raw news :", status_code)
                else:
                    del(failed_del_id[i])
    
    # implement in progress
    def run_tasks(self):
        run_event = threading.Event()
        run_event.set()
        scraper_worker = threading.Thread(target=self.__auto_scrape, args=('scraper', run_event))
        summarier_worker = threading.Thread(target=self.__auto_summarize, args=('scraper', run_event))
        scraper_worker.start()
        summarier_worker.start()
        print("System started.")
        try:
            while True:
                time.sleep(self.__delay)
        except KeyboardInterrupt:
            print("Closing system...")
            run_event.clear()
            scraper_worker.join()
            summarier_worker.join()
            print("System closed.")

    def start(self):
        try:
            print('System started.')
            while True:
                asyncio.run(self.__auto_scrape())
                asyncio.run(self.__auto_summarize())
                time.sleep(self.__delay)
        except KeyboardInterrupt:
            print("System closed.")
        return self.__checkpoints