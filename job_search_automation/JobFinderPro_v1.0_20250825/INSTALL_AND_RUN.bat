@echo off
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
set SHORTCUT=%USERPROFILE%\Desktop\Job Finder Pro.lnk
set TARGET=%~dp0JobFinderPro.bat
powershell "$s=(New-Object -COM WScript.Shell).CreateShortcut('%SHORTCUT%'); $s.TargetPath='%TARGET%'; $s.WorkingDirectory='%~dp0'; $s.IconLocation='%TARGET%'; $s.Save()" 2>nul

REM Create results folder
echo.
echo 📁 Creating results folder...
set RESULTS_DIR=%USERPROFILE%\Desktop\JobSearchResults
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
