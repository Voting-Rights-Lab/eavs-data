-- Template for adding a new year to vep_union view
-- Replace YYYY with the election year (e.g., 2024)

-- Step 1: Add this CTE at the beginning (after "with ")
  vep_YYYY as (
  select
  "YYYY" as election_year,
  -- NOTE: Check column names in your VEP file - they may vary!
  -- Common variations:
  --   - State_Abv, STATE_ABV, state_abbr
  --   - Voting_Eligible_Population__VEP_, VEP
  -- Use the actual column names from your file:
  STATE_ABV as state_abbr,  -- Adjust case if needed
  VEP as VEP                 -- Adjust name if needed
  from
  `eavs-392800.us_elections_vep.vep_YYYY`

  ),

-- Step 2: At the beginning of the UNION statements, add:
    select * from vep_YYYY
    UNION ALL

-- Example for 2024:
-- Column names in 2024 file are UPPERCASE: STATE_ABV and VEP

-- Example for potential 2026:
-- Check if UF Election Lab changes column naming in their exports
-- Adjust STATE_ABV and VEP column names accordingly
