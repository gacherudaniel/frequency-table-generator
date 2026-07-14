@echo off
REM Quick launcher for development/testing

if not exist "venv-desktop" (
    echo ERROR: Virtual environment not found!
    echo Please run setup_windows.bat first.
    pause
    exit /b 1
)

call venv-desktop\Scripts\activate.bat
python run_desktop.py
