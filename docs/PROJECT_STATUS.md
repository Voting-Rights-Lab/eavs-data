# EAVS Data Pipeline - Project Status

**Last Updated**: December 12, 2024
**Current Status**: ✅ Production Ready - 2024 Data Loaded

## Quick Stats

- **Latest Year**: 2024 (loaded Dec 2024)
- **Counties**: 3,126-3,127 per section
- **States**: 56 (including territories)
- **Sections**: Registration (A), UOCAVA (B), Mail (C), Participation (F1)
- **Dashboard Status**: All Looker Studio dashboards showing 2024 data

## Recent Milestones

### December 2024: 2024 Data Integration ✅
- Loaded all 2024 EAVS data (4 sections)
- Loaded 2024 denominators (CVAP, VEP)
- Updated all union views and staging tables
- Refreshed mart tables for dashboards
- All quality checks passed

### November 2024: Critical Fixes ✅
- Fixed hardcoded GCS bucket issue
- Added input validation and SQL injection prevention
- Improved error handling with actionable messages
- Migrated 2024 policy data from Google Sheets to native BigQuery tables
- Created CSV backups for disaster recovery
- Fixed duplicate column bug in SQL generation

## Current Architecture

```
CSV Files → GCS (eavs-data-files) → BigQuery External Tables
  → Year Datasets (eavs_2016 - eavs_2024)
  → Union Views (eavs_analytics.*_union)
  → Staging Tables (stg_*)
  → Mart Tables (mart_*_rollup)
  → Looker Studio Dashboards
```

## Known Issues & Technical Debt

### High Priority

1. **Google Sheets Dependency (2016-2022 EAVS Data)**
   - **Status**: ⚠️ Active Risk
   - **Impact**: Historical data vulnerable to accidental deletion/permission changes
   - **Mitigation**: CSV backups exist in `data/backups/google_sheets/`
   - **Plan**: Migrate to BigQuery native tables when budget allows (~$12/year)
   - **See**: [GOOGLE_SHEETS_INVENTORY.md](../GOOGLE_SHEETS_INVENTORY.md)

2. **Bus Factor = 1**
   - **Status**: ⚠️ Risk
   - **Impact**: Only one person (Fryda) knows the system
   - **Mitigation Needed**: Documentation, knowledge transfer
   - **Plan**: See Bus Factor Mitigation section below

### Medium Priority

3. **Manual View Updates Required**
   - **Status**: ⏸️ Accepted Limitation
   - **Reason**: BigQuery API limitations for complex view updates
   - **Workaround**: Scripts generate SQL, human pastes into BigQuery Console
   - **Impact**: Adds 5-10 minutes to annual load process

4. **No Automated Testing**
   - **Status**: ⏸️ Accepted for Now
   - **Reason**: Annual execution, manual testing sufficient at current scale
   - **Trade-off**: Maintenance burden of tests > benefit for 1x/year run

## Data Quality

### Validation Checks (Automated)
- ✅ Row counts after load
- ✅ BigQuery table existence
- ✅ SQL syntax validation (dry-run before execution)
- ✅ Year format and range validation
- ✅ File structure checks

### Validation Checks (Manual)
- Dashboard spot-checks
- State-level totals verification
- Year-over-year trend validation
- FIPS code coverage checks

### Missing Validations (Future Enhancement)
- Null percentage checks
- Outlier detection
- Referential integrity (EAVS ↔ CVAP/VEP)
- Data type validation

## Next Annual Load (2026)

### Preparation Checklist
1. Download 2026 EAVS data from Google Drive
2. Check for field name changes (update `config/field_mappings.yaml`)
3. Authenticate: `gcloud auth login`
4. Run load script: `python scripts/load_eavs_year.py 2026 /path/to/data`
5. Manually update union views in BigQuery Console
6. Refresh staging tables: `python scripts/load_eavs_year.py 2026 /any --refresh-tables`
7. Rebuild mart tables (see `sql/manual_updates/refresh_mart_tables_*.sql`)
8. Verify dashboards show 2026 data

### Common Issues
- **Field names changed**: Update field_mappings.yaml
- **New section added**: Add to config, update scripts
- **Drive permission error**: Check authentication, verify sharing settings
- **Row count mismatch**: Compare source CSV row counts to BigQuery

## Bus Factor Mitigation

### Critical Knowledge Transfer Needs

1. **Annual Load Process**
   - Step-by-step documented in [docs/ANNUAL_CHECKLIST.md](ANNUAL_CHECKLIST.md)
   - Field mapping logic in [CLAUDE.md](../CLAUDE.md)
   - Common issues in this file (above)

2. **Google Cloud Access**
   - Account: fryda.guedes@contractor.votingrightslab.org
   - Project: eavs-392800
   - Required IAM roles: BigQuery Admin, Storage Admin
   - **TODO**: Add backup admin account

3. **Google Drive Access**
   - EAVS data source: https://drive.google.com/drive/folders/1yE4TRNrAj-zL2bLdQAbzr_tvQ3sFTOCs
   - **TODO**: Ensure backup person has access

4. **Dashboard Access**
   - Looker Studio dashboards (URLs not documented - **TODO**: add links)
   - **TODO**: Ensure backup person has edit access

### Emergency Contacts
- **Primary**: Fryda Guedes (fryda.guedes@contractor.votingrightslab.org)
- **Backup**: **TODO**: Assign backup person
- **Stakeholders**: Voting Rights Lab analysts (consume dashboards)

## System Health Indicators

### Green (Healthy) ✅
- 2024 data loaded and validated
- All dashboards operational
- Documentation up to date
- Recent hardening (Dec 2024) tested and working

### Yellow (Monitoring) ⚠️
- Google Sheets dependency (2016-2022) - have backups
- Bus factor = 1 - need knowledge transfer
- No automated alerts - acceptable for annual cycle

### Red (Action Required) ❌
- None currently

## Resources

### Documentation
- [CLAUDE.md](../CLAUDE.md) - Comprehensive AI collaboration context
- [README.md](../README.md) - Quick start guide
- [docs/ANNUAL_CHECKLIST.md](ANNUAL_CHECKLIST.md) - Step-by-step load process
- [docs/DATA_STANDARDS.md](DATA_STANDARDS.md) - Quality standards
- [GOOGLE_SHEETS_INVENTORY.md](../GOOGLE_SHEETS_INVENTORY.md) - Fragility risk documentation
- [TODO.md](../TODO.md) - Current status and next steps

### Key Scripts
- `scripts/load_eavs_year.py` - Main ETL script
- `scripts/load_denominators_2024.py` - CVAP/VEP data loader
- `scripts/validate_mappings.py` - Field mapping validator
- `scripts/backup_from_staging_tables.py` - Create CSV backups

### Configuration
- `config/field_mappings.yaml` - Year-specific field mappings
- `.env.example` - Environment variable template

## Archive

Previous status files consolidated into this document:
- FINAL_SUMMARY.txt (Dec 4, 2024)
- MISSION_ACCOMPLISHED.md (Dec 4, 2024)
- TEST_RESULTS.md (Dec 4, 2024)

All documented the same Dec 2024 critical fixes that are now reflected above.
