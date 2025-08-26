from typing import List, Dict
import re
from urllib.parse import urljoin, quote
from .base_scraper import BaseScraper
import json

class GoogleJobsScraper(BaseScraper):
    def __init__(self):
        super().__init__("Google Jobs")
        self.base_url = "https://www.google.com/search"
    
    def search_jobs(self, keywords: List[str], location: str = "Poland", include_remote: bool = True) -> List[Dict]:
        all_jobs = []
        
        for keyword in keywords:
            try:
                jobs = self._search_keyword(keyword, location, include_remote)
                all_jobs.extend(jobs)
            except Exception as e:
                self.logger.error(f"Error searching Google Jobs for '{keyword}': {str(e)}")
        
        seen_urls = set()
        unique_jobs = []
        for job in all_jobs:
            job_id = f"{job.get('company', '')}_{job.get('job_title', '')}"
            if job_id not in seen_urls:
                seen_urls.add(job_id)
                unique_jobs.append(job)
        
        return unique_jobs
    
    def _search_keyword(self, keyword: str, location: str, include_remote: bool) -> List[Dict]:
        # Build search query
        if include_remote:
            query = f"{keyword} jobs in {location} OR remote {keyword} jobs"
        else:
            query = f"{keyword} jobs in {location}"
        
        params = {
            'q': query,
            'ibp': 'htl;jobs',
            'htichips': 'date_posted:week',
            'hl': 'en',
            'gl': 'pl'  # Search in Poland
        }
        
        try:
            response = self.make_request(self.base_url, params=params)
            if not response:
                return []
            
            soup = self.parse_html(response.text)
            
            jobs = []
            
            job_cards = soup.find_all('div', {'class': 'PwjeAc'}) or \
                       soup.find_all('li', {'class': 'iFjolb'}) or \
                       soup.find_all('div', {'jsname': 'jXK9ad'})
            
            for card in job_cards[:50]:
                job = self.parse_job_listing(card)
                if job:
                    jobs.append(job)
            
            script_tags = soup.find_all('script', type='application/ld+json')
            for script in script_tags:
                try:
                    data = json.loads(script.string)
                    if data.get('@type') == 'JobPosting':
                        job = self._parse_structured_data(data)
                        if job:
                            jobs.append(job)
                except:
                    continue
            
            return jobs
        except Exception as e:
            self.logger.error(f"Error in Google Jobs search: {str(e)}")
            return []
    
    def parse_job_listing(self, listing) -> Dict:
        try:
            title_elem = listing.find('div', {'class': 'BjJfJf'}) or \
                        listing.find('h2') or \
                        listing.find('div', {'role': 'heading'})
            
            company_elem = listing.find('div', {'class': 'vNEEBe'}) or \
                          listing.find('div', {'class': 'nJlQNd'}) or \
                          listing.find('span', {'class': 'HBvzbc'})
            
            location_elem = listing.find('div', {'class': 'Qk80Jf'}) or \
                           listing.find('span', {'class': 'LL4CDc'}) or \
                           listing.find('div', {'aria-label': lambda x: x and 'location' in x.lower()})
            
            posted_elem = listing.find('span', {'class': 'LL4CDc'}) or \
                         listing.find('span', {'aria-label': lambda x: x and 'posted' in x.lower()})
            
            if not (title_elem and company_elem):
                return None
            
            job_title = self.clean_text(title_elem.get_text())
            company = self.clean_text(company_elem.get_text())
            location = self.clean_text(location_elem.get_text()) if location_elem else "Warsaw, Poland"
            
            via_elem = listing.find('span', {'class': 'Gehpcd'})
            via_site = self.clean_text(via_elem.get_text()) if via_elem else ""
            
            job_url = self._extract_job_url(listing, via_site)
            
            posted_date = ""
            if posted_elem:
                posted_text = self.clean_text(posted_elem.get_text())
                posted_date = self._parse_posted_date(posted_text)
            
            description = self._extract_description(listing)
            
            return {
                'platform': f'Google Jobs (via {via_site})' if via_site else 'Google Jobs',
                'job_title': job_title,
                'company': company,
                'location': location,
                'job_url': job_url,
                'posted_date': posted_date,
                'description': description
            }
        except Exception as e:
            self.logger.error(f"Error parsing Google Jobs listing: {str(e)}")
            return None
    
    def _parse_structured_data(self, data: Dict) -> Dict:
        try:
            return {
                'platform': 'Google Jobs',
                'job_title': data.get('title', ''),
                'company': data.get('hiringOrganization', {}).get('name', ''),
                'location': data.get('jobLocation', {}).get('address', {}).get('addressLocality', 'Warsaw'),
                'job_url': data.get('url', ''),
                'posted_date': data.get('datePosted', ''),
                'description': data.get('description', '')
            }
        except:
            return None
    
    def _extract_job_url(self, listing, via_site: str) -> str:
        link_elem = listing.find('a', {'class': 'pMhGee'}) or \
                   listing.find('a', {'jsname': 'jXK9ad'})
        
        if link_elem and link_elem.get('href'):
            return link_elem['href']
        
        if via_site:
            return f"Search on {via_site}"
        
        return ""
    
    def _extract_description(self, listing) -> str:
        desc_elem = listing.find('span', {'class': 'HBvzbc'}) or \
                   listing.find('div', {'class': 'EPLEUe'})
        
        if desc_elem:
            return self.clean_text(desc_elem.get_text())
        return ""
    
    def _parse_posted_date(self, date_text: str) -> str:
        date_text = date_text.lower()
        
        if 'hour' in date_text:
            return 'today'
        elif 'day' in date_text:
            days_match = re.search(r'(\d+)\s*day', date_text)
            if days_match:
                return f"{days_match.group(1)} days ago"
            return '1 day ago'
        elif 'week' in date_text:
            weeks_match = re.search(r'(\d+)\s*week', date_text)
            if weeks_match:
                days = int(weeks_match.group(1)) * 7
                return f"{days} days ago"
            return '7 days ago'
        
        return date_text