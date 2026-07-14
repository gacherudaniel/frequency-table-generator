@echo off
REM ============================================================
REM Frequency Table Generator - Windows Setup Script
REM ============================================================

echo.
echo ============================================================
echo Frequency Table Generator - Windows Setup
echo ============================================================
echo.

REM Check Python installation
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH!
    echo.
    echo Please install Python 3.8 or later from:
    echo https://www.python.org/downloads/
    echo.
    echo Make sure to check "Add Python to PATH" during installation.
    pause
    exit /b 1
)

echo Python found:
python --version
echo.

REM Create virtual environment
if exist "venv-desktop" (
    echo Virtual environment already exists.
    choice /C YN /M "Do you want to recreate it"
    if errorlevel 2 goto install_deps
    echo Removing old virtual environment...
    rmdir /s /q venv-desktop
)

echo Creating virtual environment...
python -m venv venv-desktop

if errorlevel 1 (
    echo ERROR: Failed to create virtual environment!
    pause
    exit /b 1
)

:install_deps
echo.
echo Activating virtual environment...
call venv-desktop\Scripts\activate.bat

echo.
echo Installing dependencies...
echo This may take 5-10 minutes (PySide6 is ~200MB)
echo.

pip install --upgrade pip
pip install -r requirements-desktop.txt

if errorlevel 1 (
    echo.
    echo ============================================================
    echo Installation FAILED!
    echo ============================================================
    echo.
    echo Try installing with longer timeout:
    echo   venv-desktop\Scripts\activate.bat
    echo   pip install --default-timeout=1000 -r requirements-desktop.txt
    echo.
    pause
    exit /b 1
)

echo.
echo ============================================================
echo Setup completed successfully!
echo ============================================================
echo.
echo Virtual environment: venv-desktop
echo.
echo Next steps:
echo   1. Test installation: test_desktop.bat
echo   2. Build executable: build_desktop.bat
echo.
pause
