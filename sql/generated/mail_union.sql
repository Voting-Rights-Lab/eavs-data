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
  c8a_total_mail_ballots_counted as total_mail_counted,
  c9a_total_mail_ballots_rejected as total_mail_reject,
  c9b_mail_ballots_rejected_because_late as deadline_mail_reject,
  c9c_mail_ballots_rejected_because_missing_voter_signature as voter_sign_mail_reject,
  c9d_mail_ballots_rejected_because_missing_witness_signature as witness_sign_mail_reject,
  c9e_mail_ballots_rejected_because_non_matching_voter_signature as nonmatch_sign_mail_reject,
  c9f_mail_ballots_rejected_because_unofficial_envelope as unofficial_env_mail_reject,
  NULL as EO_sign_missing_mail_reject,
  c9g_mail_ballots_rejected_because_ballot_missing_from_envelope as missing_ballot_mail_reject,
  c9j_mail_ballots_rejected_because_envelope_not_sealed as unsealed_env_mail_reject,
  c9l_mail_ballots_rejected_because_no_resident_address_on_envelope as no_address_mail_reject,
  c9i_mail_ballots_rejected_because_multiple_ballots_in_one_envelope as multi_ballot_mail_reject,
  c9m_mail_ballots_rejected_because_voter_deceased as deceased_mail_reject,
  c9n_mail_ballots_rejected_because_voter_already_voted as already_voted_mail_reject,
  c9o_mail_ballots_rejected_because_missing_documentation as insufficient_ID_mail_reject,
  c9q_mail_ballots_rejected_because_no_ballot_application as no_ballot_app_mail_reject,
  (c9r_mail_ballots_rejected_other_1 + c9s_mail_ballots_rejected_other_2 + c9t_mail_ballots_rejected_other_3) as other_reason_mail_reject
FROM `eavs-392800.eavs_2024.eavs_county_24_C_MAIL`