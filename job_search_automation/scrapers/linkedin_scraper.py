from typing import List, Dict
import re
from urllib.parse import urljoin, quote
from .base_scraper import BaseScraper
import cloudscraper

class LinkedInScraper(BaseScraper):
    def __init__(self):
        super().__init__("LinkedIn")
        self.base_url = "https://www.linkedin.com/jobs/search"
        self.scraper = cloudscraper.create_scraper()
    
    def search_jobs(self, keywords: List[str], location: str = "Poland", include_remote: bool = True) -> List[Dict]:
        all_jobs = []
        
        # Search multiple location variants for Poland
        location_variants = self._get_location_variants(location, include_remote)
        
        for keyword in keywords:
            for loc_variant in location_variants:
                try:
                    jobs = self._search_keyword(keyword, loc_variant)
                    all_jobs.extend(jobs)
                except Exception as e:
                    self.logger.error(f"Error searching LinkedIn for '{keyword}' in {loc_variant}: {str(e)}")
        
        seen_urls = set()
        unique_jobs = []
        for job in all_jobs:
            if job['job_url'] not in seen_urls:
                seen_urls.add(job['job_url'])
                unique_jobs.append(job)
        
        return unique_jobs
    
    def _get_location_variants(self, location: str, include_remote: bool) -> List[str]:
        """Generate location variants for Poland-wide search"""
        variants = []
        
        if location.lower() == "poland":
            # Major Polish cities for comprehensive coverage
            variants = [
                "Poland",
                "Warsaw, Poland",
                "Krakow, Poland",
                "Wroclaw, Poland",
                "Poznan, Poland",
                "Gdansk, Poland",
                "Lodz, Poland",
                "Katowice, Poland"
            ]
            if include_remote:
                variants.extend(["Remote Poland", "Poland Remote"])
        else:
            # Use specific location provided
            variants = [location]
            if include_remote and "remote" not in location.lower():
                variants.append(f"Remote {location}")
        
        return variants
    
    def _search_keyword(self, keyword: str, location: str) -> List[Dict]:
        params = {
            'keywords': keyword,
            'location': location,
            'f_TPR': 'r604800',
            'position': 1,
            'pageNum': 0,
            'f_E': '1,2,3',
            'sortBy': 'DD'
        }
        
        try:
            response = self.scraper.get(self.base_url, params=params, timeout=30)
            if response.status_code != 200:
                return []
            
            soup = self.parse_html(response.text)
            job_listings = soup.find_all('div', {'class': 'base-card'}) or \
                          soup.find_all('li', {'class': 'jobs-search-results__list-item'}) or \
                          soup.find_all('div', {'class': 'job-search-card'})
            
            jobs = []
            for listing in job_listings[:50]:
                job = self.parse_job_listing(listing)
                if job:
                    jobs.append(job)
            
            return jobs
        except Exception as e:
            self.logger.error(f"Error in LinkedIn search: {str(e)}")
            return []
    
    def parse_job_listing(self, listing) -> Dict:
        try:
            title_elem = listing.find('h3', class_='base-search-card__title') or \
                        listing.find('a', class_='job-card-list__title') or \
                        listing.find('span', class_='job-card-search__title')
            
            company_elem = listing.find('h4', class_='base-search-card__subtitle') or \
                          listing.find('a', class_='job-card-container__company-name') or \
                          listing.find('span', class_='job-card-container__primary-description')
            
            location_elem = listing.find('span', class_='job-search-card__location') or \
                           listing.find('span', class_='job-card-container__metadata-item')
            
            link_elem = listing.find('a', class_='base-card__full-link') or \
                       listing.find('a', {'data-tracking-control-name': 'public_jobs_jserp-result_search-card'})
            
            posted_elem = listing.find('time') or \
                         listing.find('span', class_='job-search-card__listdate')
            
            if not (title_elem and company_elem):
                return None
            
            job_title = self.clean_text(title_elem.get_text())
            company = self.clean_text(company_elem.get_text())
            location = self.clean_text(location_elem.get_text()) if location_elem else "Warsaw, Poland"
            
            job_url = ""
            if link_elem and link_elem.get('href'):
                job_url = link_elem['href']
                if not job_url.startswith('http'):
                    job_url = urljoin('https://www.linkedin.com', job_url)
            
            posted_date = ""
            if posted_elem:
                if posted_elem.get('datetime'):
                    posted_date = posted_elem['datetime']
                else:
                    posted_date = self.clean_text(posted_elem.get_text())
            
            description = self._extract_description(listing)
            
            return {
                'platform': 'LinkedIn',
                'job_title': job_title,
                'company': company,
                'location': location,
                'job_url': job_url,
                'posted_date': posted_date,
                'description': description
            }
        except Exception as e:
            self.logger.error(f"Error parsing LinkedIn listing: {str(e)}")
            return None
    
    def _extract_description(self, listing) -> str:
        desc_elem = listing.find('div', class_='base-search-card__metadata') or \
                   listing.find('ul', class_='job-card-list__list-items')
        
        if desc_elem:
            return self.clean_text(desc_elem.get_text())
        return ""