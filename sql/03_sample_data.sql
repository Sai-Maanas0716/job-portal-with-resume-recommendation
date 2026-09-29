-- 03_sample_data.sql
-- Demo data. Run ONLY on a freshly created schema (ids are assumed to start at 1).
-- Every sample user has the password:  password123
-- Embeddings are left empty here; run  python scripts/generate_embeddings.py  afterwards.

-- ---------- USERS (1-2 recruiters, 3-7 candidates) ----------
INSERT INTO users (name, email, password_hash, user_role) VALUES ('Ananya Rao',   'hr@technova.example',      'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', 'recruiter');
INSERT INTO users (name, email, password_hash, user_role) VALUES ('Rahul Mehta',  'hiring@datawave.example',  'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', 'recruiter');
INSERT INTO users (name, email, password_hash, user_role) VALUES ('Priya Nair',   'priya@example.com',        'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', 'candidate');
INSERT INTO users (name, email, password_hash, user_role) VALUES ('Arjun Das',    'arjun@example.com',        'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', 'candidate');
INSERT INTO users (name, email, password_hash, user_role) VALUES ('Meera Iyer',   'meera@example.com',        'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', 'candidate');
INSERT INTO users (name, email, password_hash, user_role) VALUES ('Karthik S',    'karthik@example.com',      'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', 'candidate');
INSERT INTO users (name, email, password_hash, user_role) VALUES ('Neha Gupta',   'neha@example.com',         'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', 'candidate');

-- ---------- SKILLS ----------
INSERT INTO skills (skill_name) VALUES ('Python');
INSERT INTO skills (skill_name) VALUES ('SQL');
INSERT INTO skills (skill_name) VALUES ('Java');
INSERT INTO skills (skill_name) VALUES ('Machine Learning');
INSERT INTO skills (skill_name) VALUES ('Deep Learning');
INSERT INTO skills (skill_name) VALUES ('NLP');
INSERT INTO skills (skill_name) VALUES ('PyTorch');
INSERT INTO skills (skill_name) VALUES ('TensorFlow');
INSERT INTO skills (skill_name) VALUES ('REST APIs');
INSERT INTO skills (skill_name) VALUES ('Git');
INSERT INTO skills (skill_name) VALUES ('Excel');
INSERT INTO skills (skill_name) VALUES ('Tableau');
INSERT INTO skills (skill_name) VALUES ('Statistics');
INSERT INTO skills (skill_name) VALUES ('Docker');
INSERT INTO skills (skill_name) VALUES ('React');
INSERT INTO skills (skill_name) VALUES ('PL/SQL');

-- ---------- CANDIDATE PROFILES (profile_id 1-5 = users 3-7) ----------
INSERT INTO candidate_profiles (user_id, resume_text, experience_years, location, portfolio_url)
VALUES (3, 'Machine learning engineer with 3 years of experience building classification and recommendation models in Python and PyTorch. Deployed models as REST APIs and worked with SQL databases for feature pipelines.', 3, 'Bengaluru', 'https://github.com/example-priya');
INSERT INTO candidate_profiles (user_id, resume_text, experience_years, location, portfolio_url)
VALUES (4, 'Backend developer with 1 year of experience writing Java Spring services, REST APIs and SQL queries. Comfortable with Git, Docker and unit testing.', 1, 'Bengaluru', NULL);
INSERT INTO candidate_profiles (user_id, resume_text, experience_years, location, portfolio_url)
VALUES (5, 'Data analyst with 2 years of experience creating dashboards in Tableau and Excel, writing SQL reports and doing statistical analysis for business teams.', 2, 'Hyderabad', NULL);
INSERT INTO candidate_profiles (user_id, resume_text, experience_years, location, portfolio_url)
VALUES (6, 'NLP engineer with 4 years of experience in transformers, text classification and semantic search. Trained deep learning models in PyTorch and TensorFlow and built retrieval systems.', 4, 'Bengaluru', 'https://github.com/example-karthik');
INSERT INTO candidate_profiles (user_id, resume_text, experience_years, location, portfolio_url)
VALUES (7, 'Fresher with a degree in statistics. Completed academic projects in Python and SQL, and built Excel and Tableau dashboards during an internship.', 0, 'Hyderabad', NULL);

-- ---------- CANDIDATE SKILLS ----------
INSERT INTO candidate_skills (profile_id, skill_id) SELECT 1, skill_id FROM skills WHERE skill_name IN ('Python', 'SQL', 'Machine Learning', 'PyTorch', 'REST APIs', 'Git');
INSERT INTO candidate_skills (profile_id, skill_id) SELECT 2, skill_id FROM skills WHERE skill_name IN ('Java', 'SQL', 'REST APIs', 'Git', 'Docker');
INSERT INTO candidate_skills (profile_id, skill_id) SELECT 3, skill_id FROM skills WHERE skill_name IN ('SQL', 'Excel', 'Tableau', 'Statistics', 'Python');
INSERT INTO candidate_skills (profile_id, skill_id) SELECT 4, skill_id FROM skills WHERE skill_name IN ('Python', 'NLP', 'Deep Learning', 'PyTorch', 'TensorFlow', 'Machine Learning');
INSERT INTO candidate_skills (profile_id, skill_id) SELECT 5, skill_id FROM skills WHERE skill_name IN ('Python', 'SQL', 'Excel', 'Tableau', 'Statistics');

-- ---------- JOB POSTINGS (job_id 1-4) ----------
INSERT INTO job_postings (recruiter_id, title, description, min_experience, salary, location)
VALUES (1, 'Machine Learning Engineer', 'Build and deploy machine learning models for our recommendation platform. Work with Python, PyTorch and SQL data pipelines and expose models through REST APIs.', 2, 1200000, 'Bengaluru');
INSERT INTO job_postings (recruiter_id, title, description, min_experience, salary, location)
VALUES (1, 'Backend Developer', 'Develop and maintain Java microservices and REST APIs backed by SQL databases. Use Git and Docker in a CI workflow.', 1, 900000, 'Bengaluru');
INSERT INTO job_postings (recruiter_id, title, description, min_experience, salary, location)
VALUES (2, 'Data Analyst', 'Analyse business data with SQL and Python, build Tableau dashboards and present insights using statistics and Excel.', 0, 600000, 'Hyderabad');
INSERT INTO job_postings (recruiter_id, title, description, min_experience, salary, location)
VALUES (2, 'NLP Engineer', 'Design NLP systems including semantic search and text classification using transformers, PyTorch and Python. Remote-first team.', 2, 1500000, 'Remote');

-- ---------- JOB SKILLS ----------
INSERT INTO job_skills (job_id, skill_id) SELECT 1, skill_id FROM skills WHERE skill_name IN ('Python', 'Machine Learning', 'PyTorch', 'SQL');
INSERT INTO job_skills (job_id, skill_id) SELECT 2, skill_id FROM skills WHERE skill_name IN ('Java', 'SQL', 'REST APIs', 'Git');
INSERT INTO job_skills (job_id, skill_id) SELECT 3, skill_id FROM skills WHERE skill_name IN ('SQL', 'Python', 'Tableau', 'Statistics', 'Excel');
INSERT INTO job_skills (job_id, skill_id) SELECT 4, skill_id FROM skills WHERE skill_name IN ('Python', 'NLP', 'PyTorch', 'Machine Learning');

-- ---------- A FEW EXISTING APPLICATIONS ----------
INSERT INTO applications (job_id, profile_id, match_score) VALUES (1, 1, 78.50);
INSERT INTO applications (job_id, profile_id, match_score) VALUES (1, 4, 74.20);
INSERT INTO applications (job_id, profile_id, match_score) VALUES (2, 2, 81.00);
INSERT INTO applications (job_id, profile_id, match_score) VALUES (3, 3, 69.00);
INSERT INTO applications (job_id, profile_id, match_score) VALUES (3, 5, 55.50);
INSERT INTO applications (job_id, profile_id, match_score) VALUES (4, 4, 88.00);

COMMIT;
