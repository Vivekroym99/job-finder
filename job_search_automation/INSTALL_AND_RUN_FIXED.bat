@echo off
title Job Finder Pro - Installation and Setup
chcp 65001 >nul 2>&1

echo.
echo ============================================
echo    JOB FINDER PRO - INSTALLATION WIZARD
echo ============================================
echo.
echo This will install and run Job Finder Pro
echo.

REM Try multiple Python commands
set PYTHON_CMD=
echo 🔍 Checking for Python...

REM Check python command
python --version >nul 2>&1
if %errorlevel% equ 0 (
    set PYTHON_CMD=python
    goto :python_found
)

REM Check python3 command
python3 --version >nul 2>&1
if %errorlevel% equ 0 (
    set PYTHON_CMD=python3
    goto :python_found
)

REM Check py launcher
py --version >nul 2>&1
if %errorlevel% equ 0 (
    set PYTHON_CMD=py
    goto :python_found
)

REM Python not found
goto :python_not_found

:python_found
echo ✓ Python found
%PYTHON_CMD% --version
echo.
goto :install_packages

:python_not_found
echo ❌ Python not found!
echo.
echo Python is required to run Job Finder Pro
echo.
echo Please choose an option:
echo [1] Download and install Python automatically
echo [2] Open Python download page manually  
echo [3] Exit and install Python yourself
echo.
set /p choice="Enter your choice (1, 2, or 3): "

if "%choice%"=="1" goto :auto_install_python
if "%choice%"=="2" goto :manual_install_python
if "%choice%"=="3" goto :exit_script
goto :python_not_found

:auto_install_python
echo.
echo 📥 Downloading Python installer...
echo This may take a few minutes...

REM Create temp directory
set TEMP_DIR=%TEMP%\JobFinderProInstall
if not exist "%TEMP_DIR%" mkdir "%TEMP_DIR%"

REM Download Python installer using PowerShell
echo Downloading Python 3.11 installer...
powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe' -OutFile '%TEMP_DIR%\python-installer.exe'}"

if not exist "%TEMP_DIR%\python-installer.exe" (
    echo ❌ Download failed. Please install Python manually.
    goto :manual_install_python
)

echo.
echo 🔧 Installing Python...
echo Please wait while Python is installed...

REM Run Python installer silently
"%TEMP_DIR%\python-installer.exe" /quiet InstallAllUsers=0 PrependPath=1 Include_test=0

REM Wait for installation to complete
timeout /t 30 /nobreak >nul

REM Clean up
del "%TEMP_DIR%\python-installer.exe" 2>nul
rmdir "%TEMP_DIR%" 2>nul

echo.
echo 🔄 Refreshing environment...
REM Refresh PATH
call refreshenv 2>nul

echo.
echo 🔍 Checking Python installation...

REM Check again for Python
python --version >nul 2>&1
if %errorlevel% equ 0 (
    set PYTHON_CMD=python
    echo ✓ Python installed successfully!
    python --version
    goto :install_packages
)

py --version >nul 2>&1
if %errorlevel% equ 0 (
    set PYTHON_CMD=py
    echo ✓ Python installed successfully!
    py --version
    goto :install_packages
)

echo ❌ Python installation may not be complete.
echo Please restart this script or install Python manually.
goto :manual_install_python

:manual_install_python
echo.
echo 🌐 Opening Python download page...
start https://www.python.org/downloads/windows/
echo.
echo Please:
echo 1. Download Python 3.8 or later
echo 2. Run the installer
echo 3. ✅ CHECK "Add Python to PATH" during installation
echo 4. Restart this script after installation
echo.
pause
goto :exit_script

:install_packages
echo.
echo 📦 Installing required packages...
echo This may take a few minutes...

REM Upgrade pip first
echo Upgrading package installer...
%PYTHON_CMD% -m pip install --upgrade pip --quiet

REM Install packages one by one with better error handling
echo Installing core packages...

set PACKAGES=requests beautifulsoup4 pandas fake-useragent cloudscraper scikit-learn nltk jsonlines tabulate python-dateutil pytz lxml urllib3 undetected-chromedriver

for %%p in (%PACKAGES%) do (
    echo   Installing %%p...
    %PYTHON_CMD% -m pip install %%p --quiet
    if errorlevel 1 (
        echo   ⚠️ Failed to install %%p, trying alternative...
        %PYTHON_CMD% -m pip install %%p --user --quiet
    )
)

REM Try to install from requirements.txt if it exists
if exist requirements.txt (
    echo Installing from requirements.txt...
    %PYTHON_CMD% -m pip install -r requirements.txt --quiet
)

echo ✓ Package installation completed

REM Setup NLTK data
echo.
echo 🧠 Setting up language processing data...
%PYTHON_CMD% -c "import nltk; nltk.download('stopwords', quiet=True); nltk.download('punkt', quiet=True)" 2>nul
echo ✓ Language data ready

REM Create desktop shortcut
echo.
echo 🔗 Creating desktop shortcut...
set SHORTCUT=%USERPROFILE%\Desktop\Job Finder Pro.lnk
set TARGET=%~dp0JobFinderPro.bat
powershell -Command "& {$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%SHORTCUT%'); $Shortcut.TargetPath = '%TARGET%'; $Shortcut.WorkingDirectory = '%~dp0'; $Shortcut.Save()}" 2>nul
if exist "%SHORTCUT%" (
    echo ✓ Desktop shortcut created
) else (
    echo ⚠️ Could not create desktop shortcut
)

REM Create results folder
echo.
echo 📁 Creating results folder...
set RESULTS_DIR=%USERPROFILE%\Desktop\JobSearchResults
if not exist "%RESULTS_DIR%" mkdir "%RESULTS_DIR%"
echo ✓ Results folder: %RESULTS_DIR%

echo.
echo ============================================
echo    ✅ INSTALLATION COMPLETE!
echo ============================================
echo.
echo 🎉 Job Finder Pro is ready to use!
echo.
echo 🚀 Starting the application...
echo.

REM Launch the application
if exist job_finder_gui.py (
    echo Launching GUI application...
    start "" %PYTHON_CMD% job_finder_gui.py
) else if exist run_job_finder_gui.py (
    echo Launching via launcher...
    start "" %PYTHON_CMD% run_job_finder_gui.py
) else if exist JobFinderPro.bat (
    echo Launching via batch file...
    start "" JobFinderPro.bat
) else (
    echo ❌ Could not find application files
    echo Please ensure you're running this from the correct directory
)

echo.
echo 💡 Tips for using Job Finder Pro:
echo   • Paste your complete resume text
echo   • Start with "Poland" location for best coverage
echo   • Use 70%% minimum match for quality results
echo   • Check the Desktop\JobSearchResults folder for output
echo.
echo 📚 See USER_MANUAL.md for detailed instructions
echo.

:exit_script
echo.
pause