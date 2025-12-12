-- Manual update for vep_union to add 2024 data
-- Run this in BigQuery Console to update the view

-- The vep_2024 CTE
-- Note: Column names are UPPERCASE in the 2024 file
  vep_2024 as (
  select
  "2024" as election_year,
  STATE_ABV as state_abbr,  -- Note: UPPERCASE in new file
  VEP as VEP                 -- Note: UPPERCASE, not Voting_Eligible_Population__VEP_
  from
  `eavs-392800.us_elections_vep.vep_2024`

  )

-- Then at the beginning of the UNION statements, add:
    select * from vep_2024
    UNION ALL
