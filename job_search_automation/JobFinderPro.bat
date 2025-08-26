@echo off
title Job Finder Pro - LinkedIn Job Search Automation

echo.
echo ========================================
echo    JOB FINDER PRO
echo    LinkedIn Job Search Automation
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo.
    echo Please install Python 3.8+ from: https://python.org/downloads
    echo Make sure to check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)

echo ✓ Python found
echo.

REM Change to script directory
cd /d "%~dp0"

REM Run the launcher
python run_job_finder_gui.py

pause