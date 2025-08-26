@echo off
title Job Finder Pro - One-Click Launcher
color 0A

echo.
echo  ╔══════════════════════════════════════════════════════════════╗
echo  ║                    JOB FINDER PRO                           ║
echo  ║              One-Click Job Search Tool                      ║
echo  ╚══════════════════════════════════════════════════════════════╝
echo.
echo  🎯 Automated job search across LinkedIn, Glassdoor, and more!
echo  📊 AI-powered resume matching with Excel output
echo  🇵🇱 Optimized for Polish job market
echo.

REM Check for Python and run the portable launcher
echo  🔍 Starting Job Finder Pro...
echo.

REM Try Python commands in order of preference
python portable_launcher.py 2>nul
if %errorlevel% equ 0 goto :success

python3 portable_launcher.py 2>nul  
if %errorlevel% equ 0 goto :success

py portable_launcher.py 2>nul
if %errorlevel% equ 0 goto :success

REM If none work, show Python installation guide
echo  ❌ Python not found on this computer
echo.
echo  📥 To use Job Finder Pro, you need Python installed.
echo.
echo  🔧 EASY SETUP (one-time only):
echo     1. Go to: https://python.org/downloads
echo     2. Download Python 3.8 or later
echo     3. During installation, CHECK "Add Python to PATH"  
echo     4. Restart this program
echo.
echo  💡 Alternative: Use UNIVERSAL_INSTALLER.bat for automatic setup
echo.

set /p open_python="Open Python download page now? (Y/n): "
if /i not "%open_python%"=="n" (
    start https://python.org/downloads/windows/
)

goto :end

:success
echo.
echo  ✅ Job Finder Pro session completed!
echo.

:end
echo  👋 Thank you for using Job Finder Pro!
echo     For questions, see USER_MANUAL.md
echo.
pause