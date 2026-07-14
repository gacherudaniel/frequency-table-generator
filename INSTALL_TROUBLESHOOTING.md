# Installation Troubleshooting Guide

## Runtime Issues (After Installation)

### Qt Platform Plugin Error (Linux)

**Error Message**:
```
qt.qpa.plugin: From 6.5.0, xcb-cursor0 or libxcb-cursor0 is needed to load the Qt xcb platform plugin.
qt.qpa.plugin: Could not load the Qt platform plugin "xcb"
This application failed to start because no Qt platform plugin could be initialized.
```

**Solution**:
Install the missing system library:
```bash
sudo apt update
sudo apt install libxcb-cursor0
```

**Explanation**: PySide6 (Qt) needs system libraries to display GUI windows on Linux with X11. The `libxcb-cursor0` library is required for Qt 6.5.0 and later.

**Alternative platforms**: If you encounter other Qt plugin errors, you can try different platforms:
```bash
# Use Wayland instead of X11
export QT_QPA_PLATFORM=wayland
python run_desktop.py

# Use offscreen rendering (no display, for testing)
export QT_QPA_PLATFORM=offscreen
python run_desktop.py
```

---

## Network Timeout Issues (PySide6 Installation)

If you're experiencing timeouts while installing PySide6 (as you may be seeing now), here are several solutions:

### Solution 1: Increase pip timeout

```bash
source venv-desktop/bin/activate
pip install --default-timeout=1000 -r requirements-desktop.txt
```

### Solution 2: Install packages individually

Install the large packages separately with longer timeouts:

```bash
source venv-desktop/bin/activate

# Install in stages
pip install --default-timeout=1000 numpy pandas
pip install --default-timeout=1000 pyreadstat xlsxwriter openpyxl
pip install --default-timeout=1000 PySide6
pip install pyinstaller
```

### Solution 3: Install PySide6 from a mirror or cache

```bash
source venv-desktop/bin/activate

# Use a different index
pip install --index-url https://pypi.org/simple/ PySide6
# Then install the rest
pip install -r requirements-desktop.txt
```

### Solution 4: Download manually and install locally

If network is very slow, download the wheel files manually:

1. Go to https://pypi.org/project/PySide6/6.7.0/#files
2. Download the appropriate `.whl` file for your system (manylinux for Linux)
3. Install locally:

```bash
source venv-desktop/bin/activate
pip install /path/to/downloaded/PySide6-*.whl
pip install -r requirements-desktop.txt
```

### Solution 5: Use system packages (Ubuntu/Debian)

If available, use system packages instead:

```bash
# Install system PySide6 (if available)
sudo apt-get update
sudo apt-get install python3-pyside6.qtwidgets python3-pyside6.qtcore python3-pyside6.qtgui

# Then install only the missing packages in venv
source venv-desktop/bin/activate
pip install pandas numpy pyreadstat xlsxwriter openpyxl pyinstaller
```

Note: This may require modifying the app to use system site-packages.

### Solution 6: Try later when network is better

PySide6_Addons is 137MB. If your network is slow or unstable:

1. Wait for a better network connection
2. Try during off-peak hours
3. Consider using a wired connection instead of WiFi

## Current Status Check

After installation completes (or if you want to check current status), run:

```bash
source venv-desktop/bin/activate
python test_desktop.py
```

This will verify which packages are installed and which are missing.

## Alternative: Use the Web Version

While you work on installing the desktop dependencies, you can continue using the Flask web version:

```bash
# In a different terminal or after deactivating venv-desktop
cd /home/gacheru-daniel/KNBS_Projects/Auto-table-generate/frequency-table-webapp/webapp
pip install -r requirements.txt  # Web app requirements (much smaller)
python app.py
```

The web version has the same core functionality and much smaller dependencies.

## Still Having Issues?

If none of these work:

1. **Check disk space**: `df -h`
2. **Check network**: `ping pypi.org`
3. **Try a different mirror**: Add `--index-url https://mirrors.aliyun.com/pypi/simple/` (example)
4. **Check firewall/proxy**: Ensure pip can access PyPI

## Quick Test Without Full Installation

You can test that the core logic works without PySide6:

```bash
source venv-desktop/bin/activate
pip install pandas numpy pyreadstat xlsxwriter openpyxl

# Test just the core functionality
python -c "import core; print('Core module works!')"
```

This verifies the business logic works, even if you can't test the GUI yet.

## Next Steps After Successful Installation

Once all packages are installed:

1. Run tests: `python test_desktop.py`
2. Test the app: `python run_desktop.py` or `python gui_app.py`
3. Build executable: `python build_desktop.py`

---

**Note**: The desktop app is fully optional. The web version (using Flask) is already working and can be deployed to a server. The desktop version is just an additional distribution option for users who prefer standalone executables.
