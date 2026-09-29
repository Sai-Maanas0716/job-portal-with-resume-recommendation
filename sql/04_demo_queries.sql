-- 04_demo_queries.sql
-- Queries you can run live in your viva to show off SQL concepts.

-- 1. JOIN: every open job with its recruiter
SELECT j.job_id, j.title, j.location, u.name AS recruiter
FROM   job_postings j
JOIN   users u ON u.user_id = j.recruiter_id
WHERE  j.status = 'open';

-- 2. Many-to-many JOIN: skills required per job
SELECT j.title, s.skill_name
FROM   job_postings j
JOIN   job_skills js ON js.job_id = j.job_id
JOIN   skills s      ON s.skill_id = js.skill_id
ORDER  BY j.title, s.skill_name;

-- 3. GROUP BY + HAVING: jobs that received at least 2 applications
SELECT j.title, COUNT(*) AS applicants, ROUND(AVG(a.match_score), 2) AS avg_score
FROM   applications a
JOIN   job_postings j ON j.job_id = a.job_id
GROUP  BY j.title
HAVING COUNT(*) >= 2;

-- 4. Skill match percentage using our PL/SQL function
SELECT u.name, j.title, fn_skill_match_pct(cp.profile_id, j.job_id) AS skill_match_pct
FROM   candidate_profiles cp
JOIN   users u ON u.user_id = cp.user_id
CROSS  JOIN job_postings j
ORDER  BY j.title, skill_match_pct DESC;

-- 5. Subquery: candidates who have NOT applied to any job
SELECT u.name
FROM   candidate_profiles cp
JOIN   users u ON u.user_id = cp.user_id
WHERE  cp.profile_id NOT IN (SELECT profile_id FROM applications);

-- 6. Analytic function through the view: ranked applicants per job
SELECT job_id, candidate_name, match_score, rank_position
FROM   vw_ranked_applicants
ORDER  BY job_id, rank_position;

-- 7. Set operation: skills wanted by jobs AND owned by at least one candidate
SELECT skill_id FROM job_skills
INTERSECT
SELECT skill_id FROM candidate_skills;

-- 8. Trigger demo: close a job, then look at the audit log
UPDATE job_postings SET status = 'closed' WHERE job_id = 2;
SELECT * FROM audit_log;
-- Applying to job 2 now raises ORA-20001 (closed job):
--   EXEC sp_apply_job(2, 1, 50);
UPDATE job_postings SET status = 'open' WHERE job_id = 2;
COMMIT;

-- 9. Cursor procedure demo (prints how many were shortlisted)
SET SERVEROUTPUT ON;
DECLARE
    v_count NUMBER;
BEGIN
    sp_shortlist_applications(1, 75, v_count);
    DBMS_OUTPUT.PUT_LINE('Shortlisted: ' || v_count);
    ROLLBACK;
END;
/
