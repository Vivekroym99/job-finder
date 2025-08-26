#!/usr/bin/env python3
"""
Build script to create Windows executable for Job Finder Pro
This script uses PyInstaller to create a standalone Windows application
"""

import os
import sys
import subprocess
from pathlib import Path

def install_pyinstaller():
    """Install PyInstaller if not already installed"""
    try:
        import PyInstaller
        print("✓ PyInstaller is already installed")
    except ImportError:
        print("📦 Installing PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("✓ PyInstaller installed successfully")

def create_spec_file():
    """Create PyInstaller spec file for the application"""
    spec_content = '''
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['job_finder_gui.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('config', 'config'),
        ('scrapers', 'scrapers'),
        ('matchers', 'matchers'),
        ('utils', 'utils'),
        ('outputs', 'outputs'),
        ('requirements.txt', '.'),
    ],
    hiddenimports=[
        'tkinter',
        'tkinter.ttk',
        'tkinter.filedialog',
        'tkinter.messagebox',
        'tkinter.scrolledtext',
        'requests',
        'beautifulsoup4',
        'pandas',
        'fake_useragent',
        'cloudscraper',
        'scikit-learn',
        'nltk',
        'jsonlines',
        'tabulate',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='JobFinderPro',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico'  # Add icon if available
)
'''
    
    with open('JobFinderPro.spec', 'w') as f:
        f.write(spec_content)
    
    print("✓ Spec file created: JobFinderPro.spec")

def build_executable():
    """Build the Windows executable"""
    print("🔨 Building Windows executable...")
    
    try:
        # Build using the spec file
        result = subprocess.run([
            sys.executable, "-m", "PyInstaller", 
            "--clean", 
            "JobFinderPro.spec"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✓ Build completed successfully!")
            print("📁 Executable created: dist/JobFinderPro.exe")
            return True
        else:
            print("❌ Build failed!")
            print("Error output:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Build error: {str(e)}")
        return False

def create_installer_script():
    """Create a simple installer script"""
    installer_content = '''@echo off
echo Job Finder Pro - Installation Script
echo ====================================
echo.

REM Create installation directory
set INSTALL_DIR=%USERPROFILE%\\Desktop\\JobFinderPro
echo Creating installation directory: %INSTALL_DIR%
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"

REM Copy executable
echo Copying Job Finder Pro...
copy /Y JobFinderPro.exe "%INSTALL_DIR%\\"

REM Create shortcut on desktop
echo Creating desktop shortcut...
set SHORTCUT=%USERPROFILE%\\Desktop\\Job Finder Pro.lnk
powershell "$s=(New-Object -COM WScript.Shell).CreateShortcut('%SHORTCUT%'); $s.TargetPath='%INSTALL_DIR%\\JobFinderPro.exe'; $s.Save()"

REM Create start menu entry
echo Creating start menu entry...
set STARTMENU=%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs
if not exist "%STARTMENU%\\Job Finder Pro" mkdir "%STARTMENU%\\Job Finder Pro"
powershell "$s=(New-Object -COM WScript.Shell).CreateShortcut('%STARTMENU%\\Job Finder Pro\\Job Finder Pro.lnk'); $s.TargetPath='%INSTALL_DIR%\\JobFinderPro.exe'; $s.Save()"

echo.
echo ✓ Installation completed!
echo ✓ Desktop shortcut created
echo ✓ Start menu entry created
echo.
echo You can now run Job Finder Pro from:
echo - Desktop shortcut
echo - Start menu ^> Job Finder Pro
echo - %INSTALL_DIR%\\JobFinderPro.exe
echo.
pause
'''
    
    with open('install.bat', 'w') as f:
        f.write(installer_content)
    
    print("✓ Installer script created: install.bat")

def create_readme():
    """Create README for Windows distribution"""
    readme_content = '''# Job Finder Pro - Windows Application

## What is Job Finder Pro?

Job Finder Pro is an automated job search tool that scans multiple job platforms (LinkedIn, Glassdoor, Pracuj.pl, Google Jobs) and finds jobs that match your resume using AI-powered analysis.

## Features

✅ **Multi-Platform Search**: Searches 4 major job platforms simultaneously
✅ **AI Resume Matching**: Analyzes your resume and matches relevant jobs
✅ **Smart Location Search**: Covers all major Polish cities + remote options
✅ **Excel Output**: Generates easy-to-read spreadsheet with job matches
✅ **Advanced LinkedIn Scraping**: Uses enterprise-grade scraping techniques
✅ **Customizable Settings**: Filter by location, match percentage, and job age

## Installation

### Option 1: Simple Installation
1. Run `install.bat` as Administrator
2. This will install Job Finder Pro to your Desktop and create shortcuts

### Option 2: Manual Installation  
1. Copy `JobFinderPro.exe` to any folder
2. Double-click to run

## How to Use

1. **Launch the Application**
   - Double-click the desktop shortcut, or
   - Run from Start Menu > Job Finder Pro

2. **Enter Your Resume**
   - Click "Paste Resume Text" and paste your resume, or
   - Click "Load from File" to load a resume file

3. **Configure Search Settings**
   - Select your preferred location (Poland, Warsaw, Krakow, etc.)
   - Set minimum match percentage (70% recommended)
   - Choose max job age (14 days recommended)
   - Enable/disable remote jobs

4. **Start Job Search**
   - Click "🚀 Start Job Search"
   - Wait for the search to complete (usually 2-5 minutes)
   - View results in the generated Excel file

5. **View Results**
   - Click "📁 Open Results Folder" to see generated files
   - Open `job_matches.csv` in Excel to view matching jobs
   - Each job includes: match percentage, title, company, platform, URL

## Output Files

- **job_matches.csv**: Excel-compatible spreadsheet with job matches
- **job_matches.jsonl**: Detailed JSON data for advanced users
- **job_search_audit.log**: Search activity log for troubleshooting

## System Requirements

- Windows 10 or 11
- Internet connection
- 2GB RAM minimum
- 500MB free disk space

## Troubleshooting

**Problem**: Application won't start
**Solution**: Install Microsoft Visual C++ Redistributable

**Problem**: No jobs found
**Solution**: 
- Check your internet connection
- Try lowering the minimum match percentage
- Ensure your resume has relevant keywords

**Problem**: LinkedIn scraping blocked
**Solution**: Use the "Basic LinkedIn Scraper" option in settings

## Advanced Features

- **Dynamic Location Search**: Automatically searches multiple cities for maximum coverage
- **Smart Matching Algorithm**: Uses AI to score job relevance based on skills and experience  
- **Anti-Detection**: Advanced techniques to avoid scraping blocks
- **Automatic Fallback**: If one method fails, others continue working

## Support

For issues or questions:
1. Check the search log in the "Search Results" tab
2. Review the audit log file for detailed error information
3. Try different search settings or resume formatting

---

**Job Finder Pro** - Making job hunting easier and more efficient!
'''
    
    with open('README.txt', 'w') as f:
        f.write(readme_content)
    
    print("✓ README created: README.txt")

def create_icon():
    """Create a simple icon for the application (placeholder)"""
    # This is a placeholder - in production, you'd want a proper .ico file
    print("💡 Note: Add icon.ico file to the directory for a custom application icon")

def main():
    """Main build process"""
    print("🚀 Job Finder Pro - Windows Build Script")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists('job_finder_gui.py'):
        print("❌ Error: job_finder_gui.py not found!")
        print("Please run this script from the job_search_automation directory")
        return
    
    # Install PyInstaller
    install_pyinstaller()
    
    # Create spec file
    create_spec_file()
    
    # Build executable
    if build_executable():
        # Create additional files
        create_installer_script()
        create_readme()
        create_icon()
        
        print("\n" + "=" * 50)
        print("🎉 BUILD COMPLETED SUCCESSFULLY!")
        print("=" * 50)
        print("\n📁 Files created:")
        print("   • dist/JobFinderPro.exe - Main application")
        print("   • install.bat - Installation script")
        print("   • README.txt - User documentation")
        
        print("\n🚀 To distribute:")
        print("   1. Copy dist/JobFinderPro.exe to a folder")
        print("   2. Copy install.bat and README.txt to the same folder")
        print("   3. Share the folder with users")
        
        print("\n💡 Users can:")
        print("   • Run install.bat for easy installation")
        print("   • Or just double-click JobFinderPro.exe to run")
        
    else:
        print("\n❌ Build failed! Check the error messages above.")

if __name__ == "__main__":
    main()