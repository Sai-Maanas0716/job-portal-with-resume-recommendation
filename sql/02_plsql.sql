-- 02_plsql.sql
-- Function, procedures, triggers and a view.
-- In SQL Developer: open the file and press F5 (Run Script).
-- In SQL*Plus: @02_plsql.sql

-- ===============================================================
-- FUNCTION: percentage of a job's required skills a candidate has
-- (this is the "keyword matching done by SQL" part)
-- ===============================================================
CREATE OR REPLACE FUNCTION fn_skill_match_pct (
    p_profile_id IN NUMBER,
    p_job_id     IN NUMBER
) RETURN NUMBER IS
    v_required NUMBER;
    v_matched  NUMBER;
BEGIN
    SELECT COUNT(*) INTO v_required
    FROM job_skills
    WHERE job_id = p_job_id;

    IF v_required = 0 THEN
        RETURN 0;
    END IF;

    SELECT COUNT(*) INTO v_matched
    FROM job_skills js
    JOIN candidate_skills cs ON cs.skill_id = js.skill_id
    WHERE js.job_id = p_job_id
      AND cs.profile_id = p_profile_id;

    RETURN ROUND(v_matched / v_required * 100, 2);
END;
/

-- ===============================================================
-- PROCEDURE: apply to a job
-- final score = 60% semantic score (from Python embeddings)
--             + 40% skill match (from fn_skill_match_pct)
-- ===============================================================
CREATE OR REPLACE PROCEDURE sp_apply_job (
    p_job_id         IN NUMBER,
    p_profile_id     IN NUMBER,
    p_semantic_score IN NUMBER
) IS
    v_skill_pct NUMBER;
    v_final     NUMBER;
BEGIN
    v_skill_pct := fn_skill_match_pct(p_profile_id, p_job_id);
    v_final     := ROUND(0.6 * p_semantic_score + 0.4 * v_skill_pct, 2);

    INSERT INTO applications (job_id, profile_id, match_score, status)
    VALUES (p_job_id, p_profile_id, v_final, 'applied');
END;
/

-- ===============================================================
-- PROCEDURE: SQL pre-filter for a job. Returns candidates who meet the
-- experience and location rules, with their skill match %.
-- Python then ranks these with embeddings.  Uses a REF CURSOR.
-- ===============================================================
CREATE OR REPLACE PROCEDURE sp_get_eligible_candidates (
    p_job_id IN  NUMBER,
    p_result OUT SYS_REFCURSOR
) IS
    v_min_exp  NUMBER;
    v_location VARCHAR2(100);
BEGIN
    SELECT min_experience, location
    INTO   v_min_exp, v_location
    FROM   job_postings
    WHERE  job_id = p_job_id;

    OPEN p_result FOR
        SELECT cp.profile_id,
               u.name,
               cp.experience_years,
               cp.location,
               fn_skill_match_pct(cp.profile_id, p_job_id) AS skill_match_pct,
               cp.summary_embedding
        FROM   candidate_profiles cp
        JOIN   users u ON u.user_id = cp.user_id
        WHERE  cp.experience_years >= v_min_exp
          AND  (cp.location = v_location OR v_location = 'Remote')
          AND  cp.summary_embedding IS NOT NULL;
END;
/

-- ===============================================================
-- PROCEDURE: shortlist every application of a job that scores above a
-- threshold. Uses an explicit cursor with FOR UPDATE / WHERE CURRENT OF.
-- ===============================================================
CREATE OR REPLACE PROCEDURE sp_shortlist_applications (
    p_job_id      IN  NUMBER,
    p_threshold   IN  NUMBER,
    p_shortlisted OUT NUMBER
) IS
    CURSOR c_apps IS
        SELECT application_id, match_score
        FROM   applications
        WHERE  job_id = p_job_id
          AND  status = 'applied'
        FOR UPDATE;
BEGIN
    p_shortlisted := 0;
    FOR r IN c_apps LOOP
        IF r.match_score >= p_threshold THEN
            UPDATE applications
            SET    status = 'shortlisted'
            WHERE CURRENT OF c_apps;
            p_shortlisted := p_shortlisted + 1;
        END IF;
    END LOOP;
END;
/

-- ===============================================================
-- TRIGGER 1: block applications to closed jobs, stamp the apply time
-- ===============================================================
CREATE OR REPLACE TRIGGER trg_app_before_insert
BEFORE INSERT ON applications
FOR EACH ROW
DECLARE
    v_status job_postings.status%TYPE;
BEGIN
    SELECT status INTO v_status
    FROM   job_postings
    WHERE  job_id = :NEW.job_id;

    IF v_status <> 'open' THEN
        RAISE_APPLICATION_ERROR(-20001, 'This job is closed for applications.');
    END IF;

    :NEW.applied_at := SYSDATE;
END;
/

-- ===============================================================
-- TRIGGER 2: write to audit_log whenever a job's status changes
-- ===============================================================
CREATE OR REPLACE TRIGGER trg_job_status_audit
AFTER UPDATE OF status ON job_postings
FOR EACH ROW
BEGIN
    INSERT INTO audit_log (table_name, action, details)
    VALUES ('JOB_POSTINGS', 'STATUS_CHANGE',
            'Job ' || :OLD.job_id || ': ' || :OLD.status || ' -> ' || :NEW.status);
END;
/

-- ===============================================================
-- TRIGGER 3: keep candidate_profiles.last_updated current
-- ===============================================================
CREATE OR REPLACE TRIGGER trg_profile_touch
BEFORE UPDATE ON candidate_profiles
FOR EACH ROW
BEGIN
    :NEW.last_updated := SYSDATE;
END;
/

-- ===============================================================
-- VIEW: applicants of every job, ranked by match score
-- ===============================================================
CREATE OR REPLACE VIEW vw_ranked_applicants AS
SELECT a.application_id,
       a.job_id,
       cp.profile_id,
       u.name  AS candidate_name,
       u.email AS candidate_email,
       cp.experience_years,
       cp.location,
       a.match_score,
       a.status,
       a.applied_at,
       RANK() OVER (PARTITION BY a.job_id ORDER BY a.match_score DESC) AS rank_position
FROM   applications a
JOIN   candidate_profiles cp ON cp.profile_id = a.profile_id
JOIN   users u               ON u.user_id     = cp.user_id;
