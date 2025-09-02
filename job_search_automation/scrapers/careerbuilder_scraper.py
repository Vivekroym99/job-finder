"""
CareerBuilder Job Scraper
Scrapes job listings from CareerBuilder.com
"""

from typing import List, Dict
import re
from urllib.parse import urljoin, quote
from .base_scraper import BaseScraper
import cloudscraper
from bs4 import BeautifulSoup
import logging

class CareerBuilderScraper(BaseScraper):
    def __init__(self):
        super().__init__("CareerBuilder")
        self.base_url = "https://www.careerbuilder.com/jobs"
        self.scraper = cloudscraper.create_scraper()
        self.logger = logging.getLogger('CareerBuilderScraper')
    
    def search_jobs(self, keywords: List[str], location: str = "Poland", include_remote: bool = True) -> List[Dict]:
        """Search for jobs on CareerBuilder"""
        all_jobs = []
        
        for keyword in keywords:
            try:
                jobs = self._search_keyword(keyword, location, include_remote)
                all_jobs.extend(jobs)
            except Exception as e:
                self.logger.error(f"Error searching CareerBuilder for '{keyword}': {str(e)}")
        
        # Remove duplicates
        seen_urls = set()
        unique_jobs = []
        for job in all_jobs:
            if job['job_url'] not in seen_urls:
                seen_urls.add(job['job_url'])
                unique_jobs.append(job)
        
        return unique_jobs
    
    def _search_keyword(self, keyword: str, location: str, include_remote: bool) -> List[Dict]:
        """Search for specific keyword on CareerBuilder"""
        jobs = []
        
        # Build search URL
        search_query = f"{keyword}-jobs"
        if location and location != "Poland":
            search_query += f"-in-{location.replace(' ', '-').lower()}"
        
        url = f"{self.base_url}/{search_query}"
        
        try:
            response = self.scraper.get(url, timeout=30)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Find job cards
                job_cards = soup.find_all('div', class_='job-row') or \
                           soup.find_all('li', class_='job-listing') or \
                           soup.find_all('article', class_='job')
                
                for card in job_cards[:50]:
                    job = self._parse_job_card(card)
                    if job:
                        # Add remote tag if searching for remote
                        if include_remote and 'remote' in job.get('location', '').lower():
                            job['remote'] = True
                        jobs.append(job)
                        
        except Exception as e:
            self.logger.error(f"Error fetching CareerBuilder results: {str(e)}")
        
        return jobs
    
    def _parse_job_card(self, card) -> Dict:
        """Parse individual job card from CareerBuilder"""
        try:
            job = {}
            
            # Job title
            title_elem = card.find('h2', class_='job-title') or \
                        card.find('a', class_='job-title') or \
                        card.find('h3')
            
            if title_elem:
                job['job_title'] = self.clean_text(title_elem.get_text())
            else:
                return None
            
            # Company
            company_elem = card.find('div', class_='employer') or \
                          card.find('span', class_='company-name') or \
                          card.find('a', class_='employer-name')
            
            if company_elem:
                job['company'] = self.clean_text(company_elem.get_text())
            else:
                job['company'] = 'Unknown'
            
            # Location
            location_elem = card.find('div', class_='location') or \
                           card.find('span', class_='job-location')
            
            if location_elem:
                job['location'] = self.clean_text(location_elem.get_text())
            else:
                job['location'] = 'Not specified'
            
            # Job URL
            link_elem = card.find('a', href=True)
            if link_elem and 'href' in link_elem.attrs:
                if link_elem['href'].startswith('http'):
                    job['job_url'] = link_elem['href']
                else:
                    job['job_url'] = f"https://www.careerbuilder.com{link_elem['href']}"
            else:
                job['job_url'] = self.base_url
            
            # Description
            desc_elem = card.find('div', class_='job-description') or \
                       card.find('div', class_='job-snippet')
            
            if desc_elem:
                job['description'] = self.clean_text(desc_elem.get_text())[:500]
            else:
                job['description'] = ''
            
            # Posted date
            date_elem = card.find('div', class_='time-posted') or \
                       card.find('span', class_='job-date')
            
            if date_elem:
                job['posted_date'] = self.clean_text(date_elem.get_text())
            else:
                job['posted_date'] = 'Recently'
            
            job['platform'] = 'CareerBuilder'
            
            return job
            
        except Exception as e:
            self.logger.error(f"Error parsing CareerBuilder job card: {str(e)}")
            return None
    
    def parse_job_listing(self, listing) -> Dict:
        """Compatibility method for base class"""
        return self._parse_job_card(listing)