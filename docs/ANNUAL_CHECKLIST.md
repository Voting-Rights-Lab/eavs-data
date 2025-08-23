# EAVS Annual Data Loading Checklist

## Pre-Load Preparation
- [ ] Download EAVS data files from source
- [ ] Verify folder structure matches expected pattern:
  ```
  2024/
  ├── Section A_ Registration/
  ├── Section B_ UOCAVA/
  ├── Section C_ Mail/
  ├── Section F1_ Participation*/
  └── (other sections if available)
  ```
- [ ] Authenticate with Google Cloud:
  ```bash
  gcloud auth login fryda.guedes@contractor.votingrightslab.org
  gcloud config set project eavs-392800
  ```

## Step 1: Load Data
- [ ] Run the loader script:
  ```bash
  python load_eavs_year.py 2024 /Users/frydaguedes/Downloads/2024
  ```
- [ ] Verify output shows successful uploads for expected sections
- [ ] Check that row counts are reasonable (typically 3000+ rows per section)

## Step 2: Update Union Views
For each section that was loaded:

### Registration View (`eavs_analytics.eavs_county_reg_union`)
- [ ] Open `sql/view_updates/2024_a_reg_view_update.sql`
- [ ] Copy the CTE section
- [ ] In BigQuery Console:
  - [ ] Navigate to `eavs_analytics.eavs_county_reg_union`
  - [ ] Click "Edit Query"
  - [ ] Add the new CTE after the last year's CTE
  - [ ] Add the UNION ALL statement at the end
  - [ ] Click "Save View"

### UOCAVA View (`eavs_analytics.eavs_county_uocava_union`)
- [ ] Open `sql/view_updates/2024_b_uocava_view_update.sql`
- [ ] Follow same steps as Registration

### Mail View (`eavs_analytics.eavs_county_mail_union`)
- [ ] Open `sql/view_updates/2024_c_mail_view_update.sql`
- [ ] Follow same steps as Registration

### Participation View (`eavs_analytics.eavs_county_part_union`)
- [ ] Open `sql/view_updates/2024_f1_participation_view_update.sql`
- [ ] Follow same steps as Registration

## Step 3: Refresh Materialized Tables
- [ ] Run refresh command:
  ```bash
  python load_eavs_year.py 2024 /any/path --refresh-tables
  ```
- [ ] Verify all staging tables updated successfully

## Step 4: Create Analytics Mart Tables (if needed)
In BigQuery Console, run:
```sql
-- Only if these need refreshing
CREATE OR REPLACE TABLE `eavs_analytics.mart_eavs_analytics_county_rollup` AS
SELECT * FROM `eavs_analytics.eavs_analytics_county_rollup`;

CREATE OR REPLACE TABLE `eavs_analytics.mart_eavs_analytics_state_rollup` AS
SELECT * FROM `eavs_analytics.eavs_analytics_state_rollup`;
```

## Step 5: Validation
- [ ] Query new year data:
  ```sql
  SELECT DISTINCT election_year 
  FROM `eavs_analytics.stg_eavs_county_reg_union`
  ORDER BY election_year DESC;
  -- Should show 2024 at top
  ```
- [ ] Check row counts for new year:
  ```sql
  SELECT 
    election_year,
    COUNT(*) as county_count,
    COUNT(DISTINCT state) as state_count
  FROM `eavs_analytics.stg_eavs_county_reg_union`
  WHERE election_year = '2024'
  GROUP BY election_year;
  -- Should show ~3000+ counties, 50+ states
  ```

## Step 6: Dashboard Updates
- [ ] Open Looker Studio dashboards
- [ ] Refresh data sources if needed
- [ ] Verify 2024 data appears in year filters
- [ ] Test a few visualizations with 2024 selected

## Troubleshooting

### If data doesn't appear in views:
- Check that the CTE was added correctly (no syntax errors)
- Verify the table names match exactly
- Ensure UNION ALL was added

### If materialized tables fail:
- Check that views were saved successfully first
- Look for any data type mismatches in new year
- Review error messages in BigQuery query history

### If row counts seem wrong:
- Check the source CSV files
- Verify no filters were accidentally applied
- Ensure all expected sections were uploaded

## Notes for Next Year
- Update this checklist with any new sections or changes
- Note any field name changes in the config file
- Document any special handling required