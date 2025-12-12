-- COMPLETE SQL to update acs_population_union view with 2024 data
-- Instructions:
-- 1. Go to BigQuery Console: https://console.cloud.google.com/bigquery?project=eavs-392800
-- 2. Navigate to: eavs_analytics > acs_population_union
-- 3. Click "Edit Query"
-- 4. Find the acs_2021 CTE (around line 59)
-- 5. After the closing ) and comma, add the acs_2024 CTE below
-- 6. Find the union_all CTE and add the UNION for acs_2024
-- 7. Click "Save"

-- ============= ADD THIS CTE AFTER acs_2021 =============
  acs_2024 AS (
  SELECT
    '2024' AS election_year,
    GEOID,
    lntitle AS LNTITLE,
    TRIM(SPLIT(geoname, ',')[SAFE_OFFSET(1)]) AS state,  -- Extract state from "County, State" format
    geoname AS county_name,
    tot_est AS acs_total_population,
    adu_est AS acs_adult_population,
    cit_est AS acs_citizen_population,
    cvap_est AS acs_cvap_population
  FROM
    `eavs-392800.acs.acs_2019-2023_county_cvap` ),

-- ============= ADD THIS IN union_all CTE AFTER acs_2021 =============
    UNION ALL
    SELECT
      *
    FROM
      acs_2024

-- NOTE: The 2019-2023 Census CVAP file structure changed:
-- - No longer has a 'state' or 'State' column
-- - Must extract state from geoname field which is formatted as "County Name, State Name"
-- - Uses TRIM(SPLIT(geoname, ',')[SAFE_OFFSET(1)]) to extract state name
--
-- This differs from previous years (2016-2022) which had a direct 'State' column
