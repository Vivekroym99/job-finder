@echo off
title Job Finder Pro - Universal Installer
chcp 65001 >nul 2>&1

echo.
echo ============================================
echo    JOB FINDER PRO - UNIVERSAL INSTALLER
echo ============================================
echo.
echo This installer will automatically set up everything you need!
echo.

REM Check for Python first
echo 🔍 Checking for Python...

REM Try different Python commands
python --version >nul 2>&1
if %errorlevel% equ 0 (
    echo ✓ Python found - using Python installer
    echo.
    python installer.py
    goto :end
)

python3 --version >nul 2>&1  
if %errorlevel% equ 0 (
    echo ✓ Python3 found - using Python installer
    echo.
    python3 installer.py
    goto :end
)

py --version >nul 2>&1
if %errorlevel% equ 0 (
    echo ✓ Python launcher found - using Python installer  
    echo.
    py installer.py
    goto :end
)

REM Python not found - download and install it
echo ❌ Python not found!
echo.
echo 📥 Don't worry! I'll download and install Python for you.
echo This will take a few minutes...
echo.

set /p continue="Continue with automatic Python installation? (Y/n): "
if /i "%continue%"=="n" goto :manual_python

echo.
echo 🌐 Downloading Python...
echo Please wait while Python is downloaded and installed...

REM Create temp directory
set TEMP_DIR=%TEMP%\JobFinderProInstall
if not exist "%TEMP_DIR%" mkdir "%TEMP_DIR%"

REM Download Python installer using PowerShell
powershell -Command "Write-Host 'Downloading Python installer...'; [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe' -OutFile '%TEMP_DIR%\python-installer.exe'"

if not exist "%TEMP_DIR%\python-installer.exe" (
    echo ❌ Download failed. Trying alternative method...
    goto :manual_python
)

echo ✓ Download complete
echo.
echo 🔧 Installing Python...
echo This may take 2-3 minutes. Please be patient...

REM Install Python with all required options
"%TEMP_DIR%\python-installer.exe" /quiet InstallAllUsers=0 PrependPath=1 Include_test=0 Include_pip=1 Include_doc=0 Include_tcltk=1

REM Wait for installation
echo Waiting for installation to complete...
timeout /t 45 /nobreak >nul

REM Clean up
del "%TEMP_DIR%\python-installer.exe" 2>nul
rmdir "%TEMP_DIR%" 2>nul

echo.
echo 🔄 Refreshing system environment...

REM Multiple attempts to refresh PATH
set PATH=%PATH%;%LOCALAPPDATA%\Programs\Python\Python311;%LOCALAPPDATA%\Programs\Python\Python311\Scripts
set PATH=%PATH%;%PROGRAMFILES%\Python311;%PROGRAMFILES%\Python311\Scripts

REM Try to run the Python installer now
echo.
echo 🧪 Testing Python installation...

python --version >nul 2>&1
if %errorlevel% equ 0 (
    echo ✓ Python installation successful!
    python --version
    echo.
    echo 🚀 Running Job Finder Pro installer...
    python installer.py
    goto :end
)

py --version >nul 2>&1
if %errorlevel% equ 0 (
    echo ✓ Python installation successful!
    py --version
    echo.
    echo 🚀 Running Job Finder Pro installer...
    py installer.py
    goto :end
)

echo ⚠️ Python installation may need a system restart to complete.
echo.
echo Please:
echo 1. Restart your computer
echo 2. Run this installer again
echo.
pause
goto :end

:manual_python
echo.
echo 🌐 Opening Python download page...
start https://www.python.org/downloads/windows/
echo.
echo Please download and install Python, then run this installer again.
echo.
echo ⚠️ IMPORTANT: When installing Python, make sure to:
echo    ✅ Check "Add Python to PATH"
echo    ✅ Check "Install for all users" (if available)
echo.
echo After installing Python:
echo 1. Restart your computer
echo 2. Run this installer again
echo.
pause
goto :end

:end
echo.
echo 👋 Installer finished. 
echo If you have any issues, try restarting your computer and running this again.
echo.
pause