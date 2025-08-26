#!/usr/bin/env python3

import sys
import os
import time
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scrapers.linkedin_scraper import LinkedInScraper
from scrapers.linkedin_luminati_scraper import LinkedInLuminatiScraper

def test_basic_linkedin():
    print("🔍 Testing Basic LinkedIn Scraper...")
    scraper = LinkedInScraper()
    
    try:
        # Test with a single keyword and location
        jobs = scraper.search_jobs(['mechanical engineer'], 'Warsaw', include_remote=False)
        
        print(f"   ✓ Basic LinkedIn scraper returned {len(jobs)} jobs")
        
        if jobs:
            sample_job = jobs[0]
            print(f"   ✓ Sample job: {sample_job.get('job_title', 'N/A')} at {sample_job.get('company', 'N/A')}")
            print(f"   ✓ URL: {sample_job.get('job_url', 'N/A')[:50]}...")
        
        return jobs
        
    except Exception as e:
        print(f"   ❌ Basic LinkedIn scraper failed: {str(e)}")
        return []

def test_luminati_linkedin():
    print("\n🚀 Testing Enhanced LinkedIn Scraper (Luminati-style)...")
    scraper = LinkedInLuminatiScraper()
    
    try:
        # Test with a single keyword and location
        jobs = scraper.search_jobs(['mechanical engineer'], 'Warsaw', include_remote=False)
        
        print(f"   ✓ Enhanced LinkedIn scraper returned {len(jobs)} jobs")
        
        if jobs:
            sample_job = jobs[0]
            print(f"   ✓ Sample job: {sample_job.get('job_title', 'N/A')} at {sample_job.get('company', 'N/A')}")
            print(f"   ✓ URL: {sample_job.get('job_url', 'N/A')[:50]}...")
        
        return jobs
        
    except Exception as e:
        print(f"   ❌ Enhanced LinkedIn scraper failed: {str(e)}")
        return []

def compare_results(basic_jobs, enhanced_jobs):
    print(f"\n📊 COMPARISON RESULTS:")
    print("─" * 50)
    print(f"Basic LinkedIn Scraper:    {len(basic_jobs)} jobs")
    print(f"Enhanced LinkedIn Scraper: {len(enhanced_jobs)} jobs")
    
    if enhanced_jobs and basic_jobs:
        print(f"\nImprovement: {len(enhanced_jobs) - len(basic_jobs)} additional jobs")
        improvement_pct = ((len(enhanced_jobs) - len(basic_jobs)) / max(len(basic_jobs), 1)) * 100
        print(f"Percentage improvement: {improvement_pct:.1f}%")
    
    # Check for unique results
    basic_titles = {job.get('job_title', '') for job in basic_jobs}
    enhanced_titles = {job.get('job_title', '') for job in enhanced_jobs}
    
    unique_to_enhanced = enhanced_titles - basic_titles
    if unique_to_enhanced:
        print(f"\nUnique jobs found by enhanced scraper: {len(unique_to_enhanced)}")
        for title in list(unique_to_enhanced)[:3]:
            print(f"   • {title}")

def demonstrate_scraper_selection():
    print(f"\n⚙️ SCRAPER SELECTION OPTIONS:")
    print("─" * 50)
    
    examples = [
        {
            "cmd": "python main.py --location Warsaw",
            "desc": "Uses enhanced LinkedIn scraper (default)"
        },
        {
            "cmd": "python main.py --location Warsaw --linkedin-basic", 
            "desc": "Uses basic LinkedIn scraper (fallback)"
        }
    ]
    
    for example in examples:
        print(f"\n{example['cmd']}")
        print(f"   → {example['desc']}")
    
    print(f"\n💡 The enhanced scraper:")
    print("   • Uses LinkedIn's internal API patterns")
    print("   • Handles anti-bot protection better")
    print("   • Tries multiple search approaches")
    print("   • Falls back to basic scraper if needed")
    print("   • Based on Luminati LinkedIn scraper techniques")

def main():
    print("=" * 70)
    print("🔬 LINKEDIN SCRAPER COMPARISON TEST")
    print("=" * 70)
    print("Testing both basic and enhanced LinkedIn scrapers...")
    
    try:
        # Test both scrapers with limited scope to avoid rate limiting
        print("⚠️  Running limited tests to avoid LinkedIn rate limits...")
        
        start_time = time.time()
        basic_jobs = test_basic_linkedin()
        basic_time = time.time() - start_time
        
        print(f"   ⏱️  Basic scraper took {basic_time:.1f} seconds")
        
        # Wait between tests
        time.sleep(3)
        
        start_time = time.time()
        enhanced_jobs = test_luminati_linkedin()
        enhanced_time = time.time() - start_time
        
        print(f"   ⏱️  Enhanced scraper took {enhanced_time:.1f} seconds")
        
        compare_results(basic_jobs, enhanced_jobs)
        demonstrate_scraper_selection()
        
        print("\n" + "=" * 70)
        print("✅ LINKEDIN SCRAPER TEST COMPLETED!")
        print("=" * 70)
        
        recommendation = "enhanced" if len(enhanced_jobs) >= len(basic_jobs) else "basic"
        print(f"🎯 Recommendation: Use the {recommendation} scraper")
        
        if len(enhanced_jobs) > len(basic_jobs):
            print("   The enhanced scraper found more jobs!")
        elif len(basic_jobs) > 0 and len(enhanced_jobs) == 0:
            print("   The basic scraper may be more reliable in your environment")
        else:
            print("   Both scrapers performed similarly")
            
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()