#!/usr/bin/env python3
"""
Run the fixed version of Job Finder Pro 2.0
"""

import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def main():
    """Run the fixed Job Finder"""
    try:
        print("🚀 Starting Job Finder Pro 2.0 - Fixed Version")
        print("✅ This version includes:")
        print("   - Skills input section (40% weight)")
        print("   - Enhanced matching algorithm")
        print("   - Better error handling")
        print("   - All UI components working")
        print()
        
        from job_finder_fixed import main as run_gui
        run_gui()
        
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        input("Press Enter to exit...")

if __name__ == "__main__":
    main()