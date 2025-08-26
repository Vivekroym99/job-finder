#!/usr/bin/env python3
"""
Create distribution package for Job Finder Pro
This creates a complete package that users can download and run
"""

import os
import shutil
import zipfile
from pathlib import Path
from datetime import datetime

def create_distribution():
    """Create a complete distribution package"""
    
    print("📦 Creating Job Finder Pro Distribution Package")
    print("=" * 55)
    
    # Create distribution directory
    dist_name = f"JobFinderPro_v1.0_{datetime.now().strftime('%Y%m%d')}"
    dist_dir = Path(dist_name)
    
    if dist_dir.exists():
        shutil.rmtree(dist_dir)
    
    dist_dir.mkdir()
    
    # Core application files
    core_files = [
        "job_finder_gui.py",
        "run_job_finder_gui.py", 
        "portable_launcher.py",
        "installer.py",
        "JobFinderPro.bat",
        "CLICK_TO_RUN.bat",
        "UNIVERSAL_INSTALLER.bat",
        "main.py",
        "requirements.txt"
    ]
    
    # Core directories
    core_dirs = [
        "config",
        "scrapers", 
        "matchers",
        "utils",
        "outputs"
    ]
    
    # Documentation files
    doc_files = [
        "USER_MANUAL.md",
        "README.md",
        "LINKEDIN_PRIMARY_INTEGRATION.md"
    ]
    
    print("📁 Copying core files...")
    for file in core_files:
        if os.path.exists(file):
            shutil.copy2(file, dist_dir / file)
            print(f"   ✓ {file}")
    
    print("📁 Copying core directories...")
    for dir_name in core_dirs:
        if os.path.exists(dir_name):
            shutil.copytree(dir_name, dist_dir / dir_name)
            print(f"   ✓ {dir_name}/")
    
    print("📁 Copying documentation...")
    for file in doc_files:
        if os.path.exists(file):
            shutil.copy2(file, dist_dir / file)
            print(f"   ✓ {file}")
    
    # Create installation guide
    create_installation_guide(dist_dir)
    
    # Create sample resume
    create_sample_resume(dist_dir)
    
    # Create Windows installation script
    create_windows_installer(dist_dir)
    
    print(f"\n✓ Distribution package created: {dist_dir}/")
    
    # Create ZIP file
    create_zip_package(dist_dir)
    
    print("\n" + "=" * 55)
    print("🎉 DISTRIBUTION PACKAGE READY!")
    print("=" * 55)
    print(f"\n📁 Package directory: {dist_dir}/")
    print(f"📦 ZIP package: {dist_name}.zip")
    
    print(f"\n🚀 Users can:")
    print(f"   1. Download and extract {dist_name}.zip")
    print(f"   2. Double-click 'INSTALL_AND_RUN.bat' to start")
    print(f"   3. Or run 'JobFinderPro.bat' manually")
    
    return dist_dir

def create_installation_guide(dist_dir):
    """Create user-friendly installation guide"""
    guide_content = '''# 🚀 Job Finder Pro - Quick Installation Guide

## What You Need
- Windows 10 or 11
- Internet connection  
- Python 3.8+ (can be installed automatically)

## 🎯 EASIEST WAYS TO START

### Option 1: Super Simple (Recommended)
1. Double-click: **CLICK_TO_RUN.bat**
2. If Python isn't installed, it will guide you
3. The app handles everything else automatically!

### Option 2: Full Auto-Install
1. Double-click: **UNIVERSAL_INSTALLER.bat**  
2. This downloads and installs Python automatically
3. Then launches the application

### Option 3: Python-Based Install
1. If you have Python: double-click **portable_launcher.py**
2. Dependencies install automatically
3. Application launches immediately

## 📋 How to Use

1. **Paste Your Resume**: Click "Paste Resume Text" and add your resume
2. **Choose Location**: Select Poland, Warsaw, Krakow, etc.
3. **Start Search**: Click "🚀 Start Job Search"
4. **Get Results**: Open the Excel file when complete

## 📁 What You Get

- **job_matches.csv** - Excel file with matching jobs
- **job_matches.jsonl** - Detailed data for advanced users
- **job_search_audit.log** - Search activity log

## 🆘 Need Help?

- See **USER_MANUAL.md** for detailed instructions
- Check **README.md** for technical details
- All files are processed locally on your computer (no cloud/servers)

## 🎯 Tips for Best Results

- Include technical skills, tools, and years of experience in resume
- Start with 70% minimum match percentage
- Use "Poland" location for maximum job coverage
- Enable remote jobs for more opportunities

---

**Job Finder Pro** - Your AI-powered job search assistant! 🤖
'''
    
    with open(dist_dir / "INSTALLATION_GUIDE.txt", 'w') as f:
        f.write(guide_content)
    
    print("   ✓ INSTALLATION_GUIDE.txt")

def create_sample_resume(dist_dir):
    """Create a sample resume for testing"""
    sample_resume = '''JOHN KOWALSKI
Warsaw, Poland | +48 123 456 789 | john.kowalski@email.com

EXPERIENCE

Software Engineer
TechCorp Poland | Warsaw, Poland
January 2022 – Present
• Developed web applications using Python, Django, and React
• Collaborated with cross-functional teams on agile projects
• Implemented RESTful APIs and database optimizations
• Reduced application load times by 40% through performance optimization

Junior Developer
StartupXYZ | Krakow, Poland  
June 2020 – December 2021
• Built responsive web interfaces using HTML, CSS, JavaScript
• Worked with PostgreSQL databases and SQL queries
• Participated in code reviews and testing procedures
• Contributed to open-source projects and documentation

EDUCATION

Master's Degree in Computer Science
University of Warsaw | Warsaw, Poland
2018 – 2020

Bachelor's Degree in Information Technology
Jagiellonian University | Krakow, Poland
2014 – 2018

SKILLS

Programming Languages: Python, JavaScript, Java, SQL
Frameworks: Django, React, Node.js, Flask
Databases: PostgreSQL, MySQL, MongoDB
Tools: Git, Docker, Jenkins, VS Code
Languages: Polish (Native), English (Fluent), German (Basic)

CERTIFICATIONS

AWS Certified Developer Associate (2023)
Oracle Certified Java Programmer (2021)
'''
    
    with open(dist_dir / "sample_resume.txt", 'w') as f:
        f.write(sample_resume)
    
    print("   ✓ sample_resume.txt")

def create_windows_installer(dist_dir):
    """Create comprehensive Windows installer"""
    installer_content = '''@echo off
title Job Finder Pro - Installation and Setup

echo.
echo ============================================
echo    JOB FINDER PRO - INSTALLATION WIZARD
echo ============================================
echo.
echo This will install and run Job Finder Pro
echo.

REM Check for admin rights
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️  Note: Running without administrator rights
    echo Some features may require manual installation
    echo.
)

REM Check if Python is installed
echo 🔍 Checking for Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found!
    echo.
    echo 📥 Would you like to download and install Python?
    echo This is required to run Job Finder Pro
    echo.
    set /p install_python="Install Python now? (Y/N): "
    
    if /i "%install_python%"=="Y" (
        echo.
        echo 🌐 Opening Python download page...
        start https://www.python.org/downloads/windows/
        echo.
        echo Please:
        echo 1. Download Python 3.8+ installer
        echo 2. Run installer and CHECK "Add Python to PATH"
        echo 3. Restart this script after installation
        echo.
        pause
        exit /b 0
    ) else (
        echo.
        echo ❌ Cannot continue without Python
        echo Please install Python and run this script again
        pause
        exit /b 1
    )
)

echo ✓ Python found
python --version

REM Install/upgrade pip
echo.
echo 📦 Updating package installer...
python -m pip install --upgrade pip --quiet

REM Install required packages
echo.
echo 📚 Installing required packages...
echo This may take a few minutes...

python -m pip install -r requirements.txt --quiet

if errorlevel 1 (
    echo.
    echo ⚠️  Some packages failed to install
    echo Trying alternative installation...
    python -m pip install requests beautifulsoup4 pandas fake-useragent --quiet
    python -m pip install cloudscraper scikit-learn nltk jsonlines tabulate --quiet
)

REM Setup NLTK data
echo.
echo 🧠 Setting up natural language processing...
python -c "import nltk; nltk.download('stopwords', quiet=True); nltk.download('punkt', quiet=True)" 2>nul

REM Create desktop shortcut
echo.
echo 🔗 Creating desktop shortcut...
set SHORTCUT=%USERPROFILE%\\Desktop\\Job Finder Pro.lnk
set TARGET=%~dp0JobFinderPro.bat
powershell "$s=(New-Object -COM WScript.Shell).CreateShortcut('%SHORTCUT%'); $s.TargetPath='%TARGET%'; $s.WorkingDirectory='%~dp0'; $s.IconLocation='%TARGET%'; $s.Save()" 2>nul

REM Create results folder
echo.
echo 📁 Creating results folder...
set RESULTS_DIR=%USERPROFILE%\\Desktop\\JobSearchResults
if not exist "%RESULTS_DIR%" mkdir "%RESULTS_DIR%"

echo.
echo ============================================
echo    ✅ INSTALLATION COMPLETE!
echo ============================================
echo.
echo 🎉 Job Finder Pro is ready to use!
echo.
echo 🚀 To start the application:
echo    • Double-click the desktop shortcut, or
echo    • Run JobFinderPro.bat from this folder
echo.
echo 📋 Quick Start:
echo    1. Launch Job Finder Pro
echo    2. Paste your resume text
echo    3. Select your location (Poland, Warsaw, etc.)
echo    4. Click "Start Job Search"
echo    5. Wait for results (2-5 minutes)
echo    6. Open the generated Excel file
echo.
echo 💡 Tips:
echo    • Results will be saved to: %RESULTS_DIR%
echo    • See USER_MANUAL.md for detailed instructions
echo    • Use sample_resume.txt as a template
echo.

set /p launch_now="Launch Job Finder Pro now? (Y/N): "
if /i "%launch_now%"=="Y" (
    echo.
    echo 🚀 Launching Job Finder Pro...
    start "" "%~dp0JobFinderPro.bat"
) else (
    echo.
    echo 👋 You can launch Job Finder Pro anytime from the desktop shortcut
)

echo.
pause
'''
    
    with open(dist_dir / "INSTALL_AND_RUN.bat", 'w') as f:
        f.write(installer_content)
    
    print("   ✓ INSTALL_AND_RUN.bat")

def create_zip_package(dist_dir):
    """Create ZIP package for distribution"""
    zip_name = f"{dist_dir.name}.zip"
    
    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(dist_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, dist_dir.parent)
                zipf.write(file_path, arcname)
    
    print(f"   ✓ {zip_name}")
    return zip_name

def main():
    """Main function"""
    try:
        dist_dir = create_distribution()
        
        print(f"\n🎯 NEXT STEPS:")
        print(f"   1. Test the package by running: {dist_dir}/INSTALL_AND_RUN.bat")
        print(f"   2. Share {dist_dir.name}.zip with users")
        print(f"   3. Users extract and run INSTALL_AND_RUN.bat")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error creating distribution: {e}")
        return False

if __name__ == "__main__":
    main()