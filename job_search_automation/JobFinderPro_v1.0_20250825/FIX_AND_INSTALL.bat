@echo off
title Job Finder Pro - Fix and Install
color 0B

echo.
echo  ╔══════════════════════════════════════════════════════════════╗
echo  ║               JOB FINDER PRO - FIX INSTALLER                ║
echo  ║            Solves Common Installation Problems               ║
echo  ╚══════════════════════════════════════════════════════════════╝
echo.
echo  🔧 This installer fixes common pip and package issues
echo  📦 Handles permissions, network, and dependency problems
echo  🚀 Multiple fallback methods for reliable installation
echo.

REM Check if running as administrator
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo  ⚠️  NOTICE: Not running as Administrator
    echo     Some installation methods may fail
    echo     For best results: Right-click this file ^> "Run as Administrator"
    echo.
    set /p continue="Continue anyway? (Y/n): "
    if /i "%continue%"=="n" goto :end
    echo.
)

echo  🔍 Checking for Python...

REM Try different Python commands
python robust_installer.py 2>nul
if %errorlevel% equ 0 goto :success

python3 robust_installer.py 2>nul
if %errorlevel% equ 0 goto :success

py robust_installer.py 2>nul
if %errorlevel% equ 0 goto :success

echo  ❌ Python not found!
echo.
echo  📥 Python is required for Job Finder Pro
echo.
echo  🔧 QUICK SETUP:
echo     1. Download Python from: https://python.org/downloads
echo     2. During installation, CHECK "Add Python to PATH"
echo     3. Restart your computer
echo     4. Run this installer again
echo.

set /p open_python="Open Python download page? (Y/n): "
if /i not "%open_python%"=="n" (
    start https://python.org/downloads/windows/
)

goto :end

:success
echo.
echo  ✅ Installation process completed!
echo.

:end
echo.
echo  💡 Troubleshooting Tips:
echo     • Run as Administrator for best results
echo     • Ensure stable internet connection
echo     • Temporarily disable antivirus during installation
echo     • Try different Python versions if issues persist
echo.
echo  📚 See USER_MANUAL.md for detailed instructions
echo.
pause