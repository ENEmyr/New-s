import unittest
from newsScraper.scraper.SanookScraper import SanookScraper
from newsScraper.scraper.Scraper import ScrapeData

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

if __name__ == '__main__':
    unittest.main()