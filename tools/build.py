#!/usr/bin/env python3
"""
Spacecraft Subsystem Limits Build Tool

This script reads all CSV files from the limits/ directory, validates their headers,
merges them into a master CSV file, and generates a JSON file with metadata.
"""

import csv
import json
import os
import glob
from datetime import datetime, timezone
from pathlib import Path


# Expected CSV headers (must match exactly in this order)
EXPECTED_HEADERS = [
    "subsystem",
    "asset_id",
    "asset_type",
    "mnemonic", 
    "lower_critical",
    "lower_caution",
    "upper_caution",
    "upper_critical",
    "revision_notes"
]


def validate_csv_headers(csv_file_path, headers):
    """
    Validate that the CSV file has the expected headers in the correct order.
    
    Args:
        csv_file_path (str): Path to the CSV file
        headers (list): List of headers from the CSV file
        
    Returns:
        bool: True if headers are valid, False otherwise
    """
    if headers != EXPECTED_HEADERS:
        print(f"ERROR: Invalid headers in {csv_file_path}")
        print(f"Expected: {EXPECTED_HEADERS}")
        print(f"Found:    {headers}")
        return False
    return True


def validate_asset_id(row, csv_file, row_number):
    """
    Validate that asset_id is not empty.
    
    Args:
        row (dict): Row dictionary from CSV
        csv_file (str): Path to CSV file for error reporting
        row_number (int): Row number for error reporting
        
    Returns:
        bool: True if valid, False if invalid
    """
    if not row["asset_id"].strip():
        print(f"ERROR: Empty asset_id in {csv_file} at row {row_number}")
        return False
    return True


def read_csv_files(limits_dir):
    """
    Read all CSV files from the limits directory and validate their headers.
    
    Args:
        limits_dir (str): Path to the limits directory
        
    Returns:
        list: List of dictionaries containing row data from all CSV files
    """
    csv_files = glob.glob(os.path.join(limits_dir, "*.csv"))
    
    if not csv_files:
        print(f"WARNING: No CSV files found in {limits_dir}")
        return []
    
    all_rows = []
    
    for csv_file in csv_files:
        print(f"Processing: {csv_file}")
        
        try:
            with open(csv_file, 'r', encoding='utf-8', newline='') as f:
                reader = csv.reader(f)
                
                # Read and validate headers
                headers = next(reader, None)
                if headers is None:
                    print(f"ERROR: Empty file {csv_file}")
                    continue
                
                # Strip whitespace from headers
                headers = [header.strip() for header in headers]
                
                if not validate_csv_headers(csv_file, headers):
                    print(f"SKIPPING: {csv_file} due to invalid headers")
                    continue
                
                # Read data rows
                row_count = 0
                valid_rows = 0
                for row in reader:
                    row_number = row_count + 2  # +2 because row 1 is headers, and we're 0-indexed
                    
                    if len(row) != len(EXPECTED_HEADERS):
                        print(f"WARNING: Row {row_number} in {csv_file} has {len(row)} columns, expected {len(EXPECTED_HEADERS)}")
                        row_count += 1
                        continue
                    
                    # Create dictionary with header keys and row values
                    row_dict = {}
                    for i, header in enumerate(EXPECTED_HEADERS):
                        row_dict[header] = row[i].strip() if i < len(row) else ""
                    
                    # Validate asset_id is not empty
                    if not validate_asset_id(row_dict, csv_file, row_number):
                        print(f"SKIPPING: Row {row_number} in {csv_file} due to empty asset_id")
                        row_count += 1
                        continue
                    
                    # Add valid row
                    all_rows.append(row_dict)
                    valid_rows += 1
                    row_count += 1
                
                if valid_rows != row_count:
                    print(f"  -> Read {row_count} rows, {valid_rows} valid")
                else:
                    print(f"  -> Read {valid_rows} rows")
                
        except Exception as e:
            print(f"ERROR: Failed to process {csv_file}: {e}")
            continue
    
    return all_rows


def write_master_csv(output_path, rows):
    """
    Write all rows to a master CSV file.
    
    Args:
        output_path (str): Path to the output CSV file
        rows (list): List of row dictionaries
    """
    print(f"Writing master CSV: {output_path}")
    
    with open(output_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=EXPECTED_HEADERS)
        writer.writeheader()
        writer.writerows(rows)
    
    print(f"  -> Wrote {len(rows)} rows")


def write_json_output(output_path, rows):
    """
    Write rows to a JSON file and create a separate manifest file.
    
    Args:
        output_path (str): Path to the output JSON file
        rows (list): List of row dictionaries
    """
    print(f"Writing JSON output: {output_path}")
    
    # Transform rows to match the required JSON schema
    json_rows = []
    for row in rows:
        json_row = {
            "mnemonic": row["mnemonic"] if row["mnemonic"].strip() else None,
            "asset_id": row["asset_id"] if row["asset_id"].strip() else None,
            "subsytem": row["subsystem"] if row["subsystem"].strip() else None,  # Note: typo is intentional per schema
            "asset_type": row["asset_type"] if row["asset_type"].strip() else None,  # Use asset_type from CSV
            "lower_critical": float(row["lower_critical"]) if row["lower_critical"].strip() else None,
            "lower_caution": float(row["lower_caution"]) if row["lower_caution"].strip() else None,
            "upper_caution": float(row["upper_caution"]) if row["upper_caution"].strip() else None,
            "upper_critical": float(row["upper_critical"]) if row["upper_critical"].strip() else None
            # revision_notes removed from JSON output
        }
        json_rows.append(json_row)
    
    # Write latest.json with just the limits array
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(json_rows, f, indent=2, ensure_ascii=False)
    
    # Write manifest.json with metadata
    manifest_path = output_path.replace('latest.json', 'manifest.json')
    manifest_data = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "count": len(json_rows)
    }
    
    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(manifest_data, f, indent=2, ensure_ascii=False)
    
    print(f"  -> Wrote {len(json_rows)} rows to latest.json")
    print(f"  -> Wrote metadata to manifest.json")


def main():
    """Main function to orchestrate the build process."""
    print("Spacecraft Subsystem Limits Build Tool")
    print("=" * 40)
    
    # Define paths
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    limits_dir = project_root / "limits"
    dist_dir = project_root / "dist"
    
    # Create dist directory if it doesn't exist
    dist_dir.mkdir(exist_ok=True)
    print(f"Output directory: {dist_dir}")
    
    # Check if limits directory exists
    if not limits_dir.exists():
        print(f"ERROR: Limits directory not found: {limits_dir}")
        return 1
    
    # Read all CSV files
    print(f"Reading CSV files from: {limits_dir}")
    all_rows = read_csv_files(str(limits_dir))
    
    if not all_rows:
        print("No valid data found. Exiting.")
        return 1
    
    # Write outputs
    master_csv_path = dist_dir / "master.csv"
    json_output_path = dist_dir / "latest.json"
    manifest_path = dist_dir / "manifest.json"
    
    write_master_csv(str(master_csv_path), all_rows)
    write_json_output(str(json_output_path), all_rows)
    
    print("=" * 40)
    print(f"Build completed successfully!")
    print(f"Total rows processed: {len(all_rows)}")
    print(f"Master CSV: {master_csv_path}")
    print(f"JSON output: {json_output_path}")
    print(f"Manifest: {manifest_path}")
    
    return 0


if __name__ == "__main__":
    exit(main())
