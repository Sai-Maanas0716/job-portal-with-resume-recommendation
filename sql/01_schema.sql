-- 01_schema.sql
-- Tables, constraints and indexes for the Smart Job Portal (3NF).
-- Needs Oracle 12c or newer (identity columns). Run as the "jobportal" user.

-- ---------------------------------------------------------------
-- USERS  (one table for both roles: candidate / recruiter)
-- ---------------------------------------------------------------
CREATE TABLE users (
    user_id        NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name           VARCHAR2(100) NOT NULL,
    email          VARCHAR2(150) NOT NULL UNIQUE,
    password_hash  VARCHAR2(64)  NOT NULL,
    user_role      VARCHAR2(10)  NOT NULL
                   CONSTRAINT chk_user_role CHECK (user_role IN ('candidate', 'recruiter')),
    created_at     DATE DEFAULT SYSDATE NOT NULL
);

-- ---------------------------------------------------------------
-- CANDIDATE_PROFILES  (1:1 with a candidate user)
-- summary_embedding stores the resume vector as a JSON text
-- ---------------------------------------------------------------
CREATE TABLE candidate_profiles (
    profile_id         NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    user_id            NUMBER NOT NULL UNIQUE,
    resume_text        CLOB NOT NULL,
    experience_years   NUMBER(2) DEFAULT 0 NOT NULL
                       CONSTRAINT chk_exp_years CHECK (experience_years >= 0),
    location           VARCHAR2(100) DEFAULT 'Bengaluru' NOT NULL,
    portfolio_url      VARCHAR2(300),
    summary_embedding  CLOB,
    last_updated       DATE DEFAULT SYSDATE NOT NULL,
    CONSTRAINT fk_profile_user FOREIGN KEY (user_id)
        REFERENCES users (user_id) ON DELETE CASCADE
);

-- ---------------------------------------------------------------
-- JOB_POSTINGS  (posted by a recruiter user)
-- ---------------------------------------------------------------
CREATE TABLE job_postings (
    job_id           NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    recruiter_id     NUMBER NOT NULL,
    title            VARCHAR2(150) NOT NULL,
    description      CLOB NOT NULL,
    min_experience   NUMBER(2) DEFAULT 0 NOT NULL
                     CONSTRAINT chk_min_exp CHECK (min_experience >= 0),
    salary           NUMBER(10) NOT NULL
                     CONSTRAINT chk_salary CHECK (salary > 0),
    location         VARCHAR2(100) NOT NULL,
    status           VARCHAR2(10) DEFAULT 'open' NOT NULL
                     CONSTRAINT chk_job_status CHECK (status IN ('open', 'closed')),
    job_embedding    CLOB,
    posted_at        DATE DEFAULT SYSDATE NOT NULL,
    CONSTRAINT fk_job_recruiter FOREIGN KEY (recruiter_id)
        REFERENCES users (user_id) ON DELETE CASCADE
);

-- ---------------------------------------------------------------
-- SKILLS and the two M:N junction tables
-- ---------------------------------------------------------------
CREATE TABLE skills (
    skill_id    NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    skill_name  VARCHAR2(60) NOT NULL UNIQUE
);

CREATE TABLE candidate_skills (
    profile_id  NUMBER NOT NULL,
    skill_id    NUMBER NOT NULL,
    CONSTRAINT pk_candidate_skills PRIMARY KEY (profile_id, skill_id),
    CONSTRAINT fk_cs_profile FOREIGN KEY (profile_id)
        REFERENCES candidate_profiles (profile_id) ON DELETE CASCADE,
    CONSTRAINT fk_cs_skill FOREIGN KEY (skill_id)
        REFERENCES skills (skill_id) ON DELETE CASCADE
);

CREATE TABLE job_skills (
    job_id    NUMBER NOT NULL,
    skill_id  NUMBER NOT NULL,
    CONSTRAINT pk_job_skills PRIMARY KEY (job_id, skill_id),
    CONSTRAINT fk_js_job FOREIGN KEY (job_id)
        REFERENCES job_postings (job_id) ON DELETE CASCADE,
    CONSTRAINT fk_js_skill FOREIGN KEY (skill_id)
        REFERENCES skills (skill_id) ON DELETE CASCADE
);

-- ---------------------------------------------------------------
-- APPLICATIONS  (candidate applies to a job; stores the AI match score)
-- ---------------------------------------------------------------
CREATE TABLE applications (
    application_id  NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    job_id          NUMBER NOT NULL,
    profile_id      NUMBER NOT NULL,
    match_score     NUMBER(5,2) DEFAULT 0 NOT NULL
                    CONSTRAINT chk_match_score CHECK (match_score BETWEEN 0 AND 100),
    status          VARCHAR2(12) DEFAULT 'applied' NOT NULL
                    CONSTRAINT chk_app_status CHECK (status IN ('applied', 'shortlisted', 'rejected')),
    applied_at      DATE DEFAULT SYSDATE NOT NULL,
    CONSTRAINT uq_one_application UNIQUE (job_id, profile_id),
    CONSTRAINT fk_app_job FOREIGN KEY (job_id)
        REFERENCES job_postings (job_id) ON DELETE CASCADE,
    CONSTRAINT fk_app_profile FOREIGN KEY (profile_id)
        REFERENCES candidate_profiles (profile_id) ON DELETE CASCADE
);

-- ---------------------------------------------------------------
-- AUDIT_LOG  (filled automatically by a trigger)
-- ---------------------------------------------------------------
CREATE TABLE audit_log (
    log_id      NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    table_name  VARCHAR2(40) NOT NULL,
    action      VARCHAR2(40) NOT NULL,
    details     VARCHAR2(300),
    logged_at   DATE DEFAULT SYSDATE NOT NULL
);

-- ---------------------------------------------------------------
-- INDEXES (foreign keys and columns we filter on often)
-- ---------------------------------------------------------------
CREATE INDEX idx_jobs_recruiter    ON job_postings (recruiter_id);
CREATE INDEX idx_jobs_status_loc   ON job_postings (status, location);
CREATE INDEX idx_app_job           ON applications (job_id);
CREATE INDEX idx_app_profile       ON applications (profile_id);
CREATE INDEX idx_cs_skill          ON candidate_skills (skill_id);
CREATE INDEX idx_js_skill          ON job_skills (skill_id);
CREATE INDEX idx_profile_exp_loc   ON candidate_profiles (experience_years, location);
