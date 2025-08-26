#!/usr/bin/env python3
"""
Create distribution package for Job Finder Pro 2.0 Enhanced Version
"""

import os
import zipfile
import shutil
from datetime import datetime
import sys

def create_distribution():
    """Create a complete distribution package for the enhanced Job Finder"""
    
    # Define the version and package name
    version = "2.0"
    date_stamp = datetime.now().strftime("%Y%m%d")
    package_name = f"JobFinderPro_v{version}_Enhanced_{date_stamp}"
    
    # Create temporary directory for the package
    temp_dir = f"/tmp/{package_name}"
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    os.makedirs(temp_dir)
    
    print(f"Creating distribution package: {package_name}")
    
    # Define files to include
    files_to_copy = {
        # Main application files
        "job_search_automation/job_finder_improved.py": "job_finder_improved.py",
        "job_search_automation/job_finder_gui.py": "job_finder_gui.py",  # Include original for compatibility
        "job_search_automation/main.py": "main.py",
        "job_search_automation/run_improved_job_finder.py": "run_improved_job_finder.py",
        "job_search_automation/JobFinderPro_Enhanced.bat": "JobFinderPro_Enhanced.bat",
        
        # Configuration
        "job_search_automation/config/settings.py": "config/settings.py",
        
        # Matchers
        "job_search_automation/matchers/job_matcher.py": "matchers/job_matcher.py",
        "job_search_automation/matchers/enhanced_job_matcher.py": "matchers/enhanced_job_matcher.py",
        
        # Scrapers
        "job_search_automation/scrapers/base_scraper.py": "scrapers/base_scraper.py",
        "job_search_automation/scrapers/linkedin_scraper.py": "scrapers/linkedin_scraper.py",
        "job_search_automation/scrapers/linkedin_luminati_scraper.py": "scrapers/linkedin_luminati_scraper.py",
        "job_search_automation/scrapers/glassdoor_scraper.py": "scrapers/glassdoor_scraper.py",
        "job_search_automation/scrapers/pracuj_scraper.py": "scrapers/pracuj_scraper.py",
        "job_search_automation/scrapers/google_jobs_scraper.py": "scrapers/google_jobs_scraper.py",
        
        # Utilities
        "job_search_automation/utils/resume_parser.py": "utils/resume_parser.py",
        "job_search_automation/utils/location_manager.py": "utils/location_manager.py",
        
        # Output managers
        "job_search_automation/outputs/output_manager.py": "outputs/output_manager.py",
        
        # Requirements
        "job_search_automation/requirements.txt": "requirements.txt",
        
        # Documentation
        "IMPROVED_JOB_FINDER_README.md": "README.md",
    }
    
    # Copy all files
    for source, dest in files_to_copy.items():
        source_path = f"/workspaces/job-finder/{source}"
        dest_path = os.path.join(temp_dir, dest)
        
        # Create directory if needed
        dest_dir = os.path.dirname(dest_path)
        if dest_dir and not os.path.exists(dest_dir):
            os.makedirs(dest_dir)
        
        # Copy file
        if os.path.exists(source_path):
            shutil.copy2(source_path, dest_path)
            print(f"  Added: {dest}")
        else:
            print(f"  Warning: {source} not found")
    
    # Create __init__.py files for packages
    init_dirs = ["", "config", "matchers", "scrapers", "utils", "outputs"]
    for dir_name in init_dirs:
        init_path = os.path.join(temp_dir, dir_name, "__init__.py")
        if dir_name and not os.path.exists(os.path.dirname(init_path)):
            os.makedirs(os.path.dirname(init_path))
        with open(init_path, 'w') as f:
            f.write("")
    
    # Create an enhanced requirements.txt
    requirements_content = """# Job Finder Pro 2.0 Enhanced - Requirements
requests>=2.28.0
beautifulsoup4>=4.11.0
selenium>=4.8.0
pandas>=1.5.0
openpyxl>=3.0.0
python-dateutil>=2.8.0
pytz>=2022.7
nltk>=3.8.0
scikit-learn>=1.2.0
numpy>=1.23.0
lxml>=4.9.0
"""
    
    with open(os.path.join(temp_dir, "requirements.txt"), 'w') as f:
        f.write(requirements_content)
    
    # Create a sample resume file
    sample_resume = """# John Doe
## Software Engineer

### Contact
- Email: john.doe@email.com
- Location: Warsaw, Poland
- LinkedIn: linkedin.com/in/johndoe

### Summary
Experienced Software Engineer with 5 years of experience in full-stack development. 
Specialized in Python, JavaScript, and cloud technologies.

### Skills
- Programming: Python, JavaScript, TypeScript, Java, SQL
- Frameworks: Django, React, Node.js, Express, Flask
- Databases: PostgreSQL, MongoDB, Redis, MySQL
- Cloud: AWS, Docker, Kubernetes, CI/CD
- Tools: Git, JIRA, Jenkins, Terraform

### Experience

#### Senior Software Engineer | Tech Corp | 2021-Present
- Developed microservices architecture using Python and Docker
- Led team of 4 developers in agile environment
- Implemented CI/CD pipelines reducing deployment time by 60%

#### Software Engineer | StartupXYZ | 2019-2021
- Built RESTful APIs using Django and PostgreSQL
- Developed React-based frontend applications
- Collaborated with cross-functional teams

### Education
- Master's in Computer Science | Warsaw University | 2019
- Bachelor's in Computer Engineering | Krakow Tech | 2017

### Certifications
- AWS Certified Solutions Architect
- Certified Kubernetes Administrator
"""
    
    with open(os.path.join(temp_dir, "sample_resume.txt"), 'w') as f:
        f.write(sample_resume)
    
    # Create QUICK_START.txt
    quick_start = """========================================
Job Finder Pro 2.0 - Enhanced Version
QUICK START GUIDE
========================================

WINDOWS USERS:
1. Double-click "JobFinderPro_Enhanced.bat"
2. The application will install dependencies and start

MANUAL START:
1. Install Python 3.7 or higher
2. Run: pip install -r requirements.txt
3. Run: python run_improved_job_finder.py

FIRST TIME USE:
1. Paste or load your resume
2. Enter your location
3. Select experience level
4. Choose time range for job postings
5. Enter your key skills (important!)
6. Click "Start Job Search"

The enhanced version uses:
- 60% weight from resume content
- 40% weight from user-provided data
- 50% minimum match threshold
- Results sorted by match percentage

For full documentation, see README.md
========================================
"""
    
    with open(os.path.join(temp_dir, "QUICK_START.txt"), 'w') as f:
        f.write(quick_start)
    
    # Create installation script for Windows
    install_script = """@echo off
title Job Finder Pro 2.0 - Enhanced Installation
color 0A

echo ============================================
echo    Installing Job Finder Pro 2.0 Enhanced
echo ============================================
echo.

REM Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed
    echo Please install Python 3.7+ from python.org
    pause
    exit /b 1
)

REM Install requirements
echo Installing required packages...
pip install -r requirements.txt

REM Download NLTK data
echo Downloading language data...
python -c "import nltk; nltk.download('stopwords'); nltk.download('punkt')"

echo.
echo ============================================
echo    Installation Complete!
echo    Run JobFinderPro_Enhanced.bat to start
echo ============================================
pause
"""
    
    with open(os.path.join(temp_dir, "INSTALL.bat"), 'w') as f:
        f.write(install_script)
    
    # Create the ZIP file
    zip_path = f"/workspaces/job-finder/{package_name}.zip"
    
    print(f"\nCreating ZIP file: {package_name}.zip")
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(temp_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, os.path.dirname(temp_dir))
                zipf.write(file_path, arcname)
                print(f"  Compressed: {arcname}")
    
    # Clean up temporary directory
    shutil.rmtree(temp_dir)
    
    # Get file size
    file_size = os.path.getsize(zip_path)
    file_size_mb = file_size / (1024 * 1024)
    
    print(f"\n{'='*50}")
    print(f"✅ Distribution package created successfully!")
    print(f"📦 Package: {package_name}.zip")
    print(f"📊 Size: {file_size_mb:.2f} MB")
    print(f"📁 Location: {zip_path}")
    print(f"{'='*50}")
    
    return zip_path

if __name__ == "__main__":
    create_distribution()