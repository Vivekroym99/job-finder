import csv
import json
import jsonlines
import os
from typing import List, Dict
from datetime import datetime
import logging
from tabulate import tabulate

class OutputManager:
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger('OutputManager')
        self._ensure_output_dir()
    
    def _ensure_output_dir(self):
        os.makedirs(self.config.OUTPUT_DIR, exist_ok=True)
    
    def save_to_csv(self, jobs: List[Dict], filename: str = None):
        filename = filename or self.config.CSV_OUTPUT
        
        if not jobs:
            self.logger.warning("No jobs to save to CSV")
            return
        
        fieldnames = ['match_pct', 'job_title', 'company', 'platform', 'job_url', 'skill_match', 'location', 'posted_date']
        
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for job in jobs:
                    row = {
                        'match_pct': job.get('match_score', 0),
                        'job_title': job.get('job_title', ''),
                        'company': job.get('company', ''),
                        'platform': job.get('platform', ''),
                        'job_url': job.get('job_url', ''),
                        'skill_match': ';'.join(job.get('matching_skills', [])),
                        'location': job.get('location', ''),
                        'posted_date': job.get('posted_date', '')
                    }
                    writer.writerow(row)
            
            self.logger.info(f"Saved {len(jobs)} jobs to CSV: {filename}")
        except Exception as e:
            self.logger.error(f"Error saving to CSV: {str(e)}")
    
    def save_to_jsonl(self, jobs: List[Dict], filename: str = None):
        filename = filename or self.config.JSONL_OUTPUT
        
        if not jobs:
            self.logger.warning("No jobs to save to JSONL")
            return
        
        try:
            with jsonlines.open(filename, mode='w') as writer:
                for job in jobs:
                    normalized_job = {
                        'match_score': job.get('match_score', 0),
                        'job_title': job.get('job_title', ''),
                        'company': job.get('company', ''),
                        'platform': job.get('platform', ''),
                        'location': job.get('location', ''),
                        'job_url': job.get('job_url', ''),
                        'posted_date': job.get('posted_date', ''),
                        'description': job.get('description', ''),
                        'matching_skills': job.get('matching_skills', []),
                        'required_experience': job.get('required_experience', 0),
                        'salary': job.get('salary', ''),
                        'scraped_at': datetime.now().isoformat()
                    }
                    writer.write(normalized_job)
            
            self.logger.info(f"Saved {len(jobs)} jobs to JSONL: {filename}")
        except Exception as e:
            self.logger.error(f"Error saving to JSONL: {str(e)}")
    
    def print_summary(self, jobs: List[Dict], platform_stats: Dict):
        print("\n" + "="*100)
        print("JOB SEARCH SUMMARY")
        print("="*100)
        
        print("\nPLATFORM STATISTICS:")
        print("-"*50)
        
        stats_table = []
        total_fetched = 0
        total_kept = 0
        
        for platform, stats in platform_stats.items():
            fetched = stats.get('fetched', 0)
            kept = stats.get('kept', 0)
            total_fetched += fetched
            total_kept += kept
            stats_table.append([platform, fetched, kept, f"{kept/fetched*100:.1f}%" if fetched > 0 else "0%"])
        
        stats_table.append(["-"*15, "-"*10, "-"*10, "-"*10])
        stats_table.append(["TOTAL", total_fetched, total_kept, f"{total_kept/total_fetched*100:.1f}%" if total_fetched > 0 else "0%"])
        
        print(tabulate(stats_table, headers=["Platform", "Fetched", "Kept", "Keep Rate"], tablefmt="grid"))
        
        if jobs:
            top_jobs = sorted(jobs, key=lambda x: x.get('match_score', 0), reverse=True)[:self.config.TOP_MATCHES_DISPLAY]
            
            print(f"\nTOP {min(len(top_jobs), self.config.TOP_MATCHES_DISPLAY)} MATCHES:")
            print("-"*100)
            
            job_table = []
            for job in top_jobs:
                job_table.append([
                    f"{job.get('match_score', 0):.1f}%",
                    job.get('job_title', '')[:40],
                    job.get('company', '')[:25],
                    job.get('platform', '')[:15],
                    job.get('job_url', '')[:50],
                    ';'.join(job.get('matching_skills', [])[:3])[:30]
                ])
            
            print(tabulate(job_table, 
                         headers=["Match %", "Job Title", "Company", "Platform", "URL", "Top Skills"],
                         tablefmt="grid"))
        else:
            print("\nNo matching jobs found.")
        
        print("\n" + "="*100)
    
    def write_audit_log(self, message: str, level: str = "INFO"):
        timestamp = datetime.now().isoformat()
        
        try:
            with open(self.config.AUDIT_LOG, 'a', encoding='utf-8') as f:
                f.write(f"[{timestamp}] [{level}] {message}\n")
        except Exception as e:
            self.logger.error(f"Error writing to audit log: {str(e)}")
    
    def log_platform_results(self, platform: str, fetched: int, kept: int, errors: List[str] = None):
        message = f"Platform: {platform} | Fetched: {fetched} | Kept: {kept}"
        if errors:
            message += f" | Errors: {', '.join(errors[:3])}"
        
        self.write_audit_log(message)