#!/usr/bin/env python3
"""
Robust Job Finder Pro Installer
Handles common pip installation issues and provides multiple fallback methods
"""

import sys
import subprocess
import os
import tempfile
import urllib.request
from pathlib import Path

def print_header():
    """Print installation header"""
    print("=" * 70)
    print("    JOB FINDER PRO - ROBUST INSTALLER")
    print("=" * 70)
    print()
    print("🔧 This installer handles common installation issues")
    print("📦 Multiple methods to ensure packages are installed")
    print()

def check_internet():
    """Check internet connectivity"""
    print("🌐 Checking internet connection...")
    try:
        urllib.request.urlopen('https://pypi.org', timeout=10)
        print("✓ Internet connection available")
        return True
    except:
        print("❌ No internet connection or PyPI unreachable")
        print("Please check your internet connection and try again.")
        return False

def fix_pip():
    """Fix common pip issues"""
    print("🔧 Fixing potential pip issues...")
    
    # Upgrade pip with multiple methods
    pip_upgrade_commands = [
        [sys.executable, "-m", "pip", "install", "--upgrade", "pip"],
        [sys.executable, "-m", "pip", "install", "--upgrade", "pip", "--user"],
        [sys.executable, "-m", "pip", "install", "--upgrade", "pip", "--no-warn-script-location"],
        ["python", "-m", "ensurepip", "--upgrade"],
        ["py", "-m", "pip", "install", "--upgrade", "pip"]
    ]
    
    for command in pip_upgrade_commands:
        try:
            result = subprocess.run(command, capture_output=True, text=True, timeout=60)
            if result.returncode == 0:
                print("✓ Pip upgraded successfully")
                return True
        except:
            continue
    
    print("⚠️ Could not upgrade pip, but continuing...")
    return False

def install_package_robust(package_name, import_name=None):
    """Install package with multiple fallback methods"""
    if import_name is None:
        import_name = package_name.replace('-', '_')
    
    # Test if already installed
    try:
        __import__(import_name)
        print(f"   ✓ {package_name} (already installed)")
        return True
    except ImportError:
        pass
    
    print(f"📦 Installing {package_name}...")
    
    # Multiple installation commands to try
    install_commands = [
        # Standard install
        [sys.executable, "-m", "pip", "install", package_name],
        # User install
        [sys.executable, "-m", "pip", "install", package_name, "--user"],
        # No cache
        [sys.executable, "-m", "pip", "install", package_name, "--no-cache-dir"],
        # User + no cache
        [sys.executable, "-m", "pip", "install", package_name, "--user", "--no-cache-dir"],
        # Force reinstall
        [sys.executable, "-m", "pip", "install", package_name, "--force-reinstall"],
        # Ignore installed
        [sys.executable, "-m", "pip", "install", package_name, "--ignore-installed"],
        # With trusted host
        [sys.executable, "-m", "pip", "install", package_name, "--trusted-host", "pypi.org", "--trusted-host", "pypi.python.org", "--trusted-host", "files.pythonhosted.org"],
        # Alternative Python commands
        ["python", "-m", "pip", "install", package_name, "--user"],
        ["py", "-m", "pip", "install", package_name, "--user"]
    ]
    
    for i, command in enumerate(install_commands):
        try:
            result = subprocess.run(
                command, 
                capture_output=True, 
                text=True, 
                timeout=120,
                cwd=tempfile.gettempdir()
            )
            
            if result.returncode == 0:
                # Verify installation
                try:
                    __import__(import_name)
                    print(f"   ✓ {package_name} installed successfully")
                    return True
                except ImportError:
                    continue
            else:
                # Print error for debugging
                if i == 0:  # Only print error for first attempt
                    print(f"   ⚠️ Install attempt failed: {result.stderr[:100]}...")
        
        except subprocess.TimeoutExpired:
            print(f"   ⚠️ Install timeout for {package_name}")
        except Exception as e:
            if i == 0:
                print(f"   ⚠️ Install error: {str(e)[:50]}...")
    
    print(f"   ❌ Could not install {package_name}")
    return False

def install_from_requirements():
    """Try installing from requirements.txt if it exists"""
    req_file = Path(__file__).parent / "requirements.txt"
    
    if not req_file.exists():
        print("⚠️ requirements.txt not found, installing packages individually")
        return False
    
    print("📋 Trying to install from requirements.txt...")
    
    commands = [
        [sys.executable, "-m", "pip", "install", "-r", str(req_file)],
        [sys.executable, "-m", "pip", "install", "-r", str(req_file), "--user"],
        [sys.executable, "-m", "pip", "install", "-r", str(req_file), "--user", "--no-cache-dir"]
    ]
    
    for command in commands:
        try:
            result = subprocess.run(command, capture_output=True, text=True, timeout=300)
            if result.returncode == 0:
                print("✓ Requirements installed from file")
                return True
        except:
            continue
    
    print("⚠️ Could not install from requirements.txt")
    return False

def check_admin_rights():
    """Check if running with administrator rights"""
    try:
        import ctypes
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def suggest_solutions():
    """Suggest solutions for installation problems"""
    print("\n🔧 INSTALLATION TROUBLESHOOTING")
    print("=" * 50)
    
    print("\n💡 If packages failed to install, try these solutions:")
    print()
    print("1. 🔐 RUN AS ADMINISTRATOR:")
    print("   • Right-click this program")
    print("   • Select 'Run as Administrator'")
    print("   • Try installation again")
    print()
    print("2. 🌐 CHECK INTERNET & FIREWALL:")
    print("   • Ensure stable internet connection")
    print("   • Temporarily disable antivirus/firewall")
    print("   • Try from a different network")
    print()
    print("3. 📦 MANUAL PIP UPGRADE:")
    print("   • Open Command Prompt as Administrator")
    print("   • Run: python -m pip install --upgrade pip")
    print("   • Then run this installer again")
    print()
    print("4. 🔧 ALTERNATIVE INSTALLATION:")
    print("   • Install Anaconda Python instead")
    print("   • Many packages come pre-installed")
    print("   • Download from: https://anaconda.com")
    print()
    print("5. 💻 SYSTEM-SPECIFIC:")
    print("   • Windows: Enable 'Developer Mode' in Settings")
    print("   • Check Windows Defender exclusions")
    print("   • Ensure PATH is set correctly for Python")

def install_essential_packages():
    """Install the most essential packages"""
    print("📦 Installing essential packages...")
    
    # Core packages needed for the application
    essential_packages = {
        'requests': 'requests',
        'beautifulsoup4': 'bs4', 
        'pandas': 'pandas',
        'tkinter': 'tkinter'  # Should be built-in
    }
    
    # Optional but important packages
    optional_packages = {
        'fake-useragent': 'fake_useragent',
        'cloudscraper': 'cloudscraper',
        'scikit-learn': 'sklearn',
        'nltk': 'nltk',
        'jsonlines': 'jsonlines',
        'tabulate': 'tabulate',
        'python-dateutil': 'dateutil',
        'pytz': 'pytz'
    }
    
    essential_success = 0
    optional_success = 0
    
    # Install essential packages
    for package, import_name in essential_packages.items():
        if install_package_robust(package, import_name):
            essential_success += 1
    
    # Install optional packages
    for package, import_name in optional_packages.items():
        if install_package_robust(package, import_name):
            optional_success += 1
    
    print(f"\n📊 Installation Results:")
    print(f"   Essential packages: {essential_success}/{len(essential_packages)} installed")
    print(f"   Optional packages: {optional_success}/{len(optional_packages)} installed")
    
    # Determine if we can run the application
    can_run = essential_success >= 3  # Need at least requests, bs4, pandas, tkinter
    
    if can_run:
        print("✅ Sufficient packages installed - application should work!")
    else:
        print("⚠️ Critical packages missing - application may not work properly")
    
    return can_run

def create_offline_package():
    """Create an offline package information file"""
    offline_info = """
# Job Finder Pro - Offline Package Information

If online installation fails, you can create an offline package:

1. On a computer with internet:
   pip download -r requirements.txt -d offline_packages

2. Copy the offline_packages folder to this computer

3. Install offline:
   pip install --find-links offline_packages -r requirements.txt --no-index

This allows installation without internet connectivity.
"""
    
    try:
        with open("OFFLINE_INSTALLATION.txt", "w") as f:
            f.write(offline_info)
        print("📄 Created OFFLINE_INSTALLATION.txt with offline setup instructions")
    except:
        pass

def main():
    """Main installer function"""
    print_header()
    
    try:
        # Check Python version
        version = sys.version_info
        if version.major == 3 and version.minor >= 8:
            print(f"✓ Python {version.major}.{version.minor}.{version.micro} - Compatible")
        else:
            print(f"❌ Python {version.major}.{version.minor}.{version.micro} - May not work properly")
        
        # Check admin rights
        if check_admin_rights():
            print("✓ Running with Administrator privileges")
        else:
            print("⚠️ Not running as Administrator (may cause permission issues)")
        
        # Check internet
        if not check_internet():
            print("❌ Cannot continue without internet connection")
            input("Press Enter to exit...")
            return
        
        # Fix pip issues
        fix_pip()
        
        # Try requirements.txt first
        if not install_from_requirements():
            # Install packages individually
            success = install_essential_packages()
        else:
            success = True
        
        # Setup NLTK data if possible
        try:
            import nltk
            print("📚 Setting up language data...")
            nltk.download('stopwords', quiet=True)
            nltk.download('punkt', quiet=True)
            print("✓ Language data ready")
        except:
            print("⚠️ Could not setup language data")
        
        # Create offline package info
        create_offline_package()
        
        if success:
            print("\n" + "=" * 70)
            print("✅ INSTALLATION COMPLETED!")
            print("=" * 70)
            
            # Try to launch the application
            launch = input("\n🚀 Launch Job Finder Pro now? (Y/n): ").strip().lower()
            if launch != 'n':
                try:
                    app_file = Path(__file__).parent / "job_finder_gui.py"
                    if app_file.exists():
                        subprocess.Popen([sys.executable, str(app_file)])
                        print("✓ Application launched!")
                    else:
                        print("❌ Application file not found")
                except Exception as e:
                    print(f"❌ Could not launch application: {e}")
        else:
            suggest_solutions()
    
    except KeyboardInterrupt:
        print("\n\n👋 Installation cancelled by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        suggest_solutions()
    finally:
        input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()