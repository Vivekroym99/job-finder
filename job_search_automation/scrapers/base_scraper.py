from abc import ABC, abstractmethod
from typing import List, Dict
import requests
from bs4 import BeautifulSoup
import time
import random
from fake_useragent import UserAgent
import logging

class BaseScraper(ABC):
    def __init__(self, platform_name: str):
        self.platform_name = platform_name
        self.ua = UserAgent()
        self.session = requests.Session()
        self.logger = logging.getLogger(platform_name)
        
    def get_headers(self) -> Dict:
        return {
            'User-Agent': self.ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
    
    def make_request(self, url: str, params: Dict = None) -> requests.Response:
        try:
            time.sleep(random.uniform(1, 3))
            response = self.session.get(
                url,
                headers=self.get_headers(),
                params=params,
                timeout=30
            )
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            self.logger.error(f"Request failed for {url}: {str(e)}")
            return None
    
    def parse_html(self, html: str) -> BeautifulSoup:
        return BeautifulSoup(html, 'html.parser')
    
    @abstractmethod
    def search_jobs(self, keywords: List[str], location: str = None) -> List[Dict]:
        pass
    
    @abstractmethod
    def parse_job_listing(self, listing) -> Dict:
        pass
    
    def clean_text(self, text: str) -> str:
        if not text:
            return ""
        return ' '.join(text.strip().split())