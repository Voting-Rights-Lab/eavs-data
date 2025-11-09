#!/usr/bin/env python3
"""
Migrate Google Sheets-backed external tables to native BigQuery tables.

This script:
1. Exports data from Google Sheets external tables
2. Creates native BigQuery tables
3. Updates views to point to new native tables
4. Verifies data integrity

Run when billing is enabled on the project.
"""

import subprocess
import sys
from pathlib import Path

PROJECT_ID = "eavs-392800"
BACKUP_DIR = Path(__file__).parent.parent / "data" / "backups" / "google_sheets"

# Tables to migrate: (dataset, table_name, new_table_name)
TABLES_TO_MIGRATE = [
    # Policy tables
    ("vrl_internal_datasets", "policy_2020", "policy_2020_native"),
    ("vrl_internal_datasets", "policy_2022", "policy_2022_native"),

    # Could add EAVS 2016-2022 here if migrating those too
]


def run_bq_command(args, check=True):
    """Run a bq command and return output."""
    cmd = ["bq"] + args
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True, check=check)
    return result.stdout


def export_table_to_csv(dataset, table, output_file):
    """Export table data to CSV."""
    print(f"\n📥 Exporting {dataset}.{table}...")
    query = f"SELECT * FROM `{PROJECT_ID}.{dataset}.{table}`"

    args = [
        "query",
        f"--project_id={PROJECT_ID}",
        "--use_legacy_sql=false",
        "--format=csv",
        query
    ]

    output = run_bq_command(args)

    output_file.write_text(output)
    print(f"✅ Exported to {output_file}")

    # Verify
    row_count = len(output.strip().split('\n')) - 1  # Minus header
    print(f"   Rows exported: {row_count}")
    return row_count


def create_native_table(dataset, new_table, csv_file):
    """Create a native BigQuery table from CSV."""
    print(f"\n📤 Creating native table {dataset}.{new_table}...")

    args = [
        "load",
        f"--project_id={PROJECT_ID}",
        "--autodetect",
        "--replace",
        "--source_format=CSV",
        f"{dataset}.{new_table}",
        str(csv_file)
    ]

    run_bq_command(args)
    print(f"✅ Created {dataset}.{new_table}")


def verify_table(dataset, table, expected_rows):
    """Verify table was created correctly."""
    print(f"\n🔍 Verifying {dataset}.{table}...")

    query = f"SELECT COUNT(*) as count FROM `{PROJECT_ID}.{dataset}.{table}`"
    args = [
        "query",
        f"--project_id={PROJECT_ID}",
        "--use_legacy_sql=false",
        "--format=csv",
        query
    ]

    output = run_bq_command(args)
    actual_rows = int(output.strip().split('\n')[1])

    if actual_rows == expected_rows:
        print(f"✅ Verified: {actual_rows} rows")
        return True
    else:
        print(f"❌ Row count mismatch! Expected {expected_rows}, got {actual_rows}")
        return False


def main():
    print("=" * 60)
    print("Google Sheets → BigQuery Native Table Migration")
    print("=" * 60)

    # Create backup directory
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    print(f"\n📁 Backup directory: {BACKUP_DIR}")

    all_verified = True

    for dataset, old_table, new_table in TABLES_TO_MIGRATE:
        print(f"\n{'=' * 60}")
        print(f"Migrating: {dataset}.{old_table} → {dataset}.{new_table}")
        print(f"{'=' * 60}")

        try:
            # Export to CSV
            csv_file = BACKUP_DIR / f"{old_table}_migration.csv"
            row_count = export_table_to_csv(dataset, old_table, csv_file)

            # Create native table
            create_native_table(dataset, new_table, csv_file)

            # Verify
            verified = verify_table(dataset, new_table, row_count)
            if not verified:
                all_verified = False

        except subprocess.CalledProcessError as e:
            print(f"❌ Error migrating {dataset}.{old_table}:")
            print(e.stderr)
            all_verified = False
            continue

    # Summary
    print(f"\n{'=' * 60}")
    if all_verified:
        print("✅ MIGRATION COMPLETE - All tables verified!")
        print("\nNext steps:")
        print("1. Update policy_unioned view to use *_native tables")
        print("2. Refresh stg_policy_union")
        print("3. Rebuild mart tables")
        print("4. Test dashboards")
        print("5. Archive original Google Sheets (don't delete yet)")
    else:
        print("⚠️  MIGRATION INCOMPLETE - Some tables failed verification")
        print("Please review errors above")
        sys.exit(1)
    print("=" * 60)


if __name__ == "__main__":
    main()
