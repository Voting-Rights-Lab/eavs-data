-- EAVS eavs_county_part_union Union View
-- Automatically generated from config - all years included dynamically
-- DO NOT EDIT - regenerate using scripts/generate_dynamic_unions.py

CREATE OR REPLACE VIEW `eavs-392800.eavs_analytics.eavs_county_part_union` AS

-- 2024 Data
SELECT 
  fips,
  '2024' as election_year,
  state,
  county,
  state_abbr,
  county_name,
  NULL as election_year,
  state as state,
  county as county,
  state_name_abbreviation as state_abbr,
  county_name as county_name,
  f1a_total_voters as total_part,
  f1b_physical_polling_place as election_day_part,
  f1c_absentee_uocava as absentee_uovaca_part,
  f1d_mail_votes as mail_part,
  f1f_in_person_early_voting as in_person_early_part,
  f1g_mail_votes_in_vote_by_mail_jurisdiction as vbm_part,
  f1h_total_participation_other as other_part
FROM `eavs-392800.eavs_2024.eavs_county_24_F1_PARTICIPATION`