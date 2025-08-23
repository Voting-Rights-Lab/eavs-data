-- EAVS UOCAVA Data Union View  
-- Combines UOCAVA (military/overseas) voting data across all years with standardized field names

CREATE OR REPLACE VIEW `eavs-392800.eavs_analytics.eavs_county_uocava_union` AS

-- 2016 UOCAVA Data
SELECT 
  fips,
  '2016' as election_year,
  state,
  county, 
  state_abbr,
  county_name,
  {{ uocava_ballots_transmitted_2016 }} as uocava_ballots_transmitted,
  {{ uocava_ballots_returned_2016 }} as uocava_ballots_returned,
  {{ uocava_ballots_counted_2016 }} as uocava_ballots_counted,
  {{ uocava_ballots_rejected_2016 }} as uocava_ballots_rejected,
  {{ uocava_reject_late_2016 }} as uocava_reject_late,
  {{ uocava_reject_signature_2016 }} as uocava_reject_signature,
  {{ uocava_reject_envelope_2016 }} as uocava_reject_envelope,
  {{ uocava_reject_witness_2016 }} as uocava_reject_witness,
  {{ uocava_reject_other_2016 }} as uocava_reject_other
FROM `eavs-392800.eavs_2016.eavs_county_16_b_uocava`

UNION ALL

-- 2018 UOCAVA Data  
SELECT 
  fips,
  '2018' as election_year,
  state,
  county,
  state_abbr, 
  county_name,
  {{ uocava_ballots_transmitted_2018 }} as uocava_ballots_transmitted,
  {{ uocava_ballots_returned_2018 }} as uocava_ballots_returned,
  {{ uocava_ballots_counted_2018 }} as uocava_ballots_counted,
  {{ uocava_ballots_rejected_2018 }} as uocava_ballots_rejected,
  {{ uocava_reject_late_2018 }} as uocava_reject_late,
  {{ uocava_reject_signature_2018 }} as uocava_reject_signature,
  {{ uocava_reject_envelope_2018 }} as uocava_reject_envelope,
  {{ uocava_reject_witness_2018 }} as uocava_reject_witness,
  {{ uocava_reject_other_2018 }} as uocava_reject_other
FROM `eavs-392800.eavs_2018.eavs_county_18_b_uocava`

UNION ALL

-- 2020 UOCAVA Data
SELECT 
  fips,
  '2020' as election_year,
  state,
  county,
  state_abbr,
  county_name, 
  {{ uocava_ballots_transmitted_2020 }} as uocava_ballots_transmitted,
  {{ uocava_ballots_returned_2020 }} as uocava_ballots_returned,
  {{ uocava_ballots_counted_2020 }} as uocava_ballots_counted,
  {{ uocava_ballots_rejected_2020 }} as uocava_ballots_rejected,
  {{ uocava_reject_late_2020 }} as uocava_reject_late,
  {{ uocava_reject_signature_2020 }} as uocava_reject_signature,
  {{ uocava_reject_envelope_2020 }} as uocava_reject_envelope,
  {{ uocava_reject_witness_2020 }} as uocava_reject_witness,
  {{ uocava_reject_other_2020 }} as uocava_reject_other
FROM `eavs-392800.eavs_2020.eavs_county_20_b_uocava`

UNION ALL

-- 2022 UOCAVA Data
SELECT 
  fips,
  '2022' as election_year,
  state,
  county,
  state_abbr,
  county_name,
  {{ uocava_ballots_transmitted_2022 }} as uocava_ballots_transmitted,
  {{ uocava_ballots_returned_2022 }} as uocava_ballots_returned,
  {{ uocava_ballots_counted_2022 }} as uocava_ballots_counted,
  {{ uocava_ballots_rejected_2022 }} as uocava_ballots_rejected,
  {{ uocava_reject_late_2022 }} as uocava_reject_late,
  {{ uocava_reject_signature_2022 }} as uocava_reject_signature,
  {{ uocava_reject_envelope_2022 }} as uocava_reject_envelope,
  {{ uocava_reject_witness_2022 }} as uocava_reject_witness,
  {{ uocava_reject_other_2022 }} as uocava_reject_other
FROM `eavs-392800.eavs_2022.eavs_county_22_b_uocava`

UNION ALL

-- 2024 UOCAVA Data - PENDING RESEARCHER GUIDANCE
-- Has transmission and return data but missing counting/rejection data
-- Need guidance on whether this is methodology change or data issue
SELECT 
  fips,
  '2024' as election_year,
  state,
  county,
  state_abbr,
  county_name,
  {{ uocava_ballots_transmitted_2024 }} as uocava_ballots_transmitted,
  {{ uocava_ballots_returned_2024 }} as uocava_ballots_returned,
  {{ uocava_ballots_counted_2024 }} as uocava_ballots_counted, -- NULL for 2024
  {{ uocava_ballots_rejected_2024 }} as uocava_ballots_rejected, -- NULL for 2024
  {{ uocava_reject_late_2024 }} as uocava_reject_late, -- NULL for 2024
  {{ uocava_reject_signature_2024 }} as uocava_reject_signature, -- NULL for 2024
  {{ uocava_reject_envelope_2024 }} as uocava_reject_envelope, -- NULL for 2024
  {{ uocava_reject_witness_2024 }} as uocava_reject_witness, -- NULL for 2024
  {{ uocava_reject_other_2024 }} as uocava_reject_other -- NULL for 2024
FROM `eavs-392800.eavs_2024.eavs_county_24_b_uocava`