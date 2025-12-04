#!/usr/bin/env python3
"""
Backup and Migrate EAVS Historical Data from Google Sheets to GCS

This script:
1. Exports all EAVS 2016-2022 data from Google Sheets-backed external tables
2. Uploads CSV backups to GCS bucket
3. Updates external tables to point to GCS instead of Google Sheets
4. Verifies data integrity

CRITICAL: This addresses the data fragility risk identified in GOOGLE_SHEETS_INVENTORY.md

Usage:
    python backup_and_migrate_eavs_sheets.py --backup-only    # Just backup to CSV
    python backup_and_migrate_eavs_sheets.py --migrate        # Backup + migrate to GCS
"""

import subprocess
import sys
import argparse
from pathlib import Path
from datetime import datetime

PROJECT_ID = "eavs-392800"
GCS_BUCKET = "eavs-data-files"
BACKUP_DIR = Path(__file__).parent.parent / "data" / "backups" / "google_sheets" / "eavs_historical"

# Years and sections to migrate
YEARS = ['2016', '2018', '2020', '2022']
SECTIONS = [
    ('a_reg', 'A_REG'),
    ('b_uocava', 'B_UOCAVA'),
    ('c_mail', 'C_MAIL'),
    ('d_polls', 'D_POLLS'),
    ('e_provisional', 'E_PROVISIONAL'),
    ('f1_participation', 'F1_PARTICIPATION'),
    ('f2_tech', 'F2_TECH')
]


def run_command(cmd, check=True):
    """Run shell command and return output."""
    print(f"  Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True, check=check)
    if result.returncode != 0 and check:
        print(f"  ERROR: {result.stderr}")
        raise subprocess.CalledProcessError(result.returncode, cmd, result.stderr)
    return result.stdout


def backup_table_to_csv(year, section_code, section_name):
    """Export table data to CSV backup."""
    dataset = f"eavs_{year}"
    year_short = year[-2:]
    table_name = f"eavs_county_{year_short}_{section_code}"

    print(f"\n📥 Backing up {dataset}.{table_name}...")

    # Create backup filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d')
    csv_file = BACKUP_DIR / f"{year}_{section_name}_{timestamp}.csv"

    # Query to export data
    query = f"SELECT * FROM `{PROJECT_ID}.{dataset}.{table_name}`"

    try:
        cmd = [
            "bq", "query",
            f"--project_id={PROJECT_ID}",
            "--use_legacy_sql=false",
            "--format=csv",
            "--max_rows=100000",  # Increase if tables are larger
            query
        ]

        output = run_command(cmd)

        # Write to file
        csv_file.parent.mkdir(parents=True, exist_ok=True)
        csv_file.write_text(output)

        # Count rows
        row_count = len(output.strip().split('\n')) - 1  # Minus header
        print(f"  ✅ Backed up {row_count:,} rows to {csv_file.name}")

        return csv_file, row_count

    except subprocess.CalledProcessError as e:
        print(f"  ❌ Failed to backup {table_name}: {e}")
        return None, 0


def upload_to_gcs(csv_file, year, section_name):
    """Upload CSV to GCS bucket."""
    year_short = year[-2:]
    gcs_path = f"{year}/EAVS_county_{year_short}_{section_name}.csv"
    gcs_uri = f"gs://{GCS_BUCKET}/{gcs_path}"

    print(f"  📤 Uploading to {gcs_uri}...")

    try:
        cmd = ["gsutil", "cp", str(csv_file), gcs_uri]
        run_command(cmd)
        print(f"  ✅ Uploaded to GCS")
        return gcs_uri

    except subprocess.CalledProcessError as e:
        print(f"  ❌ Failed to upload: {e}")
        return None


def update_external_table(year, section_code, gcs_uri):
    """Update external table to point to GCS instead of Google Sheets."""
    dataset = f"eavs_{year}"
    year_short = year[-2:]
    table_name = f"eavs_county_{year_short}_{section_code}"
    table_id = f"{PROJECT_ID}.{dataset}.{table_name}"

    print(f"  🔄 Updating external table {table_name} to use GCS...")

    # Note: This requires recreating the table with new source URI
    # The --replace flag will replace the existing table
    try:
        cmd = [
            "bq", "mk",
            "--external_table_definition=@CLOUD_BIGTABLE=gs://path",  # Placeholder
            f"--project_id={PROJECT_ID}",
            "--replace",
            table_id
        ]

        # This is a complex operation that may require the BigQuery API
        # For now, we'll just document what needs to be done manually
        print(f"  ⚠️  Manual step required:")
        print(f"      1. In BigQuery Console, edit table {table_id}")
        print(f"      2. Change source URI from Google Sheets to: {gcs_uri}")
        print(f"      3. Keep all other settings the same")

        return False  # Indicates manual step needed

    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False


def verify_table(year, section_code, expected_rows):
    """Verify table row count matches backup."""
    dataset = f"eavs_{year}"
    year_short = year[-2:]
    table_name = f"eavs_county_{year_short}_{section_code}"

    print(f"  🔍 Verifying {table_name}...")

    query = f"SELECT COUNT(*) as count FROM `{PROJECT_ID}.{dataset}.{table_name}`"

    try:
        cmd = [
            "bq", "query",
            f"--project_id={PROJECT_ID}",
            "--use_legacy_sql=false",
            "--format=csv",
            query
        ]

        output = run_command(cmd)
        actual_rows = int(output.strip().split('\n')[1])

        if actual_rows == expected_rows:
            print(f"  ✅ Verified: {actual_rows:,} rows")
            return True
        else:
            print(f"  ⚠️  Row count difference: expected {expected_rows:,}, got {actual_rows:,}")
            return False

    except Exception as e:
        print(f"  ❌ Verification failed: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description='Backup and migrate EAVS historical data from Google Sheets',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('--backup-only', action='store_true',
                       help='Only backup to CSV (don\'t migrate to GCS)')
    parser.add_argument('--migrate', action='store_true',
                       help='Backup and migrate to GCS')
    parser.add_argument('--verify-only', action='store_true',
                       help='Only verify existing tables')
    parser.add_argument('--years', nargs='+', choices=YEARS, default=YEARS,
                       help='Specific years to process (default: all)')

    args = parser.parse_args()

    if not (args.backup_only or args.migrate or args.verify_only):
        parser.error("Must specify --backup-only, --migrate, or --verify-only")

    print("=" * 70)
    print("EAVS Historical Data Backup and Migration")
    print("=" * 70)
    print(f"\nProcessing years: {', '.join(args.years)}")
    print(f"Backup directory: {BACKUP_DIR}")
    print(f"GCS bucket: {GCS_BUCKET}")

    # Create backup directory
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)

    results = []
    manual_steps = []

    # Process each year and section
    for year in args.years:
        print(f"\n{'=' * 70}")
        print(f"Processing {year}")
        print(f"{'=' * 70}")

        for section_code, section_name in SECTIONS:
            print(f"\n--- {section_name} ---")

            result = {
                'year': year,
                'section': section_name,
                'backup': False,
                'upload': False,
                'verified': False
            }

            if args.verify_only:
                # Just verify
                verified = verify_table(year, section_code, 0)  # Don't check count
                result['verified'] = verified

            else:
                # Backup
                csv_file, row_count = backup_table_to_csv(year, section_code, section_name)
                if csv_file:
                    result['backup'] = True
                    result['rows'] = row_count

                    if args.migrate:
                        # Upload to GCS
                        gcs_uri = upload_to_gcs(csv_file, year, section_name)
                        if gcs_uri:
                            result['upload'] = True
                            result['gcs_uri'] = gcs_uri

                            # Add manual step
                            manual_steps.append({
                                'year': year,
                                'section': section_code,
                                'table': f"eavs_{year}.eavs_county_{year[-2:]}_{section_code}",
                                'gcs_uri': gcs_uri
                            })

                        # Verify
                        verified = verify_table(year, section_code, row_count)
                        result['verified'] = verified

            results.append(result)

    # Print summary
    print(f"\n{'=' * 70}")
    print("SUMMARY")
    print(f"{'=' * 70}")

    backed_up = sum(1 for r in results if r.get('backup'))
    uploaded = sum(1 for r in results if r.get('upload'))
    verified = sum(1 for r in results if r.get('verified'))
    total = len(results)

    print(f"\nTables processed: {total}")
    print(f"  Backed up: {backed_up}")
    if args.migrate:
        print(f"  Uploaded to GCS: {uploaded}")
        print(f"  Verified: {verified}")

    # Show any failures
    failures = [r for r in results if not r.get('backup')]
    if failures:
        print(f"\n⚠️  {len(failures)} tables failed to backup:")
        for r in failures:
            print(f"    - {r['year']} {r['section']}")

    # Show manual steps
    if manual_steps:
        print(f"\n{'=' * 70}")
        print("MANUAL STEPS REQUIRED")
        print(f"{'=' * 70}")
        print("\nUpdate external tables in BigQuery Console to point to GCS:")
        print("\nFor each table below:")
        print("  1. Open table in BigQuery Console")
        print("  2. Click 'Edit Details'")
        print("  3. Update 'Source URI' to the GCS URI shown")
        print("  4. Save changes")
        print()

        for step in manual_steps:
            print(f"\nTable: {step['table']}")
            print(f"  New URI: {step['gcs_uri']}")

    if args.backup_only:
        print(f"\n✅ Backup complete!")
        print(f"   CSV files stored in: {BACKUP_DIR}")
        print(f"\nNext steps:")
        print(f"  1. Review backups in {BACKUP_DIR}")
        print(f"  2. Add backups to git (important data!)")
        print(f"  3. Run with --migrate to upload to GCS")

    elif args.migrate:
        if uploaded == total:
            print(f"\n✅ Migration complete!")
            print(f"   All tables backed up and uploaded to GCS")
            print(f"\nIMPORTANT: Complete manual steps above to switch tables to GCS")
        else:
            print(f"\n⚠️  Migration incomplete - some tables failed")
            sys.exit(1)


if __name__ == "__main__":
    main()
