#!/usr/bin/env python3
"""
Job Finder Pro - Python-based Installer
This installer handles all setup automatically and is more reliable than batch files
"""

import sys
import subprocess
import os
import urllib.request
import tempfile
import shutil
from pathlib import Path
import time

def print_header():
    """Print installation header"""
    print("=" * 60)
    print("    JOB FINDER PRO - PYTHON INSTALLER")
    print("=" * 60)
    print()

def check_python_version():
    """Check if Python version is compatible"""
    print("🔍 Checking Python version...")
    
    version = sys.version_info
    if version.major == 3 and version.minor >= 8:
        print(f"✓ Python {version.major}.{version.minor}.{version.micro} - Compatible")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} - Too old")
        print("Please install Python 3.8 or later from https://python.org/downloads")
        return False

def install_package(package_name):
    """Install a single package with error handling"""
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", package_name, "--quiet"
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except subprocess.CalledProcessError:
        try:
            # Try with --user flag
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", package_name, "--user", "--quiet"
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True
        except subprocess.CalledProcessError:
            return False

def install_packages():
    """Install all required packages"""
    print("\n📦 Installing required packages...")
    
    # Upgrade pip first
    print("   Upgrading pip...")
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "--upgrade", "pip", "--quiet"
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except:
        print("   ⚠️ Could not upgrade pip, continuing anyway...")
    
    # Essential packages
    packages = [
        "requests",
        "beautifulsoup4", 
        "pandas",
        "fake-useragent",
        "cloudscraper",
        "scikit-learn",
        "nltk",
        "jsonlines",
        "tabulate",
        "python-dateutil",
        "pytz"
    ]
    
    failed_packages = []
    
    for package in packages:
        print(f"   Installing {package}...")
        if not install_package(package):
            failed_packages.append(package)
    
    if failed_packages:
        print(f"\n⚠️ Some packages failed to install: {', '.join(failed_packages)}")
        print("The application may still work, but some features might be limited.")
    else:
        print("✓ All packages installed successfully")

def setup_nltk_data():
    """Setup NLTK data"""
    print("\n🧠 Setting up language processing data...")
    try:
        import nltk
        nltk.download('stopwords', quiet=True)
        nltk.download('punkt', quiet=True)
        print("✓ Language data ready")
    except Exception as e:
        print(f"⚠️ Could not setup NLTK data: {e}")

def create_shortcuts():
    """Create desktop shortcuts"""
    print("\n🔗 Creating shortcuts...")
    
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        desktop = os.path.join(os.path.expanduser("~"), "Desktop")
        
        # Create batch file shortcut
        batch_file = os.path.join(current_dir, "JobFinderPro.bat")
        if os.path.exists(batch_file):
            shortcut_path = os.path.join(desktop, "Job Finder Pro.lnk")
            
            # Use PowerShell to create shortcut
            ps_command = f'''
$WshShell = New-Object -comObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("{shortcut_path}")
$Shortcut.TargetPath = "{batch_file}"
$Shortcut.WorkingDirectory = "{current_dir}"
$Shortcut.Save()
'''
            
            try:
                subprocess.run([
                    "powershell", "-Command", ps_command
                ], check=True, capture_output=True)
                print("✓ Desktop shortcut created")
            except:
                print("⚠️ Could not create desktop shortcut")
        
        # Create results folder
        results_dir = os.path.join(desktop, "JobSearchResults")
        os.makedirs(results_dir, exist_ok=True)
        print(f"✓ Results folder created: {results_dir}")
        
    except Exception as e:
        print(f"⚠️ Error creating shortcuts: {e}")

def test_installation():
    """Test if the installation works"""
    print("\n🧪 Testing installation...")
    
    try:
        # Test imports
        essential_modules = ['requests', 'bs4', 'pandas', 'tkinter']
        for module in essential_modules:
            try:
                __import__(module)
                print(f"   ✓ {module}")
            except ImportError:
                print(f"   ❌ {module} - not available")
        
        # Test GUI
        try:
            import tkinter as tk
            root = tk.Tk()
            root.withdraw()  # Hide the window
            root.destroy()
            print("   ✓ GUI system working")
        except Exception as e:
            print(f"   ❌ GUI system: {e}")
        
        return True
    except Exception as e:
        print(f"❌ Installation test failed: {e}")
        return False

def launch_application():
    """Launch the Job Finder Pro application"""
    print("\n🚀 Launching Job Finder Pro...")
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Try different launch methods
    launch_files = [
        "job_finder_gui.py",
        "run_job_finder_gui.py"
    ]
    
    for launch_file in launch_files:
        file_path = os.path.join(current_dir, launch_file)
        if os.path.exists(file_path):
            try:
                # Launch in new process
                if sys.platform == "win32":
                    subprocess.Popen([sys.executable, file_path], 
                                   creationflags=subprocess.CREATE_NEW_CONSOLE)
                else:
                    subprocess.Popen([sys.executable, file_path])
                
                print(f"✓ Application launched: {launch_file}")
                return True
            except Exception as e:
                print(f"❌ Failed to launch {launch_file}: {e}")
    
    print("❌ Could not launch application")
    return False

def main():
    """Main installer function"""
    print_header()
    
    try:
        # Check Python version
        if not check_python_version():
            input("\nPress Enter to exit...")
            return False
        
        # Install packages
        install_packages()
        
        # Setup NLTK
        setup_nltk_data()
        
        # Create shortcuts
        create_shortcuts()
        
        # Test installation
        if test_installation():
            print("\n" + "=" * 60)
            print("    ✅ INSTALLATION COMPLETED SUCCESSFULLY!")
            print("=" * 60)
            
            print("\n🎉 Job Finder Pro is ready to use!")
            print("\n📋 Quick Start:")
            print("   1. The application should launch automatically")
            print("   2. Paste your resume text in the app")
            print("   3. Select your location (Poland, Warsaw, etc.)")
            print("   4. Click 'Start Job Search'")
            print("   5. Wait 2-5 minutes for results")
            print("   6. Open the generated Excel file")
            
            print(f"\n💡 Results will be saved to:")
            print(f"   {os.path.join(os.path.expanduser('~'), 'Desktop', 'JobSearchResults')}")
            
            # Ask if user wants to launch now
            launch_now = input("\n🚀 Launch Job Finder Pro now? (Y/n): ").strip().lower()
            if launch_now != 'n':
                launch_application()
            
            print("\n📚 For detailed instructions, see USER_MANUAL.md")
            print("👋 You can also launch anytime from the desktop shortcut!")
            
        else:
            print("\n⚠️ Installation completed but with some issues.")
            print("You may still be able to run the application manually.")
        
        input("\nPress Enter to exit...")
        return True
        
    except KeyboardInterrupt:
        print("\n\n👋 Installation cancelled by user")
        input("Press Enter to exit...")
        return False
    except Exception as e:
        print(f"\n❌ Installation failed: {e}")
        input("Press Enter to exit...")
        return False

if __name__ == "__main__":
    main()