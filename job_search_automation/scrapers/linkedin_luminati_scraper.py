from typing import List, Dict
import requests
import json
import time
import random
import re
from urllib.parse import quote, urlencode, parse_qs, urlparse
from .base_scraper import BaseScraper
import logging
from fake_useragent import UserAgent
from .linkedin_robust_methods import add_robust_methods_to_scraper

class LinkedInLuminatiScraper(BaseScraper):
    """
    Enhanced LinkedIn scraper using Luminati-style approach
    Based on: https://github.com/luminati-io/LinkedIn-Scraper
    """
    
    def __init__(self):
        super().__init__("LinkedIn-Primary")
        self.base_url = "https://www.linkedin.com"
        self.jobs_api_url = "https://www.linkedin.com/voyager/api/search/hits"
        self.jobs_search_url = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"
        
        # Initialize session with rotating user agents
        self.ua = UserAgent()
        self.session = requests.Session()
        self.csrf_token = None
        self.jsessionid = None
        self.li_at = None
        
        # Request tracking for rate limiting
        self.request_count = 0
        self.last_request_time = 0
        
        self._setup_session()
    
    def _setup_session(self):
        """Setup session with rotating headers and proper configuration"""
        # Rotate user agent
        user_agent = self.ua.random
        
        # Enhanced headers mimicking real browser behavior
        self.session.headers.update({
            'User-Agent': user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'en-US,en;q=0.9,pl;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
            'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"'
        })
    
    def _smart_delay(self):
        """Implement intelligent delays to avoid rate limiting"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        # Adaptive delay based on request frequency
        if self.request_count > 10:
            delay = random.uniform(3, 7)  # Longer delay after many requests
        elif self.request_count > 5:
            delay = random.uniform(2, 5)  # Medium delay
        else:
            delay = random.uniform(1, 3)  # Short delay
        
        # Ensure minimum delay between requests
        if time_since_last < 1:
            delay = max(delay, 1.5 - time_since_last)
        
        time.sleep(delay)
        self.last_request_time = time.time()
        self.request_count += 1
    
    def _make_robust_request(self, url: str, params: dict = None, headers: dict = None, max_retries: int = 3):
        """Make HTTP request with retry logic and error handling"""
        for attempt in range(max_retries):
            try:
                self._smart_delay()
                
                # Merge custom headers
                request_headers = self.session.headers.copy()
                if headers:
                    request_headers.update(headers)
                
                response = self.session.get(
                    url, 
                    params=params, 
                    headers=request_headers,
                    timeout=30,
                    allow_redirects=True
                )
                
                # Handle different response codes
                if response.status_code == 200:
                    return response
                elif response.status_code == 429:  # Rate limited
                    self.logger.warning(f"Rate limited, waiting longer... (attempt {attempt + 1})")
                    time.sleep(random.uniform(10, 20))
                    continue
                elif response.status_code == 403:  # Forbidden
                    self.logger.warning(f"Access forbidden, trying with different headers... (attempt {attempt + 1})")
                    self._setup_session()  # Reset session
                    continue
                elif response.status_code == 404:
                    self.logger.warning(f"URL not found: {url}")
                    return None
                else:
                    self.logger.warning(f"Unexpected status code {response.status_code} for {url}")
                    
            except requests.RequestException as e:
                self.logger.warning(f"Request failed (attempt {attempt + 1}): {str(e)}")
                if attempt == max_retries - 1:
                    self.logger.error(f"All retry attempts failed for {url}")
                    return None
                time.sleep(random.uniform(2, 5))
        
        return None
    
    def search_jobs(self, keywords: List[str], location: str = "Poland", include_remote: bool = True) -> List[Dict]:
        """Search LinkedIn jobs using robust multi-strategy approach"""
        all_jobs = []
        
        self.logger.info(f"Starting LinkedIn search for {len(keywords)} keywords in {location}")
        
        # Get location variants for comprehensive search  
        location_variants = self._get_location_variants(location, include_remote)
        
        # Strategy 1: Guest API (most reliable)
        self.logger.info("Trying LinkedIn Guest API...")
        guest_jobs = self._search_via_guest_api(keywords, location_variants)
        all_jobs.extend(guest_jobs)
        
        # Strategy 2: Public job search (fallback)
        if len(all_jobs) < 10:  # If guest API didn't work well
            self.logger.info("Trying LinkedIn public job search...")
            public_jobs = self._search_via_public_search(keywords, location_variants)
            all_jobs.extend(public_jobs)
        
        # Strategy 3: RSS feeds (alternative)
        if len(all_jobs) < 5:  # If other methods failed
            self.logger.info("Trying LinkedIn RSS feeds...")
            rss_jobs = self._search_via_rss_feeds(keywords, location_variants)
            all_jobs.extend(rss_jobs)
        
        # Strategy 4: Fallback to basic scraper if enhanced methods yielded few results
        if len(all_jobs) < 3:
            self.logger.info("Enhanced methods yielded few results, falling back to basic scraper...")
            try:
                from .linkedin_scraper import LinkedInScraper
                basic_scraper = LinkedInScraper()
                fallback_jobs = basic_scraper.search_jobs(keywords, location, include_remote)
                all_jobs.extend(fallback_jobs)
                self.logger.info(f"Basic scraper fallback found {len(fallback_jobs)} additional jobs")
            except Exception as e:
                self.logger.warning(f"Fallback to basic scraper failed: {str(e)}")
        
        self.logger.info(f"Total jobs found: {len(all_jobs)}")
        
        # Deduplicate results
        seen_urls = set()
        unique_jobs = []
        for job in all_jobs:
            job_id = job.get('job_url', '') or f"{job.get('company', '')}_{job.get('job_title', '')}"
            if job_id not in seen_urls:
                seen_urls.add(job_id)
                unique_jobs.append(job)
        
        self.logger.info(f"Unique LinkedIn jobs after deduplication: {len(unique_jobs)}")
        return unique_jobs
    
    def _initialize_session(self):
        """Initialize LinkedIn session with proper authentication tokens"""
        try:
            # First, get the main LinkedIn page to establish session
            response = self.session.get(f"{self.base_url}/jobs/")
            
            if response.status_code == 200:
                # Extract CSRF token from cookies or page content
                for cookie in response.cookies:
                    if 'JSESSIONID' in cookie.name:
                        self.jsessionid = cookie.value
                    elif 'csrf' in cookie.name.lower():
                        self.csrf_token = cookie.value
                
                # Update session headers with tokens
                if self.csrf_token:
                    self.session.headers['csrf-token'] = self.csrf_token
                
                self.logger.info("LinkedIn session initialized successfully")
            else:
                raise Exception(f"Failed to initialize session: {response.status_code}")
                
        except Exception as e:
            self.logger.warning(f"Session initialization failed: {str(e)}")
            raise
    
    def _search_keyword_enhanced(self, keyword: str, location: str) -> List[Dict]:
        """Enhanced keyword search using LinkedIn's internal API patterns"""
        
        # Build search parameters using LinkedIn's query structure
        search_params = {
            'keywords': keyword,
            'location': location,
            'locationFallback': location,
            'f_TPR': 'r604800',  # Last 2 weeks
            'f_E': '1,2,3,4',   # Experience levels
            'f_JT': 'F,P,T,C',  # Job types: Full-time, Part-time, Temporary, Contract
            'sortBy': 'DD',     # Date descending
            'start': 0,
            'count': 25
        }
        
        # Try multiple search approaches
        jobs = []
        
        # Approach 1: Direct jobs search
        jobs.extend(self._try_jobs_search(search_params))
        
        # Approach 2: Voyager API (if available)
        if self.csrf_token:
            jobs.extend(self._try_voyager_api(search_params))
        
        # Approach 3: Public jobs feed
        jobs.extend(self._try_public_jobs_feed(keyword, location))
        
        return jobs
    
    def _try_jobs_search(self, params: Dict) -> List[Dict]:
        """Try standard LinkedIn jobs search"""
        jobs = []
        
        try:
            search_url = f"{self.base_url}/jobs/search?"
            
            response = self.session.get(search_url, params=params, timeout=30)
            
            if response.status_code == 200:
                soup = self.parse_html(response.text)
                job_listings = soup.find_all('div', {'class': 'base-card'}) or \
                              soup.find_all('li', {'class': 'jobs-search-results__list-item'})
                
                for listing in job_listings[:25]:  # Limit results
                    job = self.parse_job_listing(listing)
                    if job:
                        jobs.append(job)
            
        except Exception as e:
            self.logger.debug(f"Standard jobs search failed: {str(e)}")
        
        return jobs
    
    def _try_voyager_api(self, params: Dict) -> List[Dict]:
        """Try LinkedIn Voyager API for more detailed results"""
        jobs = []
        
        try:
            # Convert search params to Voyager API format
            voyager_params = {
                'count': 25,
                'filters': f"(keywords:{params['keywords']},locationFallback:{params['location']},timePostedRange:List(r604800))",
                'origin': 'JOBS_HOME_SEARCH_SUGGESTIONS',
                'q': 'all',
                'start': 0
            }
            
            voyager_url = f"{self.jobs_api_url}?" + urlencode(voyager_params)
            
            response = self.session.get(voyager_url, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                # Parse Voyager API response
                if 'elements' in data:
                    for element in data['elements']:
                        job = self._parse_voyager_job(element)
                        if job:
                            jobs.append(job)
            
        except Exception as e:
            self.logger.debug(f"Voyager API search failed: {str(e)}")
        
        return jobs
    
    def _try_public_jobs_feed(self, keyword: str, location: str) -> List[Dict]:
        """Try LinkedIn's public jobs feed"""
        jobs = []
        
        try:
            # Use LinkedIn's public job posting URLs
            public_search_url = f"{self.base_url}/jobs/search"
            
            params = {
                'keywords': keyword,
                'location': location,
                'trk': 'public_jobs_jobs-search-bar_search-submit',
                'position': 1,
                'pageNum': 0
            }
            
            # Use different user agent for public search
            headers = self.session.headers.copy()
            headers['User-Agent'] = 'Mozilla/5.0 (compatible; LinkedInBot/1.0)'
            
            response = self.session.get(public_search_url, params=params, headers=headers, timeout=30)
            
            if response.status_code == 200:
                soup = self.parse_html(response.text)
                
                # Look for job cards in public view
                job_cards = soup.find_all('div', {'data-entity-urn': True}) or \
                           soup.find_all('div', {'class': 'job-search-card'})
                
                for card in job_cards[:25]:
                    job = self._parse_public_job_card(card)
                    if job:
                        jobs.append(job)
        
        except Exception as e:
            self.logger.debug(f"Public jobs feed failed: {str(e)}")
        
        return jobs
    
    def _parse_voyager_job(self, element: Dict) -> Dict:
        """Parse job from LinkedIn Voyager API response"""
        try:
            hit_info = element.get('hitInfo', {})
            job_posting = hit_info.get('jobPosting', {})
            
            if not job_posting:
                return None
            
            # Extract job details from Voyager format
            title = job_posting.get('title', '')
            company_info = job_posting.get('companyDetails', {})
            company = company_info.get('company', {}).get('name', '')
            location_info = job_posting.get('formattedLocation', '')
            job_id = job_posting.get('jobPostingId', '')
            
            job_url = f"{self.base_url}/jobs/view/{job_id}" if job_id else ""
            
            # Extract posting date
            posted_date = job_posting.get('listedAt', '')
            if posted_date:
                import datetime
                try:
                    timestamp = int(posted_date) / 1000
                    date_obj = datetime.datetime.fromtimestamp(timestamp)
                    posted_date = date_obj.strftime('%Y-%m-%d')
                except:
                    posted_date = ''
            
            return {
                'platform': 'LinkedIn-Luminati',
                'job_title': title,
                'company': company,
                'location': location_info,
                'job_url': job_url,
                'posted_date': posted_date,
                'description': job_posting.get('description', {}).get('text', '')
            }
            
        except Exception as e:
            self.logger.debug(f"Error parsing Voyager job: {str(e)}")
            return None
    
    def _parse_public_job_card(self, card) -> Dict:
        """Parse job from public LinkedIn job card"""
        try:
            title_elem = card.find('h3') or card.find('a', {'data-tracking-control-name': True})
            company_elem = card.find('h4') or card.find('span', class_='job-search-card__subtitle-link')
            location_elem = card.find('span', class_='job-search-card__location')
            date_elem = card.find('time') or card.find('span', class_='job-search-card__listdate')
            link_elem = card.find('a', href=True)
            
            if not (title_elem and company_elem):
                return None
            
            job_title = self.clean_text(title_elem.get_text())
            company = self.clean_text(company_elem.get_text())
            location = self.clean_text(location_elem.get_text()) if location_elem else ""
            posted_date = self.clean_text(date_elem.get_text()) if date_elem else ""
            
            job_url = ""
            if link_elem:
                href = link_elem.get('href', '')
                if href.startswith('/'):
                    job_url = f"{self.base_url}{href}"
                elif href.startswith('http'):
                    job_url = href
            
            return {
                'platform': 'LinkedIn-Luminati',
                'job_title': job_title,
                'company': company,
                'location': location,
                'job_url': job_url,
                'posted_date': posted_date,
                'description': ''
            }
            
        except Exception as e:
            self.logger.debug(f"Error parsing public job card: {str(e)}")
            return None
    
    def _fallback_search(self, keywords: List[str], location: str, include_remote: bool) -> List[Dict]:
        """Fallback to basic scraping if enhanced methods fail"""
        self.logger.info("Using fallback LinkedIn scraping method")
        
        from .linkedin_scraper import LinkedInScraper
        fallback_scraper = LinkedInScraper()
        return fallback_scraper.search_jobs(keywords, location, include_remote)
    
    def _get_location_variants(self, location: str, include_remote: bool) -> List[str]:
        """Generate location variants for comprehensive search"""
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
                variants.extend(["Remote Poland", "Poland Remote", "Remote"])
        else:
            # Use specific location provided
            variants = [location]
            if include_remote and "remote" not in location.lower():
                variants.append(f"Remote {location}")
        
        return variants
    
    def parse_job_listing(self, listing) -> Dict:
        """Parse job listing from HTML element"""
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
            location = self.clean_text(location_elem.get_text()) if location_elem else "Poland"
            
            job_url = ""
            if link_elem and link_elem.get('href'):
                job_url = link_elem['href']
                if not job_url.startswith('http'):
                    job_url = f"{self.base_url}{job_url}"
            
            posted_date = ""
            if posted_elem:
                if posted_elem.get('datetime'):
                    posted_date = posted_elem['datetime']
                else:
                    posted_date = self.clean_text(posted_elem.get_text())
            
            description = self._extract_description(listing)
            
            return {
                'platform': 'LinkedIn-Luminati',
                'job_title': job_title,
                'company': company,
                'location': location,
                'job_url': job_url,
                'posted_date': posted_date,
                'description': description
            }
        except Exception as e:
            self.logger.error(f"Error parsing LinkedIn-Luminati listing: {str(e)}")
            return None
    
    def _extract_description(self, listing) -> str:
        """Extract job description from listing"""
        desc_elem = listing.find('div', class_='base-search-card__metadata') or \
                   listing.find('ul', class_='job-card-list__list-items')
        
        if desc_elem:
            return self.clean_text(desc_elem.get_text())
        return ""


# Apply robust methods to the scraper class
add_robust_methods_to_scraper(LinkedInLuminatiScraper)