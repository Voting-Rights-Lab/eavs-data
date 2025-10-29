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
  b18a_uocava_counted_total as uocava_total_counted,
  b19a_postal_mail_counted_total as uocava_mail_counted,
  b20a_email_counted_total as uocava_email_counted,
  b24a_uocava_rejected_total as uocava_total_rejected,
  b25a_deadline_rejected_total as uocava_deadline_rejected,
  b26a_signature_rejected_total as uocava_voter_signature_total,
  b27a_postmark_rejected_total as uocava_postmark_rejected_total,
  b28a_other_rejected_total as uocava_other_rejected_total,
  b5b_uniformed_service_transmitted_total as military_transmitted,
  b6b_post_mail_transmitted_uniformed_service as military_mail_transmitted,
  b7b_email_transmitted_uniformed_service as military_email_transmitted,
  b11b_uniformed_service_returned_total as military_returned_total,
  b12b_post_mail_returned_uniformed_service as military_mail_returned,
  b13b_email_returned_uniformed_service as military_email_returned,
  b18b_uniformed_service_counted_total as military_counted_total,
  b19b_postal_mail_counted_uniformed_service as military_mail_counted,
  b20b_email_counted_uniformed_service as military_email_counted,
  b24b_uniformed_service_rejected_total as military_rejected_total,
  b25b_deadline_rejected_uniformed_service as military_deadline_rejected,
  b26b_signature_rejected_uniformed_service as military_signature_rejected,
  b27b_postmark_rejected_uniformed_service as military_postmark_rejected,
  b28b_other_rejected_uniformed_service as military_other_rejected
FROM `eavs-392800.eavs_2024.eavs_county_24_B_UOCAVA`