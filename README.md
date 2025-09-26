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
├── build.py      # Main build script
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

### Manual Build
```bash
python tools/build.py
```

### Automatic Build Setup (One-time)
```bash
python tools/install-hooks.py
```

After setup, the build runs automatically when you commit changes to the `limits/` folder.

## Rules

- Asset IDs are required (no empty values)
- Empty CSV values become `null` in JSON output
- Distribution files are read-only (automatically locked)
- Only the build script can modify `dist/` files

## Team Workflow

1. Edit your subsystem's CSV file in `limits/`
2. Commit your changes
3. Distribution files update automatically
4. Push to share with other teams

## Output Files

- **master.csv**: Complete data including revision notes
- **latest.json**: Operational limits only (no revision notes)
- **manifest.json**: Build timestamp and row count
