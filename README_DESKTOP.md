# Frequency Table Generator - Desktop Application

A standalone desktop application for generating frequency tables from Stata (.dta) files. No installation or Python knowledge required for end users!

## Features

- 🖥️ Native desktop application (Windows & Linux)
- 📊 Generate weighted/unweighted frequency tables from Stata files
- 📈 Automatic variable classification (ID, continuous, categorical)
- 📑 Export to formatted Excel workbooks
- 🚀 Single executable file - no dependencies needed for users

## For End Users

### Installation

**No installation needed!** Simply:

1. Download the executable file for your platform:
   - **Windows**: `FrequencyTableGenerator.exe`
   - **Linux**: `FrequencyTableGenerator`

2. Double-click to run (Windows) or make executable and run (Linux):
   ```bash
   chmod +x FrequencyTableGenerator
   ./FrequencyTableGenerator
   ```

### Usage

1. **Upload Dataset**: Click "Browse..." and select your `.dta` file
2. **Choose Options**: 
   - Select weighting options (none, variable, or constant value)
   - Configure filtering (exclude IDs, continuous variables, etc.)
   - Set maximum categories threshold
3. **Generate**: Click "Generate Frequency Tables" and choose where to save
4. **View Results**: Open the Excel file directly from the app

## For Developers

### Development Setup

1. **Clone the repository** and navigate to the webapp directory

2. **Install dependencies**:
   ```bash
   pip install -r requirements-desktop.txt
   ```

3. **Run the application** (without building):
   ```bash
   python gui_app.py
   ```

### Building Executables

#### Method 1: Using the build script (Recommended)

```bash
python build_desktop.py
```

This will create a standalone executable in the `dist/` folder.

#### Method 2: Manual PyInstaller

**Windows**:
```bash
pyinstaller --name=FrequencyTableGenerator --onefile --windowed ^
    --hidden-import=pandas --hidden-import=numpy ^
    --hidden-import=pyreadstat --hidden-import=xlsxwriter ^
    --hidden-import=openpyxl --hidden-import=PySide6 ^
    --collect-all=pyreadstat --collect-all=PySide6 ^
    gui_app.py
```

**Linux**:
```bash
pyinstaller --name=FrequencyTableGenerator --onefile --windowed \
    --hidden-import=pandas --hidden-import=numpy \
    --hidden-import=pyreadstat --hidden-import=xlsxwriter \
    --hidden-import=openpyxl --hidden-import=PySide6 \
    --collect-all=pyreadstat --collect-all=PySide6 \
    gui_app.py
```

The executable will be in `dist/FrequencyTableGenerator` (or `.exe` on Windows).

### Cross-Compilation Notes

PyInstaller creates executables for the **platform you build on**:
- Build on Windows → Windows `.exe`
- Build on Linux → Linux binary

To create both versions, you need to build on both platforms (or use a CI/CD system with both runners).

### File Size Optimization

The default build includes all dependencies and is ~100-200MB. To reduce size:

1. **Use `--onefile` mode** (already default in our script)
2. **Exclude unnecessary packages** in the .spec file
3. **Use UPX compression** (add `--upx-dir=/path/to/upx` to PyInstaller)

### Adding an Icon

To add a custom icon:

1. Create an icon file:
   - Windows: `.ico` file
   - Linux: `.png` file

2. Update the build command:
   ```bash
   pyinstaller --icon=path/to/icon.ico ...
   ```

## Project Structure

```
webapp/
├── gui_app.py              # Desktop application UI (PySide6)
├── core.py                 # Business logic (shared with web version)
├── app.py                  # Flask web application (separate)
├── requirements-desktop.txt # Desktop dependencies
├── requirements.txt        # Web dependencies
├── build_desktop.py        # Build script for executables
└── README_DESKTOP.md       # This file
```

## Dependencies

### Runtime (for end users)
- **None!** Everything is bundled in the executable

### Development (for building)
- Python 3.8+
- PySide6 (Qt for Python)
- pandas, numpy
- pyreadstat (Stata file reader)
- xlsxwriter, openpyxl (Excel export)
- PyInstaller (for building executables)

## Troubleshooting

### Build Issues

**"Module not found" errors during build:**
```bash
# Add to PyInstaller command:
--hidden-import=<module_name>
```

**Large executable size:**
- This is normal for bundled applications
- PyInstaller includes the entire Python runtime and all dependencies

**"Permission denied" on Linux:**
```bash
chmod +x dist/FrequencyTableGenerator
```

### Runtime Issues

**Application won't start:**
- Check if antivirus is blocking the executable
- On Windows, you may see a SmartScreen warning (click "More info" → "Run anyway")
- On Linux, ensure the file is executable

**File processing errors:**
- Ensure the `.dta` file is not corrupted
- Check that the file is a valid Stata format
- Try with a smaller test file first

## Comparison: Desktop vs Web Version

| Feature | Desktop App | Web App |
|---------|-------------|---------|
| Installation | Single file, no install | Requires server setup |
| Internet Required | No | Yes (if deployed) |
| File Size Limit | Limited by RAM/disk | Configurable (300MB default) |
| Multi-user | One user at a time | Multiple concurrent users |
| Updates | Redistribute executable | Update server code |
| Privacy | All processing local | Data uploaded to server |

## License

Same as the main project.

## Support

For issues or questions:
- Check the troubleshooting section above
- Review the main README.md
- Contact the development team

---

**Note**: This desktop version shares the same core logic (`core.py`) as the web version, ensuring consistent results across both interfaces.
