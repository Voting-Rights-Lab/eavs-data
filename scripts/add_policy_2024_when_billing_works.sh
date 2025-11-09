#!/bin/bash
# Add 2024 Policy Data to BigQuery
# Run this script ONCE billing is restored on eavs-392800 project

set -e

PROJECT_ID="eavs-392800"
POLICY_CSV="/Users/frydaguedes/Projects/eavs-data/data/backups/google_sheets/policy_2024_backup.csv"

echo "================================================"
echo "Adding 2024 Policy Data to BigQuery"
echo "Project: $PROJECT_ID"
echo "================================================"

# Step 1: Check if billing works
echo ""
echo "Step 1: Checking if billing is enabled..."
if bq query --project_id=$PROJECT_ID --use_legacy_sql=false --dry_run \
  "CREATE TABLE test_billing (test STRING)" 2>&1 | grep -q "Billing has not been enabled"; then
  echo "❌ ERROR: Billing is still not enabled!"
  echo "Please enable billing first: https://console.cloud.google.com/billing"
  exit 1
fi
echo "✅ Billing is active!"

# Step 2: Load CSV to BigQuery
echo ""
echo "Step 2: Loading policy_2024.csv to BigQuery..."
bq load \
  --project_id=$PROJECT_ID \
  --autodetect \
  --replace \
  --source_format=CSV \
  vrl_internal_datasets.policy_2024 \
  "$POLICY_CSV"
echo "✅ policy_2024 table created!"

# Step 3: Verify data loaded
echo ""
echo "Step 3: Verifying data..."
ROW_COUNT=$(bq query --project_id=$PROJECT_ID --use_legacy_sql=false --format=csv \
  "SELECT COUNT(*) as count FROM \`$PROJECT_ID.vrl_internal_datasets.policy_2024\`" | tail -n 1)
echo "✅ Loaded $ROW_COUNT states"

# Step 4: Update policy union view
echo ""
echo "Step 4: Updating policy_unioned view..."
bq query --project_id=$PROJECT_ID --use_legacy_sql=false <<'EOF'
CREATE OR REPLACE VIEW `eavs-392800.eavs_analytics.policy_unioned` AS
with policy_2020 as (
  select
  '2020' as election_year,
  STATE as state_abbr,
  cast(OVR as boolean) as OVR,
  cast(SDR as boolean) as SDR,
  cast(EDR as boolean) as EDR,
  cast(NO_EX_MAIL as boolean) as NO_EX_MAIL,
  cast(STATEWIDE_All_MAIL as boolean) as STATEWIDE_ALL_MAIL,
  cast(NULL as boolean) as DROP_BOXES,
  cast(NULL as boolean) as CURE,
  cast(NO_EX_EARLY_IN_PERSON as boolean) as NO_EX_EARLY_IN_PERSON,
  cast(PROVISIONAL as boolean) as PROVISIONAL,
  ID
  from `eavs-392800.vrl_internal_datasets.policy_2020`
),

policy_2022 as (
  select
  '2022' as election_year,
  STATE as state_abbr,
  cast(OVR as boolean) as OVR,
  cast(SDR as boolean) as SDR,
  cast(EDR as boolean) as EDR,
  cast(NO_EX_MAIL as boolean) as NO_EX_MAIL,
  cast(STATEWIDE_All_MAIL as boolean) as STATEWIDE_ALL_MAIL,
  cast(DROP_BOXES as boolean) as DROP_BOXES,
  cast(CURE as boolean) as CURE,
  cast(NO_EX_EARLY_IN_PERSON as boolean) as NO_EX_EARLY_IN_PERSON,
  cast(PROVISIONAL as boolean) as PROVISIONAL,
  ID
  from `eavs-392800.vrl_internal_datasets.policy_2022`
),

policy_2024 as (
  select
  '2024' as election_year,
  STATE as state_abbr,
  case when OVR = 'YES' then true when OVR = 'NO' then false else null end as OVR,
  case when SDR = 'YES' then true when SDR = 'NO' then false else null end as SDR,
  case when EDR = 'YES' then true when EDR = 'NO' then false else null end as EDR,
  case when NO_EX_MAIL = 'YES' then true when NO_EX_MAIL = 'NO' then false else null end as NO_EX_MAIL,
  case when STATEWIDE_All_MAIL = 'YES' then true when STATEWIDE_All_MAIL = 'NO' then false else null end as STATEWIDE_ALL_MAIL,
  case when DROP_BOXES = 'YES' then true when DROP_BOXES = 'NO' then false else null end as DROP_BOXES,
  case when CURE = 'YES' then true when CURE = 'NO' then false else null end as CURE,
  case when NO_EX_EARLY_IN_PERSON = 'YES' then true when NO_EX_EARLY_IN_PERSON = 'NO' then false else null end as NO_EX_EARLY_IN_PERSON,
  case when PROVISIONAL = 'YES' then true when PROVISIONAL = 'NO' then false else null end as PROVISIONAL,
  ID
  from `eavs-392800.vrl_internal_datasets.policy_2024`
),

unioned as (
  select * from policy_2020
  union all
  select * from policy_2022
  union all
  select * from policy_2024
)

select * from unioned
EOF
echo "✅ policy_unioned view updated!"

# Step 5: Refresh staging table
echo ""
echo "Step 5: Refreshing stg_policy_union..."
bq query --project_id=$PROJECT_ID --use_legacy_sql=false \
  "CREATE OR REPLACE TABLE \`eavs-392800.eavs_analytics.stg_policy_union\` AS
   SELECT * FROM \`eavs-392800.eavs_analytics.policy_unioned\`"
echo "✅ Staging table refreshed!"

# Step 6: Rebuild mart tables
echo ""
echo "Step 6: Rebuilding mart tables (this may take a minute)..."
bq query --project_id=$PROJECT_ID --use_legacy_sql=false \
  "CREATE OR REPLACE TABLE \`eavs-392800.eavs_analytics.mart_eavs_analytics_county_rollup\` AS
   SELECT * FROM \`eavs-392800.eavs_analytics.eavs_analytics_county_rollup\`"
echo "✅ County rollup rebuilt!"

bq query --project_id=$PROJECT_ID --use_legacy_sql=false \
  "CREATE OR REPLACE TABLE \`eavs-392800.eavs_analytics.mart_eavs_analytics_state_rollup\` AS
   SELECT * FROM \`eavs-392800.eavs_analytics.eavs_analytics_state_rollup\`"
echo "✅ State rollup rebuilt!"

# Step 7: Verify 2024 data in marts
echo ""
echo "Step 7: Verifying 2024 policy data in mart tables..."
COUNTY_2024=$(bq query --project_id=$PROJECT_ID --use_legacy_sql=false --format=csv \
  "SELECT COUNT(*) as count FROM \`eavs-392800.eavs_analytics.mart_eavs_analytics_county_rollup\`
   WHERE election_year = '2024' AND has_SDR_policy IS NOT NULL" | tail -n 1)

echo "✅ Found $COUNTY_2024 counties with 2024 policy data in mart table"

# Summary
echo ""
echo "================================================"
echo "✅ SUCCESS! 2024 Policy Data Added"
echo "================================================"
echo ""
echo "Next steps:"
echo "1. Open your Looker Studio dashboards"
echo "2. Verify 2024 appears in year filters"
echo "3. Check that policy filters (SDR, EDR, etc.) work for 2024"
echo ""
echo "If dashboards don't update immediately, try:"
echo "- Refresh the data source in Looker Studio"
echo "- Clear browser cache"
echo "- Wait a few minutes for BigQuery cache to clear"
echo "================================================"
