"""
build_desktop.py
----------------
Script to build standalone executables for the Frequency Table Generator
desktop application using PyInstaller.

Usage:
    python build_desktop.py

This will create executables in the 'dist' folder:
- Windows: FrequencyTableGenerator.exe
- Linux: FrequencyTableGenerator (binary)
"""
import sys
import platform
import subprocess
from pathlib import Path

def build_executable():
    """Build the executable using PyInstaller."""
    
    # Determine the executable name based on platform
    system = platform.system()
    if system == "Windows":
        exe_name = "FrequencyTableGenerator.exe"
        icon_option = []  # Add --icon=icon.ico if you have an icon file
    else:
        exe_name = "FrequencyTableGenerator"
        icon_option = []
    
    # PyInstaller command
    cmd = [
        "pyinstaller",
        "--name=FrequencyTableGenerator",
        "--onefile",  # Create a single executable file
        "--windowed",  # Don't show console window (GUI app)
        "--clean",  # Clean cache before building
        
        # Add hidden imports that PyInstaller might miss
        "--hidden-import=pandas",
        "--hidden-import=numpy",
        "--hidden-import=pyreadstat",
        "--hidden-import=xlsxwriter",
        "--hidden-import=openpyxl",
        "--hidden-import=PySide6",
        
        # Collect all necessary data files
        "--collect-all=pyreadstat",
        "--collect-all=PySide6",
        
        # Entry point
        "gui_app.py"
    ]
    
    if icon_option:
        cmd.extend(icon_option)
    
    print(f"Building executable for {system}...")
    print(f"Command: {' '.join(cmd)}")
    print()
    
    try:
        subprocess.run(cmd, check=True)
        print("\n" + "="*60)
        print("✓ Build successful!")
        print(f"✓ Executable location: dist/{exe_name}")
        print("="*60)
        print("\nYou can now distribute the executable to users.")
        print("They don't need Python or any dependencies installed!")
        
    except subprocess.CalledProcessError as e:
        print(f"\n✗ Build failed with error: {e}")
        sys.exit(1)
    except FileNotFoundError:
        print("\n✗ PyInstaller not found!")
        print("Install it with: pip install pyinstaller")
        sys.exit(1)


if __name__ == "__main__":
    # Check if we're in the right directory
    if not Path("gui_app.py").exists():
        print("Error: gui_app.py not found in current directory!")
        print("Please run this script from the webapp directory.")
        sys.exit(1)
    
    if not Path("core.py").exists():
        print("Error: core.py not found in current directory!")
        print("Please run this script from the webapp directory.")
        sys.exit(1)
    
    build_executable()
