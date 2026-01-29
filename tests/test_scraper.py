import sys
import unittest
from unittest.mock import patch, MagicMock
# Add project root to path
sys.path.append(".")
from app.core.scraper import WebScraper

class TestWebScraper(unittest.TestCase):
    def setUp(self):
        self.scraper = WebScraper()

    @patch('app.core.scraper.trafilatura.fetch_url')
    @patch('app.core.scraper.trafilatura.extract')
    @patch('app.core.scraper.trafilatura.bare_extraction')
    def test_fetch_and_extract_success(self, mock_bare, mock_extract, mock_fetch):
        # Setup mocks
        mock_fetch.return_value = "<html>Mock HTML</html>"
        mock_extract.return_value = "Mock extracted content."
        mock_bare.return_value = {'title': 'Mock Title'}
        
        url = "http://example.com"
        result = self.scraper.fetch_and_extract(url)
        
        self.assertEqual(result["content"], "Mock extracted content.")
        self.assertEqual(result["title"], "Mock Title")
        self.assertEqual(result["url"], url)
        self.assertIsNone(result["error"])

    @patch('app.core.scraper.trafilatura.fetch_url')
    def test_fetch_failure(self, mock_fetch):
        # Simulate download failure
        mock_fetch.return_value = None
        
        url = "http://bad-url.com"
        result = self.scraper.fetch_and_extract(url)
        
        self.assertEqual(result["error"], "Failed to download content.")
        self.assertEqual(result["content"], "")

    @patch('app.core.scraper.trafilatura.fetch_url')
    @patch('app.core.scraper.trafilatura.extract')
    def test_extract_failure(self, mock_extract, mock_fetch):
        # Simulate fetch success but extract failure (no content)
        mock_fetch.return_value = "<html>Empty/Ads</html>"
        mock_extract.return_value = None # No content found
        
        url = "http://empty.com"
        result = self.scraper.fetch_and_extract(url)
        
        self.assertEqual(result["error"], "No main content found.")

if __name__ == '__main__':
    unittest.main()
