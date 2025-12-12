-- COMPLETE SQL to update vep_union view with 2024 data
-- Instructions:
-- 1. Go to BigQuery Console: https://console.cloud.google.com/bigquery?project=eavs-392800
-- 2. Navigate to: eavs_analytics > vep_union
-- 3. Click "Edit Query"
-- 4. At the very beginning after "with ", add the vep_2024 CTE below
-- 5. Find the first "select * from vep_YYYY" and add UNION before it
-- 6. Click "Save"

-- ============= ADD THIS CTE AT THE BEGINNING (after "with ") =============
  vep_2024 as (
  select
  "2024" as election_year,
  STATE_ABV as state_abbr,  -- Column is UPPERCASE in 2024 file
  VEP as VEP                 -- Column is just "VEP", not "Voting_Eligible_Population__VEP_"
  from
  `eavs-392800.us_elections_vep.vep_2024`

  ),

-- ============= ADD THIS BEFORE THE FIRST select * from vep_YYYY =============
    select * from vep_2024
    UNION ALL

-- NOTE: The 2024 VEP file from UF Election Lab changed column naming:
-- - Previous files: State_Abv, Voting_Eligible_Population__VEP_
-- - 2024 file: STATE_ABV (uppercase), VEP (shortened)
--
-- The new file also includes additional columns:
-- - TOTAL_BALLOTS_COUNTED, VAP, NONCITIZEN_PCT
-- - INELIGIBLE_PRISON, INELIGIBLE_PROBATION, INELIGIBLE_PAROLE
-- - INELIGIBLE_FELONS_TOTAL, ELIGIBLE_OVERSEAS
-- - VEP_TURNOUT_RATE, VAP_TURNOUT_RATE
--
-- We only select STATE_ABV and VEP to match the existing union view structure
