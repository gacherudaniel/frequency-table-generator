# Frequency Table Generator - User Guide

## What is this?

The Frequency Table Generator is a desktop application that helps you create frequency tables from Stata (.dta) files. You can generate weighted or unweighted frequency tables and export them to Excel format.

**No programming knowledge required!**

## Installation

### Windows

1. Download `FrequencyTableGenerator.exe`
2. Double-click to run
3. If Windows shows a "Windows protected your PC" message:
   - Click **"More info"**
   - Click **"Run anyway"**
   - This is normal for new applications

**No installation needed!** The application runs directly.

### Linux

1. Download `FrequencyTableGenerator`
2. Open a terminal in the download folder
3. Make it executable:
   ```bash
   chmod +x FrequencyTableGenerator
   ```
4. Run it:
   ```bash
   ./FrequencyTableGenerator
   ```

**Alternative:** Double-click the file (may need to set "Allow executing file as program" in file properties)

## How to Use

### Step 1: Upload Your Dataset

1. Click the **"Browse..."** button
2. Select your Stata `.dta` file
3. Click **"Upload & Continue"**

The application will load your dataset and show:
- Number of observations (rows)
- Number of variables (columns)
- A detailed variable list (expand to view)

### Step 2: Choose Analysis Options

#### Weighting Options

Choose one of three weighting methods:

**1. No weighting (unweighted frequencies)**
- Simple frequency counts
- Each observation counts as 1
- Use this for most basic analyses

**2. Use a weight variable**
- Select a variable from your dataset that contains weights
- Common for survey data with sampling weights
- Example: if your dataset has a variable called `weight` or `sample_weight`

**3. Apply a constant weight value**
- Enter a single number to apply to all observations
- Useful when you know the design weight (e.g., 1/probability of selection)
- Example: If sampling fraction is 1%, use weight = 100

#### Filtering Options

**Exclude ID variables**
- ✓ Checked (recommended): Skips variables that look like identifiers
- Examples skipped: `id`, `respondent_id`, `unique_key`

**Exclude continuous numeric variables**
- ✓ Checked: Skips variables like age, income, scores
- ☐ Unchecked: Include all numeric variables

**Only tabulate categorical variables**
- ✓ Checked: Only process variables with value labels or few unique values
- ☐ Unchecked: Process all variables (except those filtered above)

**Maximum categories**
- Default: 50
- Variables with more unique values than this will be skipped
- Increase if you want to process variables with many categories
- Decrease to skip high-cardinality variables

### Step 3: Generate Tables

1. Click **"Generate Frequency Tables"**
2. Choose where to save the output Excel file
3. Wait while the application processes your data
   - A progress dialog shows which variable is being processed
   - Processing time depends on dataset size

### Step 4: View Results

After processing completes:

1. **Summary** shows:
   - Dataset information
   - Number of variables processed
   - Number of variables skipped (and why)
   - Processing time

2. **Open Excel File** - Opens the output in your default spreadsheet program

3. **Save As...** - Copy the file to another location

4. **Start Over** - Analyze a new dataset

## Understanding the Output

The Excel workbook contains:

### Summary Sheet
- Dataset name and generation date
- Total observations and variables
- Weight information (if used)
- List of successfully processed variables
- List of skipped variables with reasons

### Variable Sheets (one per variable)
Each sheet shows:
- **Variable Name**: The column name from your dataset
- **Variable Label**: The descriptive label (if available)
- **Analysis Type**: Weighted or Unweighted
- **Weight Source**: Which weight was used
- **Frequency Table**:
  - Category: The value or value label
  - Frequency: Count (or weighted count)
  - Percent: Percentage of total

**Special features:**
- Header row is frozen for easy scrolling
- Percent values formatted to 2 decimal places
- Missing values shown at the bottom
- Professional formatting with colored headers

## Common Questions

### What file formats are supported?

Only Stata `.dta` files are supported. If you have data in another format:
- **Excel/CSV**: Import into Stata and save as .dta
- **SPSS**: Use Stata's `import spss` command
- **SAS**: Use Stata's `import sas` command

### My dataset is very large. Will it work?

The application can handle most datasets, but very large files may:
- Take longer to process (several minutes)
- Use significant memory
- Produce very large Excel files

Recommendations:
- Datasets with <100,000 observations: Should work fine
- Datasets with >100,000 observations: May be slow but should work
- Datasets with >1,000 variables: Consider filtering more aggressively

### Some variables were skipped. Why?

Common reasons:
1. **ID variable**: Unique identifier (every value is different)
2. **Continuous numeric**: Variables like age, income, measurements
3. **Too many categories**: More unique values than your threshold
4. **Processing error**: Rare, usually due to data issues

Check the Summary sheet in the output for specific reasons.

### Can I use this offline?

**Yes!** The desktop application works completely offline:
- No internet connection needed after download
- All processing happens on your computer
- Your data never leaves your machine
- No accounts or login required

### How do I get help?

If you encounter issues:
1. Check this user guide
2. Verify your .dta file opens in Stata
3. Try with a smaller test file first
4. Contact your system administrator or the person who provided the application

## System Requirements

### Windows
- Windows 10 or later (64-bit)
- 4 GB RAM minimum (8 GB recommended)
- 500 MB free disk space

### Linux
- Most modern distributions (Ubuntu 20.04+, Fedora, etc.)
- 4 GB RAM minimum (8 GB recommended)
- 500 MB free disk space

## Privacy & Security

- **All processing is local**: Your data stays on your computer
- **No data collection**: The application doesn't send any information anywhere
- **No internet required**: Works completely offline
- **No installation**: Portable application, doesn't modify your system

## Troubleshooting

### Application won't start (Windows)

**SmartScreen warning:**
- This is normal for new applications
- Click "More info" → "Run anyway"

**Antivirus blocking:**
- Add an exception for the application
- The file is safe but may be flagged as "unknown publisher"

### Application won't start (Linux)

**Permission denied:**
```bash
chmod +x FrequencyTableGenerator
./FrequencyTableGenerator
```

**Missing libraries:**
```bash
# Ubuntu/Debian
sudo apt-get install libxcb-xinerama0

# Fedora
sudo dnf install xcb-util
```

### "Could not read file" error

- Verify the file is a valid Stata .dta file
- Try opening it in Stata first
- Check the file isn't corrupted
- Ensure you have read permissions

### Application freezes during processing

- This is normal for large datasets
- Check the progress dialog for updates
- Wait a few minutes before canceling
- Try with a smaller subset of data first

### Excel file is too large

- Reduce the number of variables processed
- Increase the "maximum categories" threshold to skip high-cardinality variables
- Use filtering options more aggressively

---

**Version**: 1.0  
**Last Updated**: 2026  

For technical support, contact your IT department or the application provider.
