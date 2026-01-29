import requests
import trafilatura
import re
from typing import Optional, Dict, Any

class WebScraper:
    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def fetch_and_extract(self, url: str) -> Dict[str, Any]:
        """
        Fetches a URL and extracts the main text content, title, and metadata.
        
        Args:
            url (str): The URL to scrape.
            
        Returns:
            Dict: {
                "content": str (Cleaned main text),
                "title": str (Page title),
                "url": str,
                "error": str (Optional error message)
            }
        """
        result = {
            "content": "",
            "title": "",
            "url": url,
            "error": None
        }
        
        try:
            # 1. Fetch
            downloaded = trafilatura.fetch_url(url)
            
            if downloaded is None:
                # trafilatura fetch failed (maybe 404 or network), try requests manually as backup
                # or just report error. trafilatura.fetch_url uses requests under the hood usually.
                # Let's try explicit requests for better error control if needed, 
                # but trafilatura.fetch_url is robust.
                result["error"] = "Failed to download content."
                return result

            # 2. Extract
            # include_comments=False, include_tables=False for cleaner text
            content = trafilatura.extract(downloaded, include_comments=False, include_tables=False, no_fallback=False)
            
            if not content:
                result["error"] = "No main content found."
                return result

            # 3. Metadata (Title etc)
            # trafilatura.extract usually returns just text.
            # To get metadata, we might need bare_extraction
            metadata = trafilatura.bare_extraction(downloaded)
            
            if metadata:
                # metadata is a Document object (or dict depending on version, but error said Document)
                # It usually acts as a dict in older versions but error implies object.
                # Let's try attribute access or generic check.
                # Safer: check if it has .get, if not assume attribute.
                if hasattr(metadata, 'get'):
                    result["title"] = metadata.get('title') or ""
                else:
                    # Assume object with attributes
                    result["title"] = getattr(metadata, 'title', "") or ""
            
            # Fallback: Regex for title if missing
            if not result["title"]:
                title_match = re.search(r'<title>(.*?)</title>', downloaded, re.IGNORECASE | re.DOTALL)
                if title_match:
                    result["title"] = title_match.group(1).strip()

            result["content"] = content
            
        except Exception as e:
            result["error"] = str(e)
            
        return result
