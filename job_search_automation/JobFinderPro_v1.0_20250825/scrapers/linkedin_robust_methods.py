"""
Robust LinkedIn scraping methods for the enhanced scraper
These methods implement multiple strategies for reliable job data extraction
"""

def add_robust_methods_to_scraper(scraper_class):
    """Add robust scraping methods to the LinkedIn scraper class"""
    
    def _search_via_guest_api(self, keywords, location_variants):
        """Search using LinkedIn's guest API - most reliable method"""
        jobs = []
        
        for keyword in keywords[:3]:  # Limit keywords to avoid rate limiting
            for location in location_variants[:5]:  # Limit locations
                try:
                    # LinkedIn guest API endpoint
                    api_url = f"{self.base_url}/jobs-guest/jobs/api/seeMoreJobPostings/search"
                    
                    params = {
                        'keywords': keyword,
                        'location': location,
                        'locationId': '',
                        'f_TPR': 'r604800',  # Last 2 weeks
                        'f_E': '2,3,4',     # Experience levels
                        'sortBy': 'DD',     # Date descending
                        'start': 0,
                        'count': 25
                    }
                    
                    headers = {
                        'Accept': 'application/json, text/plain, */*',
                        'Referer': f'{self.base_url}/jobs/search?keywords={keyword}&location={location}'
                    }
                    
                    response = self._make_robust_request(api_url, params=params, headers=headers)
                    
                    if response and response.status_code == 200:
                        try:
                            data = response.json()
                            if 'jobPostings' in data:
                                for job_data in data['jobPostings'][:20]:
                                    job = self._parse_guest_api_job(job_data)
                                    if job:
                                        jobs.append(job)
                        except json.JSONDecodeError:
                            # Try HTML parsing as fallback
                            soup = self.parse_html(response.text)
                            jobs.extend(self._parse_job_cards_from_html(soup))
                    
                except Exception as e:
                    self.logger.debug(f"Guest API failed for {keyword} in {location}: {str(e)}")
                    continue
        
        self.logger.info(f"Guest API found {len(jobs)} jobs")
        return jobs
    
    def _search_via_public_search(self, keywords, location_variants):
        """Search using public LinkedIn job search pages"""
        jobs = []
        
        for keyword in keywords[:5]:  # More keywords allowed for public search
            for location in location_variants[:3]:  # Fewer locations to balance
                try:
                    search_url = f"{self.base_url}/jobs/search"
                    
                    params = {
                        'keywords': keyword,
                        'location': location,
                        'trk': 'public_jobs_jobs-search-bar_search-submit',
                        'position': 1,
                        'pageNum': 0,
                        'f_TPR': 'r604800'
                    }
                    
                    response = self._make_robust_request(search_url, params=params)
                    
                    if response and response.status_code == 200:
                        soup = self.parse_html(response.text)
                        page_jobs = self._parse_job_cards_from_html(soup)
                        jobs.extend(page_jobs)
                    
                except Exception as e:
                    self.logger.debug(f"Public search failed for {keyword} in {location}: {str(e)}")
                    continue
        
        self.logger.info(f"Public search found {len(jobs)} jobs")
        return jobs
    
    def _search_via_rss_feeds(self, keywords, location_variants):
        """Search using LinkedIn RSS feeds (alternative method)"""
        jobs = []
        
        for keyword in keywords[:2]:  # Very limited for RSS
            try:
                # LinkedIn job RSS feed URL
                rss_url = f"{self.base_url}/jobs/search"
                
                params = {
                    'keywords': keyword,
                    'location': location_variants[0] if location_variants else 'Poland',
                    'f_TPR': 'r604800',
                    'format': 'rss'
                }
                
                response = self._make_robust_request(rss_url, params=params)
                
                if response and response.status_code == 200:
                    # Try to parse RSS or fall back to HTML
                    if 'xml' in response.headers.get('content-type', '').lower():
                        rss_jobs = self._parse_rss_jobs(response.text)
                        jobs.extend(rss_jobs)
                    else:
                        soup = self.parse_html(response.text)
                        jobs.extend(self._parse_job_cards_from_html(soup))
                
            except Exception as e:
                self.logger.debug(f"RSS search failed for {keyword}: {str(e)}")
                continue
        
        self.logger.info(f"RSS feeds found {len(jobs)} jobs")
        return jobs
    
    def _parse_guest_api_job(self, job_data):
        """Parse job from LinkedIn guest API JSON response"""
        try:
            # Extract job details from API response
            job_id = job_data.get('jobPostingId', '')
            title = job_data.get('title', '')
            company_info = job_data.get('companyDetails', {})
            company = company_info.get('companyName', '') or company_info.get('company', {}).get('name', '')
            location = job_data.get('formattedLocation', '')
            
            # Build job URL
            job_url = f"{self.base_url}/jobs/view/{job_id}" if job_id else ""
            
            # Extract posting date
            posted_date = ''
            if 'listedAt' in job_data:
                try:
                    import datetime
                    timestamp = int(job_data['listedAt']) / 1000
                    date_obj = datetime.datetime.fromtimestamp(timestamp)
                    posted_date = date_obj.strftime('%Y-%m-%d')
                except:
                    pass
            
            # Extract description
            description = job_data.get('description', {})
            if isinstance(description, dict):
                description = description.get('text', '')
            elif not isinstance(description, str):
                description = str(description)
            
            return {
                'platform': 'LinkedIn-Primary',
                'job_title': title,
                'company': company,
                'location': location,
                'job_url': job_url,
                'posted_date': posted_date,
                'description': description[:500]  # Limit description length
            }
            
        except Exception as e:
            self.logger.debug(f"Error parsing guest API job: {str(e)}")
            return None
    
    def _parse_job_cards_from_html(self, soup):
        """Parse job cards from HTML soup"""
        jobs = []
        
        # Multiple selectors for different LinkedIn page layouts
        job_selectors = [
            'div[data-entity-urn*="jobPosting"]',
            '.base-card',
            '.job-search-card',
            '.jobs-search-results__list-item',
            'li[data-occludable-job-id]',
            '.job-card-container'
        ]
        
        job_elements = []
        for selector in job_selectors:
            elements = soup.select(selector)
            if elements:
                job_elements = elements
                break
        
        for element in job_elements[:30]:  # Limit results
            try:
                job = self._parse_html_job_element(element)
                if job:
                    jobs.append(job)
            except Exception as e:
                self.logger.debug(f"Error parsing job element: {str(e)}")
                continue
        
        return jobs
    
    def _parse_html_job_element(self, element):
        """Parse individual job element from HTML"""
        try:
            # Extract title
            title_selectors = ['h3 a', '.job-title a', 'h2 a', '[data-test="job-title"]']
            title = ""
            title_elem = None
            
            for selector in title_selectors:
                title_elem = element.select_one(selector)
                if title_elem:
                    title = self.clean_text(title_elem.get_text())
                    break
            
            # Extract company
            company_selectors = ['h4 a', '.company-name', '[data-test="job-company"]', '.job-card-container__company-name']
            company = ""
            
            for selector in company_selectors:
                company_elem = element.select_one(selector)
                if company_elem:
                    company = self.clean_text(company_elem.get_text())
                    break
            
            # Extract location
            location_selectors = ['.job-card-container__metadata-item', '[data-test="job-location"]', '.job-search-card__location']
            location = ""
            
            for selector in location_selectors:
                location_elem = element.select_one(selector)
                if location_elem:
                    location = self.clean_text(location_elem.get_text())
                    break
            
            # Extract job URL
            job_url = ""
            if title_elem and title_elem.get('href'):
                href = title_elem['href']
                if href.startswith('/'):
                    job_url = f"{self.base_url}{href}"
                elif href.startswith('http'):
                    job_url = href
            
            # Extract posting date
            date_selectors = ['time', '.job-search-card__listdate', '[data-test="job-posted-date"]']
            posted_date = ""
            
            for selector in date_selectors:
                date_elem = element.select_one(selector)
                if date_elem:
                    if date_elem.get('datetime'):
                        posted_date = date_elem['datetime']
                    else:
                        posted_date = self.clean_text(date_elem.get_text())
                    break
            
            # Basic validation
            if not (title and company):
                return None
            
            return {
                'platform': 'LinkedIn-Primary',
                'job_title': title,
                'company': company,
                'location': location or 'Poland',
                'job_url': job_url,
                'posted_date': posted_date,
                'description': ''
            }
            
        except Exception as e:
            self.logger.debug(f"Error parsing HTML job element: {str(e)}")
            return None
    
    def _parse_rss_jobs(self, rss_content):
        """Parse jobs from RSS feed content"""
        jobs = []
        
        try:
            from xml.etree import ElementTree as ET
            root = ET.fromstring(rss_content)
            
            # Find job items in RSS
            for item in root.findall('.//item')[:20]:
                try:
                    title = item.find('title')
                    title = title.text if title is not None else ""
                    
                    link = item.find('link')
                    job_url = link.text if link is not None else ""
                    
                    description = item.find('description')
                    desc_text = description.text if description is not None else ""
                    
                    # Try to extract company from description or title
                    company = ""
                    if " at " in title:
                        company = title.split(" at ")[-1]
                    
                    if title and job_url:
                        jobs.append({
                            'platform': 'LinkedIn-Primary',
                            'job_title': title,
                            'company': company,
                            'location': 'Poland',
                            'job_url': job_url,
                            'posted_date': '',
                            'description': desc_text[:300]
                        })
                        
                except Exception as e:
                    self.logger.debug(f"Error parsing RSS item: {str(e)}")
                    continue
                    
        except Exception as e:
            self.logger.debug(f"Error parsing RSS content: {str(e)}")
        
        return jobs
    
    # Add methods to the scraper class
    scraper_class._search_via_guest_api = _search_via_guest_api
    scraper_class._search_via_public_search = _search_via_public_search
    scraper_class._search_via_rss_feeds = _search_via_rss_feeds
    scraper_class._parse_guest_api_job = _parse_guest_api_job
    scraper_class._parse_job_cards_from_html = _parse_job_cards_from_html
    scraper_class._parse_html_job_element = _parse_html_job_element
    scraper_class._parse_rss_jobs = _parse_rss_jobs
    
    return scraper_class