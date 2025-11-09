# Manual Steps to Add Policy 2024 Data (No Billing Required)

## Background
CLI commands are blocked by billing restrictions, but the BigQuery Console UI sometimes allows operations that the CLI doesn't.

## Steps to Try in BigQuery Console

### Option 1: Create External Table via UI

1. **Open BigQuery Console**: https://console.cloud.google.com/bigquery?project=eavs-392800

2. **Navigate to dataset**: `vrl_internal_datasets`

3. **Click "Create Table"** (or "+ CREATE TABLE" button)

4. **Configure the table:**
   - **Source**:
     - Create table from: `Drive`
     - Drive URI: `https://docs.google.com/spreadsheets/d/1J6SjY3aCcZyuhnHKP-MFxpcYLd1OcdASCCXq9609htM`
     - File format: `Google Sheets`

   - **Destination**:
     - Project: `eavs-392800`
     - Dataset: `vrl_internal_datasets`
     - Table: `policy_2024`
     - Table type: `External table`

   - **Schema**: `Auto detect` (check this box)

5. **Click "Create Table"**

### Option 2: Run SQL in Console

If Option 1 doesn't work, try running this SQL in the BigQuery Console query editor:

```sql
CREATE OR REPLACE EXTERNAL TABLE `eavs-392800.vrl_internal_datasets.policy_2024`
OPTIONS (
  format = 'GOOGLE_SHEETS',
  uris = ['https://docs.google.com/spreadsheets/d/1J6SjY3aCcZyuhnHKP-MFxpcYLd1OcdASCCXq9609htM'],
  skip_leading_rows = 1
);
```

## If Both Fail (Billing Required)

If the UI also requires billing, we'll need to:
1. Store policy_24.csv in git backups for safekeeping
2. Document what needs to happen when billing is enabled
3. Dashboards won't show 2024 policy data until billing is enabled

## After Table is Created

Once the external table exists, run these commands to integrate it:

```bash
# 1. Update the policy union view (I'll do this)
# 2. Refresh staging table
bq query --project_id=eavs-392800 --use_legacy_sql=false \
  "CREATE OR REPLACE TABLE eavs_analytics.stg_policy_union AS
   SELECT * FROM eavs_analytics.policy_unioned"

# 3. Rebuild mart tables
bq query --project_id=eavs-392800 --use_legacy_sql=false \
  "CREATE OR REPLACE TABLE eavs_analytics.mart_eavs_analytics_county_rollup AS
   SELECT * FROM eavs_analytics.eavs_analytics_county_rollup"

bq query --project_id=eavs-392800 --use_legacy_sql=false \
  "CREATE OR REPLACE TABLE eavs_analytics.mart_eavs_analytics_state_rollup AS
   SELECT * FROM eavs_analytics.eavs_analytics_state_rollup"
```

## Alternative: Try Creating via API

If you have access to the Google Cloud Console, you might be able to create the table via the API Explorer which sometimes has different permissions.

## Last Resort: Manual Looker Studio Connection

If BigQuery won't allow the table creation at all without billing, you could:
1. Connect Looker Studio directly to the Google Sheet
2. Join it manually with the EAVS data in Looker Studio
3. This is less elegant but works without BigQuery changes
