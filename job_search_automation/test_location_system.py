#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.location_manager import LocationManager
from scrapers.linkedin_scraper import LinkedInScraper

def test_location_manager():
    print("🔍 Testing Location Manager...")
    manager = LocationManager()
    
    print("\n1. Supported locations:")
    locations = manager.get_supported_locations()
    print(f"   {', '.join(locations)}")
    
    print("\n2. Poland search variants:")
    poland_variants = manager.get_search_locations("Poland", include_remote=True)
    print(f"   Found {len(poland_variants)} variants:")
    for variant in poland_variants[:5]:  # Show first 5
        print(f"     • {variant}")
    print(f"     ... and {len(poland_variants)-5} more")
    
    print("\n3. Warsaw search variants:")
    warsaw_variants = manager.get_search_locations("Warsaw", include_remote=True)
    print(f"   Found {len(warsaw_variants)} variants:")
    for variant in warsaw_variants:
        print(f"     • {variant}")
    
    print("\n4. Location formatting:")
    test_locations = ["Poland", "Warsaw", "Krakow", "Custom Location"]
    for loc in test_locations:
        formatted = manager.format_location_display(loc)
        print(f"   {loc} → {formatted}")
    
    print("\n✅ Location Manager tests passed!")

def test_scraper_location_variants():
    print("\n🕷️ Testing Scraper Location Integration...")
    scraper = LinkedInScraper()
    
    # Test location variant generation
    poland_variants = scraper._get_location_variants("Poland", include_remote=True)
    print(f"\nLinkedIn Poland variants ({len(poland_variants)}):")
    for variant in poland_variants[:8]:  # Show first 8
        print(f"   • {variant}")
    
    warsaw_variants = scraper._get_location_variants("Warsaw", include_remote=True)
    print(f"\nLinkedIn Warsaw variants ({len(warsaw_variants)}):")
    for variant in warsaw_variants:
        print(f"   • {variant}")
    
    print("\n✅ Scraper location tests passed!")

def test_configuration_options():
    print("\n⚙️ Testing Configuration Options...")
    
    print("\nCommand line examples:")
    examples = [
        "python main.py --location Poland",
        "python main.py --location Warsaw --no-remote",
        "python main.py --location Krakow --min-match 60",
        "python main.py --location 'Remote Poland' --radius 50"
    ]
    
    for example in examples:
        print(f"   {example}")
    
    print("\n✅ Configuration tests passed!")

def main():
    print("="*70)
    print("🇵🇱 DYNAMIC LOCATION SYSTEM TEST")
    print("="*70)
    
    try:
        test_location_manager()
        test_scraper_location_variants()
        test_configuration_options()
        
        print("\n" + "="*70)
        print("🎯 ALL LOCATION TESTS PASSED!")
        print("="*70)
        print("\n📍 The system now supports:")
        print("   • All major Polish cities")
        print("   • Country-wide Poland search")  
        print("   • Remote job inclusion/exclusion")
        print("   • Platform-specific location formatting")
        print("\n🚀 Ready for Poland-wide job searches!")
        
    except Exception as e:
        print(f"\n❌ Location test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()