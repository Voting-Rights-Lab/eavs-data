# 2024 EAVS Data Transformation Plan

## Current BigQuery Pattern
Based on analysis of 2016-2022 data:

### 1. Year-Specific Datasets
Each election year gets its own dataset (e.g., `eavs_2022`)

### 2. External Tables
CSV files are loaded as EXTERNAL tables pointing to Google Cloud Storage:
- `eavs_county_22_a_reg` (Registration)
- `eavs_county_22_b_uocava` (UOCAVA)
- `eavs_county_22_c_mail` (Mail voting)
- `eavs_county_22_d_polls` (Polling places) - *Not in 2024*
- `eavs_county_22_e_provisional` (Provisional) - *Not in 2024*
- `eavs_county_22_f1_participation` (Participation)
- `eavs_county_22_f2_tech` (Technology) - *Not in 2024*

### 3. Union Views in `eavs_analytics`
Views that union all years together with standardized column names:
- `eavs_county_reg_union`
- `eavs_county_uocava_union`
- `eavs_county_mail_union`
- `eavs_county_part_union`
- `eavs_county_prov_union`

### 4. Materialized Tables
For performance, views are materialized as tables:
- `stg_eavs_county_reg_union`
- `stg_eavs_county_mail_union`
- `stg_eavs_county_part_union`
- `stg_eavs_county_uocava_union`

## 2024 Implementation Steps

### Step 1: Upload CSV files to Google Cloud Storage
```bash
# Create GCS bucket or folder for 2024 data
gsutil mb -p eavs-392800 gs://eavs-data-2024/
# Or use existing bucket structure

# Upload CSV files
gsutil cp "/Users/frydaguedes/Downloads/2024/Section A_ Registration/EAVS_county_24_A_REG.csv" gs://eavs-data-2024/
gsutil cp "/Users/frydaguedes/Downloads/2024/Section B_ UOCAVA/EAVS_county_24_B_UOCAVA.csv" gs://eavs-data-2024/
gsutil cp "/Users/frydaguedes/Downloads/2024/Section C_ Mail/EAVS_county_24_C_MAIL.csv" gs://eavs-data-2024/
gsutil cp "/Users/frydaguedes/Downloads/2024/Section F1_ Participation and Method/EAVS_county_24_F1_PARTICIPATION.csv" gs://eavs-data-2024/
```

### Step 2: Create eavs_2024 dataset
```sql
CREATE SCHEMA IF NOT EXISTS `eavs-392800.eavs_2024`
OPTIONS(
  description="2024 EAVS County-level data",
  location="US"
);
```

### Step 3: Create External Tables
```sql
-- Registration table
CREATE OR REPLACE EXTERNAL TABLE `eavs-392800.eavs_2024.eavs_county_24_a_reg`
OPTIONS (
  format = 'CSV',
  uris = ['gs://eavs-data-2024/EAVS_county_24_A_REG.csv'],
  skip_leading_rows = 1,
  allow_jagged_rows = false,
  allow_quoted_newlines = true
);

-- Similar for B_UOCAVA, C_MAIL, F1_PARTICIPATION
```

### Step 4: Update Union Views
Add 2024 CTEs to each union view following the pattern:

```sql
registration_2024 AS (
  SELECT
    '2024' AS election_year,
    state,
    county,
    state_name_abbreviation AS state_abbr,
    county_name,
    a1a_total_reg AS total_reg,
    a1b_total_active as total_active_reg,
    a1c_total_inactive as total_inactive_reg,
    -- Map all fields following 2022 pattern
  FROM
    `eavs_2024.eavs_county_24_a_reg`
)
```

### Step 5: Recreate Materialized Tables
After updating views, refresh the staging tables:
```sql
CREATE OR REPLACE TABLE `eavs_analytics.stg_eavs_county_reg_union` AS
SELECT * FROM `eavs_analytics.eavs_county_reg_union`;
```

## Field Mapping Considerations

### Consistent fields across years:
- Geographic identifiers (fips, state, county)
- Core metrics (total registrations, active/inactive)

### Fields that may need special handling:
- Column name changes between years
- New fields in 2024 not present in earlier years
- Missing sections (D, E, F2) in 2024

## Automation Opportunities

1. **Python script to automate the process:**
   - Upload CSVs to GCS
   - Create external tables
   - Generate SQL for view updates
   - Run materialization queries

2. **Configuration-driven approach:**
   - YAML file with field mappings
   - Template SQL files
   - Reusable for future years

## Next Steps

1. Confirm GCS bucket location for 2024 data
2. Test with Section A (Registration) first
3. Validate data quality against 2022
4. Update all union views
5. Recreate materialized tables
6. Update Looker Studio dashboards if needed