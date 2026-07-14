# Quick Start Guide - Desktop Application

This guide will help you get the desktop application running quickly.

## For Testing During Development

### Step 1: Install Dependencies

```bash
# Navigate to the webapp directory
cd frequency-table-webapp/webapp

# Install desktop dependencies
pip install -r requirements-desktop.txt
```

### Step 2: Run Without Building

You can test the application without building an executable:

```bash
# Option 1: Direct run
python gui_app.py

# Option 2: Use the launcher script
python run_desktop.py
```

The application window should open immediately.

### Step 3: Test the Workflow

1. Click **"Browse..."** to select a `.dta` file
2. Click **"Upload & Continue"**
3. Review the dataset information and variable list
4. Choose your analysis options:
   - Select weighting method
   - Configure filtering options
   - Set maximum categories
5. Click **"Generate Frequency Tables"**
6. Choose where to save the output Excel file
7. Wait for processing to complete
8. Open the Excel file directly from the app

## For Building Executables

### Step 1: Ensure Dependencies Are Installed

```bash
pip install -r requirements-desktop.txt
```

PyInstaller should be included (version 6.6.0).

### Step 2: Build the Executable

#### Quick Method (Recommended)

```bash
python build_desktop.py
```

This script will:
- Detect your operating system
- Run PyInstaller with the correct options
- Create a single executable file in `dist/`

#### Advanced Method (Using .spec file)

For more control:

```bash
pyinstaller FrequencyTableGenerator.spec
```

Edit the `.spec` file to customize:
- Excluded packages (reduce file size)
- Icon files
- Hidden imports
- UPX compression

### Step 3: Test the Executable

The executable will be in the `dist/` folder:

**Windows:**
```
dist/FrequencyTableGenerator.exe
```

**Linux:**
```
dist/FrequencyTableGenerator
```

Double-click to run (or `./FrequencyTableGenerator` on Linux after making it executable).

### Step 4: Distribute

Simply share the executable file! Users don't need:
- Python installed
- Any dependencies
- Technical knowledge

They just run the file and use the application.

## Build on Multiple Platforms

To create executables for both Windows and Linux:

### Option 1: Build on Each Platform
- Build on Windows → get `.exe` for Windows users
- Build on Linux → get binary for Linux users

### Option 2: Use Virtual Machines
- Windows developers: Use WSL or a Linux VM to build Linux binary
- Linux developers: Use Wine or a Windows VM to build `.exe`

### Option 3: Use CI/CD (Advanced)
Set up GitHub Actions to automatically build on both platforms:

```yaml
# .github/workflows/build.yml
name: Build Desktop App

on: [push, pull_request]

jobs:
  build:
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest]
    runs-on: ${{ matrix.os }}
    
    steps:
    - uses: actions/checkout@v3
    - uses: actions/setup-python@v4
      with:
        python-version: '3.10'
    - name: Install dependencies
      run: pip install -r requirements-desktop.txt
    - name: Build executable
      run: python build_desktop.py
    - name: Upload artifact
      uses: actions/upload-artifact@v3
      with:
        name: FrequencyTableGenerator-${{ matrix.os }}
        path: dist/FrequencyTableGenerator*
```

## Troubleshooting

### "ModuleNotFoundError" during build

Add the missing module to hidden imports in `build_desktop.py`:

```python
"--hidden-import=missing_module_name",
```

### Executable is very large (>200MB)

This is normal! It includes:
- Python runtime (~40MB)
- All libraries (pandas, numpy, etc.)
- Qt framework (PySide6)

To reduce size:
1. Enable UPX compression (add to build script)
2. Exclude unused packages in `.spec` file
3. Consider using `--onedir` instead of `--onefile` (creates folder with multiple files but smaller total size)

### "Permission denied" on Linux

Make the executable runnable:

```bash
chmod +x dist/FrequencyTableGenerator
./dist/FrequencyTableGenerator
```

### Antivirus blocks the executable

This can happen with PyInstaller executables. Solutions:
1. Add an exception in your antivirus
2. Code-sign the executable (requires certificate, mainly for distribution)
3. Submit to antivirus vendors for whitelisting

### Application crashes immediately

Run from terminal to see error messages:

**Windows:**
```cmd
cd dist
FrequencyTableGenerator.exe
```

**Linux:**
```bash
cd dist
./FrequencyTableGenerator
```

Check the error output and add missing dependencies to build script.

## Performance Tips

### For Development
- Use `python gui_app.py` for faster iteration
- Build executable only when ready to test distribution

### For Users
- First run may be slower as the OS verifies the file
- Processing large datasets (100k+ rows) may take a few minutes
- Progress dialog shows current status

## File Locations

After building, you'll have:

```
webapp/
├── build/                  # Temporary build files (can delete)
├── dist/                   # Final executable here!
│   └── FrequencyTableGenerator[.exe]
├── FrequencyTableGenerator.spec  # Build configuration
├── gui_app.py             # Source code
├── core.py                # Business logic
└── requirements-desktop.txt
```

The **only file you need to distribute** is the executable in `dist/`.

## Next Steps

1. **Test thoroughly** with various .dta files
2. **Get feedback** from users
3. **Iterate** on features
4. **Version** your releases (e.g., v1.0, v1.1)
5. **Share** the executable with your team!

---

For detailed documentation, see [README_DESKTOP.md](README_DESKTOP.md)
