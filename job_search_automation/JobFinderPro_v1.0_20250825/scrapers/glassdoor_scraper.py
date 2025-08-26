from typing import List, Dict
import re
from urllib.parse import urljoin
from .base_scraper import BaseScraper
import cloudscraper

class GlassdoorScraper(BaseScraper):
    def __init__(self):
        super().__init__("Glassdoor")
        self.scraper = cloudscraper.create_scraper()
        # Location IDs for Polish cities
        self.location_ids = {
            "poland": "2616",
            "warsaw": "3089098", 
            "krakow": "3089171",
            "wroclaw": "3089235",
            "poznan": "3089197",
            "gdansk": "3089093",
            "lodz": "3089181",
            "katowice": "3089154"
        }
    
    def search_jobs(self, keywords: List[str], location: str = "Poland", include_remote: bool = True) -> List[Dict]:
        all_jobs = []
        
        for keyword in keywords:
            try:
                jobs = self._search_keyword(keyword, location)
                all_jobs.extend(jobs)
            except Exception as e:
                self.logger.error(f"Error searching Glassdoor for '{keyword}': {str(e)}")
        
        seen_urls = set()
        unique_jobs = []
        for job in all_jobs:
            if job['job_url'] not in seen_urls:
                seen_urls.add(job['job_url'])
                unique_jobs.append(job)
        
        return unique_jobs
    
    def _get_location_id(self, location: str) -> str:
        """Get Glassdoor location ID for Polish locations"""
        location_lower = location.lower().replace(", poland", "").replace("poland", "").strip()
        return self.location_ids.get(location_lower, self.location_ids["poland"])
    
    def _search_keyword(self, keyword: str, location: str) -> List[Dict]:
        location_id = self._get_location_id(location)
        location_name = location.lower().replace(", poland", "").replace(" ", "-")
        
        # Build URL based on location
        if "poland" in location.lower():
            search_url = f"https://www.glassdoor.com/Job/poland-{keyword.replace(' ', '-')}-jobs-SRCH_IL.0,6_IN193_KO7,30.htm"
        else:
            search_url = f"https://www.glassdoor.com/Job/{location_name}-{keyword.replace(' ', '-')}-jobs-SRCH_IL.0,{len(location_name)}_IC{location_id}_KO{len(location_name)+1},50.htm"
        
        params = {
            'fromAge': '14',
            'radius': '25'
        }
        
        try:
            response = self.scraper.get(search_url, params=params, timeout=30)
            if response.status_code != 200:
                return []
            
            soup = self.parse_html(response.text)
            
            job_listings = soup.find_all('li', {'class': 'react-job-listing'}) or \
                          soup.find_all('div', {'class': 'jobContainer'}) or \
                          soup.find_all('article', {'data-test': 'job-card'})
            
            jobs = []
            for listing in job_listings[:50]:
                job = self.parse_job_listing(listing)
                if job:
                    jobs.append(job)
            
            return jobs
        except Exception as e:
            self.logger.error(f"Error in Glassdoor search: {str(e)}")
            return []
    
    def parse_job_listing(self, listing) -> Dict:
        try:
            title_elem = listing.find('a', {'data-test': 'job-link'}) or \
                        listing.find('a', class_='jobLink') or \
                        listing.find('div', {'data-test': 'job-title'})
            
            company_elem = listing.find('div', {'data-test': 'employer-name'}) or \
                          listing.find('div', class_='e1n63ojh0') or \
                          listing.find('span', class_='employer-name')
            
            location_elem = listing.find('div', {'data-test': 'employer-location'}) or \
                           listing.find('span', {'data-test': 'job-location'}) or \
                           listing.find('div', class_='location')
            
            link_elem = listing.find('a', {'data-test': 'job-link'}) or \
                       listing.find('a', class_='jobLink')
            
            posted_elem = listing.find('div', {'data-test': 'job-age'}) or \
                         listing.find('span', class_='minor') or \
                         listing.find('div', class_='d-flex align-items-end')
            
            if not (title_elem and company_elem):
                return None
            
            job_title = self.clean_text(title_elem.get_text())
            company = self.clean_text(company_elem.get_text())
            location = self.clean_text(location_elem.get_text()) if location_elem else "Warsaw, Poland"
            
            job_url = ""
            if link_elem and link_elem.get('href'):
                job_url = link_elem['href']
                if not job_url.startswith('http'):
                    job_url = urljoin('https://www.glassdoor.com', job_url)
            
            posted_date = ""
            if posted_elem:
                posted_text = self.clean_text(posted_elem.get_text())
                posted_date = self._parse_posted_date(posted_text)
            
            description = self._extract_description(listing)
            
            return {
                'platform': 'Glassdoor',
                'job_title': job_title,
                'company': company,
                'location': location,
                'job_url': job_url,
                'posted_date': posted_date,
                'description': description
            }
        except Exception as e:
            self.logger.error(f"Error parsing Glassdoor listing: {str(e)}")
            return None
    
    def _extract_description(self, listing) -> str:
        desc_elem = listing.find('div', class_='jobDescriptionContent') or \
                   listing.find('div', {'data-test': 'job-snippet'})
        
        if desc_elem:
            return self.clean_text(desc_elem.get_text())
        return ""
    
    def _parse_posted_date(self, date_text: str) -> str:
        date_text = date_text.lower()
        
        if 'today' in date_text or 'just posted' in date_text:
            return 'today'
        elif 'yesterday' in date_text:
            return 'yesterday'
        elif 'd' in date_text or 'day' in date_text:
            days_match = re.search(r'(\d+)\s*d', date_text)
            if days_match:
                return f"{days_match.group(1)} days ago"
        elif 'h' in date_text or 'hour' in date_text:
            return 'today'
        
        return date_text