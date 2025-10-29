# EAVS Data Pipeline - 2024 Integration Complete

## Current Status: ✅ Production Ready

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

## Project Info

- **BigQuery Project**: eavs-392800
- **Dataset**: eavs_analytics
- **GCS Buckets**: eavs-data-files-{year}
- **Account**: fryda.guedes@contractor.votingrightslab.org
