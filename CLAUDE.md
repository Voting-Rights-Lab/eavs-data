# CLAUDE.md - EAVS Data Pipeline Context

Comprehensive background for AI collaboration on the EAVS (Election Administration and Voting Survey) annual data processing pipeline.

## Project Overview

This is a **yearly ETL pipeline** that processes EAVS election data from CSV files into BigQuery for analysis and dashboards. The process runs annually when new EAVS data is released, typically processing 3000+ counties across 50+ states.

**Key Facts:**
- **Yearly cycle**: New data arrives annually, requires processing into existing structure
- **Data volume**: ~3000+ counties per section, multiple sections per year
- **Timeline**: Usually process previous election year (e.g., processing 2024 data in 2025)
- **Output**: BigQuery tables/views feeding Looker Studio dashboards
- **Users**: Voting rights analysts and researchers

## Architecture & Data Flow

```
Local CSV Files (Downloaded from Google Drive)
    ↓ (Python ETL Script)
Google Cloud Storage (eavs-data-files bucket)
    ↓ (BigQuery External Tables)
Year-specific Datasets (eavs_2024, eavs_2022, etc.)
    ↓ (Union Views)
Analytics Dataset (eavs_analytics.*_union views)
    ↓ (Materialized Tables)
Staging Tables (eavs_analytics.stg_*)
    ↓ (Analytics Marts)
Dashboard Tables & Looker Studio
```

### Denominator Data (CVAP/VEP) Architecture

**Legacy (2016-2022):** Google Sheets → External Tables
**New (2024+):** Local CSV → GCS → Native BigQuery Tables (safer, more controlled)

```
Census Bureau / UF Election Lab
    ↓ (Download CSV)
Local CSV Files
    ↓ (bq load or gsutil cp)
GCS Bucket: gs://eavs-data-files/denominators/
    ↓ (bq load or CREATE TABLE)
Native Tables: acs.*, us_elections_vep.*
    ↓ (Union Views)
eavs_analytics.acs_population_union
eavs_analytics.vep_union
    ↓ (Materialized Tables)
eavs_analytics.stg_acs_population_union
eavs_analytics.stg_vep_union
    ↓ (Join with EAVS data on election_year + FIPS/state)
Analytics & Dashboards
```

**Year-Denominator Matching:**
- 2016 election → ACS 2012-2016 5-year CVAP + VEP 2016
- 2018 election → ACS 2014-2018 5-year CVAP + VEP 2018
- 2020 election → ACS 2016-2020 5-year CVAP + VEP 2020
- 2022 election → ACS 2017-2021 5-year CVAP + VEP 2022
- **2024 election → ACS 2019-2023 5-year CVAP + VEP 2024**

**Key Points:**
- **CVAP (County-level)**: Citizen Voting Age Population from Census ACS 5-year estimates (~3,220 counties)
- **VEP (State-level)**: Voting Eligible Population from UF Election Lab (~51 states/DC)
- **Join keys**: CVAP joins on `FIPS`, VEP joins on `state_abbr`, both use `election_year`

**2024 Loaded (Dec 2024):** ✅
- CVAP: 41,886 rows → `acs.acs_2019-2023_county_cvap` (note: no `state` column, extract from `geoname`)
- VEP: 52 rows → `us_elections_vep.vep_2024` (note: columns are `STATE_ABV`, `VEP` - uppercase)
- Views updated, staging/mart tables refreshed

### Data Sections (varies by year)
- **Section A**: Registration - Voter registration statistics
- **Section B**: UOCAVA - Military and overseas voting
- **Section C**: Mail - Absentee/mail ballot data  
- **Section F1**: Participation - Voter turnout by method
- **Others**: Additional sections vary by year

## Core Commands

### Primary Workflow
```bash
# Complete annual load process
python scripts/load_eavs_year.py 2024 /Users/frydaguedes/Downloads/2024

# Refresh materialized tables only
python scripts/load_eavs_year.py 2024 /any/path --refresh-tables
```

### Authentication (run first)
```bash
gcloud auth login fryda.guedes@contractor.votingrightslab.org
gcloud config set project eavs-392800
```

### Validation
```bash
# Check available years in BigQuery
bq query "SELECT DISTINCT election_year FROM \`eavs_analytics.eavs_county_reg_union\` ORDER BY election_year DESC"

# Verify new year loaded
bq query "SELECT COUNT(*) as counties FROM \`eavs_2024.eavs_county_24_a_reg\`"
```

## Technical Constraints & Patterns

### File Structure Expectations
```
2024/                           # Year folder
├── Section A_ Registration/    # Registration data
├── Section B_ UOCAVA/         # Military/overseas  
├── Section C_ Mail/           # Mail voting
├── Section F1_ Participation* # Participation (name varies)
└── (other sections)           # Additional sections vary
```

### Critical Data Rules
1. **Field mappings are year-specific** - column names change between years
2. **Not all sections exist every year** - check what's available
3. **FIPS codes are the primary key** - 5-digit county identifiers
4. **Missing fields must map to NULL** - never guess field names
5. **Preserve original data** - raw tables are never modified

### BigQuery Structure
- **Year datasets**: `eavs_2016`, `eavs_2018`, `eavs_2020`, `eavs_2022`, `eavs_2024`
- **Analytics dataset**: `eavs_analytics` (contains union views)
- **Union views**: `eavs_county_*_union` (all years combined)
- **Staging tables**: `stg_eavs_county_*_union` (materialized for performance)
- **Mart tables**: `mart_eavs_analytics_*_rollup` (dashboard feeds)

## Annual Workflow

### Step 1: Data Acquisition
- Download from Google Drive: https://drive.google.com/drive/folders/1yE4TRNrAj-zL2bLdQAbzr_tvQ3sFTOCs
- Files typically in `/Users/frydaguedes/Downloads/2024/` structure
- Verify expected sections are present

### Step 2: Field Mapping Analysis
**CRITICAL**: Field names change between years. Must analyze actual CSV headers.
- Compare with previous years in `config/field_mappings.yaml`
- Document any new or changed field names
- Map missing fields to `null` (never guess)

### Step 3: Load Data
```bash
python scripts/load_eavs_year.py 2024 /Users/frydaguedes/Downloads/2024
```
This automatically:
- Uploads CSVs to GCS bucket
- Creates BigQuery external tables
- Generates union view update SQL
- Validates row counts

### Step 4: Update Union Views (Manual)
**The script generates SQL but cannot update views directly**
- Check `sql/view_updates/2024_*_view_update.sql` files
- In BigQuery Console, edit each union view
- Add the new CTE and UNION ALL statement
- Save view

### Step 5: Refresh Materialized Tables
```bash
python scripts/load_eavs_year.py 2024 /any/path --refresh-tables
```

### Step 6: Dashboard Verification
- Check Looker Studio dashboards
- Verify 2024 appears in year filters
- Test key visualizations

## Repository Structure

```
eavs-data/
├── scripts/                    # Main pipeline scripts
│   ├── load_eavs_year.py      # Primary ETL script
│   └── validate_mappings.py    # Field validation
├── config/                     # Configuration
│   ├── field_mappings.yaml     # Year-specific field mappings
│   └── corrected_*_mappings.yaml # Corrected mappings
├── sql/                        # SQL files  
│   └── view_updates/           # Generated union view SQL (created by script)
├── docs/                       # Documentation
│   ├── DATA_STANDARDS.md       # Quality standards reference
│   └── ANNUAL_CHECKLIST.md     # Detailed step-by-step guide
├── logs/                       # Processing logs (gitignored)
├── requirements.txt            # Python dependencies
├── CLAUDE.md                   # This context file
└── README.md                   # Human-readable overview
```

## Key Configuration: field_mappings.yaml

This file contains year-specific field mappings since CSV column names change:

```yaml
registration_mappings:
  2024:
    state: state                    # Maps source field to standard name
    county: county
    state_abbr: state_name_abbreviation
    total_reg: a1a_total_reg
    # ... more mappings
  2022:
    state: state
    county: county  
    state_abbr: state_abbr          # Note: different from 2024
    total_reg: total_active_reg     # Note: different field name
```

## Common Issues & Solutions

### Authentication Problems
```bash
gcloud auth list  # Check current account
gcloud auth login fryda.guedes@contractor.votingrightslab.org
```

### Field Mapping Errors
- **Error**: "Column X not found" → Field name changed, update mapping
- **Error**: "NULL values" → Expected if field doesn't exist in that year
- **Fix**: Always validate actual CSV headers first

### Union View Updates Not Working
- Check generated SQL syntax in `sql/view_updates/`
- Verify table names match exactly
- Ensure CTE name is unique
- Confirm UNION ALL is added properly

### Row Count Mismatches
- Compare with source CSV row counts
- Check for data filtering issues
- Verify all expected sections were processed

## Project Context

- **Google Drive Source**: https://drive.google.com/drive/folders/1yE4TRNrAj-zL2bLdQAbzr_tvQ3sFTOCs
- **BigQuery Project**: eavs-392800  
- **GCS Bucket**: eavs-data-files
- **Primary Account**: fryda.guedes@contractor.votingrightslab.org

## Git Practices

**Committed**: Scripts, config, SQL templates, documentation
**NOT Committed**: Raw CSVs, processed data, credentials, logs

**Security**: Never commit data files or credentials. Use .gitignore for data/ and logs/ folders.

# important-instruction-reminders
Do what has been asked; nothing more, nothing less.
NEVER create files unless they're absolutely necessary for achieving your goal.
ALWAYS prefer editing an existing file to creating a new one.
NEVER proactively create documentation files (*.md) or README files. Only create documentation files if explicitly requested by the User.