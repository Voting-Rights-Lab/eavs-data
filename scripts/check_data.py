#!/usr/bin/env python3
"""
Quick data checker for EAVS files
Validates CSV structure and shows summary statistics
"""

import sys
import pandas as pd
from pathlib import Path
import argparse

def check_csv_file(file_path):
    """Check a single CSV file and print summary"""
    print(f"\n📊 Checking: {file_path.name}")
    print("-" * 50)
    
    try:
        # Read CSV
        df = pd.read_csv(file_path, low_memory=False)
        
        # Basic info
        print(f"✓ Rows: {len(df):,}")
        print(f"✓ Columns: {len(df.columns)}")
        
        # Check for required columns
        required_cols = ['fips', 'state', 'county']
        missing = [col for col in required_cols if col not in df.columns]
        if missing:
            print(f"⚠️  Missing required columns: {missing}")
        else:
            print(f"✓ All required columns present")
        
        # Check for nulls in key columns
        if 'fips' in df.columns:
            null_fips = df['fips'].isna().sum()
            if null_fips > 0:
                print(f"⚠️  {null_fips} rows with null FIPS codes")
        
        # Show first few column names
        print(f"\nFirst 10 columns:")
        for col in df.columns[:10]:
            print(f"  - {col}")
        
        # Data types summary
        print(f"\nData types:")
        print(f"  - Numeric columns: {len(df.select_dtypes(include=['int64', 'float64']).columns)}")
        print(f"  - Text columns: {len(df.select_dtypes(include=['object']).columns)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Check EAVS CSV files')
    parser.add_argument('path', help='Path to CSV file or directory')
    args = parser.parse_args()
    
    path = Path(args.path)
    
    if path.is_file():
        check_csv_file(path)
    elif path.is_dir():
        csv_files = list(path.glob("**/*.csv"))
        print(f"Found {len(csv_files)} CSV files")
        
        for csv_file in csv_files:
            check_csv_file(csv_file)
    else:
        print(f"Error: {path} not found")
        sys.exit(1)

if __name__ == '__main__':
    main()