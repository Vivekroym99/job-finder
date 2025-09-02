"""
Monster Job Scraper
Scrapes job listings from Monster.com
"""

from typing import List, Dict
import re
from urllib.parse import urljoin, quote
from .base_scraper import BaseScraper
import cloudscraper
from bs4 import BeautifulSoup
import logging
import json

class MonsterScraper(BaseScraper):
    def __init__(self):
        super().__init__("Monster")
        self.base_url = "https://www.monster.com/jobs/search"
        self.scraper = cloudscraper.create_scraper()
        self.logger = logging.getLogger('MonsterScraper')
    
    def search_jobs(self, keywords: List[str], location: str = "Poland", include_remote: bool = True) -> List[Dict]:
        """Search for jobs on Monster"""
        all_jobs = []
        
        # Monster uses different location formats
        location_formatted = self._format_location(location)
        
        for keyword in keywords:
            try:
                jobs = self._search_keyword(keyword, location_formatted, include_remote)
                all_jobs.extend(jobs)
            except Exception as e:
                self.logger.error(f"Error searching Monster for '{keyword}': {str(e)}")
        
        # Remove duplicates
        seen_urls = set()
        unique_jobs = []
        for job in all_jobs:
            if job['job_url'] not in seen_urls:
                seen_urls.add(job['job_url'])
                unique_jobs.append(job)
        
        return unique_jobs
    
    def _format_location(self, location: str) -> str:
        """Format location for Monster search"""
        location_map = {
            "Poland": "Poland",
            "Warsaw": "Warsaw, Poland",
            "Krakow": "Krakow, Poland",
            "Wroclaw": "Wroclaw, Poland",
            "Poznan": "Poznan, Poland",
            "Gdansk": "Gdansk, Poland",
            "Remote Poland": "Remote"
        }
        return location_map.get(location, location)
    
    def _search_keyword(self, keyword: str, location: str, include_remote: bool) -> List[Dict]:
        """Search for specific keyword on Monster"""
        jobs = []
        
        params = {
            'q': keyword,
            'where': location,
            'page': 1,
            'perPage': 50
        }
        
        if include_remote:
            params['cy'] = 'pl'  # Country code for Poland
            params['rad'] = 'virtual'  # Include remote jobs
        
        try:
            response = self.scraper.get(self.base_url, params=params, timeout=30)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Look for job data in script tags (Monster often uses JSON-LD)
                script_tags = soup.find_all('script', type='application/ld+json')
                for script in script_tags:
                    try:
                        data = json.loads(script.string)
                        if isinstance(data, dict) and data.get('@type') == 'JobPosting':
                            job = self._parse_json_job(data)
                            if job:
                                jobs.append(job)
                    except:
                        pass
                
                # Also try parsing HTML job cards
                job_cards = soup.find_all('div', class_='job-cardstyle') or \
                           soup.find_all('section', {'data-testid': 'job-card'}) or \
                           soup.find_all('article', class_='js_result_row')
                
                for card in job_cards[:50]:
                    job = self._parse_job_card(card)
                    if job:
                        jobs.append(job)
                        
        except Exception as e:
            self.logger.error(f"Error fetching Monster results: {str(e)}")
        
        return jobs
    
    def _parse_json_job(self, data: dict) -> Dict:
        """Parse job from JSON-LD data"""
        try:
            job = {
                'job_title': data.get('title', ''),
                'company': data.get('hiringOrganization', {}).get('name', 'Unknown'),
                'location': data.get('jobLocation', {}).get('address', {}).get('addressLocality', 'Not specified'),
                'description': data.get('description', ''),
                'posted_date': data.get('datePosted', 'Recently'),
                'job_url': data.get('url', self.base_url),
                'platform': 'Monster'
            }
            
            # Clean up the data
            for key in job:
                if isinstance(job[key], str):
                    job[key] = self.clean_text(job[key])
            
            return job if job['job_title'] else None
            
        except Exception as e:
            self.logger.error(f"Error parsing Monster JSON job: {str(e)}")
            return None
    
    def _parse_job_card(self, card) -> Dict:
        """Parse individual job card from Monster"""
        try:
            job = {}
            
            # Job title
            title_elem = card.find('h2', class_='title') or \
                        card.find('h3', class_='jobTitle') or \
                        card.find('a', class_='job-title')
            
            if title_elem:
                job['job_title'] = self.clean_text(title_elem.get_text())
            else:
                return None
            
            # Company
            company_elem = card.find('div', class_='company') or \
                          card.find('span', class_='name') or \
                          card.find('a', class_='company-name')
            
            if company_elem:
                job['company'] = self.clean_text(company_elem.get_text())
            else:
                job['company'] = 'Unknown'
            
            # Location
            location_elem = card.find('div', class_='location') or \
                           card.find('span', class_='location-name') or \
                           card.find('div', class_='job-location')
            
            if location_elem:
                job['location'] = self.clean_text(location_elem.get_text())
            else:
                job['location'] = 'Not specified'
            
            # Job URL
            link_elem = card.find('a', href=True)
            if link_elem and link_elem['href'].startswith('http'):
                job['job_url'] = link_elem['href']
            elif link_elem:
                job['job_url'] = f"https://www.monster.com{link_elem['href']}"
            else:
                job['job_url'] = self.base_url
            
            # Description
            desc_elem = card.find('div', class_='details-text') or \
                       card.find('p', class_='job-description')
            
            if desc_elem:
                job['description'] = self.clean_text(desc_elem.get_text())
            else:
                job['description'] = ''
            
            # Posted date
            date_elem = card.find('time') or \
                       card.find('span', class_='posted-date')
            
            if date_elem:
                job['posted_date'] = self.clean_text(date_elem.get_text())
            else:
                job['posted_date'] = 'Recently'
            
            job['platform'] = 'Monster'
            
            return job
            
        except Exception as e:
            self.logger.error(f"Error parsing Monster job card: {str(e)}")
            return None
    
    def parse_job_listing(self, listing) -> Dict:
        """Compatibility method for base class"""
        return self._parse_job_card(listing)