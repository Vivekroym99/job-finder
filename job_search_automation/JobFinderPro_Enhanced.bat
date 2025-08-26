@echo off
title Job Finder Pro 2.0 - Enhanced Version
color 0A

echo ============================================
echo    Job Finder Pro 2.0 - Enhanced Version
echo    With Improved UI and Matching Algorithm
echo ============================================
echo.
echo Features:
echo - New UI with detailed input forms
echo - 60%% Resume + 40%% User Data matching
echo - Minimum 50%% match threshold
echo - Results sorted by match percentage
echo - Enhanced skill matching
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.7+ from python.org
    pause
    exit /b 1
)

REM Check and install required packages
echo Checking dependencies...
python -c "import tkinter" >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: tkinter is not available
    echo Please reinstall Python with tkinter support
    pause
    exit /b 1
)

REM Install/upgrade required packages
echo Installing/updating required packages...
pip install --upgrade nltk scikit-learn numpy requests beautifulsoup4 python-dateutil pytz >nul 2>&1

REM Download NLTK data
echo Downloading language data...
python -c "import nltk; nltk.download('stopwords', quiet=True); nltk.download('punkt', quiet=True)" >nul 2>&1

REM Run the improved job finder
echo.
echo Starting Job Finder Pro 2.0...
echo.
python run_improved_job_finder.py

if %errorlevel% neq 0 (
    echo.
    echo ERROR: Failed to start Job Finder Pro 2.0
    echo Please check the error messages above
    pause
)

exit /b 0