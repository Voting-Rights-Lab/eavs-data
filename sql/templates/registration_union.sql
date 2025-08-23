-- EAVS Registration Data Union View
-- Combines registration data across all years with standardized field names

CREATE OR REPLACE VIEW `eavs-392800.eavs_analytics.eavs_county_reg_union` AS

-- 2016 Registration Data
SELECT 
  fips,
  '2016' as election_year,
  state,
  county, 
  state_abbr,
  county_name,
  {{ total_reg_2016 }} as total_reg,
  {{ active_reg_2016 }} as active_reg,
  {{ inactive_reg_2016 }} as inactive_reg,
  {{ new_reg_2016 }} as new_reg,
  {{ rejected_reg_2016 }} as rejected_reg,
  {{ invalid_reg_2016 }} as invalid_reg,
  {{ duplicate_reg_2016 }} as duplicate_reg,
  {{ dmv_reg_2016 }} as dmv_reg,
  {{ armed_forces_reg_2016 }} as armed_forces_reg,
  {{ public_assistance_reg_2016 }} as public_assistance_reg,
  {{ disability_reg_2016 }} as disability_reg,
  {{ other_reg_2016 }} as other_reg,
  {{ confirmation_notices_sent_2016 }} as confirmation_notices_sent,
  {{ confirmation_responses_received_2016 }} as confirmation_responses_received,
  {{ removals_moved_2016 }} as removals_moved,
  {{ removals_died_2016 }} as removals_died,
  {{ removals_felony_2016 }} as removals_felony,
  {{ removals_mental_2016 }} as removals_mental,
  {{ removals_confirmation_2016 }} as removals_confirmation,
  {{ removals_other_2016 }} as removals_other
FROM `eavs-392800.eavs_2016.eavs_county_16_a_reg`

UNION ALL

-- 2018 Registration Data  
SELECT 
  fips,
  '2018' as election_year,
  state,
  county,
  state_abbr, 
  county_name,
  {{ total_reg_2018 }} as total_reg,
  {{ active_reg_2018 }} as active_reg,
  {{ inactive_reg_2018 }} as inactive_reg,
  {{ new_reg_2018 }} as new_reg,
  {{ rejected_reg_2018 }} as rejected_reg,
  {{ invalid_reg_2018 }} as invalid_reg,
  {{ duplicate_reg_2018 }} as duplicate_reg,
  {{ dmv_reg_2018 }} as dmv_reg,
  {{ armed_forces_reg_2018 }} as armed_forces_reg,
  {{ public_assistance_reg_2018 }} as public_assistance_reg,
  {{ disability_reg_2018 }} as disability_reg,
  {{ other_reg_2018 }} as other_reg,
  {{ confirmation_notices_sent_2018 }} as confirmation_notices_sent,
  {{ confirmation_responses_received_2018 }} as confirmation_responses_received,
  {{ removals_moved_2018 }} as removals_moved,
  {{ removals_died_2018 }} as removals_died,
  {{ removals_felony_2018 }} as removals_felony,
  {{ removals_mental_2018 }} as removals_mental,
  {{ removals_confirmation_2018 }} as removals_confirmation,
  {{ removals_other_2018 }} as removals_other
FROM `eavs-392800.eavs_2018.eavs_county_18_a_reg`

UNION ALL

-- 2020 Registration Data
SELECT 
  fips,
  '2020' as election_year,
  state,
  county,
  state_abbr,
  county_name, 
  {{ total_reg_2020 }} as total_reg,
  {{ active_reg_2020 }} as active_reg,
  {{ inactive_reg_2020 }} as inactive_reg,
  {{ new_reg_2020 }} as new_reg,
  {{ rejected_reg_2020 }} as rejected_reg,
  {{ invalid_reg_2020 }} as invalid_reg,
  {{ duplicate_reg_2020 }} as duplicate_reg,
  {{ dmv_reg_2020 }} as dmv_reg,
  {{ armed_forces_reg_2020 }} as armed_forces_reg,
  {{ public_assistance_reg_2020 }} as public_assistance_reg,
  {{ disability_reg_2020 }} as disability_reg,
  {{ other_reg_2020 }} as other_reg,
  {{ confirmation_notices_sent_2020 }} as confirmation_notices_sent,
  {{ confirmation_responses_received_2020 }} as confirmation_responses_received,
  {{ removals_moved_2020 }} as removals_moved,
  {{ removals_died_2020 }} as removals_died,
  {{ removals_felony_2020 }} as removals_felony,
  {{ removals_mental_2020 }} as removals_mental,
  {{ removals_confirmation_2020 }} as removals_confirmation,
  {{ removals_other_2020 }} as removals_other
FROM `eavs-392800.eavs_2020.eavs_county_20_a_reg`

UNION ALL

-- 2022 Registration Data
SELECT 
  fips,
  '2022' as election_year,
  state,
  county,
  state_abbr,
  county_name,
  {{ total_reg_2022 }} as total_reg,
  {{ active_reg_2022 }} as active_reg,
  {{ inactive_reg_2022 }} as inactive_reg,
  {{ new_reg_2022 }} as new_reg,
  {{ rejected_reg_2022 }} as rejected_reg,
  {{ invalid_reg_2022 }} as invalid_reg,
  {{ duplicate_reg_2022 }} as duplicate_reg,
  {{ dmv_reg_2022 }} as dmv_reg,
  {{ armed_forces_reg_2022 }} as armed_forces_reg,
  {{ public_assistance_reg_2022 }} as public_assistance_reg,
  {{ disability_reg_2022 }} as disability_reg,
  {{ other_reg_2022 }} as other_reg,
  {{ confirmation_notices_sent_2022 }} as confirmation_notices_sent,
  {{ confirmation_responses_received_2022 }} as confirmation_responses_received,
  {{ removals_moved_2022 }} as removals_moved,
  {{ removals_died_2022 }} as removals_died,
  {{ removals_felony_2022 }} as removals_felony,
  {{ removals_mental_2022 }} as removals_mental,
  {{ removals_confirmation_2022 }} as removals_confirmation,
  {{ removals_other_2022 }} as removals_other
FROM `eavs-392800.eavs_2022.eavs_county_22_a_reg`

UNION ALL

-- 2024 Registration Data - PENDING RESEARCHER GUIDANCE
-- Some fields missing in 2024 (confirmation_notices, removals data)
-- Will be updated once methodology changes are clarified
SELECT 
  fips,
  '2024' as election_year,
  state,
  county,
  state_abbr,
  county_name,
  {{ total_reg_2024 }} as total_reg,
  {{ active_reg_2024 }} as active_reg,
  {{ inactive_reg_2024 }} as inactive_reg,
  {{ new_reg_2024 }} as new_reg,
  {{ rejected_reg_2024 }} as rejected_reg,
  {{ invalid_reg_2024 }} as invalid_reg,
  {{ duplicate_reg_2024 }} as duplicate_reg,
  {{ dmv_reg_2024 }} as dmv_reg,
  {{ armed_forces_reg_2024 }} as armed_forces_reg,
  {{ public_assistance_reg_2024 }} as public_assistance_reg,
  {{ disability_reg_2024 }} as disability_reg,
  {{ other_reg_2024 }} as other_reg,
  {{ confirmation_notices_sent_2024 }} as confirmation_notices_sent, -- NULL for 2024
  {{ confirmation_responses_received_2024 }} as confirmation_responses_received, -- NULL for 2024
  {{ removals_moved_2024 }} as removals_moved, -- NULL for 2024
  {{ removals_died_2024 }} as removals_died, -- NULL for 2024
  {{ removals_felony_2024 }} as removals_felony, -- NULL for 2024
  {{ removals_mental_2024 }} as removals_mental, -- NULL for 2024
  {{ removals_confirmation_2024 }} as removals_confirmation, -- NULL for 2024
  {{ removals_other_2024 }} as removals_other -- NULL for 2024
FROM `eavs-392800.eavs_2024.eavs_county_24_a_reg`