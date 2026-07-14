@echo off
REM Package for distribution on Windows

echo.
echo ============================================================
echo Frequency Table Generator - Package for Distribution
echo ============================================================
echo.

if not exist "dist\FrequencyTableGenerator.exe" (
    echo ERROR: Executable not found!
    echo Please run build_desktop.bat first.
    pause
    exit /b 1
)

set RELEASE_DIR=FrequencyTableGenerator_v1.0_Windows

echo Creating release package: %RELEASE_DIR%
echo.

REM Create release directory
if exist "%RELEASE_DIR%" rmdir /s /q "%RELEASE_DIR%"
mkdir "%RELEASE_DIR%"

REM Copy executable
echo Copying executable...
copy dist\FrequencyTableGenerator.exe "%RELEASE_DIR%\"

REM Copy documentation
echo Copying documentation...
copy USER_GUIDE.md "%RELEASE_DIR%\"

REM Create README for Windows
echo Creating README...
(
echo Frequency Table Generator - Windows
echo ====================================
echo.
echo INSTALLATION
echo ------------
echo No installation required! This is a standalone application.
echo.
echo RUNNING THE APPLICATION
echo -----------------------
echo Simply double-click FrequencyTableGenerator.exe to launch.
echo.
echo FIRST RUN
echo ---------
echo Windows may show a security warning:
echo   "Windows protected your PC"
echo.
echo This is normal for applications without a code signing certificate.
echo To run the application:
echo   1. Click "More info"
echo   2. Click "Run anyway"
echo.
echo The application is safe - it's built from open source Python code.
echo.
echo QUICK START
echo -----------
echo 1. Launch FrequencyTableGenerator.exe
echo 2. Click "Upload Stata Dataset" and select your .dta file
echo 3. Configure weight and filter options
echo 4. Generate frequency tables
echo 5. Export to Excel
echo.
echo For detailed instructions, see USER_GUIDE.md
echo.
echo TROUBLESHOOTING
echo ---------------
echo If the application won't start:
echo - Try running from Command Prompt to see error messages
echo - Make sure you have the Visual C++ Redistributable installed:
echo   https://aka.ms/vs/17/release/vc_redist.x64.exe
echo.
echo SUPPORT
echo -------
echo For issues or questions, contact your system administrator.
echo.
) > "%RELEASE_DIR%\README.txt"

REM Create batch launcher (optional)
echo Creating launcher script...
(
echo @echo off
echo start FrequencyTableGenerator.exe
) > "%RELEASE_DIR%\Launch.bat"

echo.
echo ============================================================
echo Package created successfully!
echo ============================================================
echo.
echo Distribution folder: %RELEASE_DIR%
echo.
echo Files included:
dir /b "%RELEASE_DIR%"
echo.
echo To create a ZIP archive:
echo   1. Right-click the folder
echo   2. Send to ^> Compressed ^(zipped^) folder
echo.
echo Or use 7-Zip/WinRAR to create:
echo   FrequencyTableGenerator_v1.0_Windows.zip
echo.
pause
