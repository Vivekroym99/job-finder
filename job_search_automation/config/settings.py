import os
from datetime import datetime, timedelta
import pytz

class Config:
    RESUME_FILE = "/workspaces/job-finder/resume/resume.md"
    MIN_MATCH_PCT = 70
    TIMEZONE = pytz.timezone("Europe/Warsaw")
    MAX_JOB_AGE_DAYS = 14
    
    # Location settings - can be customized
    SEARCH_LOCATION = "Poland"  # Can be: "Poland", "Warsaw", "Krakow", "Remote Poland", etc.
    SEARCH_RADIUS_KM = 100  # Search radius in kilometers (for applicable platforms)
    INCLUDE_REMOTE = True  # Include remote jobs in search
    
    OUTPUT_DIR = "/tmp/job_search_results"
    CSV_OUTPUT = os.path.join(OUTPUT_DIR, "job_matches.csv")
    JSONL_OUTPUT = os.path.join(OUTPUT_DIR, "job_matches.jsonl")
    AUDIT_LOG = os.path.join(OUTPUT_DIR, "job_search_audit.log")
    
    TOP_MATCHES_DISPLAY = 30
    
    USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    
    # LinkedIn scraper options
    USE_BASIC_LINKEDIN = False  # Set to True to use basic LinkedIn scraper instead of enhanced
    
    # Job matching algorithm
    MATCHER_TYPE = 'description_focused'  # Options: 'standard', 'enhanced', 'description_focused'
    
    PLATFORMS = {
        "linkedin": {
            "enabled": True,
            "base_url": "https://www.linkedin.com/jobs/search",
            "search_params": {
                "location": "Warsaw, Poland",
                "f_TPR": "r604800"
            }
        },
        "glassdoor": {
            "enabled": True,
            "base_url": "https://www.glassdoor.com/Job",
            "search_params": {
                "locId": "2105",
                "fromAge": "14"
            }
        },
        "pracuj": {
            "enabled": True,
            "base_url": "https://www.pracuj.pl/praca",
            "search_params": {
                "et": "1,17",
                "di": "14"
            }
        },
        "google_jobs": {
            "enabled": True,
            "base_url": "https://www.google.com/search",
            "search_params": {
                "q": "jobs",
                "ibp": "htl;jobs",
                "chips": "date_posted:week"
            }
        }
    }
    
    JOB_SEARCH_KEYWORDS = [
        "mechanical engineer",
        "thermal engineer",
        "power engineer",
        "HVAC engineer",
        "energy engineer",
        "renewable energy",
        "project engineer",
        "sales engineer",
        "technical sales",
        "CAD engineer",
        "design engineer",
        "simulation engineer",
        "CFD engineer",
        "FEA engineer",
        "engineering intern",
        "graduate engineer"
    ]