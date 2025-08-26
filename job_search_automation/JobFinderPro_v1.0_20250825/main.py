#!/usr/bin/env python3

import logging
import sys
import os
import argparse

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.settings import Config
from utils.resume_parser import ResumeParser
from matchers.job_matcher import JobMatcher
from scrapers.linkedin_scraper import LinkedInScraper
from scrapers.linkedin_luminati_scraper import LinkedInLuminatiScraper
from scrapers.glassdoor_scraper import GlassdoorScraper
from scrapers.pracuj_scraper import PracujScraper
from scrapers.google_jobs_scraper import GoogleJobsScraper
from outputs.output_manager import OutputManager

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('job_search.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('JobSearchAutomation')

class JobSearchAutomation:
    def __init__(self, config: Config):
        self.config = config
        self.output_manager = OutputManager(config)
        self.resume_parser = ResumeParser(config.RESUME_FILE)
        self.resume_profile = self.resume_parser.extract_profile()
        self.job_matcher = JobMatcher(self.resume_profile)
        
        # Use enhanced LinkedIn scraper as primary, with fallback option
        if getattr(config, 'USE_BASIC_LINKEDIN', False):
            linkedin_scraper = LinkedInScraper()
            logger.info("Using basic LinkedIn scraper")
        else:
            linkedin_scraper = LinkedInLuminatiScraper()
            logger.info("Using enhanced LinkedIn scraper (Luminati-based)")
        
        self.scrapers = {
            'LinkedIn': linkedin_scraper,
            'Glassdoor': GlassdoorScraper(),
            'Pracuj.pl': PracujScraper(),
            'Google Jobs': GoogleJobsScraper()
        }
        
        logger.info("Job Search Automation initialized")
        logger.info(f"Resume: {self.resume_profile['name']}")
        logger.info(f"Experience: {self.resume_profile['experience_years']} years")
        logger.info(f"Skills found: {len(self.resume_profile['skills'])}")
    
    def search_platform(self, platform_name: str, scraper) -> tuple:
        logger.info(f"Searching {platform_name} for location: {self.config.SEARCH_LOCATION}")
        self.output_manager.write_audit_log(f"Starting search on {platform_name} - Location: {self.config.SEARCH_LOCATION}")
        
        fetched_jobs = []
        errors = []
        
        try:
            raw_jobs = scraper.search_jobs(
                keywords=self.config.JOB_SEARCH_KEYWORDS,
                location=self.config.SEARCH_LOCATION,
                include_remote=self.config.INCLUDE_REMOTE
            )
            fetched_jobs = raw_jobs
            logger.info(f"{platform_name}: Fetched {len(fetched_jobs)} jobs")
        except Exception as e:
            error_msg = f"Error searching {platform_name}: {str(e)}"
            logger.error(error_msg)
            errors.append(error_msg)
        
        matched_jobs = []
        
        for job in fetched_jobs:
            try:
                if not self.job_matcher.is_job_recent(job.get('posted_date', ''), self.config.MAX_JOB_AGE_DAYS):
                    continue
                
                job['required_experience'] = self.job_matcher.extract_experience_requirement(
                    job.get('description', '')
                )
                
                match_score, matching_skills = self.job_matcher.calculate_match_score(job)
                
                if match_score >= self.config.MIN_MATCH_PCT:
                    job['match_score'] = match_score
                    job['matching_skills'] = matching_skills
                    matched_jobs.append(job)
            except Exception as e:
                logger.warning(f"Error processing job from {platform_name}: {str(e)}")
        
        logger.info(f"{platform_name}: Kept {len(matched_jobs)} jobs (>= {self.config.MIN_MATCH_PCT}% match)")
        
        self.output_manager.log_platform_results(
            platform_name, 
            len(fetched_jobs), 
            len(matched_jobs),
            errors
        )
        
        return matched_jobs, len(fetched_jobs), len(matched_jobs)
    
    def run(self):
        logger.info("="*60)
        logger.info("STARTING JOB SEARCH AUTOMATION")
        logger.info(f"Timezone: {self.config.TIMEZONE}")
        logger.info(f"Max job age: {self.config.MAX_JOB_AGE_DAYS} days")
        logger.info(f"Min match percentage: {self.config.MIN_MATCH_PCT}%")
        logger.info("="*60)
        
        self.output_manager.write_audit_log("Job search started")
        
        all_matched_jobs = []
        platform_stats = {}
        
        for platform_name, scraper in self.scrapers.items():
            if self.config.PLATFORMS.get(platform_name.lower().replace(' ', '_').replace('.', ''), {}).get('enabled', True):
                matched_jobs, fetched, kept = self.search_platform(platform_name, scraper)
                all_matched_jobs.extend(matched_jobs)
                platform_stats[platform_name] = {
                    'fetched': fetched,
                    'kept': kept
                }
            else:
                logger.info(f"Skipping {platform_name} (disabled)")
        
        seen_jobs = set()
        unique_jobs = []
        for job in all_matched_jobs:
            job_key = f"{job.get('company', '')}_{job.get('job_title', '')}"
            if job_key not in seen_jobs:
                seen_jobs.add(job_key)
                unique_jobs.append(job)
        
        unique_jobs.sort(key=lambda x: x.get('match_score', 0), reverse=True)
        
        logger.info(f"\nTotal unique matched jobs: {len(unique_jobs)}")
        
        self.output_manager.save_to_csv(unique_jobs)
        self.output_manager.save_to_jsonl(unique_jobs)
        
        self.output_manager.print_summary(unique_jobs, platform_stats)
        
        self.output_manager.write_audit_log(
            f"Job search completed. Total matches: {len(unique_jobs)}"
        )
        
        logger.info("Job search automation completed successfully!")
        
        return unique_jobs

def main():
    parser = argparse.ArgumentParser(description='Job Search Automation')
    parser.add_argument('--resume', type=str, help='Path to resume file')
    parser.add_argument('--min-match', type=int, default=70, help='Minimum match percentage')
    parser.add_argument('--max-age', type=int, default=14, help='Maximum job age in days')
    parser.add_argument('--output-dir', type=str, default='/mnt/data', help='Output directory')
    parser.add_argument('--location', type=str, default='Poland', help='Search location (Poland, Warsaw, Krakow, etc.)')
    parser.add_argument('--radius', type=int, default=100, help='Search radius in km')
    parser.add_argument('--no-remote', action='store_true', help='Exclude remote jobs from search')
    parser.add_argument('--linkedin-basic', action='store_true', help='Use basic LinkedIn scraper instead of enhanced Luminati approach')
    
    args = parser.parse_args()
    
    config = Config()
    
    # Apply command line arguments
    if args.resume:
        config.RESUME_FILE = args.resume
    if args.min_match:
        config.MIN_MATCH_PCT = args.min_match
    if args.max_age:
        config.MAX_JOB_AGE_DAYS = args.max_age
    if args.output_dir:
        config.OUTPUT_DIR = args.output_dir
        config.CSV_OUTPUT = os.path.join(args.output_dir, "job_matches.csv")
        config.JSONL_OUTPUT = os.path.join(args.output_dir, "job_matches.jsonl")
        config.AUDIT_LOG = os.path.join(args.output_dir, "job_search_audit.log")
    
    # Location settings
    config.SEARCH_LOCATION = args.location
    config.SEARCH_RADIUS_KM = args.radius
    config.INCLUDE_REMOTE = not args.no_remote
    
    # Scraper settings
    config.USE_BASIC_LINKEDIN = args.linkedin_basic
    
    try:
        automation = JobSearchAutomation(config)
        automation.run()
    except KeyboardInterrupt:
        logger.info("Job search interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()