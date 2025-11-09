# Google Sheets Dependencies - Risk Assessment

## CRITICAL: Data Fragility Issue Identified

**ALL EAVS data from 2016-2022 is stored in Google Sheets**, making the entire historical dataset vulnerable to accidental deletion.

## Confirmed Google Sheets Tables

### Policy Data
1. **vrl_internal_datasets.policy_2020**
   - URL: https://docs.google.com/spreadsheets/d/17tX1S1SOpCXrDY0_YQX7cw8ILfWUd0TFPmUtIx9Mh4o/edit?usp=sharing
   - Data: State-level voting policies for 2020

2. **vrl_internal_datasets.policy_2022**
   - URL: https://docs.google.com/spreadsheets/d/1f2lteFd5VPC0NbtRXoV3PTboJAHYNzl4FJpcLpGjK0A/edit?usp=sharing
   - Data: State-level voting policies for 2022

### EAVS Data (2016-2022)
All sections (A, B, C, D, E, F1, F2) for years 2016, 2018, 2020, 2022 are stored in Google Sheets:
- **eavs_2016.*** - All tables (registration, UOCAVA, mail, etc.)
- **eavs_2018.*** - All tables
- **eavs_2020.*** - All tables
- **eavs_2022.*** - All tables

Example URLs (truncated):
- 2022: https://docs.google.com/spreadsheets/d/1CvKL6-zHWXx-ehHThlOG9NeYJGSFSsO64DPNf5U-...
- 2020: https://docs.google.com/spreadsheets/d/1qusl0GLrvASdpG8_PJ9pcfVvsgLqDl1n9geCgfyO...

### Safe: 2024 EAVS Data
- **eavs_2024.*** - Stored in GCS bucket (gs://eavs-data-files-2024/)
- **Format**: CSV files in Cloud Storage
- **Status**: ✅ SAFE - Not dependent on Google Sheets

## Risks

1. **Accidental Deletion**: Anyone with edit access to these Sheets can delete them
2. **Permission Changes**: If Sheet permissions change, BigQuery loses access
3. **Sheet Corruption**: Sheets can be corrupted or modified, breaking data integrity
4. **No Version Control**: Changes to Sheets aren't tracked like git
5. **Performance**: Sheets are slower than native BigQuery or GCS

## Impact if Sheets are Deleted

- ❌ All dashboards showing 2016-2022 data will break
- ❌ Historical trend analysis becomes impossible
- ❌ Year-over-year comparisons fail
- ❌ Mart tables and union views return incomplete data
- ❌ No easy recovery without backups

## Immediate Safeguards (Can Do Now)

1. **Document all Sheet URLs** (this file)
2. **Export CSVs as backups** (store in repo or Google Drive)
3. **Restrict Sheet permissions** to view-only for most users
4. **Add warning comments** in Sheets: "DO NOT DELETE - Powers BigQuery dashboards"

## Long-term Solution (Requires Billing Enabled)

### Migration Plan: Google Sheets → BigQuery Native Tables

**Step 1: Export Data**
- Query all Sheets-based tables
- Export to CSV files
- Store in version-controlled location

**Step 2: Load to BigQuery**
- Create native BigQuery tables from CSVs
- OR: Upload CSVs to GCS and create GCS-backed external tables

**Step 3: Update Views**
- Update union views to point to native tables
- Refresh staging tables
- Rebuild mart tables

**Step 4: Verify & Switch**
- Verify all data matches
- Update documentation
- Archive/protect original Sheets (don't delete immediately)

## Recommended Actions

### Immediate (No Billing Required)
- [ ] Export all Google Sheets to CSV backups
- [ ] Store CSVs in repo under `data/backups/google_sheets/`
- [ ] Document all Sheet URLs and owners
- [ ] Add `.gitignore` exception for backup CSVs (important data)
- [ ] Add warnings to Sheet files

### When Billing Enabled
- [ ] Migrate policy tables (2020, 2022, 2024) to native BigQuery
- [ ] Consider migrating EAVS 2016-2022 to GCS (like 2024)
- [ ] Test dashboards with migrated data
- [ ] Update documentation with new sources

## Cost Estimate

**Storage in BigQuery vs Sheets:**
- Google Sheets: Free but fragile
- BigQuery storage: ~$0.02/GB/month (likely <$1/month for all data)
- Query costs: Same regardless of source

**Recommendation**: The tiny cost is worth the reliability and peace of mind.
