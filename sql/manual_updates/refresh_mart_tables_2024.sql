-- Refresh Mart Tables to Include 2024 Denominator Data
-- Run these queries in BigQuery Console after updating denominator staging tables
-- Each query will take 30-60 seconds to complete

-- ============================================
-- 1. Refresh County-Level Mart Table
-- ============================================
-- This creates the main analytics table that dashboards use
-- Joins EAVS data with CVAP/VEP denominators

CREATE OR REPLACE TABLE `eavs-392800.eavs_analytics.mart_eavs_analytics_county_rollup` AS
SELECT * FROM `eavs-392800.eavs_analytics.eavs_analytics_county_rollup`;

-- Wait for this to complete before running the next one
-- Expected: ~16,000 rows (3,220 counties × 5 years)

-- ============================================
-- 2. Refresh State-Level Mart Table
-- ============================================
-- This aggregates county data to state level
-- Joins with state-level VEP data

CREATE OR REPLACE TABLE `eavs-392800.eavs_analytics.mart_eavs_analytics_state_rollup` AS
SELECT * FROM `eavs-392800.eavs_analytics.eavs_analytics_state_rollup`;

-- Expected: ~255 rows (51 states/territories × 5 years)

-- ============================================
-- 3. Validation Query
-- ============================================
-- Check that 2024 data is present with denominators

SELECT
  election_year,
  COUNT(*) as county_count,
  COUNT(DISTINCT state_abbr) as state_count,
  COUNT(DISTINCT CASE WHEN acs_cvap_population IS NOT NULL THEN FIPS END) as counties_with_cvap,
  AVG(CASE WHEN total_reg > 0 AND acs_cvap_population > 0
      THEN total_reg / acs_cvap_population * 100 END) as avg_registration_rate
FROM `eavs-392800.eavs_analytics.mart_eavs_analytics_county_rollup`
WHERE election_year IN ('2022', '2024')
GROUP BY election_year
ORDER BY election_year;

-- Expected results:
-- 2022: ~3,220 counties, 50+ states, with CVAP data
-- 2024: ~3,220 counties, 50+ states, with CVAP data
-- Both should have reasonable registration rates (70-100%)
