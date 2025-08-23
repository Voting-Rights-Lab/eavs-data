-- EAVS Mail Voting Data Union View
-- Combines mail voting data across all years with standardized field names

CREATE OR REPLACE VIEW `eavs-392800.eavs_analytics.eavs_county_mail_union` AS

-- 2016 Mail Data
SELECT 
  fips,
  '2016' as election_year,
  state,
  county, 
  state_abbr,
  county_name,
  {{ mail_ballots_sent_2016 }} as mail_ballots_sent,
  {{ mail_ballots_returned_2016 }} as mail_ballots_returned,
  {{ mail_ballots_rejected_2016 }} as mail_ballots_rejected,
  {{ reject_signature_2016 }} as reject_signature,
  {{ reject_late_2016 }} as reject_late,
  {{ reject_envelope_2016 }} as reject_envelope,
  {{ reject_witness_2016 }} as reject_witness,
  {{ reject_ballot_missing_2016 }} as reject_ballot_missing,
  {{ reject_no_record_2016 }} as reject_no_record,
  {{ reject_other_2016 }} as reject_other,
  NULL as drop_box_ballots, -- New field not in 2016
  NULL as ballot_curing_offered, -- New field not in 2016
  NULL as ballot_curing_accepted -- New field not in 2016
FROM `eavs-392800.eavs_2016.eavs_county_16_c_mail`

UNION ALL

-- 2018 Mail Data  
SELECT 
  fips,
  '2018' as election_year,
  state,
  county,
  state_abbr, 
  county_name,
  {{ mail_ballots_sent_2018 }} as mail_ballots_sent,
  {{ mail_ballots_returned_2018 }} as mail_ballots_returned,
  {{ mail_ballots_rejected_2018 }} as mail_ballots_rejected,
  {{ reject_signature_2018 }} as reject_signature,
  {{ reject_late_2018 }} as reject_late,
  {{ reject_envelope_2018 }} as reject_envelope,
  {{ reject_witness_2018 }} as reject_witness,
  {{ reject_ballot_missing_2018 }} as reject_ballot_missing,
  {{ reject_no_record_2018 }} as reject_no_record,
  {{ reject_other_2018 }} as reject_other,
  NULL as drop_box_ballots, -- New field not in 2018
  NULL as ballot_curing_offered, -- New field not in 2018
  NULL as ballot_curing_accepted -- New field not in 2018
FROM `eavs-392800.eavs_2018.eavs_county_18_c_mail`

UNION ALL

-- 2020 Mail Data
SELECT 
  fips,
  '2020' as election_year,
  state,
  county,
  state_abbr,
  county_name, 
  {{ mail_ballots_sent_2020 }} as mail_ballots_sent,
  {{ mail_ballots_returned_2020 }} as mail_ballots_returned,
  {{ mail_ballots_rejected_2020 }} as mail_ballots_rejected,
  {{ reject_signature_2020 }} as reject_signature,
  {{ reject_late_2020 }} as reject_late,
  {{ reject_envelope_2020 }} as reject_envelope,
  {{ reject_witness_2020 }} as reject_witness,
  {{ reject_ballot_missing_2020 }} as reject_ballot_missing,
  {{ reject_no_record_2020 }} as reject_no_record,
  {{ reject_other_2020 }} as reject_other,
  NULL as drop_box_ballots, -- New field not in 2020
  NULL as ballot_curing_offered, -- New field not in 2020
  NULL as ballot_curing_accepted -- New field not in 2020
FROM `eavs-392800.eavs_2020.eavs_county_20_c_mail`

UNION ALL

-- 2022 Mail Data
SELECT 
  fips,
  '2022' as election_year,
  state,
  county,
  state_abbr,
  county_name,
  {{ mail_ballots_sent_2022 }} as mail_ballots_sent,
  {{ mail_ballots_returned_2022 }} as mail_ballots_returned,
  {{ mail_ballots_rejected_2022 }} as mail_ballots_rejected,
  {{ reject_signature_2022 }} as reject_signature,
  {{ reject_late_2022 }} as reject_late,
  {{ reject_envelope_2022 }} as reject_envelope,
  {{ reject_witness_2022 }} as reject_witness,
  {{ reject_ballot_missing_2022 }} as reject_ballot_missing,
  {{ reject_no_record_2022 }} as reject_no_record,
  {{ reject_other_2022 }} as reject_other,
  NULL as drop_box_ballots, -- New field not in 2022
  NULL as ballot_curing_offered, -- New field not in 2022
  NULL as ballot_curing_accepted -- New field not in 2022
FROM `eavs-392800.eavs_2022.eavs_county_22_c_mail`

UNION ALL

-- 2024 Mail Data - PENDING RESEARCHER GUIDANCE
-- Major structural change: detailed rejection reasons replaced with drop box/curing data
-- Need guidance on whether to keep old rejection fields NULL or add new fields
SELECT 
  fips,
  '2024' as election_year,
  state,
  county,
  state_abbr,
  county_name,
  {{ mail_ballots_sent_2024 }} as mail_ballots_sent,
  {{ mail_ballots_returned_2024 }} as mail_ballots_returned,
  {{ mail_ballots_rejected_2024 }} as mail_ballots_rejected,
  {{ reject_signature_2024 }} as reject_signature, -- NULL for 2024
  {{ reject_late_2024 }} as reject_late, -- NULL for 2024
  {{ reject_envelope_2024 }} as reject_envelope, -- NULL for 2024
  {{ reject_witness_2024 }} as reject_witness, -- NULL for 2024
  {{ reject_ballot_missing_2024 }} as reject_ballot_missing, -- NULL for 2024
  {{ reject_no_record_2024 }} as reject_no_record, -- NULL for 2024
  {{ reject_other_2024 }} as reject_other, -- NULL for 2024
  {{ drop_box_ballots_2024 }} as drop_box_ballots, -- New in 2024
  {{ ballot_curing_offered_2024 }} as ballot_curing_offered, -- New in 2024
  {{ ballot_curing_accepted_2024 }} as ballot_curing_accepted -- New in 2024
FROM `eavs-392800.eavs_2024.eavs_county_24_c_mail`