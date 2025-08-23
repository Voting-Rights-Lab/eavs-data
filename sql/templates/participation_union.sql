-- EAVS Participation Data Union View
-- Combines voter participation data across all years with standardized field names

CREATE OR REPLACE VIEW `eavs-392800.eavs_analytics.eavs_county_part_union` AS

-- 2016 Participation Data
SELECT 
  fips,
  '2016' as election_year,
  state,
  county, 
  state_abbr,
  county_name,
  {{ total_ballots_cast_2016 }} as total_ballots_cast,
  {{ in_person_ballots_2016 }} as in_person_ballots,
  {{ mail_ballots_cast_2016 }} as mail_ballots_cast,
  {{ provisional_ballots_cast_2016 }} as provisional_ballots_cast,
  {{ early_in_person_2016 }} as early_in_person,
  {{ election_day_in_person_2016 }} as election_day_in_person,
  {{ turnout_rate_2016 }} as turnout_rate,
  {{ voter_participation_rate_2016 }} as voter_participation_rate
FROM `eavs-392800.eavs_2016.eavs_county_16_f1_participation`

UNION ALL

-- 2018 Participation Data  
SELECT 
  fips,
  '2018' as election_year,
  state,
  county,
  state_abbr, 
  county_name,
  {{ total_ballots_cast_2018 }} as total_ballots_cast,
  {{ in_person_ballots_2018 }} as in_person_ballots,
  {{ mail_ballots_cast_2018 }} as mail_ballots_cast,
  {{ provisional_ballots_cast_2018 }} as provisional_ballots_cast,
  {{ early_in_person_2018 }} as early_in_person,
  {{ election_day_in_person_2018 }} as election_day_in_person,
  {{ turnout_rate_2018 }} as turnout_rate,
  {{ voter_participation_rate_2018 }} as voter_participation_rate
FROM `eavs-392800.eavs_2018.eavs_county_18_f1_participation`

UNION ALL

-- 2020 Participation Data
SELECT 
  fips,
  '2020' as election_year,
  state,
  county,
  state_abbr,
  county_name, 
  {{ total_ballots_cast_2020 }} as total_ballots_cast,
  {{ in_person_ballots_2020 }} as in_person_ballots,
  {{ mail_ballots_cast_2020 }} as mail_ballots_cast,
  {{ provisional_ballots_cast_2020 }} as provisional_ballots_cast,
  {{ early_in_person_2020 }} as early_in_person,
  {{ election_day_in_person_2020 }} as election_day_in_person,
  {{ turnout_rate_2020 }} as turnout_rate,
  {{ voter_participation_rate_2020 }} as voter_participation_rate
FROM `eavs-392800.eavs_2020.eavs_county_20_f1_participation`

UNION ALL

-- 2022 Participation Data
SELECT 
  fips,
  '2022' as election_year,
  state,
  county,
  state_abbr,
  county_name,
  {{ total_ballots_cast_2022 }} as total_ballots_cast,
  {{ in_person_ballots_2022 }} as in_person_ballots,
  {{ mail_ballots_cast_2022 }} as mail_ballots_cast,
  {{ provisional_ballots_cast_2022 }} as provisional_ballots_cast,
  {{ early_in_person_2022 }} as early_in_person,
  {{ election_day_in_person_2022 }} as election_day_in_person,
  {{ turnout_rate_2022 }} as turnout_rate,
  {{ voter_participation_rate_2022 }} as voter_participation_rate
FROM `eavs-392800.eavs_2022.eavs_county_22_f1_participation`

UNION ALL

-- 2024 Participation Data
SELECT 
  fips,
  '2024' as election_year,
  state,
  county,
  state_abbr,
  county_name,
  {{ total_ballots_cast_2024 }} as total_ballots_cast,
  {{ in_person_ballots_2024 }} as in_person_ballots,
  {{ mail_ballots_cast_2024 }} as mail_ballots_cast,
  {{ provisional_ballots_cast_2024 }} as provisional_ballots_cast,
  {{ early_in_person_2024 }} as early_in_person,
  {{ election_day_in_person_2024 }} as election_day_in_person,
  {{ turnout_rate_2024 }} as turnout_rate,
  {{ voter_participation_rate_2024 }} as voter_participation_rate
FROM `eavs-392800.eavs_2024.eavs_county_24_f1_participation`