import unittest
from newsScraper.scraper.SanookScraper import SanookScraper
from newsScraper.scraper.Scraper import ScrapeData
from newsScraper.NewsScraper import NewsScraper

class TestSanookScraper(unittest.TestCase):
    ''' Unit test for SanookScraper class '''
    def test_trace(self):
        limit = 5
        scraper = SanookScraper(limit)
        scraper.trace()
        self.assertTrue(len(scraper.urls) != 0, 'Traced urls equal to 0')

    def test_scrape(self):
        limit = 2
        scraper = SanookScraper(limit)
        valid_key = ScrapeData().legal_key
        scraper.trace()
        scraped_list = scraper.scrape()
        scraped_data = scraped_list[0]
        self.assertTrue(isinstance(scraped_data, dict), f'Unexpected scraped_data type {scraped_data}')
        self.assertTrue(all([x in valid_key for x in scraped_data.keys()]), f'Unexpected Api return {scraped_data}')

class TestNewsScraper(unittest.TestCase):
    ''' Unit test for NewsScraper adapter '''
    def test_baseurls(self):
        news_scraper = NewsScraper(2)
        self.assertTrue(len(news_scraper.base_url) > 0, 'base urls = 0')
    
    def test_trace(self):
        news_scraper = NewsScraper(2)
        news_scraper.trace()
        self.assertTrue(len(news_scraper.urls) != 0, 'Traced urls equal to 0')
    
    def test_scrape(self):
        news_scraper = NewsScraper(2)
        valid_key = ScrapeData().legal_key
        news_scraper.trace(checkpoint={news_scraper.PUBLISHER_NAME.SANOOK: '8064866'})
        scraped_list = news_scraper.scrape()
        scraped_data = scraped_list[0]
        self.assertTrue(isinstance(scraped_data, dict), f'Unexpected scraped_data type {scraped_data}')
        self.assertTrue(all([x in valid_key for x in scraped_data.keys()]), f'Unexpected Api return {scraped_data}')