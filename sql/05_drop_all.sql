-- 05_drop_all.sql
-- Use this to reset the database and start again from 01_schema.sql.
-- (Errors like "table does not exist" are fine if you run it twice.)

DROP VIEW vw_ranked_applicants;
DROP PROCEDURE sp_apply_job;
DROP PROCEDURE sp_get_eligible_candidates;
DROP PROCEDURE sp_shortlist_applications;
DROP FUNCTION fn_skill_match_pct;

DROP TABLE audit_log CASCADE CONSTRAINTS;
DROP TABLE applications CASCADE CONSTRAINTS;
DROP TABLE job_skills CASCADE CONSTRAINTS;
DROP TABLE candidate_skills CASCADE CONSTRAINTS;
DROP TABLE skills CASCADE CONSTRAINTS;
DROP TABLE job_postings CASCADE CONSTRAINTS;
DROP TABLE candidate_profiles CASCADE CONSTRAINTS;
DROP TABLE users CASCADE CONSTRAINTS;
