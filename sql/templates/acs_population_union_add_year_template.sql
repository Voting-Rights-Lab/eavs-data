-- Template for adding a new year to acs_population_union view
-- Replace YYYY with the election year (e.g., 2024)
-- Replace YYYY-4 to YYYY with the ACS 5-year range (e.g., 2019-2023)

-- Step 1: Add this CTE after the last existing year CTE
  acs_YYYY AS (
  SELECT
    'YYYY' AS election_year,
    GEOID,
    lntitle AS LNTITLE,
    -- NOTE: Check if your Census file has a 'state' or 'State' column
    -- If YES: use "state AS state" or "State AS state"
    -- If NO: extract from geoname with this line:
    TRIM(SPLIT(geoname, ',')[SAFE_OFFSET(1)]) AS state,
    geoname AS county_name,
    tot_est AS acs_total_population,
    adu_est AS acs_adult_population,
    cit_est AS acs_citizen_population,
    cvap_est AS acs_cvap_population
  FROM
    `eavs-392800.acs.acs_YYYY-4-YYYY_county_cvap` ),

-- Step 2: In the union_all CTE, after the last year's SELECT, add:
    UNION ALL
    SELECT
      *
    FROM
      acs_YYYY

-- Example for 2024:
-- Replace YYYY with 2024
-- Replace YYYY-4-YYYY with 2019-2023
-- The 2019-2023 file doesn't have 'state' column, so use SPLIT extraction

-- Example for potential 2026:
-- Replace YYYY with 2026
-- Replace YYYY-4-YYYY with 2021-2025
-- Check if 2021-2025 file has 'state' column and adjust accordingly
