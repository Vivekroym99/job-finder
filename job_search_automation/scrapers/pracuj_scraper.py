from typing import List, Dict
import re
from urllib.parse import urljoin, quote
from .base_scraper import BaseScraper

class PracujScraper(BaseScraper):
    def __init__(self):
        super().__init__("Pracuj.pl")
        self.base_url = "https://www.pracuj.pl/praca"
    
    def search_jobs(self, keywords: List[str], location: str = "Poland", include_remote: bool = True) -> List[Dict]:
        all_jobs = []
        
        # Convert location for Pracuj.pl
        location_formatted = self._format_location(location)
        
        for keyword in keywords:
            try:
                jobs = self._search_keyword(keyword, location_formatted, include_remote)
                all_jobs.extend(jobs)
            except Exception as e:
                self.logger.error(f"Error searching Pracuj.pl for '{keyword}': {str(e)}")
        
        seen_urls = set()
        unique_jobs = []
        for job in all_jobs:
            if job['job_url'] not in seen_urls:
                seen_urls.add(job['job_url'])
                unique_jobs.append(job)
        
        return unique_jobs
    
    def _format_location(self, location: str) -> str:
        """Format location for Pracuj.pl URLs"""
        location_map = {
            "poland": "",  # Empty means all of Poland
            "warsaw": "warszawa",
            "krakow": "krakow", 
            "wroclaw": "wroclaw",
            "poznan": "poznan",
            "gdansk": "gdansk",
            "lodz": "lodz",
            "katowice": "katowice"
        }
        
        location_lower = location.lower().replace(", poland", "").strip()
        return location_map.get(location_lower, "")
    
    def _search_keyword(self, keyword: str, location: str, include_remote: bool) -> List[Dict]:
        keyword_formatted = keyword.replace(' ', '%20')
        
        # Build URL - if location is empty, search all Poland
        if location:
            search_url = f"{self.base_url}/{keyword_formatted};kw/{location};wp"
        else:
            search_url = f"{self.base_url}/{keyword_formatted};kw"
        
        params = {
            'et': '1,17',  # Employment types
            'di': '14',    # Days (last 14 days)
            'sal': '0,100000'  # Salary range
        }
        
        # Add remote work parameter if requested
        if include_remote:
            params['rw'] = '1'  # Remote work option
        
        try:
            response = self.make_request(search_url, params=params)
            if not response:
                return []
            
            soup = self.parse_html(response.text)
            
            job_listings = soup.find_all('div', {'data-test': 'default-offer'}) or \
                          soup.find_all('div', {'data-test': 'premium-offer'}) or \
                          soup.find_all('li', {'data-test': 'offer-item'})
            
            jobs = []
            for listing in job_listings[:50]:
                job = self.parse_job_listing(listing)
                if job:
                    jobs.append(job)
            
            return jobs
        except Exception as e:
            self.logger.error(f"Error in Pracuj.pl search: {str(e)}")
            return []
    
    def parse_job_listing(self, listing) -> Dict:
        try:
            title_elem = listing.find('h2', {'data-test': 'offer-title'}) or \
                        listing.find('a', {'data-test': 'link-offer'}) or \
                        listing.find('h3', class_='offer-title')
            
            company_elem = listing.find('h3', {'data-test': 'text-company-name'}) or \
                          listing.find('a', {'data-test': 'link-company-name'}) or \
                          listing.find('span', class_='employer')
            
            location_elem = listing.find('h4', {'data-test': 'text-region'}) or \
                           listing.find('span', {'data-test': 'offer-location'}) or \
                           listing.find('span', class_='location')
            
            link_elem = listing.find('a', {'data-test': 'link-offer'}) or \
                       listing.find('a', class_='offer-title__link')
            
            posted_elem = listing.find('span', {'data-test': 'text-published'}) or \
                         listing.find('span', class_='offer-published')
            
            if not (title_elem and company_elem):
                return None
            
            job_title = self.clean_text(title_elem.get_text())
            company = self.clean_text(company_elem.get_text())
            location = self.clean_text(location_elem.get_text()) if location_elem else "Warszawa"
            
            job_url = ""
            if link_elem and link_elem.get('href'):
                job_url = link_elem['href']
                if not job_url.startswith('http'):
                    job_url = urljoin('https://www.pracuj.pl', job_url)
            
            posted_date = ""
            if posted_elem:
                posted_text = self.clean_text(posted_elem.get_text())
                posted_date = self._parse_polish_date(posted_text)
            
            description = self._extract_description(listing)
            salary = self._extract_salary(listing)
            
            return {
                'platform': 'Pracuj.pl',
                'job_title': job_title,
                'company': company,
                'location': location,
                'job_url': job_url,
                'posted_date': posted_date,
                'description': description,
                'salary': salary
            }
        except Exception as e:
            self.logger.error(f"Error parsing Pracuj.pl listing: {str(e)}")
            return None
    
    def _extract_description(self, listing) -> str:
        desc_elem = listing.find('div', {'data-test': 'text-benefit'}) or \
                   listing.find('ul', class_='offer-benefits')
        
        if desc_elem:
            return self.clean_text(desc_elem.get_text())
        return ""
    
    def _extract_salary(self, listing) -> str:
        salary_elem = listing.find('span', {'data-test': 'offer-salary'}) or \
                     listing.find('span', class_='salary')
        
        if salary_elem:
            return self.clean_text(salary_elem.get_text())
        return ""
    
    def _parse_polish_date(self, date_text: str) -> str:
        date_text = date_text.lower()
        
        if 'dzisiaj' in date_text or 'dziś' in date_text:
            return 'today'
        elif 'wczoraj' in date_text:
            return 'yesterday'
        elif 'dni' in date_text or 'dzień' in date_text:
            days_match = re.search(r'(\d+)\s*dni', date_text)
            if days_match:
                return f"{days_match.group(1)} days ago"
            return '1 day ago'
        elif 'tydzień' in date_text or 'tygodni' in date_text:
            weeks_match = re.search(r'(\d+)\s*tygodni', date_text)
            if weeks_match:
                days = int(weeks_match.group(1)) * 7
                return f"{days} days ago"
            return '7 days ago'
        elif 'godzin' in date_text:
            return 'today'
        
        return date_text