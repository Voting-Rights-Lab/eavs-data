# Bus Factor Mitigation Guide
## "If Fryda Gets Hit By a Bus" Documentation

**Purpose**: This document ensures someone else can take over the EAVS data pipeline if the primary maintainer (Fryda Guedes) is unavailable.

**Last Updated**: December 12, 2024

---

## TL;DR - Emergency Quick Start

If you need to process EAVS data RIGHT NOW and Fryda is unavailable:

1. **Authenticate**:
   ```bash
   gcloud config configurations activate eavs-data
   # If that doesn't work: gcloud config set account YOUR_EMAIL && gcloud config set project eavs-392800
   ```

2. **Get the data** from Google Drive: https://drive.google.com/drive/folders/1yE4TRNrAj-zL2bLdQAbzr_tvQ3sFTOCs

3. **Run the pipeline**:
   ```bash
   cd /Users/frydaguedes/Projects/eavs-data
   source venv/bin/activate
   python scripts/preflight_validation.py 2026 /path/to/2026/data  # Check first!
   python scripts/load_eavs_year.py 2026 /path/to/2026/data
   ```

4. **Manual step** (required): Update union views in BigQuery Console
   - The script will generate SQL files in `sql/view_updates/`
   - Open BigQuery Console, find each view, paste the SQL
   - Details in [ANNUAL_CHECKLIST.md](ANNUAL_CHECKLIST.md)

5. **Get help**: Read [CLAUDE.md](../CLAUDE.md) for full context, or ask Claude with this file as context

---

## What This System Does

**Purpose**: Processes annual EAVS (Election Administration and Voting Survey) data from CSV files into BigQuery dashboards.

**Who Uses It**: Voting Rights Lab analysts and researchers use Looker Studio dashboards powered by this data.

**How Often**: Once per year when new EAVS data is released (typically processing the previous election year).

**Impact If Broken**: Analysts can't access election data for research and advocacy work. Not real-time critical, but important for organizational mission.

---

## Access & Permissions Needed

### Google Cloud Platform

**Project**: `eavs-392800`

**Account**: Must have BigQuery Admin and Storage Admin roles

**Current Account**: fryda.guedes@contractor.votingrightslab.org

**To Add a Backup Admin**:
1. Go to https://console.cloud.google.com/iam-admin/iam?project=eavs-392800
2. Click "GRANT ACCESS"
3. Add email address
4. Assign roles:
   - BigQuery Admin
   - Storage Admin
5. Save

**Configuration**:
```bash
gcloud config configurations create eavs-data  # If doesn't exist
gcloud config set account YOUR_EMAIL@votingrightslab.org
gcloud config set project eavs-392800
```

### Google Drive

**EAVS Data Folder**: https://drive.google.com/drive/folders/1yE4TRNrAj-zL2bLdQAbzr_tvQ3sFTOCs

**What's There**: Downloaded EAVS CSV files organized by year (2016, 2018, 2020, 2022, 2024, etc.)

**Access**: Make sure backup person has at least "Viewer" access to this folder.

### Looker Studio Dashboards

**Current Owner**: Likely under Fryda's account or a shared VRL account

**Action Needed**: Document dashboard URLs and ensure backup person has edit access.

**TODO**: Add dashboard links here once identified.

---

## The Annual Workflow (Step-by-Step)

### When New Data Arrives

Typically happens in early-to-mid year following an election (e.g., 2026 data arrives in 2027).

### Step 1: Download Data

1. EAVS publishes data (usually to eac.gov or sent via email)
2. Download CSV files
3. Upload to Google Drive folder (link above) for backup
4. Save locally to `/Users/[YOU]/Downloads/2026/` or similar

Typical structure:
```
2026/
├── Section A_ Registration/
│   └── A. Registration.csv
├── Section B_ UOCAVA/
│   └── B. UOCAVA.csv
├── Section C_ Mail/
│   └── C. Absentee _ Mail.csv
└── Section F1_ Participation.../
    └── F1. Participation and Method.csv
```

### Step 2: Check Field Mappings

**Critical**: Field names change every year!

1. Open one of the CSV files
2. Compare headers to `config/field_mappings.yaml`
3. If field names changed:
   ```bash
   # This script will help you identify differences
   python scripts/validate_mappings.py 2026 /path/to/2026/data
   ```
4. Update `config/field_mappings.yaml` with new field names for 2026
5. Map missing fields to `null` (don't guess!)

### Step 3: Run Pre-Flight Validation

```bash
python scripts/preflight_validation.py 2026 /path/to/2026/data
```

This checks:
- CSV files exist and are readable
- Headers match your field mappings
- Basic data quality (row counts, required fields)

Fix any errors before proceeding.

### Step 4: Load Data to BigQuery

```bash
python scripts/load_eavs_year.py 2026 /path/to/2026/data
```

This script:
1. Uploads CSVs to Google Cloud Storage (`gs://eavs-data-files/2026/`)
2. Creates BigQuery external tables in `eavs_2026` dataset
3. Generates SQL for union view updates (saved to `sql/view_updates/`)
4. Validates row counts

Takes 5-15 minutes typically.

### Step 5: Update Union Views (MANUAL - Cannot Be Automated)

**Why Manual**: BigQuery API limitations prevent automated view updates.

For each section (registration, uocava, mail, participation):

1. Open BigQuery Console: https://console.cloud.google.com/bigquery?project=eavs-392800
2. Navigate to `eavs_analytics` dataset
3. Find view: `eavs_county_reg_union` (for registration section)
4. Click view → Click "Edit View"
5. Open generated SQL file: `sql/view_updates/2026_registration_view_update.sql`
6. Copy the new CTE and UNION ALL statement
7. Paste into the view SQL (at the end before final SELECT)
8. Click "Save"
9. Repeat for other sections:
   - `eavs_county_uocava_union`
   - `eavs_county_mail_union`
   - `eavs_county_part_union`

Detailed instructions: [ANNUAL_CHECKLIST.md](ANNUAL_CHECKLIST.md) Step 11

### Step 6: Refresh Materialized Tables

```bash
python scripts/load_eavs_year.py 2026 /any --refresh-tables
```

This rebuilds staging tables (`stg_*`) and mart tables (`mart_*`) with the new data.

Takes 2-5 minutes.

### Step 7: Validate Data Quality

```bash
python scripts/postload_validation.py 2026 --compare-to 2024
```

This checks:
- Row counts are reasonable
- No NULL FIPS codes
- No duplicate counties
- No suspicious negative values
- Year-over-year changes aren't too drastic

### Step 8: Verify Dashboards

1. Open each Looker Studio dashboard
2. Check that 2026 appears in year filters
3. Spot-check a few states to ensure data looks reasonable
4. Compare to previous year for sanity

---

## Key Files & Their Purpose

### Scripts (in `scripts/`)

| Script | Purpose | When to Use |
|--------|---------|-------------|
| `load_eavs_year.py` | Main ETL pipeline | Every annual load |
| `preflight_validation.py` | Pre-load CSV checks | Before loading |
| `postload_validation.py` | Post-load data quality | After loading |
| `validate_mappings.py` | Field mapping validator | When CSVs have different headers |
| `migrate_sheets_backups_to_native.py` | Migrate Google Sheets to native tables | When billing enabled (future) |
| `backup_from_staging_tables.py` | Export backups | Monthly or before major changes |

### Configuration (in `config/`)

| File | Purpose | When to Edit |
|------|---------|--------------|
| `field_mappings.yaml` | Maps CSV columns to standard fields | Every year (field names change!) |

### Documentation (in `docs/` and root)

| File | Purpose |
|------|---------|
| `CLAUDE.md` | **Complete system context** - read this first! |
| `docs/ANNUAL_CHECKLIST.md` | Step-by-step annual load process |
| `docs/DATA_STANDARDS.md` | Data quality standards |
| `docs/PROJECT_STATUS.md` | Current status, what's loaded |
| `docs/ROLLBACK_PROCEDURES.md` | How to undo mistakes |
| `docs/SETUP.md` | Local development setup |
| `docs/BUS_FACTOR_MITIGATION.md` | This file! |
| `GOOGLE_SHEETS_INVENTORY.md` | Known data fragility risks |

### SQL (in `sql/`)

| Directory | Purpose |
|-----------|---------|
| `sql/view_updates/` | Generated SQL for union views (auto-created by script) |
| `sql/manual_updates/` | Manual SQL updates for denominator data |
| `sql/templates/` | Templates for creating SQL |

---

## Common Problems & Solutions

### Problem: "Permission denied" errors

**Cause**: Wrong Google account or insufficient permissions

**Fix**:
```bash
# Check which account is active
gcloud auth list

# Switch to VRL account
gcloud config set account fryda.guedes@contractor.votingrightslab.org

# Or use your own VRL email
gcloud config set account YOUR_EMAIL@votingrightslab.org
```

### Problem: "Field X not found in CSV"

**Cause**: EAVS changed field names for this year

**Fix**:
1. Open the CSV file and look at actual headers
2. Update `config/field_mappings.yaml` for the new year
3. Map old field name to new field name
4. If field doesn't exist in this year, map to `null`

Example:
```yaml
registration_mappings:
  2026:
    total_reg: a1a_total_reg  # If field name changed
    new_field: null  # If field doesn't exist this year
```

### Problem: "Row count looks too low"

**Cause**: CSV file incomplete or corrupted, or wrong file loaded

**Fix**:
1. Check source CSV row count: `wc -l /path/to/file.csv`
2. Expected: ~3,000-3,300 rows (one per county)
3. If low, re-download from source
4. If re-download unavailable, check Google Drive backup

### Problem: "Dashboards show no data for new year"

**Cause**: Forgot to refresh mart tables, or view update wasn't saved

**Fix**:
1. Check union views include new year:
   ```bash
   bq query "SELECT DISTINCT election_year FROM \`eavs_analytics.eavs_county_reg_union\` ORDER BY election_year"
   ```
2. If new year missing, re-do union view update (Step 5 above)
3. If new year present, refresh mart tables:
   ```bash
   python scripts/load_eavs_year.py 2026 /any --refresh-tables
   ```

### Problem: "Google Sheets permission error"

**Cause**: Historical data (2016-2022) still stored in Google Sheets, and you don't have access

**Context**: Known issue documented in `GOOGLE_SHEETS_INVENTORY.md`

**Workaround**: Use CSV backups in `data/backups/staging_tables/`

**Long-term Fix**: Run migration script when billing enabled:
```bash
python scripts/migrate_sheets_backups_to_native.py
```

---

## Important Context & Gotchas

### This is an ANNUAL Pipeline, Not Real-Time

- Runs once per year, sits dormant for 11 months
- Manual steps are OKAY because frequency is low
- Over-automation would add complexity for little benefit

### Field Names Change Every Year

- EAVS survey changes field names between election years
- **Never assume** 2026 fields match 2024 fields
- Always validate with `preflight_validation.py`

### Manual View Updates Are Required

- BigQuery API doesn't support programmatic complex view updates
- Script generates the SQL, but you must paste it manually
- Takes 5-10 minutes, not worth weeks of engineering to automate

### Google Sheets Fragility (2016-2022 Data)

- Historical EAVS data stored in Google Sheets (bad practice, we know)
- Risk: Accidental deletion
- Mitigation: CSV backups in `data/backups/`
- Future: Migrate to native BigQuery tables (script ready, needs billing enabled)

### Billing Has Been an Issue

- Project billing has been disabled in the past
- Affects ability to create new tables
- Workarounds exist (external tables, Google Sheets)
- If billing needed, contact VRL finance/operations

---

## Backup Person Onboarding Checklist

Use this checklist to prepare someone to take over:

### Access & Permissions
- [ ] Added to Google Cloud Project (`eavs-392800`) as BigQuery/Storage Admin
- [ ] Has access to Google Drive EAVS folder
- [ ] Has edit access to Looker Studio dashboards
- [ ] Can authenticate: `gcloud config configurations activate eavs-data`
- [ ] Can run test query: `bq ls eavs_analytics`

### Knowledge Transfer
- [ ] Read [CLAUDE.md](../CLAUDE.md) (comprehensive context)
- [ ] Read [ANNUAL_CHECKLIST.md](ANNUAL_CHECKLIST.md) (step-by-step process)
- [ ] Review `config/field_mappings.yaml` (understand how mappings work)
- [ ] Run a test validation: `python scripts/preflight_validation.py 2024 /path/to/old/data`
- [ ] Practice manual view update in test environment (or on already-loaded year)

### Environment Setup
- [ ] Clone repository: `git clone [repo-url]`
- [ ] Create virtualenv: `python3 -m venv venv && source venv/bin/activate`
- [ ] Install dependencies: `pip install -r requirements.txt`
- [ ] Configure gcloud: Follow [docs/SETUP.md](SETUP.md)
- [ ] Test scripts run without errors

### Emergency Contacts
- [ ] Know who to ask for help at VRL
- [ ] Know who consumes the dashboards (stakeholders)
- [ ] Have Fryda's contact info for emergency questions

---

## Monitoring & Maintenance

### Monthly (or When You Remember)

**Run Backup Script**:
```bash
python scripts/backup_from_staging_tables.py
```

This exports current BigQuery data to CSV backups in `data/backups/staging_tables/`.

**Why**: Protects against Google Sheets fragility and accidental deletions.

### Before Annual Load

**Update Dependencies**:
```bash
pip install --upgrade -r requirements.txt
```

**Pull Latest Code**:
```bash
git pull origin main
```

**Check BigQuery Quotas/Billing**:
- Go to https://console.cloud.google.com/bigquery?project=eavs-392800
- Check no billing warnings
- Verify queries still run

### After Annual Load

**Commit Changes**:
```bash
git add config/field_mappings.yaml  # If updated
git add sql/view_updates/  # Generated SQL
git commit -m "Load 2026 EAVS data"
git push
```

**Update Documentation**:
- Update [docs/PROJECT_STATUS.md](PROJECT_STATUS.md) with new year
- Note any issues encountered for next year

---

## Resources

### External Documentation

- **EAVS Data Source**: https://www.eac.gov/research-and-data/datasets-codebooks-and-surveys
- **BigQuery Docs**: https://cloud.google.com/bigquery/docs
- **Google Cloud Storage**: https://cloud.google.com/storage/docs

### Internal Links

- **Google Drive**: https://drive.google.com/drive/folders/1yE4TRNrAj-zL2bLdQAbzr_tvQ3sFTOCs
- **BigQuery Console**: https://console.cloud.google.com/bigquery?project=eavs-392800
- **GCP IAM**: https://console.cloud.google.com/iam-admin/iam?project=eavs-392800

---

## TODO for Fryda

Make this document even better by adding:

- [ ] Looker Studio dashboard URLs
- [ ] Backup admin account email
- [ ] Stakeholder contact list
- [ ] Git repository URL
- [ ] VRL internal wiki link (if exists)
- [ ] Record a quick screen recording of the annual load process
- [ ] Add to VRL's institutional knowledge base

---

## Final Notes

This system is **pragmatic and fit-for-purpose**. It's not over-engineered because:
- It runs once per year
- Manual steps are acceptable at this frequency
- The team is small
- Budget/resources are limited

Don't try to make it perfect. Make it **understandable** and **repeatable**.

If you're reading this because Fryda is unavailable: You can do this! The documentation exists, the scripts work, and the process is straightforward. Take it one step at a time, and don't hesitate to ask Claude for help with this file as context.

**Good luck! 🚀**
