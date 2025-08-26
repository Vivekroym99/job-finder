#!/usr/bin/env python3
"""
Portable Job Finder Pro Launcher
This launcher automatically installs missing dependencies and runs the application
No separate installation step required
"""

import sys
import subprocess
import os
import importlib
from pathlib import Path

# Configuration
APP_NAME = "Job Finder Pro"
REQUIRED_PACKAGES = {
    'requests': 'requests',
    'bs4': 'beautifulsoup4',
    'pandas': 'pandas', 
    'fake_useragent': 'fake-useragent',
    'cloudscraper': 'cloudscraper',
    'sklearn': 'scikit-learn',
    'nltk': 'nltk',
    'jsonlines': 'jsonlines',
    'tabulate': 'tabulate',
    'dateutil': 'python-dateutil',
    'pytz': 'pytz',
    'tkinter': 'tkinter'  # Built-in, but we'll check
}

def print_banner():
    """Print application banner"""
    print("=" * 60)
    print(f"    {APP_NAME.upper()} - PORTABLE LAUNCHER")
    print("=" * 60)
    print()
    print("🚀 No installation required!")
    print("📦 Dependencies will be installed automatically")
    print()

def check_python():
    """Check Python version"""
    if sys.version_info < (3, 8):
        print(f"❌ Python {sys.version_info.major}.{sys.version_info.minor} is too old")
        print("Please install Python 3.8 or later from https://python.org/downloads")
        return False
    
    print(f"✓ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    return True

def install_package(package_name, import_name):
    """Install a package if missing"""
    try:
        importlib.import_module(import_name)
        return True
    except ImportError:
        print(f"📦 Installing {package_name}...")
        try:
            # Try regular install
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", package_name, "--quiet", "--no-warn-script-location"
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True
        except subprocess.CalledProcessError:
            try:
                # Try user install
                subprocess.check_call([
                    sys.executable, "-m", "pip", "install", package_name, "--user", "--quiet", "--no-warn-script-location"
                ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                return True
            except subprocess.CalledProcessError:
                print(f"   ⚠️ Failed to install {package_name}")
                return False

def ensure_dependencies():
    """Ensure all dependencies are available"""
    print("🔍 Checking dependencies...")
    
    # Upgrade pip first
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "--upgrade", "pip", "--quiet"
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except:
        pass  # Continue if pip upgrade fails
    
    missing_packages = []
    
    for import_name, package_name in REQUIRED_PACKAGES.items():
        if import_name == 'tkinter':
            # Special handling for tkinter
            try:
                import tkinter
                print("   ✓ tkinter (GUI system)")
            except ImportError:
                print("   ❌ tkinter - GUI system not available")
                print("      Please install tkinter or use Python from python.org")
                missing_packages.append(package_name)
        else:
            if install_package(package_name, import_name):
                print(f"   ✓ {import_name}")
            else:
                missing_packages.append(package_name)
    
    # Setup NLTK data
    try:
        import nltk
        print("   📚 Setting up language data...")
        nltk.download('stopwords', quiet=True)
        nltk.download('punkt', quiet=True)
    except:
        pass
    
    if missing_packages:
        print(f"\n⚠️ Some packages could not be installed: {', '.join(missing_packages)}")
        print("The application may still work with reduced functionality.")
    else:
        print("✓ All dependencies ready!")
    
    return len(missing_packages) < 3  # Allow app to run if most packages are available

def find_application():
    """Find the main application file"""
    current_dir = Path(__file__).parent
    
    app_files = [
        'job_finder_gui.py',
        'run_job_finder_gui.py'
    ]
    
    for app_file in app_files:
        app_path = current_dir / app_file
        if app_path.exists():
            return str(app_path)
    
    return None

def create_results_folder():
    """Create results folder on desktop"""
    try:
        desktop = Path.home() / "Desktop"
        results_dir = desktop / "JobSearchResults"
        results_dir.mkdir(exist_ok=True)
        print(f"📁 Results folder: {results_dir}")
        return str(results_dir)
    except:
        # Fallback to current directory
        results_dir = Path.cwd() / "results"
        results_dir.mkdir(exist_ok=True)
        return str(results_dir)

def launch_application():
    """Launch the main application"""
    app_path = find_application()
    
    if not app_path:
        print("❌ Application files not found!")
        print("Please ensure job_finder_gui.py is in the same directory")
        return False
    
    print(f"🚀 Launching {APP_NAME}...")
    print()
    
    try:
        # Set up environment
        os.environ['PYTHONPATH'] = str(Path(__file__).parent)
        
        # Import and run the GUI
        sys.path.insert(0, str(Path(__file__).parent))
        
        if 'job_finder_gui' in app_path:
            from job_finder_gui import main as app_main
        else:
            from run_job_finder_gui import main as app_main
        
        app_main()
        return True
        
    except ImportError as e:
        print(f"❌ Failed to import application: {e}")
        print("\nTrying alternative launch method...")
        
        try:
            # Launch as subprocess
            subprocess.run([sys.executable, app_path], check=True)
            return True
        except Exception as e:
            print(f"❌ Failed to launch application: {e}")
            return False
    
    except Exception as e:
        print(f"❌ Application error: {e}")
        return False

def show_help():
    """Show usage instructions"""
    print("\n" + "=" * 60)
    print("📋 USAGE INSTRUCTIONS")
    print("=" * 60)
    print()
    print("🎯 How to use Job Finder Pro:")
    print()
    print("1. 📄 PASTE YOUR RESUME:")
    print("   • Click 'Paste Resume Text' button")
    print("   • Copy and paste your complete resume")
    print()
    print("2. ⚙️ CONFIGURE SETTINGS:")
    print("   • Location: Poland, Warsaw, Krakow, etc.")
    print("   • Min Match: 70% (recommended)")
    print("   • Max Age: 14 days (recommended)")
    print()
    print("3. 🚀 START SEARCH:")
    print("   • Click 'Start Job Search'") 
    print("   • Wait 2-5 minutes for completion")
    print()
    print("4. 📊 VIEW RESULTS:")
    print("   • Open job_matches.csv in Excel")
    print("   • Review matching jobs with scores")
    print()
    print("💡 Tips:")
    print("   • Include skills, tools, and experience in resume")
    print("   • Use 'Poland' location for maximum coverage")
    print("   • Check results folder on Desktop")
    print()

def main():
    """Main launcher function"""
    print_banner()
    
    try:
        # Check Python version
        if not check_python():
            input("Press Enter to exit...")
            return
        
        # Ensure dependencies
        if not ensure_dependencies():
            print("\n⚠️ Critical dependencies missing. Application may not work properly.")
            continue_anyway = input("Continue anyway? (y/N): ").strip().lower()
            if continue_anyway != 'y':
                print("Installation cancelled.")
                input("Press Enter to exit...")
                return
        
        # Create results folder
        create_results_folder()
        
        # Show quick help
        show_help()
        
        # Launch application
        print("=" * 60)
        if launch_application():
            print("✓ Application launched successfully!")
        else:
            print("❌ Failed to launch application")
            print("\nTroubleshooting:")
            print("1. Ensure all files are in the same directory")
            print("2. Try running: python job_finder_gui.py")
            print("3. Check that Python is properly installed")
        
    except KeyboardInterrupt:
        print("\n\n👋 Cancelled by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
    finally:
        input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()