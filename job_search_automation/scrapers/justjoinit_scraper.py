"""
JustJoinIT Scraper
Popular Polish IT job board focused on tech positions
"""

from typing import List, Dict
import re
import json
from urllib.parse import urljoin
from .base_scraper import BaseScraper
import cloudscraper
from bs4 import BeautifulSoup
import logging

class JustJoinITScraper(BaseScraper):
    def __init__(self):
        super().__init__("JustJoinIT")
        self.base_url = "https://justjoin.it"
        self.api_url = "https://justjoin.it/api/offers"
        self.scraper = cloudscraper.create_scraper()
        self.logger = logging.getLogger('JustJoinITScraper')
    
    def search_jobs(self, keywords: List[str], location: str = "Poland", include_remote: bool = True) -> List[Dict]:
        """Search for jobs on JustJoinIT"""
        all_jobs = []
        
        # Map locations to JustJoinIT format
        location_map = {
            "Poland": "all",
            "Warsaw": "warszawa",
            "Krakow": "krakow",
            "Wroclaw": "wroclaw",
            "Poznan": "poznan",
            "Gdansk": "trojmiasto",  # Tri-city area
            "Katowice": "katowice",
            "Lodz": "lodz",
            "Remote Poland": "remote"
        }
        
        search_location = location_map.get(location, "all")
        
        for keyword in keywords:
            try:
                jobs = self._search_keyword(keyword, search_location, include_remote)
                all_jobs.extend(jobs)
            except Exception as e:
                self.logger.error(f"Error searching JustJoinIT for '{keyword}': {str(e)}")
        
        # Remove duplicates
        seen_urls = set()
        unique_jobs = []
        for job in all_jobs:
            if job['job_url'] not in seen_urls:
                seen_urls.add(job['job_url'])
                unique_jobs.append(job)
        
        return unique_jobs
    
    def _search_keyword(self, keyword: str, location: str, include_remote: bool) -> List[Dict]:
        """Search for specific keyword on JustJoinIT"""
        jobs = []
        
        try:
            # JustJoinIT has a good API
            response = self.scraper.get(self.api_url, timeout=30)
            
            if response.status_code == 200:
                try:
                    all_offers = response.json()
                    
                    # Filter offers based on keyword and location
                    for offer in all_offers:
                        # Check if keyword matches title or skills
                        title_match = keyword.lower() in offer.get('title', '').lower()
                        skills_match = any(keyword.lower() in skill.get('name', '').lower() 
                                          for skill in offer.get('skills', []))
                        
                        if title_match or skills_match:
                            # Check location
                            if location == 'all' or \
                               location in offer.get('city', '').lower() or \
                               (include_remote and offer.get('remote', False)):
                                
                                job = self._parse_api_job(offer)
                                if job:
                                    jobs.append(job)
                                    
                                if len(jobs) >= 50:  # Limit results
                                    break
                                    
                except json.JSONDecodeError:
                    self.logger.error("Failed to parse JustJoinIT API response")
                    
        except Exception as e:
            self.logger.error(f"Error fetching JustJoinIT results: {str(e)}")
        
        return jobs
    
    def _parse_api_job(self, offer: dict) -> Dict:
        """Parse job from API response"""
        try:
            # Extract employment types and salary
            salary_info = self._extract_salary(offer)
            
            job = {
                'job_title': offer.get('title', ''),
                'company': offer.get('company_name', 'Unknown'),
                'location': offer.get('city', 'Poland'),
                'description': offer.get('body', ''),
                'posted_date': offer.get('published_at', 'Recently'),
                'job_url': f"{self.base_url}/offers/{offer.get('id', '')}",
                'platform': 'JustJoinIT',
                'original_language': 'en' if self._is_english(offer.get('title', '')) else 'pl',
                'remote': offer.get('remote', False),
                'salary': salary_info,
                'experience_level': offer.get('experience_level', ''),
                'employment_type': offer.get('employment_types', [{}])[0].get('type', '') if offer.get('employment_types') else ''
            }
            
            # Extract skills
            skills = []
            for skill in offer.get('skills', []):
                skill_name = skill.get('name', '')
                skill_level = skill.get('level', 0)
                if skill_name:
                    skills.append(f"{skill_name} ({skill_level}/5)" if skill_level else skill_name)
            
            job['required_skills'] = skills
            
            # Extract tech stack
            tech_stack = offer.get('marker_icon', '')  # Main technology
            if tech_stack:
                job['main_technology'] = tech_stack
            
            return job if job['job_title'] else None
            
        except Exception as e:
            self.logger.error(f"Error parsing JustJoinIT job: {str(e)}")
            return None
    
    def _extract_salary(self, offer: dict) -> str:
        """Extract salary information from offer"""
        try:
            employment_types = offer.get('employment_types', [])
            if employment_types:
                emp_type = employment_types[0]  # Take first employment type
                salary = emp_type.get('salary')
                if salary:
                    from_sal = salary.get('from', 0)
                    to_sal = salary.get('to', 0)
                    currency = salary.get('currency', 'PLN')
                    
                    if from_sal or to_sal:
                        return f"{from_sal}-{to_sal} {currency}"
        except:
            pass
        return ''
    
    def _is_english(self, text: str) -> bool:
        """Simple check if text is in English"""
        # Common Polish characters
        polish_chars = set('ąćęłńóśźżĄĆĘŁŃÓŚŹŻ')
        return not any(char in polish_chars for char in text)
    
    def parse_job_listing(self, listing) -> Dict:
        """Compatibility method for base class"""
        return self._parse_api_job(listing)