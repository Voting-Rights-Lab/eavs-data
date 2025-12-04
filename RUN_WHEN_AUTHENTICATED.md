# Run When GCP Authenticated - Action Checklist

## Status: Code Changes Complete ✅ | Testing Required ⏳

All critical code fixes have been implemented. The following steps require GCP/BigQuery authentication to execute.

---

## What Was Completed (No Auth Required)

### ✅ Code Fixes Implemented
1. **Fixed hardcoded GCS bucket** - [scripts/load_eavs_year.py](scripts/load_eavs_year.py#L29-L31)
   - Changed from `eavs-data-files-2024` → `eavs-data-files`
   - Now configurable via `EAVS_GCS_BUCKET` environment variable

2. **Added input validation** - [scripts/load_eavs_year.py](scripts/load_eavs_year.py#L39-L65)
   - Validates year format (4 digits, 2010-2040 range)
   - Prevents SQL injection and typos

3. **Improved error handling** - [scripts/load_eavs_year.py](scripts/load_eavs_year.py#L68-L89)
   - Specific exceptions (NotFound, Forbidden)
   - Actionable error messages with commands to fix

4. **Added SQL validation** - [scripts/load_eavs_year.py](scripts/load_eavs_year.py#L205-L216, L311-L331)
   - BigQuery dry run before updating views
   - Prevents invalid SQL from breaking dashboards

5. **Fixed duplicate column bug** - [scripts/generate_dynamic_unions.py](scripts/generate_dynamic_unions.py#L52-L78)
   - Base fields no longer duplicated in SELECT
   - Also fixed in [scripts/load_eavs_year.py](scripts/load_eavs_year.py#L243-L257)

6. **Created backup script** - [scripts/backup_and_migrate_eavs_sheets.py](scripts/backup_and_migrate_eavs_sheets.py)
   - Backs up all 2016-2022 EAVS data from Google Sheets
   - Migrates to GCS for reliable storage

### ✅ Documentation Created
- [CRITICAL_FIXES_2025-12-04.md](CRITICAL_FIXES_2025-12-04.md) - Detailed fix documentation
- [RUN_WHEN_AUTHENTICATED.md](RUN_WHEN_AUTHENTICATED.md) - This file

---

## What Requires GCP Authentication

### Step 1: Authenticate (5 minutes)

```bash
# Switch to EAVS project account
gcloud auth login fryda.guedes@contractor.votingrightslab.org
gcloud config set project eavs-392800
gcloud auth application-default login

# Verify authentication
gcloud config list
bq ls eavs_2024
```

**Expected:** You should see tables in eavs_2024 dataset

---

### Step 2: Backup Historical Data (30-60 minutes)

#### Critical: This addresses the Google Sheets fragility risk

```bash
# Test with 2022 first (validates script works)
python scripts/backup_and_migrate_eavs_sheets.py --backup-only --years 2022

# Check backups created
ls -lh data/backups/google_sheets/eavs_historical/
# Should see: 2022_A_REG_*.csv, 2022_B_UOCAVA_*.csv, etc.

# Backup remaining years
python scripts/backup_and_migrate_eavs_sheets.py --backup-only --years 2016 2018 2020

# Verify all backups
ls -lh data/backups/google_sheets/eavs_historical/
# Should see 28 CSV files (4 years × 7 sections)
```

**Why this matters:**
- All 2016-2022 EAVS data currently lives in Google Sheets
- One accidental deletion = historical data gone forever
- These backups create a safety net

---

### Step 3: Commit Backups to Git (10 minutes)

```bash
# Check backup file sizes
du -sh data/backups/google_sheets/eavs_historical/

# Add to git (important historical data!)
git add data/backups/google_sheets/eavs_historical/
git add scripts/backup_and_migrate_eavs_sheets.py
git add scripts/load_eavs_year.py
git add scripts/generate_dynamic_unions.py
git add CRITICAL_FIXES_2025-12-04.md
git add RUN_WHEN_AUTHENTICATED.md

# Commit with descriptive message
git commit -m "Critical fixes: Backup historical data and fix pipeline bugs

- Fix hardcoded GCS bucket (will break in 2026)
- Add input validation and SQL injection prevention
- Improve error handling with specific exceptions
- Add SQL validation before updating production views
- Fix duplicate column bug in union SQL generation
- Create backup script for Google Sheets data (2016-2022)
- Backup all EAVS 2016-2022 data (28 tables) as CSV files

Addresses critical reliability and data loss risks identified in code review."

# Push to remote
git push origin main
```

---

### Step 4: Test SQL Validation (15 minutes)

```bash
# Test that new validation catches bad SQL
# This should pass (2024 already loaded)
python scripts/load_eavs_year.py 2024 /Users/frydaguedes/Downloads/2024 --refresh-tables

# Watch for these log messages:
# ✓ SQL validation passed
# ✓ Updated eavs_county_reg_union with 2024 data
```

**What to verify:**
- Script runs without errors
- Materialized tables refresh successfully
- No "SQL validation failed" messages

---

### Step 5: Test Duplicate Column Fix (15 minutes)

```bash
# Regenerate union views with fixed code
python scripts/generate_dynamic_unions.py

# Check generated SQL for duplicates
cat sql/view_updates/*_union.sql | grep -E "state.*state|county.*county"

# Should return EMPTY (no duplicates)

# Manually verify a view
bq show --format=prettyjson eavs_analytics.eavs_county_reg_union | grep view_query
```

**What to verify:**
- No duplicate columns in SELECT statements
- Each field appears only once

---

### Step 6: Migrate Data to GCS (Optional - 1-2 hours)

**When to do this:** After backups are safely committed to git

```bash
# Pilot: Migrate 2022 to GCS
python scripts/backup_and_migrate_eavs_sheets.py --migrate --years 2022

# Script will:
# 1. Backup 2022 data to CSV
# 2. Upload CSV files to gs://eavs-data-files/2022/
# 3. Provide instructions for updating external table URIs

# Follow manual steps to update external tables in BigQuery Console

# Verify migration worked
bq query --use_legacy_sql=false "
  SELECT COUNT(*) as count
  FROM \`eavs-392800.eavs_2022.eavs_county_22_a_reg\`
"
# Should return 3120 rows

# If successful, migrate remaining years
python scripts/backup_and_migrate_eavs_sheets.py --migrate --years 2016 2018 2020
```

**Manual steps after upload:**
1. Open BigQuery Console
2. Navigate to each table (e.g., `eavs_2022.eavs_county_22_a_reg`)
3. Click "Edit Details"
4. Update "Source URI" from Google Sheets URL to GCS URI
5. Save changes
6. Verify queries still work

---

### Step 7: Validate All Changes (30 minutes)

```bash
# 1. Test input validation
python scripts/load_eavs_year.py "abc" /tmp
# Expected: ValueError: Invalid year format

python scripts/load_eavs_year.py "1999" /tmp
# Expected: ValueError: Year 1999 out of expected range

python scripts/load_eavs_year.py "2024" /tmp --refresh-tables
# Expected: Should work (refreshes tables only)

# 2. Query all years in staging tables
bq query --use_legacy_sql=false "
  SELECT election_year, COUNT(*) as counties
  FROM \`eavs-392800.eavs_analytics.stg_eavs_county_reg_union_with_2024\`
  GROUP BY election_year
  ORDER BY election_year
"
# Expected: 2016, 2018, 2020, 2022, 2024 all present

# 3. Check mart tables have 2024
bq query --use_legacy_sql=false "
  SELECT election_year, COUNT(*) as states
  FROM \`eavs-392800.eavs_analytics.mart_eavs_analytics_state_rollup\`
  GROUP BY election_year
  ORDER BY election_year
"
# Expected: 2024 present with 56 states

# 4. Verify Looker Studio dashboard shows 2024 data
# Open: https://lookerstudio.google.com/reporting/7804aa3c-2585-4f6d-a3f4-4e503c99e15b
# Check: Population data shows 2024
```

---

## Success Criteria

### ✅ All steps complete when:
- [ ] Authenticated to eavs-392800 project
- [ ] All 2016-2022 data backed up to CSV (28 files)
- [ ] Backups committed to git and pushed
- [ ] SQL validation tested and working
- [ ] Duplicate column fix verified
- [ ] Input validation tested
- [ ] All staging tables include 2024 data
- [ ] Mart tables rebuilt and include 2024
- [ ] Looker Studio dashboard shows 2024 data

### Optional (but recommended):
- [ ] 2022 data migrated to GCS (pilot)
- [ ] Remaining years migrated to GCS
- [ ] External tables updated to use GCS
- [ ] Google Sheets archived as read-only

---

## Troubleshooting

### Authentication Issues
```bash
# If queries fail with permission errors:
gcloud auth list
# Ensure fryda.guedes@contractor.votingrightslab.org is active

gcloud config get-value project
# Should be: eavs-392800

# Re-authenticate if needed
gcloud auth login fryda.guedes@contractor.votingrightslab.org
gcloud auth application-default login
```

### Backup Script Fails
```bash
# Check if tables exist
bq ls eavs_2022

# Try manual query
bq query --use_legacy_sql=false \
  "SELECT COUNT(*) FROM \`eavs-392800.eavs_2022.eavs_county_22_a_reg\`"

# If permission denied:
# - Check authentication
# - Verify project is eavs-392800
# - Contact GCP admin if needed
```

### Mart Table Not Updated
```bash
# Manually refresh
bq query --use_legacy_sql=false "
  CREATE OR REPLACE TABLE \`eavs-392800.eavs_analytics.mart_eavs_analytics_state_rollup\` AS
  SELECT * FROM \`eavs-392800.eavs_analytics.eavs_analytics_state_rollup\`
"
```

---

## Timeline Estimate

| Step | Time | Can Skip? |
|------|------|-----------|
| 1. Authenticate | 5 min | No |
| 2. Backup data | 30-60 min | No - CRITICAL |
| 3. Commit to git | 10 min | No - CRITICAL |
| 4. Test SQL validation | 15 min | No |
| 5. Test duplicate fix | 15 min | No |
| 6. Migrate to GCS | 1-2 hours | Yes - can do later |
| 7. Validate all | 30 min | No |
| **Total (required)** | **~2 hours** | |
| **Total (with GCS migration)** | **~4 hours** | |

---

## Questions?

- **Code questions:** See [CRITICAL_FIXES_2025-12-04.md](CRITICAL_FIXES_2025-12-04.md)
- **Process questions:** See [CLAUDE.md](CLAUDE.md)
- **Migration questions:** See [GOOGLE_SHEETS_INVENTORY.md](GOOGLE_SHEETS_INVENTORY.md)

---

**Document Created:** 2025-12-04
**Status:** Ready to execute when authenticated
**Priority:** HIGH (backups) + MEDIUM (testing)
