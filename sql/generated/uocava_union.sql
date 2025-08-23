-- EAVS eavs_county_uocava_union Union View
-- Automatically generated from config - all years included dynamically
-- DO NOT EDIT - regenerate using scripts/generate_dynamic_unions.py

CREATE OR REPLACE VIEW `eavs-392800.eavs_analytics.eavs_county_uocava_union` AS

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
  b1a_uocava_total_reg as uocava_total_reg,
  b1b_uocava_uniformed_service_total as military_total,
  b1c_uocava_non_military_total as civilian_total,
  b5a_uocava_transmitted_total as uocava_transmitted_total,
  b6a_post_mail_transmitted_total as uocava_mail_transmitted,
  b7a_email_transmitted_total as uocava_email_transmitted,
  b11a_uocava_returned_total as uocava_returned_total,
  b12a_post_mail_returned_total as uocava_mail_returned,
  b13a_email_returned_total as uocava_email_returned,
  NULL as uocava_total_counted,
  NULL as uocava_mail_counted,
  NULL as uocava_email_counted,
  NULL as uocava_total_rejected,
  NULL as uocava_deadline_rejected,
  NULL as uocava_voter_signature_total,
  NULL as uocava_postmark_rejected_total,
  NULL as uocava_other_rejected_total,
  b5b_uniformed_service_transmitted_total as military_transmitted,
  b6b_post_mail_transmitted_uniformed_service as military_mail_transmitted,
  b7b_email_transmitted_uniformed_service as military_email_transmitted,
  b11b_uniformed_service_returned_total as military_returned_total,
  b12b_post_mail_returned_uniformed_service as military_mail_returned,
  b13b_email_returned_uniformed_service as military_email_returned
FROM `eavs-392800.eavs_2024.eavs_county_24_B_UOCAVA`