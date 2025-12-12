-- Manual update for acs_population_union to add 2024 data
-- Run this in BigQuery Console to update the view

-- The acs_2024 CTE for the 2019-2023 CVAP data
-- Note: This table doesn't have a 'state' column, we extract it from geoname
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
    `eavs-392800.acs.acs_2019-2023_county_cvap` )

-- Then in the union_all CTE, add:
    UNION ALL
    SELECT
      *
    FROM
      acs_2024
