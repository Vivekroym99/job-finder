#!/usr/bin/env python3
"""
Job Finder Pro Launcher
This script ensures all dependencies are installed before launching the GUI
"""

import sys
import subprocess
import os
from pathlib import Path

def check_and_install_dependencies():
    """Check and install required dependencies"""
    required_packages = [
        'requests',
        'beautifulsoup4', 
        'pandas',
        'fake-useragent',
        'cloudscraper',
        'scikit-learn',
        'nltk',
        'jsonlines',
        'tabulate',
        'python-dateutil',
        'pytz'
    ]
    
    print("🔍 Checking dependencies...")
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"📦 Installing {len(missing_packages)} missing packages...")
        for package in missing_packages:
            print(f"   Installing {package}...")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", package], 
                                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except subprocess.CalledProcessError:
                print(f"   ⚠️  Failed to install {package}")
        print("✓ Dependencies installation completed")
    else:
        print("✓ All dependencies are already installed")

def setup_nltk_data():
    """Download required NLTK data"""
    try:
        import nltk
        print("📚 Setting up NLTK data...")
        nltk.download('stopwords', quiet=True)
        nltk.download('punkt', quiet=True)
        print("✓ NLTK data ready")
    except Exception as e:
        print(f"⚠️  NLTK setup failed: {e}")

def launch_gui():
    """Launch the Job Finder GUI"""
    try:
        print("🚀 Launching Job Finder Pro...")
        
        # Import and run the GUI
        from job_finder_gui import main
        main()
        
    except ImportError as e:
        print(f"❌ Failed to import GUI module: {e}")
        print("Please ensure job_finder_gui.py is in the same directory")
        input("Press Enter to exit...")
    except Exception as e:
        print(f"❌ Error launching GUI: {e}")
        input("Press Enter to exit...")

def main():
    """Main launcher function"""
    print("=" * 60)
    print("    JOB FINDER PRO - LinkedIn Job Search Automation")
    print("=" * 60)
    print()
    
    try:
        # Check dependencies
        check_and_install_dependencies()
        
        # Setup NLTK
        setup_nltk_data()
        
        print()
        print("=" * 60)
        print()
        
        # Launch GUI
        launch_gui()
        
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ Startup error: {e}")
        input("Press Enter to exit...")

if __name__ == "__main__":
    main()