# Google Sheets Migration Plan

## Problem
ALL EAVS data from 2016-2022 and policy data for 2020-2022 are stored in Google Sheets. This is fragile and risky.

## Current Blockers
1. **Billing disabled** on eavs-392800 project → Can't create new tables or load data
2. **Drive permissions** → Can't query Google Sheets directly from current account

## Immediate Actions (No Billing Required)

### 1. Manual Backup via Google Sheets UI
Since automated export is blocked by permissions, manually download the Sheets:

**Policy Sheets:**
- policy_2020: https://docs.google.com/spreadsheets/d/17tX1S1SOpCXrDY0_YQX7cw8ILfWUd0TFPmUtIx9Mh4o/edit?usp=sharing
  - File → Download → CSV
  - Save as: `data/backups/google_sheets/policy_2020_backup.csv`

- policy_2022: https://docs.google.com/spreadsheets/d/1f2lteFd5VPC0NbtRXoV3PTboJAHYNzl4FJpcLpGjK0A/edit?usp=sharing
  - File → Download → CSV
  - Save as: `data/backups/google_sheets/policy_2022_backup.csv`

**EAVS Sheets (2022 - most critical):**
- Find Sheet URLs in BigQuery console or via `bq show` command
- Download registration, UOCAVA, mail, participation sheets
- Save as: `data/backups/google_sheets/eavs_county_22_{section}_backup.csv`

### 2. Add Sheet Protection Warnings
For each Google Sheet:
1. Open the Sheet
2. Add a comment/note at the top: "⚠️ WARNING: DO NOT DELETE - Powers BigQuery dashboards and analytics"
3. Share → Restrict edit access to only essential users

### 3. Commit Backups to Git
```bash
git add data/backups/google_sheets/*.csv
git commit -m "Add Google Sheets backups for disaster recovery"
git push
```

## When Billing is Enabled

### Option A: Quick Fix for Policy 2024 Only
Just add policy_24.csv to Google Sheets and create external table (maintains current pattern):

```bash
# Upload policy_24.csv to Google Sheets manually
# Then create external table:
bq mk --external_table_definition=::GOOGLE_SHEETS \
  vrl_internal_datasets.policy_2024 \
  "https://docs.google.com/spreadsheets/d/{SHEET_ID}"
```

### Option B: Full Migration (Recommended)
Migrate ALL Google Sheets to native BigQuery tables:

1. **Run migration script:**
   ```bash
   python scripts/migrate_sheets_to_bigquery.py
   ```

2. **Update policy union view:**
   ```sql
   -- Replace policy_2020 with policy_2020_native
   -- Replace policy_2022 with policy_2022_native
   -- Add policy_2024_native
   ```

3. **Refresh downstream tables:**
   ```bash
   # Refresh staging
   bq query --use_legacy_sql=false \
     "CREATE OR REPLACE TABLE eavs_analytics.stg_policy_union AS
      SELECT * FROM eavs_analytics.policy_unioned"

   # Rebuild marts
   bq query --use_legacy_sql=false \
     "CREATE OR REPLACE TABLE eavs_analytics.mart_eavs_analytics_county_rollup AS
      SELECT * FROM eavs_analytics.eavs_analytics_county_rollup"
   ```

4. **Verify dashboards work**

5. **Keep Sheets as archive** (don't delete immediately - keep for 30 days)

## Long-Term Best Practice

**For all future data:**
- Upload CSVs to GCS buckets (like 2024 EAVS)
- OR load directly to native BigQuery tables
- NEVER use Google Sheets for production data

**Annual Maintenance:**
- Run `scripts/export_google_sheets_backups.sh` monthly
- Commit backups to git
- Monitor Sheet access logs

## Cost
- BigQuery storage: ~$0.02/GB/month
- Estimated total: <$1/month for all policy + EAVS data
- **Worth it for reliability!**

## Files Created
- `GOOGLE_SHEETS_INVENTORY.md` - Complete inventory of Sheets dependencies
- `scripts/export_google_sheets_backups.sh` - Automated export script (run when permissions fixed)
- `scripts/migrate_sheets_to_bigquery.py` - Migration script for when billing enabled
- `data/backups/google_sheets/` - Backup directory (add to git!)
- `MIGRATION_PLAN.md` - This file

## Next Steps (Priority Order)

1. ✅ **Document the issue** (done - this file)
2. 🔲 **Manual backup critical Sheets** (policy_2020, policy_2022, eavs_2022 tables)
3. 🔲 **Add warnings to Sheets** (prevent accidental deletion)
4. 🔲 **Enable billing** on eavs-392800 project
5. 🔲 **Run migration script** to move to native tables
6. 🔲 **Add policy_24 data**
7. 🔲 **Set up monthly backup cron job**
