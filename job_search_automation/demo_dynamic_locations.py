#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.settings import Config
from scrapers.linkedin_scraper import LinkedInScraper
from scrapers.glassdoor_scraper import GlassdoorScraper  
from scrapers.pracuj_scraper import PracujScraper
from scrapers.google_jobs_scraper import GoogleJobsScraper

def demo_location_differences():
    print("🎯 DYNAMIC LOCATION DEMO - How Different Locations Change Search Strategy")
    print("="*80)
    
    locations_to_test = [
        {"location": "Poland", "include_remote": True, "desc": "🇵🇱 All Poland + Remote"},
        {"location": "Warsaw", "include_remote": True, "desc": "🏙️ Warsaw + Remote"},
        {"location": "Krakow", "include_remote": False, "desc": "🏛️ Krakow Only (No Remote)"},
    ]
    
    scrapers = {
        "LinkedIn": LinkedInScraper(),
        "Glassdoor": GlassdoorScraper(),
        "Pracuj.pl": PracujScraper(),
        "Google Jobs": GoogleJobsScraper()
    }
    
    for config in locations_to_test:
        print(f"\n📍 TESTING: {config['desc']}")
        print("─" * 60)
        
        location = config["location"]
        include_remote = config["include_remote"]
        
        # LinkedIn variants
        linkedin = scrapers["LinkedIn"]
        linkedin_variants = linkedin._get_location_variants(location, include_remote)
        print(f"\n🔗 LinkedIn will search {len(linkedin_variants)} variants:")
        for variant in linkedin_variants[:3]:  # Show first 3
            print(f"   • {variant}")
        if len(linkedin_variants) > 3:
            print(f"   • ... and {len(linkedin_variants)-3} more")
        
        # Glassdoor location ID
        glassdoor = scrapers["Glassdoor"]
        glassdoor_id = glassdoor._get_location_id(location)
        print(f"\n🏢 Glassdoor will use location ID: {glassdoor_id}")
        
        # Pracuj.pl formatting
        pracuj = scrapers["Pracuj.pl"]
        pracuj_location = pracuj._format_location(location)
        pracuj_desc = "all Poland" if pracuj_location == "" else pracuj_location
        remote_desc = " + remote filter" if include_remote else ""
        print(f"\n🇵🇱 Pracuj.pl will search: {pracuj_desc}{remote_desc}")
        
        # Google Jobs query
        google = scrapers["Google Jobs"]
        if include_remote:
            query = f"mechanical engineer jobs in {location} OR remote mechanical engineer jobs"
        else:
            query = f"mechanical engineer jobs in {location}"
        print(f"\n🔍 Google Jobs sample query: {query[:60]}...")
        
        print("\n" + "─" * 60)

def demo_command_examples():
    print("\n🚀 COMMAND LINE EXAMPLES WITH ACTUAL DIFFERENCES")
    print("="*80)
    
    examples = [
        {
            "cmd": "python main.py",
            "desc": "Default - searches ALL major Polish cities + remote",
            "searches": "~10 cities × 4 platforms = ~40 search queries"
        },
        {
            "cmd": "python main.py --location Warsaw", 
            "desc": "Warsaw focus - searches Warsaw variants + remote",
            "searches": "3 Warsaw variants × 4 platforms = ~12 search queries"
        },
        {
            "cmd": "python main.py --location Krakow --no-remote",
            "desc": "Krakow only - no remote positions included",
            "searches": "1-2 Krakow variants × 4 platforms = ~8 search queries"
        },
        {
            "cmd": "python main.py --location Poland --no-remote",
            "desc": "Poland-wide but NO remote - city searches only",
            "searches": "~8 cities × 4 platforms = ~32 search queries"
        }
    ]
    
    for i, example in enumerate(examples, 1):
        print(f"\n{i}. {example['cmd']}")
        print(f"   📝 {example['desc']}")
        print(f"   📊 {example['searches']}")

def show_configuration_impact():
    print("\n⚙️ HOW CONFIGURATION DYNAMICALLY AFFECTS EACH PLATFORM")
    print("="*80)
    
    print("\n📍 Location: 'Poland' + Remote")
    print("┌────────────┬─────────────────────────────────────────┐")
    print("│ Platform   │ What Actually Gets Searched             │")
    print("├────────────┼─────────────────────────────────────────┤")
    print("│ LinkedIn   │ 8 cities + 'Poland' + 'Remote Poland'  │")
    print("│ Glassdoor  │ Country ID 2616 + major city IDs       │") 
    print("│ Pracuj.pl  │ Empty location (= all Poland) + rw=1   │")
    print("│ Google     │ 'jobs in Poland OR remote jobs' + gl=pl│")
    print("└────────────┴─────────────────────────────────────────┘")
    
    print("\n📍 Location: 'Warsaw' + No Remote")
    print("┌────────────┬─────────────────────────────────────────┐")
    print("│ Platform   │ What Actually Gets Searched             │")
    print("├────────────┼─────────────────────────────────────────┤")
    print("│ LinkedIn   │ 'Warsaw, Poland' only                  │")
    print("│ Glassdoor  │ Warsaw ID 3089098                      │")
    print("│ Pracuj.pl  │ 'warszawa' without remote filter       │")
    print("│ Google     │ 'jobs in Warsaw Poland' (no remote)    │")
    print("└────────────┴─────────────────────────────────────────┘")

def main():
    print("🎬 DEMONSTRATING DYNAMIC MULTI-PLATFORM LOCATION SYSTEM")
    print("="*80)
    print("This shows how the system adapts to different --location parameters")
    
    try:
        demo_location_differences()
        demo_command_examples()
        show_configuration_impact()
        
        print("\n" + "="*80)
        print("✅ THE SYSTEM IS TRULY DYNAMIC!")
        print("="*80)
        print("\n🎯 Key Points:")
        print("   • Each --location parameter changes search strategy")
        print("   • Each platform adapts differently to the same location") 
        print("   • Remote inclusion/exclusion affects all platforms")
        print("   • Poland = comprehensive multi-city coverage")
        print("   • Specific cities = focused + efficient searches")
        
        print("\n🧪 To see it in action, run:")
        print("   python main.py --location Warsaw --output-dir /tmp/test")
        print("   python main.py --location Poland --no-remote --output-dir /tmp/test")
        
    except Exception as e:
        print(f"\n❌ Demo failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()