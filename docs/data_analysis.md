# EAVS Data Analysis

## Data Structure Comparison: 2022 vs 2024

### Common Sections (present in both years):
- **Section A: Registration** - Voter registration data
- **Section B: UOCAVA** - Uniformed and Overseas Citizens Absentee Voting Act data  
- **Section C: Mail** - Mail voting/absentee ballot data
- **Section F1: Participation** - Voter participation statistics

### Sections only in 2022 (missing from 2024):
- **Section D: Polling Places** - Physical polling location data
- **Section E: Provisional** - Provisional ballot data
- **Section F2: Voting Technology** - Voting equipment and technology data

### 2024 Unique Features:
- Section F1 renamed to "Participation and Method" (was just "Participation" in 2022)
- Includes Policy Survey data in documentation folder
- Has supplemental CVAP (Citizen Voting Age Population) data

## File Types per Section:
Each section typically contains:
- CSV data file (e.g., `EAVS_county_24_A_REG.csv`)
- R script file for processing
- Codebook CSV explaining variables
- Some 2022 sections also have Excel versions

## Key Identifiers:
All data files include standard geographic identifiers:
- `fips` - Federal Information Processing Standards code
- `state_name_full` / `state_name_abbreviation`
- `county` / `county_name`

## Row Counts:
- Section A Registration: 4,323 rows (likely one per county/jurisdiction)

## Next Steps:
1. Connect to BigQuery to examine existing transformation views
2. Understand how previous years were processed
3. Design ETL pipeline for loading 2024 data
4. Handle missing sections appropriately