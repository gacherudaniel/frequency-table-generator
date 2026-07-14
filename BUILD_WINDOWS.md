# Building for Windows - Complete Guide

## Prerequisites

You need a **Windows computer** with:
- Windows 10 or Windows 11
- Python 3.8 or later installed
- Internet connection for downloading dependencies
- Git (optional, for cloning the repository)

## Quick Start (3 Steps)

### Step 1: Get the Code

**Option A - Using Git:**
```cmd
git clone <your-repository-url>
cd frequency-table-webapp\webapp
```

**Option B - Manual:**
1. Copy the entire `frequency-table-webapp/webapp` folder to your Windows machine
2. Open Command Prompt (cmd.exe)
3. Navigate to the folder:
   ```cmd
   cd path\to\frequency-table-webapp\webapp
   ```

### Step 2: Setup Environment and Install Dependencies

Double-click: **`setup_windows.bat`**

Or from Command Prompt:
```cmd
setup_windows.bat
```

This will:
- Create a virtual environment (`venv-desktop`)
- Install all required packages (pandas, PySide6, PyInstaller, etc.)
- Takes 5-10 minutes (PySide6 is ~200 MB)

**Wait for**: "Setup completed successfully!"

### Step 3: Build the Executable

Double-click: **`build_desktop.bat`**

Or from Command Prompt:
```cmd
build_desktop.bat
```

This will:
- Build the standalone executable
- Takes 2-5 minutes
- Creates: `dist\FrequencyTableGenerator.exe`

**Result**: Your Windows executable is ready at `dist\FrequencyTableGenerator.exe`

---

## Testing the Executable

### Quick Test

Double-click: `dist\FrequencyTableGenerator.exe`

Or from Command Prompt:
```cmd
dist\FrequencyTableGenerator.exe
```

### Full Verification

Run the test suite first:

Double-click: **`test_desktop.bat`**

Or:
```cmd
test_desktop.bat
```

This verifies all imports and functionality before building.

---

## Creating Distribution Package

After building successfully:

Double-click: **`package_for_distribution_windows.bat`**

Or:
```cmd
package_for_distribution_windows.bat
```

This creates:
- Folder: `FrequencyTableGenerator_v1.0_Windows\`
- Contains: `.exe`, documentation, and README

**To create a ZIP file:**
1. Right-click the folder
2. Send to → Compressed (zipped) folder
3. Rename to: `FrequencyTableGenerator_v1.0_Windows.zip`

---

## Distributing to Users

### Simple Method
Send users: `dist\FrequencyTableGenerator.exe` (200-300 MB)

### Professional Method (Recommended)
1. Run `package_for_distribution_windows.bat`
2. Create ZIP file of the package folder
3. Send: `FrequencyTableGenerator_v1.0_Windows.zip`

### What Users Need to Do

**Nothing!** Just:
1. Extract the ZIP (if using packaged version)
2. Double-click `FrequencyTableGenerator.exe`
3. If Windows shows security warning:
   - Click "More info"
   - Click "Run anyway"

**No Python, no installation, no dependencies required!**

---

## Troubleshooting

### Python Not Found

**Error**: `'python' is not recognized as an internal or external command`

**Solution**:
1. Install Python from: https://www.python.org/downloads/
2. **Important**: Check "Add Python to PATH" during installation
3. Restart Command Prompt after installing

### Setup Fails - Network Timeout

**Error**: Timeout while downloading PySide6

**Solution 1** - Increase timeout:
```cmd
venv-desktop\Scripts\activate.bat
pip install --default-timeout=2000 -r requirements-desktop.txt
```

**Solution 2** - Install in stages:
```cmd
venv-desktop\Scripts\activate.bat
pip install --default-timeout=2000 numpy pandas
pip install --default-timeout=2000 PySide6
pip install -r requirements-desktop.txt
```

### Build Fails

**Error**: PyInstaller errors during build

**Solution**:
1. Make sure virtual environment is activated
2. Verify all dependencies installed:
   ```cmd
   venv-desktop\Scripts\activate.bat
   python test_desktop.py
   ```
3. Clean and rebuild:
   ```cmd
   rmdir /s /q build dist
   build_desktop.bat
   ```

### Executable Won't Run

**Error**: Application crashes or won't start

**Solution 1** - Missing Visual C++ Redistributable:
- Download and install: https://aka.ms/vs/17/release/vc_redist.x64.exe

**Solution 2** - Test from Command Prompt (see error messages):
```cmd
cd dist
FrequencyTableGenerator.exe
```

### Windows Defender SmartScreen Warning

**Message**: "Windows protected your PC"

**Explanation**: This is normal for unsigned applications (no code signing certificate)

**Solution**: 
1. Click "More info"
2. Click "Run anyway"

**Note**: Code signing certificates cost $100-400/year. For internal distribution, SmartScreen warnings are acceptable.

---

## File Structure After Build

```
frequency-table-webapp/webapp/
├── setup_windows.bat              ← Run this FIRST
├── build_desktop.bat              ← Then run this
├── test_desktop.bat               ← Optional: verify setup
├── run_desktop.bat                ← Optional: quick test
├── package_for_distribution_windows.bat  ← Create distribution package
│
├── gui_app.py                     ← Desktop application code
├── core.py                        ← Business logic
├── requirements-desktop.txt       ← Dependencies list
│
├── venv-desktop\                  ← Virtual environment (created by setup)
├── build\                         ← Build files (created by build)
└── dist\                          ← Final executable (created by build)
    └── FrequencyTableGenerator.exe  ⭐ THE EXECUTABLE!
```

---

## Development Workflow

### Making Changes

If you modify `gui_app.py` or `core.py`:

1. **Test without rebuilding** (faster):
   ```cmd
   run_desktop.bat
   ```

2. **Rebuild executable** (when ready to distribute):
   ```cmd
   build_desktop.bat
   ```

### Testing Cycle

```cmd
REM 1. Make code changes in gui_app.py

REM 2. Quick test
run_desktop.bat

REM 3. Verify functionality
test_desktop.bat

REM 4. Rebuild when satisfied
build_desktop.bat

REM 5. Test executable
dist\FrequencyTableGenerator.exe
```

---

## Advanced Options

### Custom Icon (Optional)

Add your own icon to the executable:

1. Create or obtain a `.ico` file (e.g., `icon.ico`)
2. Edit `build_desktop.bat`, add to the pyinstaller command:
   ```cmd
   --icon=icon.ico
   ```

### Exclude Unnecessary Modules (Reduce Size)

Edit `build_desktop.bat`, add:
```cmd
--exclude-module=matplotlib --exclude-module=scipy
```

### Create Installer (Optional)

Use tools like:
- **Inno Setup** (free): https://jrsoftware.org/isinfo.php
- **NSIS** (free): https://nsis.sourceforge.io/
- **Advanced Installer** (commercial)

---

## Batch Script Reference

| Script | Purpose | When to Use |
|--------|---------|-------------|
| `setup_windows.bat` | Create venv and install dependencies | Once, at the beginning |
| `test_desktop.bat` | Verify installation | Before building, after changes |
| `run_desktop.bat` | Quick test app during development | While developing |
| `build_desktop.bat` | Build the executable | When ready to distribute |
| `package_for_distribution_windows.bat` | Create distribution package | When ready to share |

---

## Building on Different Windows Versions

### Windows 11
✅ Fully supported - recommended

### Windows 10
✅ Fully supported

### Windows 8.1
⚠️ May work, but Python 3.8+ requires updates
- Install all Windows updates
- Install Visual C++ Redistributable

### Windows 7
❌ Not recommended - Python 3.9+ doesn't officially support Windows 7

---

## Expected Build Times

On a typical Windows machine:

| Task | Time | Notes |
|------|------|-------|
| Python installation | 2-5 min | One-time |
| Virtual environment creation | 30 sec | One-time |
| Dependency installation | 5-10 min | One-time, PySide6 is large |
| First build | 3-5 min | Analyzes all dependencies |
| Subsequent builds | 2-3 min | Uses cached data |

---

## Expected File Sizes

| Item | Size |
|------|------|
| PySide6 package | ~200 MB |
| venv-desktop folder | ~600 MB |
| build folder | ~300 MB |
| Final .exe | 200-300 MB |

**Total disk space needed**: ~1.5 GB during build, ~300 MB for final executable

---

## Security Notes

### Antivirus False Positives

Some antivirus software may flag the executable as suspicious (common with PyInstaller executables).

**Solutions**:
1. Add exception in antivirus
2. Use code signing certificate (eliminates most false positives)
3. Build on the same network/domain as users (establishes trust)

### Code Signing (Optional)

For professional distribution:
- Purchase code signing certificate ($100-400/year)
- Sign the executable with `signtool.exe`
- Eliminates SmartScreen warnings
- Builds user trust

**Providers**:
- DigiCert
- Sectigo
- GlobalSign

---

## Support & Resources

**Documentation Files**:
- `USER_GUIDE.md` - For end users
- `README_DESKTOP.md` - General desktop app info
- `DISTRIBUTION_GUIDE.md` - Distribution strategies

**Online Resources**:
- PySide6 docs: https://doc.qt.io/qtforpython/
- PyInstaller manual: https://pyinstaller.org/
- Python Windows FAQ: https://docs.python.org/3/faq/windows.html

---

## Quick Command Reference

```cmd
REM Setup (run once)
setup_windows.bat

REM Test installation
test_desktop.bat

REM Quick test during development
run_desktop.bat

REM Build executable
build_desktop.bat

REM Test executable
dist\FrequencyTableGenerator.exe

REM Package for distribution
package_for_distribution_windows.bat

REM Manual virtual environment activation
venv-desktop\Scripts\activate.bat

REM Manual build
venv-desktop\Scripts\activate.bat
python build_desktop.py
```

---

## Congratulations!

You now have a Windows executable that you can distribute to users!

**Executable**: `dist\FrequencyTableGenerator.exe`  
**Size**: 200-300 MB  
**Requirements for users**: None! (except Visual C++ Redistributable, usually pre-installed)  
**Installation**: None needed - just run the .exe

🎉 **Ready to distribute!**
