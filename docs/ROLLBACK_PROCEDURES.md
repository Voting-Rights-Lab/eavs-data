# Rollback Procedures - EAVS Data Pipeline

## When to Use This Guide

Use these procedures if:
- A view update breaks dashboards
- Bad data was loaded and needs to be removed
- You need to undo recent changes to restore working state
- An annual load partially failed and you need to clean up

## Quick Reference

| What Went Wrong | Jump To |
|-----------------|---------|
| Union view update broke dashboards | [Rollback View Update](#rollback-view-update) |
| Bad data loaded to BigQuery tables | [Rollback Data Load](#rollback-data-load) |
| Mart tables showing incorrect data | [Rebuild Mart Tables](#rebuild-mart-tables) |
| Staging tables corrupted | [Refresh Staging Tables](#refresh-staging-tables) |
| Accidentally deleted data | [Restore from Backup](#restore-from-backup) |

---

## Rollback View Update

### Problem
You updated a union view (e.g., `eavs_analytics.eavs_county_reg_union`) and now dashboards are broken or showing wrong data.

### Solution: Use BigQuery View History

BigQuery automatically tracks view versions. You can see and restore previous versions.

#### Step 1: View Version History

1. Open BigQuery Console: https://console.cloud.google.com/bigquery?project=eavs-392800
2. Navigate to the broken view (e.g., `eavs_analytics` → `eavs_county_reg_union`)
3. Click the view name
4. Click **"Details"** tab
5. Scroll to **"Version History"** section

You'll see a list of all changes with timestamps.

#### Step 2: Copy Previous Working Version

1. Find the most recent version BEFORE your change (look at timestamp)
2. Click **"View SQL"** for that version
3. Copy the SQL query

#### Step 3: Restore the View

**Option A: Via Console (Easiest)**
1. Click **"Edit View"** button
2. Paste the copied SQL
3. Click **"Save"**

**Option B: Via Command Line**
```bash
# Save current (broken) view as backup
bq show --format=prettyjson eavs_analytics.eavs_county_reg_union > /tmp/broken_view_backup.json

# Create SQL file with old query (paste from version history)
cat > /tmp/restore_view.sql << 'EOF'
-- Paste the working SQL query here
SELECT ...
EOF

# Update the view
bq update --view "$(cat /tmp/restore_view.sql)" eavs_analytics.eavs_county_reg_union
```

#### Step 4: Verify Fix

```bash
# Test the view
bq query --use_legacy_sql=false \
  "SELECT COUNT(*) FROM \`eavs_analytics.eavs_county_reg_union\`"

# Check dashboards are working
```

#### Step 5: Refresh Dependent Tables

If staging or mart tables depend on this view:

```bash
# Refresh staging table
bq query --use_legacy_sql=false \
  "CREATE OR REPLACE TABLE eavs_analytics.stg_eavs_county_reg_union AS
   SELECT * FROM eavs_analytics.eavs_county_reg_union"

# Refresh mart table
bq query --use_legacy_sql=false \
  "CREATE OR REPLACE TABLE eavs_analytics.mart_eavs_analytics_county_rollup AS
   SELECT * FROM eavs_analytics.eavs_analytics_county_rollup"
```

---

## Rollback Data Load

### Problem
You loaded bad data for a year (e.g., 2024) and need to remove it.

### Solution: Drop and Recreate Tables

#### Step 1: Identify Affected Tables

```bash
# List all tables for the year
bq ls eavs_2024

# Should show: eavs_county_24_a_reg, eavs_county_24_b_uocava, etc.
```

#### Step 2: Delete External Tables

External tables just point to GCS files, so deleting them is safe:

```bash
# Delete all 2024 external tables
bq rm -t eavs_2024.eavs_county_24_a_reg
bq rm -t eavs_2024.eavs_county_24_b_uocava
bq rm -t eavs_2024.eavs_county_24_c_mail
bq rm -t eavs_2024.eavs_county_24_f1_participation
```

#### Step 3: Delete GCS Files (Optional)

If the source CSV files are also bad:

```bash
# List files to delete
gsutil ls gs://eavs-data-files/2024/

# Delete all 2024 files
gsutil rm gs://eavs-data-files/2024/*.csv
```

#### Step 4: Reload Correct Data

```bash
# Re-run the load with correct data
python scripts/load_eavs_year.py 2024 /path/to/correct/data
```

#### Step 5: Update Union Views

Since you removed 2024 data, you may need to:
- Remove 2024 CTEs from union views if it was a partial year
- Or keep them if you successfully reloaded

---

## Rebuild Mart Tables

### Problem
Mart tables (e.g., `mart_eavs_analytics_county_rollup`) are showing incorrect data after changes upstream.

### Solution: Rebuild from Rollup Views

Mart tables are materialized snapshots. Safe to drop and recreate anytime.

#### Step 1: Verify Rollup Views Are Correct

```bash
# Test the source rollup view
bq query --use_legacy_sql=false --dry_run \
  "SELECT COUNT(*) FROM \`eavs_analytics.eavs_analytics_county_rollup\`"
```

#### Step 2: Rebuild Mart Tables

```bash
# Rebuild county rollup
bq query --use_legacy_sql=false \
  "CREATE OR REPLACE TABLE eavs_analytics.mart_eavs_analytics_county_rollup AS
   SELECT * FROM eavs_analytics.eavs_analytics_county_rollup"

# Rebuild state rollup
bq query --use_legacy_sql=false \
  "CREATE OR REPLACE TABLE eavs_analytics.mart_eavs_analytics_state_rollup AS
   SELECT * FROM eavs_analytics.eavs_analytics_state_rollup"
```

#### Step 3: Verify Row Counts

```bash
# Check row counts make sense
bq query --use_legacy_sql=false \
  "SELECT
     'county_rollup' as table_name,
     COUNT(*) as row_count,
     COUNT(DISTINCT election_year) as years
   FROM \`eavs_analytics.mart_eavs_analytics_county_rollup\`
   UNION ALL
   SELECT
     'state_rollup' as table_name,
     COUNT(*) as row_count,
     COUNT(DISTINCT election_year) as years
   FROM \`eavs_analytics.mart_eavs_analytics_state_rollup\`"
```

Expected:
- County rollup: ~15,000-16,000 rows (3,000 counties × 5 years)
- State rollup: ~250-280 rows (50-56 states × 5 years)

---

## Refresh Staging Tables

### Problem
Staging tables (`stg_*`) are out of sync with union views.

### Solution: Recreate from Views

Staging tables cache data from views for performance. Safe to rebuild.

#### Refresh All Staging Tables

```bash
# Registration
bq query --use_legacy_sql=false \
  "CREATE OR REPLACE TABLE eavs_analytics.stg_eavs_county_reg_union AS
   SELECT * FROM eavs_analytics.eavs_county_reg_union"

# UOCAVA
bq query --use_legacy_sql=false \
  "CREATE OR REPLACE TABLE eavs_analytics.stg_eavs_county_uocava_union AS
   SELECT * FROM eavs_analytics.eavs_county_uocava_union"

# Mail
bq query --use_legacy_sql=false \
  "CREATE OR REPLACE TABLE eavs_analytics.stg_eavs_county_mail_union AS
   SELECT * FROM eavs_analytics.eavs_county_mail_union"

# Participation
bq query --use_legacy_sql=false \
  "CREATE OR REPLACE TABLE eavs_analytics.stg_eavs_county_part_union AS
   SELECT * FROM eavs_analytics.eavs_county_part_union"

# ACS Population
bq query --use_legacy_sql=false \
  "CREATE OR REPLACE TABLE eavs_analytics.stg_acs_population_union AS
   SELECT * FROM eavs_analytics.acs_population_union"

# VEP
bq query --use_legacy_sql=false \
  "CREATE OR REPLACE TABLE eavs_analytics.stg_vep_union AS
   SELECT * FROM eavs_analytics.vep_union"
```

Or use the automated script:

```bash
python scripts/load_eavs_year.py 2024 /any --refresh-tables
```

---

## Restore from Backup

### Problem
Data was accidentally deleted or corrupted, and you need to restore from CSV backups.

### Available Backups

Backups are stored in:
```
data/backups/
├── google_sheets/       # Original Google Sheets exports
└── staging_tables/      # BigQuery staging table exports (Dec 4, 2024)
```

#### Step 1: Check What Backups Exist

```bash
# List available backups
ls -lh data/backups/staging_tables/

# Should show files like:
# stg_eavs_county_reg_union_2022_20251204.csv
```

#### Step 2: Load Backup to BigQuery

**Option A: Load to Temporary Table First (Safer)**

```bash
# Load to temp table for verification
bq load --autodetect --source_format=CSV \
  eavs_2022.eavs_county_22_a_reg_temp \
  data/backups/staging_tables/stg_eavs_county_reg_union_2022_20251204.csv

# Verify row count
bq query "SELECT COUNT(*) FROM eavs_2022.eavs_county_22_a_reg_temp"

# If looks good, swap with production
bq cp -f eavs_2022.eavs_county_22_a_reg_temp eavs_2022.eavs_county_22_a_reg
bq rm eavs_2022.eavs_county_22_a_reg_temp
```

**Option B: Direct Restore (Faster)**

```bash
bq load --replace --autodetect --source_format=CSV \
  eavs_2022.eavs_county_22_a_reg \
  data/backups/staging_tables/stg_eavs_county_reg_union_2022_20251204.csv
```

#### Step 3: Refresh Dependent Tables

After restoring data, refresh staging and mart tables (see above sections).

---

## Emergency Contacts

If rollback procedures don't work or you need help:

1. **Check documentation**: Review [CLAUDE.md](../CLAUDE.md) and [PROJECT_STATUS.md](PROJECT_STATUS.md)
2. **Review recent changes**: `git log --oneline -10`
3. **Check BigQuery logs**: https://console.cloud.google.com/logs?project=eavs-392800

---

## Prevention Tips

### Before Making Changes

1. **Test queries with `--dry_run` first**:
   ```bash
   bq query --use_legacy_sql=false --dry_run "CREATE OR REPLACE VIEW ..."
   ```

2. **Save current view definitions**:
   ```bash
   bq show --format=prettyjson eavs_analytics.eavs_county_reg_union > backup_view.json
   ```

3. **Run validation after changes**:
   ```bash
   python scripts/postload_validation.py 2024
   ```

4. **Test on dashboards before announcing**:
   - Check Looker Studio dashboards
   - Verify key metrics look correct
   - Compare to previous year if possible

### After Making Changes

1. **Document what you did**:
   - Update [PROJECT_STATUS.md](PROJECT_STATUS.md)
   - Commit changes with descriptive message

2. **Monitor for issues**:
   - Check dashboard usage for errors
   - Verify query costs haven't spiked

---

## Appendix: Common Commands

### Check View Definition
```bash
bq show --format=prettyjson eavs_analytics.eavs_county_reg_union | grep -A 20 '"view"'
```

### List All Tables in Dataset
```bash
bq ls eavs_analytics
```

### Copy Table (Backup Before Changing)
```bash
bq cp eavs_analytics.stg_eavs_county_reg_union \
      eavs_analytics.stg_eavs_county_reg_union_backup_20241212
```

### Check Table Row Count
```bash
bq query "SELECT COUNT(*) as row_count FROM \`eavs_analytics.stg_eavs_county_reg_union\`"
```

### Dry Run a Query (Test Without Executing)
```bash
bq query --use_legacy_sql=false --dry_run "SELECT * FROM ..."
```
