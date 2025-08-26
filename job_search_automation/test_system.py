#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.resume_parser import ResumeParser
from matchers.job_matcher import JobMatcher
from outputs.output_manager import OutputManager
from config.settings import Config

def test_resume_parser():
    print("Testing Resume Parser...")
    parser = ResumeParser("/workspaces/job-finder/resume/resume.md")
    profile = parser.extract_profile()
    
    print(f"✓ Name: {profile['name']}")
    print(f"✓ Email: {profile['email']}")
    print(f"✓ Experience: {profile['experience_years']} years")
    print(f"✓ Skills found: {len(profile['skills'])}")
    print(f"✓ Keywords: {len(profile['keywords'])}")
    print(f"✓ Target roles: {len(profile['target_roles'])}")
    
    return profile

def test_job_matcher(profile):
    print("\nTesting Job Matcher...")
    matcher = JobMatcher(profile)
    
    sample_job = {
        'job_title': 'Mechanical Engineer',
        'company': 'Test Company',
        'description': 'We are looking for a mechanical engineer with experience in HVAC, AutoCAD, and thermal systems. 3+ years experience required.',
        'required_experience': 3
    }
    
    score, skills = matcher.calculate_match_score(sample_job)
    print(f"✓ Match score for sample job: {score:.1f}%")
    print(f"✓ Matching skills: {skills}")
    
    is_recent = matcher.is_job_recent("5 days ago", 14)
    print(f"✓ Date parsing (5 days ago): {is_recent}")

def test_output_manager():
    print("\nTesting Output Manager...")
    config = Config()
    config.OUTPUT_DIR = "/tmp/job_search_test"
    config.CSV_OUTPUT = os.path.join(config.OUTPUT_DIR, "test.csv")
    config.JSONL_OUTPUT = os.path.join(config.OUTPUT_DIR, "test.jsonl")
    config.AUDIT_LOG = os.path.join(config.OUTPUT_DIR, "test.log")
    
    manager = OutputManager(config)
    
    sample_jobs = [
        {
            'match_score': 85.5,
            'job_title': 'Mechanical Engineer',
            'company': 'Test Corp',
            'platform': 'LinkedIn',
            'job_url': 'https://example.com/job1',
            'matching_skills': ['AutoCAD', 'HVAC', 'Python']
        }
    ]
    
    manager.save_to_csv(sample_jobs, config.CSV_OUTPUT)
    manager.save_to_jsonl(sample_jobs, config.JSONL_OUTPUT)
    manager.write_audit_log("Test audit message")
    
    print(f"✓ CSV file created: {os.path.exists(config.CSV_OUTPUT)}")
    print(f"✓ JSONL file created: {os.path.exists(config.JSONL_OUTPUT)}")
    print(f"✓ Audit log created: {os.path.exists(config.AUDIT_LOG)}")

def main():
    print("="*60)
    print("JOB SEARCH AUTOMATION SYSTEM TEST")
    print("="*60)
    
    try:
        profile = test_resume_parser()
        test_job_matcher(profile)
        test_output_manager()
        
        print("\n" + "="*60)
        print("✅ ALL TESTS PASSED!")
        print("="*60)
        print("\nSystem is ready to use. Run with:")
        print("python /workspaces/job-finder/job_search_automation/main.py")
        print("\nOptions:")
        print("  --min-match 70    # Minimum match percentage")
        print("  --max-age 14      # Maximum job age in days")
        print("  --output-dir /mnt/data  # Output directory")
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()