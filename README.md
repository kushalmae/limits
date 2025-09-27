# Spacecraft Subsystem Limits

A build system for managing spacecraft subsystem operational limits across multiple teams.

## Overview

This project consolidates CSV limit files from different subsystem teams into unified distribution files. Each subsystem team maintains their own CSV file with operational limits, and the build system automatically generates combined outputs.

## File Structure

```
limits/           # Individual subsystem CSV files
├── power.csv
├── thermal.csv
└── propulsion.csv

tools/            # Build and setup scripts
├── build_master_limit_files_from_csvs.py      # Main build script
└── install-hooks.py  # Git hooks installer

dist/             # Generated files (read-only)
├── master.csv    # Combined CSV data
├── latest.json   # JSON limits array
└── manifest.json # Build metadata
```

## CSV Format

All CSV files must use these exact headers in order:

```
subsystem,asset_id,asset_type,mnemonic,lower_critical,lower_caution,upper_caution,upper_critical,revision_notes
```

## Usage

### Automatic Method (Recommended)
**Step 1:** Setup (one-time only)
```bash
python tools/install-hooks.py
```

**Step 2:** Update & commit
- Edit your CSV file in `limits/`
- `git add .` and `git commit` → builds automatically

**Step 3:** Share (files auto-generated)
```bash
git push
```
*Creates: `master.csv`, `latest.json`, `manifest.json` in `dist/`*

### Manual Method
**Step 1:** Update limits
- Edit your CSV file in `limits/`

**Step 2:** Run build
```bash
python tools/build_master_limit_files_from_csvs.py
```

**Step 3:** Commit & push (with generated files)
```bash
git add .
git commit -m "Update limits"
git push
```
*Includes: `master.csv`, `latest.json`, `manifest.json` in `dist/`*

## What Happens Under the Hood

**Build Process:**
1. Scans all CSV files in `limits/` folder
2. Validates headers and data format
3. Combines all rows into unified datasets
4. Generates 3 distribution files in `dist/`
5. Locks files as read-only to prevent manual edits

**Distribution Files:**
- **`master.csv`**: Complete dataset with all columns including revision notes
- **`latest.json`**: JSON array of operational limits (excludes revision notes)
- **`manifest.json`**: Build metadata (timestamp, row count)

**Using the Output:**
```python
# Load JSON limits in your application
import json
with open('dist/latest.json') as f:
    limits = json.load(f)

# Or use CSV for spreadsheet analysis
import pandas as pd
df = pd.read_csv('dist/master.csv')
```

## Rules
- Asset IDs required (no empty values)
- Empty CSV values become `null` in JSON
- Distribution files are read-only
