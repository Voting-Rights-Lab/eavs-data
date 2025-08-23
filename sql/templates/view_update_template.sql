-- Template for adding a new year to a union view
-- Replace {YEAR} with the actual year (e.g., 2024)
-- Replace {SECTION} with the section name (e.g., registration, mail, uocava, participation)

-- Step 1: Add this CTE to the existing view (before the final union_all CTE)
  {SECTION}_{YEAR} AS (
  SELECT
    '{YEAR}' AS election_year,
    -- Copy field mappings from generated SQL file
    -- ...fields here...
  FROM
    `eavs_{YEAR}.eavs_county_{YR}_{SECTION_TABLE}`
  ),

-- Step 2: Add this to the UNION ALL section (inside the union_all CTE)
UNION ALL
SELECT * FROM {SECTION}_{YEAR}

-- Step 3: Update the final SELECT to add FIPS if needed
select
  concat(state, LPAD(cast(county as string), 3, '0')) AS fips,
  union_all.*
from union_all