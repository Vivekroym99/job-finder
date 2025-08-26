@echo off
title Job Finder Pro 2.0 - Fixed Version
color 0A

echo ============================================
echo    Job Finder Pro 2.0 - Fixed Version
echo    All Issues Resolved!
echo ============================================
echo.
echo Fixed Issues:
echo ✓ Skills input section now visible
echo ✓ JobSearchAutomation import error resolved
echo ✓ Enhanced matching algorithm working
echo ✓ Better error handling
echo ✓ All UI components functional
echo.

REM Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed
    echo Please install Python 3.7+ from python.org
    pause
    exit /b 1
)

echo Installing/updating dependencies...
pip install --quiet requests beautifulsoup4 nltk scikit-learn numpy python-dateutil pytz

echo.
echo Starting Job Finder Pro 2.0 (Fixed Version)...
echo.

python run_fixed_version.py

if %errorlevel% neq 0 (
    echo.
    echo ERROR: Application failed to start
    pause
)

exit /b 0