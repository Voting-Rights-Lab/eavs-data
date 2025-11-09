# EAVS Data Pipeline - 2024 Integration Status

## Current Status: ⏸️ BLOCKED - Waiting for Billing Restoration

All 2024 EAVS data has been successfully loaded and integrated into BigQuery. The pipeline is ready for future years.

### Latest Year Loaded: 2024
- **Counties**: 3,126-3,127 per section
- **Sections**: Registration (A), UOCAVA (B), Mail (C), Participation (F1)
- **All rejection/removal fields**: Fully mapped and working

## Quick Reference

### For Next Year's Data Load

1. **Authenticate**:
   ```bash
   gcloud auth login fryda.guedes@contractor.votingrightslab.org
   gcloud config set project eavs-392800
   ```

2. **Load data**:
   ```bash
   python scripts/load_eavs_year.py 2026 /path/to/2026/data
   ```

3. **Update field mappings** if needed:
   - Check `config/field_mappings.yaml`
   - Add new year mappings if field names changed

4. **Regenerate union views**:
   ```bash
   python scripts/generate_dynamic_unions.py
   ```

5. **Rebuild mart tables** (if needed - see notes below)

### 2024 Integration Notes

Due to Google Drive permission limitations on older data sources, we created workaround views:
- `stg_eavs_county_mail_union_with_2024`
- `stg_eavs_county_reg_union_with_2024`
- `stg_eavs_county_uocava_union_with_2024`
- `stg_eavs_county_part_union_with_2024`

The rollup views and mart tables have been updated to use these:
- `eavs_analytics_county_rollup` → uses `*_with_2024` staging tables
- `eavs_analytics_state_rollup` → uses `*_with_2024` staging tables
- `mart_eavs_analytics_county_rollup` → rebuilt with 2024 data
- `mart_eavs_analytics_state_rollup` → rebuilt with 2024 data

**For next year**: If Drive permissions are still an issue, create new `*_with_2026` views following the same pattern, update rollup views, and rebuild marts.

## Key Resources

- **Main loader**: `scripts/load_eavs_year.py`
- **Union generator**: `scripts/generate_dynamic_unions.py`
- **Field config**: `config/field_mappings.yaml`
- **Documentation**: `CLAUDE.md`, `README.md`, `docs/ANNUAL_CHECKLIST.md`

## 🚨 Urgent: Billing Blocker

**Project billing has lapsed** - payment card not working on `eavs-392800`.

**What's blocked:**
- Adding 2024 policy data
- Migrating Google Sheets to safe native tables
- Any data loading operations

**What's ready to execute when billing works:**
- Policy 2024 CSV backed up and ready: `data/backups/google_sheets/policy_2024_backup.csv`
- Script ready to run: `./scripts/add_policy_2024_when_billing_works.sh`
- Migration script ready: `python scripts/migrate_sheets_to_bigquery.py`

**See**: [BLOCKED_WAITING_FOR_BILLING.md](BLOCKED_WAITING_FOR_BILLING.md) for details.

**Action needed**: Someone at organization must restore billing at https://console.cloud.google.com/billing

## Project Info

- **BigQuery Project**: eavs-392800
- **Dataset**: eavs_analytics
- **GCS Buckets**: eavs-data-files-{year}
- **Account**: fryda.guedes@contractor.votingrightslab.org
