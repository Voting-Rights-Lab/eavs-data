# Google Sheets Backups

## Purpose
This directory stores CSV backups of all BigQuery tables that depend on Google Sheets as their data source.

## Why This Matters
If the Google Sheets are accidentally deleted, modified, or become inaccessible, these backups allow us to:
- Recreate the data in BigQuery
- Verify data integrity
- Recover from disasters

## What to Back Up

### Policy Data
- `policy_2020_backup.csv` - 2020 state voting policies
- `policy_2022_backup.csv` - 2022 state voting policies
- `policy_2024_backup.csv` - 2024 state voting policies (when added)

### EAVS Data (if migrating from Sheets)
- `eavs_county_{year}_{section}_backup.csv` - EAVS data for years 2016-2022

## How to Create Backups

### Manual Method (No Billing Required)
1. Open the Google Sheet (URLs in [GOOGLE_SHEETS_INVENTORY.md](../../../GOOGLE_SHEETS_INVENTORY.md))
2. File → Download → Comma Separated Values (.csv)
3. Save to this directory with naming convention: `{table_name}_backup.csv`
4. Commit to git: `git add . && git commit -m "Update Google Sheets backups"`

### Automated Method (When Permissions Allow)
```bash
# Run from repo root
./scripts/export_google_sheets_backups.sh
```

## Maintenance Schedule
- **Monthly**: Export fresh backups (especially before major changes)
- **Before deletions**: Always backup before deleting any Sheets
- **After updates**: Backup when policy data changes

## Git Policy
**These backups SHOULD be committed to git** despite the general rule to exclude CSVs. The .gitignore has been updated to allow this directory specifically.

## Using Backups for Recovery

If a Google Sheet is deleted:

1. **Create native BigQuery table from backup:**
   ```bash
   bq load --autodetect --replace --source_format=CSV \
     vrl_internal_datasets.policy_2022 \
     data/backups/google_sheets/policy_2022_backup.csv
   ```

2. **Update external table to point to new source** (or convert to native)

3. **Verify data integrity:**
   ```sql
   SELECT COUNT(*) FROM `eavs-392800.vrl_internal_datasets.policy_2022`
   ```

## See Also
- [GOOGLE_SHEETS_INVENTORY.md](../../../GOOGLE_SHEETS_INVENTORY.md) - Complete list of Sheets dependencies
- [MIGRATION_PLAN.md](../../../MIGRATION_PLAN.md) - Plan to migrate away from Sheets
- [scripts/migrate_sheets_to_bigquery.py](../../../scripts/migrate_sheets_to_bigquery.py) - Migration script
