#!/usr/bin/env python3
"""
Backup EAVS Data from Staging Tables

Since we can't access Google Sheets directly (Drive permission issues),
this script backs up data from the staging tables which already have
all historical data aggregated.

Usage:
    python backup_from_staging_tables.py
"""

import subprocess
import sys
from pathlib import Path
from datetime import datetime

PROJECT_ID = "eavs-392800"
BACKUP_DIR = Path(__file__).parent.parent / "data" / "backups" / "staging_tables"

# Staging tables to backup
TABLES = [
    'stg_eavs_county_reg_union',
    'stg_eavs_county_mail_union',
    'stg_eavs_county_part_union',
    'stg_eavs_county_uocava_union'
]

YEARS = ['2016', '2018', '2020', '2022', '2024']


def run_command(cmd):
    """Run shell command and return output."""
    print(f"  Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  ERROR: {result.stderr}")
        raise subprocess.CalledProcessError(result.returncode, cmd, result.stderr)
    return result.stdout


def backup_table_by_year(table_name, year):
    """Export data for specific year from staging table."""
    print(f"\n📥 Backing up {table_name} - {year}...")

    # Create filename
    timestamp = datetime.now().strftime('%Y%m%d')
    csv_file = BACKUP_DIR / f"{table_name}_{year}_{timestamp}.csv"
    csv_file.parent.mkdir(parents=True, exist_ok=True)

    # Query to export year data
    query = f"""
    SELECT *
    FROM `{PROJECT_ID}.eavs_analytics.{table_name}`
    WHERE election_year = '{year}'
    ORDER BY state, county
    """

    try:
        cmd = [
            "bq", "query",
            "--use_legacy_sql=false",
            "--format=csv",
            "--max_rows=10000",
            query
        ]

        output = run_command(cmd)

        # Write to file
        csv_file.write_text(output)

        # Count rows
        row_count = len(output.strip().split('\n')) - 1
        print(f"  ✅ Backed up {row_count:,} rows to {csv_file.name}")

        return csv_file, row_count

    except subprocess.CalledProcessError as e:
        print(f"  ❌ Failed to backup {table_name} {year}: {e}")
        return None, 0


def main():
    print("=" * 70)
    print("EAVS Data Backup from Staging Tables")
    print("=" * 70)
    print(f"\nBackup directory: {BACKUP_DIR}")
    print(f"Years: {', '.join(YEARS)}")
    print(f"Tables: {len(TABLES)}")

    # Create backup directory
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)

    results = []

    for table in TABLES:
        print(f"\n{'=' * 70}")
        print(f"Backing up: {table}")
        print(f"{'=' * 70}")

        for year in YEARS:
            result = {
                'table': table,
                'year': year,
                'success': False,
                'rows': 0
            }

            csv_file, row_count = backup_table_by_year(table, year)
            if csv_file:
                result['success'] = True
                result['rows'] = row_count

            results.append(result)

    # Summary
    print(f"\n{'=' * 70}")
    print("SUMMARY")
    print(f"{'=' * 70}")

    total = len(results)
    succeeded = sum(1 for r in results if r['success'])
    failed = total - succeeded
    total_rows = sum(r['rows'] for r in results)

    print(f"\nBackups: {succeeded}/{total} successful")
    print(f"Total rows backed up: {total_rows:,}")

    if failed > 0:
        print(f"\n⚠️  {failed} backups failed:")
        for r in results:
            if not r['success']:
                print(f"    - {r['table']} {r['year']}")
        sys.exit(1)
    else:
        print(f"\n✅ All backups complete!")
        print(f"   Files stored in: {BACKUP_DIR}")
        print(f"\nNext steps:")
        print(f"  1. Review backups: ls -lh {BACKUP_DIR}")
        print(f"  2. Add to git: git add {BACKUP_DIR}")
        print(f"  3. Commit: git commit -m 'Add EAVS historical data backups'")


if __name__ == "__main__":
    main()
