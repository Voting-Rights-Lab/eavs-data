-- EAVS eavs_county_mail_union Union View
-- Automatically generated from config - all years included dynamically
-- DO NOT EDIT - regenerate using scripts/generate_dynamic_unions.py

CREATE OR REPLACE VIEW `eavs-392800.eavs_analytics.eavs_county_mail_union` AS

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
  c1a_mail_transmitted_total as total_mail_transmit,
  c1b_mail_returned_by_voters_total as total_mail_return,
  NULL as total_mail_counted,
  NULL as total_mail_reject,
  NULL as deadline_mail_reject,
  NULL as voter_sign_mail_reject,
  NULL as witness_sign_mail_reject,
  NULL as nonmatch_sign_mail_reject,
  NULL as unofficial_env_mail_reject,
  NULL as EO_sign_missing_mail_reject,
  NULL as missing_ballot_mail_reject,
  NULL as unsealed_env_mail_reject,
  NULL as no_address_mail_reject,
  NULL as multi_ballot_mail_reject,
  NULL as deceased_mail_reject,
  NULL as already_voted_mail_reject,
  NULL as insufficient_ID_mail_reject,
  NULL as no_ballot_app_mail_reject,
  NULL as other_reason_mail_reject
FROM `eavs-392800.eavs_2024.eavs_county_24_C_MAIL`