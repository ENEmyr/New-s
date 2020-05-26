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
            'sanook' : []
        }
    
    def __update_checkpoint(self, latest_news_ids:Dict[str, str]) -> None:
        for publisher in latest_news_ids:
            latest_news = []
            if len(latest_news_ids[publisher]) == 0:
                continue
            else:
                for news_id in latest_news_ids[publisher]:
                    if len(self.__checkpoints[publisher]) > 0:
                        self.__checkpoints[publisher] = latest_news_ids[publisher]
                    #if news_id not in self.__checkpoints:
                    #    if len(self.__checkpoints[publisher]) > 0:
                    #        self.__checkpoints[publisher].pop()
                    #    self.__checkpoints[publisher].insert(0, news_id)

    def __auto_scrape(self, name=None, run_event=None):
        print('Scraper worker is starting...')
        api_connector = ApiConnector()
        while run_event.is_set():
            try:
                urls, latest_news_ids = self.__news_scraper.trace(limit=self.__trace_limit, checkpoint=[])
                if latest_news_ids['sanook'] != self.__checkpoints['sanook']:
                    for news_id in latest_news_ids['sanook']:
                        if news_id not in self.__checkpoints['sanook']:
                            scraped_news = self.__news_scraper.scrape()
                            api_connector.setModel('raw')
                            for news in scraped_news:
                                status_code, status_text = api_connector.post(news)
                                if not status_code in api_connector.PASS_STATUS:
                                    print("Bad status code at post raw news :", status_code)
                                    continue
                                else:
                                    print("Raw news pushed.")
                    self.__update_checkpoint(latest_news_ids)
                print('Sleeping now')
                time.sleep(self.__delay)
            except:
                pass

    def __auto_summarize(self, name=None, run_event=None):
        print('Summarize worker is starting...')
        failed_mark_as_summarized = []
        raw_connector = ApiConnector()
        summarized_connector = ApiConnector()
        raw_connector.setModel('raw')
        summarized_connector.setModel('summarized')
        while run_event.is_set():
            try:
                get_raw_params = {'limit':24, 'summarizeStatus': 'false'}
                status_code, raw_news = raw_connector.get(get_raw_params)
                if len(raw_news) != 0:
                    for news in raw_news:
                        if type(news['_id']) != str:
                            if news['_id'] in failed_mark_as_summarized:
                                continue
                        mark_as_summarized = news['_id']
                        summarized_news = summarize(news['content'], self.__compression_rate, lang='th', algorithm=self.__summarize_algorithm)
                        if len(summarized_news) == 0: # return nothing from summarize system
                            try_different_algo = 'sentence_rank' if self.__summarize_algorithm == 'text_rank' else 'text_rank'
                            summarized_news = summarize(news['content'], self.__compression_rate, lang='th', algorithm=try_different_algo)
                        news['content'] = summarized_news if bool(summarized_news) else news['content']
                        del(news['_id'])
                        del(news['__v'])
                        del(news['insertDt'])
                        del(news['summarizeStatus'])
                        status_code, status_text = summarized_connector.post(news)
                        if not status_code in summarized_connector.PASS_STATUS:
                            print("Bad status code at post summarized news :", status_code)
                            continue
                        else:
                            print("Summarized news pushed")
                        status_code, status_text = raw_connector.put(mark_as_summarized, {"summarizeStatus": 'true'})
                        if not status_code in raw_connector.PASS_STATUS:
                            print("Failed to re-assign summarizeStatus with bad code :", status_code)
                            failed_mark_as_summarized.append(mark_as_summarized)
                        else:
                            print("Re-assign summarizeStatus completed on raw news id {}".format(mark_as_summarized))
                if len(failed_mark_as_summarized) != 0:
                    for i in range(0, len(failed_mark_as_summarized)):
                        status_code, status_text = raw_connector.put(failed_mark_as_summarized[i], {"summarizeStatus": True})
                        if not status_code in raw_connector.PASS_STATUS:
                            print("Failed to re-assign summarizeStatus with bad code :", status_code)
                        else:
                            print("Re-assign summarizeStatus completed on raw news id {}".format(mark_as_summarized))
                            del(failed_mark_as_summarized[i])
                time.sleep(self.__delay/2)
            except:
                pass
    
    # in progress
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
                #print('Delay...')
                time.sleep(self.__delay)
        except KeyboardInterrupt:
            print("Closing system...")
            run_event.clear()
            scraper_worker.join()
            summarier_worker.join()
            print("System closed.")
        return self.__checkpoints

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