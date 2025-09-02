"""
Indeed Job Scraper
Scrapes job listings from Indeed.com
"""

from typing import List, Dict
import re
from urllib.parse import urljoin, quote
from .base_scraper import BaseScraper
import cloudscraper
from bs4 import BeautifulSoup
import logging

class IndeedScraper(BaseScraper):
    def __init__(self):
        super().__init__("Indeed")
        self.base_url = "https://www.indeed.com/jobs"
        self.scraper = cloudscraper.create_scraper()
        self.logger = logging.getLogger('IndeedScraper')
    
    def search_jobs(self, keywords: List[str], location: str = "Poland", include_remote: bool = True) -> List[Dict]:
        """Search for jobs on Indeed"""
        all_jobs = []
        
        # Handle location variations
        location_map = {
            "Poland": "Poland",
            "Warsaw": "Warsaw, Poland",
            "Krakow": "Kraków, Poland",
            "Wroclaw": "Wrocław, Poland",
            "Poznan": "Poznań, Poland",
            "Gdansk": "Gdańsk, Poland",
            "Remote Poland": "Remote"
        }
        
        search_location = location_map.get(location, location)
        
        for keyword in keywords:
            try:
                jobs = self._search_keyword(keyword, search_location, include_remote)
                all_jobs.extend(jobs)
            except Exception as e:
                self.logger.error(f"Error searching Indeed for '{keyword}': {str(e)}")
        
        # Remove duplicates
        seen_urls = set()
        unique_jobs = []
        for job in all_jobs:
            if job['job_url'] not in seen_urls:
                seen_urls.add(job['job_url'])
                unique_jobs.append(job)
        
        return unique_jobs
    
    def _search_keyword(self, keyword: str, location: str, include_remote: bool) -> List[Dict]:
        """Search for specific keyword on Indeed"""
        jobs = []
        
        params = {
            'q': keyword,
            'l': location,
            'sort': 'date',  # Sort by date
            'fromage': '14',  # Jobs from last 14 days
        }
        
        if include_remote:
            params['remotejob'] = '1'
        
        try:
            response = self.scraper.get(self.base_url, params=params, timeout=30)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Find job cards
                job_cards = soup.find_all('div', class_='job_seen_beacon') or \
                           soup.find_all('div', class_='jobsearch-SerpJobCard') or \
                           soup.find_all('div', {'data-testid': 'job-card'})
                
                for card in job_cards[:50]:  # Limit to 50 jobs per keyword
                    job = self._parse_job_card(card)
                    if job:
                        jobs.append(job)
                        
        except Exception as e:
            self.logger.error(f"Error fetching Indeed results: {str(e)}")
        
        return jobs
    
    def _parse_job_card(self, card) -> Dict:
        """Parse individual job card from Indeed"""
        try:
            job = {}
            
            # Job title
            title_elem = card.find('h2', class_='jobTitle') or \
                        card.find('a', {'data-testid': 'job-title'}) or \
                        card.find('span', {'title': True})
            
            if title_elem:
                job['job_title'] = self.clean_text(title_elem.get_text())
            else:
                return None
            
            # Company
            company_elem = card.find('span', class_='companyName') or \
                          card.find('div', class_='companyName') or \
                          card.find('a', {'data-testid': 'company-name'})
            
            if company_elem:
                job['company'] = self.clean_text(company_elem.get_text())
            else:
                job['company'] = 'Unknown'
            
            # Location
            location_elem = card.find('div', class_='companyLocation') or \
                           card.find('span', class_='locationsContainer') or \
                           card.find('div', {'data-testid': 'job-location'})
            
            if location_elem:
                job['location'] = self.clean_text(location_elem.get_text())
            else:
                job['location'] = 'Not specified'
            
            # Job URL
            link_elem = card.find('a', href=True)
            if link_elem:
                job['job_url'] = f"https://www.indeed.com{link_elem['href']}"
            else:
                job['job_url'] = self.base_url
            
            # Description snippet
            desc_elem = card.find('div', class_='job-snippet') or \
                       card.find('div', class_='summary')
            
            if desc_elem:
                job['description'] = self.clean_text(desc_elem.get_text())
            else:
                job['description'] = ''
            
            # Posted date
            date_elem = card.find('span', class_='date') or \
                       card.find('span', {'data-testid': 'myJobsStateDate'})
            
            if date_elem:
                job['posted_date'] = self.clean_text(date_elem.get_text())
            else:
                job['posted_date'] = 'Recently'
            
            # Platform
            job['platform'] = 'Indeed'
            
            return job
            
        except Exception as e:
            self.logger.error(f"Error parsing Indeed job card: {str(e)}")
            return None
    
    def parse_job_listing(self, listing) -> Dict:
        """Compatibility method for base class"""
        return self._parse_job_card(listing)