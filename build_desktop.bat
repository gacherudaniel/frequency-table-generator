@echo off
REM ============================================================
REM Frequency Table Generator - Windows Build Script
REM ============================================================

echo.
echo ============================================================
echo Building Frequency Table Generator for Windows
echo ============================================================
echo.

REM Check if virtual environment exists
if not exist "venv-desktop" (
    echo ERROR: Virtual environment not found!
    echo Please run setup_windows.bat first.
    pause
    exit /b 1
)

REM Activate virtual environment
echo Activating virtual environment...
call venv-desktop\Scripts\activate.bat

REM Verify PyInstaller is installed
python -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo ERROR: PyInstaller not found!
    echo Please run: pip install -r requirements-desktop.txt
    pause
    exit /b 1
)

echo.
echo Building executable for Windows...
echo Command: pyinstaller --name=FrequencyTableGenerator --onefile --windowed --clean ^
 --hidden-import=pandas --hidden-import=numpy --hidden-import=pyreadstat ^
 --hidden-import=xlsxwriter --hidden-import=openpyxl --hidden-import=PySide6 ^
 --collect-all=pyreadstat --collect-all=PySide6 gui_app.py
echo.

pyinstaller --name=FrequencyTableGenerator --onefile --windowed --clean ^
 --hidden-import=pandas --hidden-import=numpy --hidden-import=pyreadstat ^
 --hidden-import=xlsxwriter --hidden-import=openpyxl --hidden-import=PySide6 ^
 --collect-all=pyreadstat --collect-all=PySide6 gui_app.py

if errorlevel 1 (
    echo.
    echo ============================================================
    echo Build FAILED!
    echo ============================================================
    pause
    exit /b 1
)

echo.
echo ============================================================
echo Build successful!
echo Executable location: dist\FrequencyTableGenerator.exe
echo ============================================================
echo.
echo You can now distribute the executable to users.
echo They don't need Python or any dependencies installed!
echo.

REM Show file size
if exist "dist\FrequencyTableGenerator.exe" (
    for %%I in (dist\FrequencyTableGenerator.exe) do echo Executable size: %%~zI bytes
)

echo.
echo Next steps:
echo   1. Test: dist\FrequencyTableGenerator.exe
echo   2. Package: run package_for_distribution_windows.bat
echo   3. Distribute to users!
echo.
pause
