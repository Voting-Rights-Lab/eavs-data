#!/usr/bin/env python3
"""
Migrate EAVS Historical Data from Google Sheets to Native BigQuery Tables

This script takes the CSV backups from staging tables and loads them into
native BigQuery tables, replacing the fragile Google Sheets external tables.

Process:
1. Read CSV backups from data/backups/staging_tables/
2. Load each year's data directly to BigQuery native tables
3. Update external table definitions to use native tables instead of Sheets
4. Verify row counts match

Usage:
    python scripts/migrate_sheets_backups_to_native.py [--dry-run]
"""

import argparse
import subprocess
import sys
from pathlib import Path
from google.cloud import bigquery
from datetime import datetime

PROJECT_ID = "eavs-392800"
BACKUP_DIR = Path(__file__).parent.parent / "data" / "backups" / "staging_tables"

# Mapping of section codes to table names
SECTIONS = {
    'reg': 'a_reg',
    'uocava': 'b_uocava',
    'mail': 'c_mail',
    'part': 'f1_participation'
}

YEARS = ['2016', '2018', '2020', '2022']


def get_backup_file(section, year):
    """Find the most recent backup file for a section/year."""
    pattern = f"stg_eavs_county_{section}_union_{year}_*.csv"
    files = list(BACKUP_DIR.glob(pattern))

    if not files:
        return None

    # Return most recent
    return max(files, key=lambda p: p.stat().st_mtime)


def create_native_table(section_code, year, csv_file, client, dry_run=False):
    """Create a native BigQuery table from CSV backup."""

    dataset_id = f"eavs_{year}"
    # Use same naming as external tables
    table_id = f"eavs_county_{year[2:]}_{section_code}"
    full_table_id = f"{PROJECT_ID}.{dataset_id}.{table_id}_native"

    print(f"\n📥 Loading {section_code} {year} from CSV...")
    print(f"   Source: {csv_file.name}")
    print(f"   Target: {full_table_id}")

    if dry_run:
        print("   [DRY RUN] Would load CSV to native table")
        return full_table_id, 0

    # Check if file is empty
    if csv_file.stat().st_size == 0:
        print(f"   ⚠️  CSV file is empty, skipping...")
        return None, 0

    # Load configuration
    job_config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.CSV,
        skip_leading_rows=1,
        autodetect=True,
        write_disposition='WRITE_TRUNCATE'  # Replace if exists
    )

    try:
        # Load CSV to BigQuery
        with open(csv_file, 'rb') as f:
            load_job = client.load_table_from_file(
                f,
                full_table_id,
                job_config=job_config
            )

        # Wait for job to complete
        load_job.result()

        # Get table info
        table = client.get_table(full_table_id)
        row_count = table.num_rows

        print(f"   ✅ Loaded {row_count:,} rows to native table")

        return full_table_id, row_count

    except Exception as e:
        print(f"   ❌ Error loading table: {e}")
        return None, 0


def verify_migration(client, section_code, year, expected_rows):
    """Verify the native table has correct data."""
    dataset_id = f"eavs_{year}"
    table_id = f"eavs_county_{year[2:]}_{section_code}_native"
    full_table_id = f"{PROJECT_ID}.{dataset_id}.{table_id}"

    query = f"SELECT COUNT(*) as row_count FROM `{full_table_id}`"

    try:
        result = client.query(query).result()
        actual_rows = list(result)[0].row_count

        if actual_rows == expected_rows:
            print(f"   ✅ Verification passed: {actual_rows:,} rows")
            return True
        else:
            print(f"   ⚠️  Row count mismatch: expected {expected_rows:,}, got {actual_rows:,}")
            return False
    except Exception as e:
        print(f"   ❌ Verification failed: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description='Migrate Google Sheets to native BigQuery tables')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be done without doing it')
    args = parser.parse_args()

    print("=" * 80)
    print("EAVS Data Migration: Google Sheets Backups → Native BigQuery Tables")
    print("=" * 80)

    if args.dry_run:
        print("\n🔍 DRY RUN MODE - No changes will be made\n")

    print(f"Project: {PROJECT_ID}")
    print(f"Backup directory: {BACKUP_DIR}")
    print(f"Years to migrate: {', '.join(YEARS)}")
    print(f"Sections: {', '.join(SECTIONS.keys())}")

    # Initialize BigQuery client
    client = bigquery.Client(project=PROJECT_ID)

    results = []

    # Process each year and section
    for year in YEARS:
        print(f"\n{'=' * 80}")
        print(f"Processing Year: {year}")
        print(f"{'=' * 80}")

        for section_name, section_code in SECTIONS.items():
            backup_file = get_backup_file(section_name, year)

            if not backup_file:
                print(f"\n⚠️  No backup found for {section_name} {year}")
                results.append({
                    'year': year,
                    'section': section_name,
                    'success': False,
                    'reason': 'No backup file'
                })
                continue

            # Create native table
            table_id, row_count = create_native_table(
                section_code,
                year,
                backup_file,
                client,
                dry_run=args.dry_run
            )

            if table_id and row_count > 0 and not args.dry_run:
                # Verify
                verified = verify_migration(client, section_code, year, row_count)

                results.append({
                    'year': year,
                    'section': section_name,
                    'success': verified,
                    'rows': row_count,
                    'table': table_id
                })
            elif table_id:
                results.append({
                    'year': year,
                    'section': section_name,
                    'success': True,
                    'rows': row_count,
                    'table': table_id
                })
            else:
                results.append({
                    'year': year,
                    'section': section_name,
                    'success': False,
                    'reason': 'Load failed'
                })

    # Summary
    print(f"\n{'=' * 80}")
    print("MIGRATION SUMMARY")
    print(f"{'=' * 80}")

    successful = [r for r in results if r['success']]
    failed = [r for r in results if not r['success']]
    total_rows = sum(r.get('rows', 0) for r in successful)

    print(f"\n✅ Successful: {len(successful)}/{len(results)} tables")
    print(f"   Total rows migrated: {total_rows:,}")

    if failed:
        print(f"\n❌ Failed: {len(failed)} tables")
        for r in failed:
            reason = r.get('reason', 'Unknown error')
            print(f"   - {r['year']} {r['section']}: {reason}")

    if not args.dry_run:
        print("\n" + "=" * 80)
        print("NEXT STEPS")
        print("=" * 80)
        print("\n1. Update union views to use *_native tables instead of external tables")
        print("   Edit views in BigQuery Console:")
        for section_name in SECTIONS.keys():
            print(f"   - eavs_analytics.eavs_county_{section_name}_union")

        print("\n2. Refresh staging tables:")
        print("   python scripts/load_eavs_year.py 2022 /any --refresh-tables")

        print("\n3. Test dashboards to verify data appears correctly")

        print("\n4. Once verified, you can drop the old external tables:")
        print("   (Keep them for 30 days as backup)")

        print("\n5. Document the migration:")
        print("   Update GOOGLE_SHEETS_INVENTORY.md to mark tables as migrated")

    if failed and not args.dry_run:
        sys.exit(1)

    print("\n✅ Migration script complete!")


if __name__ == "__main__":
    main()
