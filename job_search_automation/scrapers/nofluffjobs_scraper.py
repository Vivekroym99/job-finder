"""
NoFluffJobs Scraper
Popular Polish IT job board with transparent salary information
"""

from typing import List, Dict
import re
import json
from urllib.parse import urljoin
from .base_scraper import BaseScraper
import cloudscraper
from bs4 import BeautifulSoup
import logging

class NoFluffJobsScraper(BaseScraper):
    def __init__(self):
        super().__init__("NoFluffJobs")
        self.base_url = "https://nofluffjobs.com"
        self.api_url = "https://nofluffjobs.com/api/search/posting"
        self.scraper = cloudscraper.create_scraper()
        self.logger = logging.getLogger('NoFluffJobsScraper')
    
    def search_jobs(self, keywords: List[str], location: str = "Poland", include_remote: bool = True) -> List[Dict]:
        """Search for jobs on NoFluffJobs"""
        all_jobs = []
        
        # Map locations to NoFluffJobs format
        location_map = {
            "Poland": "pl",
            "Warsaw": "warszawa",
            "Krakow": "krakow",
            "Wroclaw": "wroclaw",
            "Poznan": "poznan",
            "Gdansk": "gdansk",
            "Katowice": "katowice",
            "Lodz": "lodz",
            "Remote Poland": "remote"
        }
        
        search_location = location_map.get(location, "pl")
        
        for keyword in keywords:
            try:
                jobs = self._search_keyword(keyword, search_location, include_remote)
                all_jobs.extend(jobs)
            except Exception as e:
                self.logger.error(f"Error searching NoFluffJobs for '{keyword}': {str(e)}")
        
        # Remove duplicates
        seen_urls = set()
        unique_jobs = []
        for job in all_jobs:
            if job['job_url'] not in seen_urls:
                seen_urls.add(job['job_url'])
                unique_jobs.append(job)
        
        return unique_jobs
    
    def _search_keyword(self, keyword: str, location: str, include_remote: bool) -> List[Dict]:
        """Search for specific keyword on NoFluffJobs"""
        jobs = []
        
        # Build search parameters
        params = {
            'criteria': keyword,
            'page': 1,
            'sortBy': 'newest'
        }
        
        if location and location != 'pl':
            params['city'] = location
        
        if include_remote:
            params['remoteWork'] = 'true'
        
        try:
            # Try API endpoint first
            response = self.scraper.get(self.api_url, params=params, timeout=30)
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    if 'postings' in data:
                        for posting in data['postings'][:50]:
                            job = self._parse_api_job(posting)
                            if job:
                                jobs.append(job)
                except json.JSONDecodeError:
                    # Fall back to HTML parsing
                    jobs = self._search_html(keyword, location, include_remote)
            else:
                # Fall back to HTML parsing
                jobs = self._search_html(keyword, location, include_remote)
                
        except Exception as e:
            self.logger.error(f"Error fetching NoFluffJobs results: {str(e)}")
            # Try HTML as fallback
            jobs = self._search_html(keyword, location, include_remote)
        
        return jobs
    
    def _search_html(self, keyword: str, location: str, include_remote: bool) -> List[Dict]:
        """Fallback HTML search method"""
        jobs = []
        
        search_url = f"{self.base_url}/pl/jobs/{keyword}"
        if location and location != 'pl':
            search_url += f"/{location}"
        
        try:
            response = self.scraper.get(search_url, timeout=30)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Find job postings
                job_cards = soup.find_all('a', class_='posting-list-item') or \
                           soup.find_all('div', {'data-cy': 'job-offer'})
                
                for card in job_cards[:50]:
                    job = self._parse_html_job(card)
                    if job:
                        jobs.append(job)
                        
        except Exception as e:
            self.logger.error(f"Error in HTML fallback: {str(e)}")
        
        return jobs
    
    def _parse_api_job(self, posting: dict) -> Dict:
        """Parse job from API response"""
        try:
            job = {
                'job_title': posting.get('title', ''),
                'company': posting.get('name', 'Unknown'),
                'location': posting.get('location', {}).get('places', [{}])[0].get('city', 'Poland'),
                'description': posting.get('basics', {}).get('description', ''),
                'posted_date': posting.get('posted', 'Recently'),
                'job_url': f"{self.base_url}/pl/job/{posting.get('url', '')}",
                'platform': 'NoFluffJobs',
                'original_language': 'pl',  # Most NoFluffJobs postings are in Polish
                'remote': posting.get('remoteWork', False),
                'salary': self._extract_salary(posting)
            }
            
            # Add skills/requirements
            if 'requirements' in posting:
                skills = []
                for req in posting.get('requirements', []):
                    if isinstance(req, dict):
                        skills.append(req.get('value', ''))
                job['required_skills'] = skills
            
            return job if job['job_title'] else None
            
        except Exception as e:
            self.logger.error(f"Error parsing NoFluffJobs API job: {str(e)}")
            return None
    
    def _parse_html_job(self, card) -> Dict:
        """Parse job from HTML card"""
        try:
            job = {}
            
            # Job title
            title_elem = card.find('h3') or card.find('h4') or \
                        card.find('span', class_='title')
            
            if title_elem:
                job['job_title'] = self.clean_text(title_elem.get_text())
            else:
                return None
            
            # Company
            company_elem = card.find('span', class_='company') or \
                          card.find('div', class_='company-name')
            
            if company_elem:
                job['company'] = self.clean_text(company_elem.get_text())
            else:
                job['company'] = 'Unknown'
            
            # Location
            location_elem = card.find('span', class_='location') or \
                           card.find('div', class_='cities')
            
            if location_elem:
                job['location'] = self.clean_text(location_elem.get_text())
            else:
                job['location'] = 'Poland'
            
            # Job URL
            if card.name == 'a' and 'href' in card.attrs:
                job['job_url'] = urljoin(self.base_url, card['href'])
            else:
                link_elem = card.find('a', href=True)
                if link_elem:
                    job['job_url'] = urljoin(self.base_url, link_elem['href'])
                else:
                    job['job_url'] = self.base_url
            
            # Salary
            salary_elem = card.find('span', class_='salary') or \
                         card.find('div', class_='salary-range')
            
            if salary_elem:
                job['salary'] = self.clean_text(salary_elem.get_text())
            
            # Technologies/Skills
            tech_elements = card.find_all('span', class_='technology') or \
                           card.find_all('div', class_='skill-tag')
            
            if tech_elements:
                job['required_skills'] = [self.clean_text(tech.get_text()) for tech in tech_elements]
            
            job['platform'] = 'NoFluffJobs'
            job['original_language'] = 'pl'
            job['posted_date'] = 'Recently'
            job['description'] = ''  # Will need to fetch from detail page
            
            return job
            
        except Exception as e:
            self.logger.error(f"Error parsing NoFluffJobs HTML job: {str(e)}")
            return None
    
    def _extract_salary(self, posting: dict) -> str:
        """Extract salary information from posting"""
        try:
            salary_info = posting.get('salary')
            if salary_info:
                if isinstance(salary_info, dict):
                    min_sal = salary_info.get('from', '')
                    max_sal = salary_info.get('to', '')
                    currency = salary_info.get('currency', 'PLN')
                    return f"{min_sal}-{max_sal} {currency}"
                return str(salary_info)
        except:
            pass
        return ''
    
    def parse_job_listing(self, listing) -> Dict:
        """Compatibility method for base class"""
        if isinstance(listing, dict):
            return self._parse_api_job(listing)
        return self._parse_html_job(listing)