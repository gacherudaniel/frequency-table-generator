#!/usr/bin/env python3
"""
Quick launcher for the desktop application during development.
Use this to test the GUI without building the executable.

Usage:
    python run_desktop.py
    
    or
    
    ./run_desktop.py (Linux/Mac)
"""
import sys
from pathlib import Path

# Add current directory to path to ensure imports work
sys.path.insert(0, str(Path(__file__).parent))

from gui_app import main

if __name__ == "__main__":
    main()
