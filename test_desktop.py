#!/usr/bin/env python3
"""
test_desktop.py
---------------
Simple test script to verify the desktop application dependencies
and core functionality are working correctly.

Run this before building to ensure everything is properly set up.

Usage:
    python test_desktop.py
"""
import sys

def test_imports():
    """Test that all required packages can be imported."""
    print("Testing package imports...")
    
    tests = [
        ("pandas", "Data processing"),
        ("numpy", "Numerical operations"),
        ("pyreadstat", "Stata file reading"),
        ("xlsxwriter", "Excel export"),
        ("openpyxl", "Excel operations"),
        ("PySide6.QtWidgets", "Qt GUI framework"),
        ("PySide6.QtCore", "Qt core"),
        ("PySide6.QtGui", "Qt GUI"),
    ]
    
    failed = []
    for module, description in tests:
        try:
            __import__(module)
            print(f"  ✓ {module:25s} - {description}")
        except ImportError as e:
            print(f"  ✗ {module:25s} - FAILED: {e}")
            failed.append(module)
    
    if failed:
        print(f"\n❌ {len(failed)} import(s) failed!")
        print("Install missing packages with:")
        print("  pip install -r requirements-desktop.txt")
        return False
    else:
        print(f"\n✓ All imports successful!")
        return True


def test_core_functionality():
    """Test basic core.py functions."""
    print("\nTesting core functionality...")
    
    try:
        import core
        print("  ✓ core.py imported successfully")
        
        # Check that key functions exist
        functions = [
            "load_stata_dataset",
            "build_variable_overview",
            "classify_variable",
            "compute_frequency_table",
            "export_to_excel",
            "run_full_pipeline"
        ]
        
        for func_name in functions:
            if hasattr(core, func_name):
                print(f"  ✓ Function '{func_name}' found")
            else:
                print(f"  ✗ Function '{func_name}' NOT found")
                return False
        
        print("\n✓ Core functionality check passed!")
        return True
        
    except Exception as e:
        print(f"  ✗ Error testing core: {e}")
        return False


def test_gui_imports():
    """Test that GUI components can be loaded."""
    print("\nTesting GUI application...")
    
    try:
        # Try importing without running the app
        import gui_app
        print("  ✓ gui_app.py imported successfully")
        
        # Check main components exist
        if hasattr(gui_app, 'MainWindow'):
            print("  ✓ MainWindow class found")
        else:
            print("  ✗ MainWindow class NOT found")
            return False
        
        if hasattr(gui_app, 'ProcessingThread'):
            print("  ✓ ProcessingThread class found")
        else:
            print("  ✗ ProcessingThread class NOT found")
            return False
        
        print("\n✓ GUI application check passed!")
        return True
        
    except Exception as e:
        print(f"  ✗ Error loading GUI: {e}")
        return False


def test_pyinstaller():
    """Test that PyInstaller is available."""
    print("\nTesting PyInstaller availability...")
    
    try:
        import PyInstaller
        print(f"  ✓ PyInstaller version {PyInstaller.__version__} installed")
        return True
    except ImportError:
        print("  ✗ PyInstaller not found")
        print("    Install it with: pip install pyinstaller")
        return False


def main():
    """Run all tests."""
    print("="*60)
    print("Desktop Application Pre-Build Test Suite")
    print("="*60)
    print()
    
    results = []
    
    # Run tests
    results.append(("Package imports", test_imports()))
    results.append(("Core functionality", test_core_functionality()))
    results.append(("GUI application", test_gui_imports()))
    results.append(("PyInstaller", test_pyinstaller()))
    
    # Summary
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    
    for test_name, passed in results:
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{status:12s} - {test_name}")
    
    all_passed = all(result[1] for result in results)
    
    print("="*60)
    
    if all_passed:
        print("\n🎉 All tests passed! You're ready to build the executable.")
        print("\nNext steps:")
        print("  1. Run: python build_desktop.py")
        print("  2. Test the executable in dist/")
        print("  3. Distribute to users!")
        return 0
    else:
        print("\n❌ Some tests failed. Please fix the issues above before building.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
