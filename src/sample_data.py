"""Sample seed data mirroring sql/03_sample_data.sql for initial seeding and Demo Mode."""

USERS = [
    {"user_id": 1, "name": "Ananya Rao", "email": "hr@technova.example", "password_hash": "password123", "user_role": "recruiter"},
    {"user_id": 2, "name": "Rahul Mehta", "email": "hiring@datawave.example", "password_hash": "password123", "user_role": "recruiter"},
    {"user_id": 3, "name": "Priya Nair", "email": "priya@example.com", "password_hash": "password123", "user_role": "candidate"},
    {"user_id": 4, "name": "Arjun Das", "email": "arjun@example.com", "password_hash": "password123", "user_role": "candidate"},
    {"user_id": 5, "name": "Meera Iyer", "email": "meera@example.com", "password_hash": "password123", "user_role": "candidate"},
    {"user_id": 6, "name": "Karthik S", "email": "karthik@example.com", "password_hash": "password123", "user_role": "candidate"},
    {"user_id": 7, "name": "Neha Gupta", "email": "neha@example.com", "password_hash": "password123", "user_role": "candidate"},
]

SKILLS = [
    "Python", "SQL", "Java", "Machine Learning", "Deep Learning",
    "NLP", "PyTorch", "TensorFlow", "REST APIs", "Git",
    "Excel", "Tableau", "Statistics", "Docker", "React", "PL/SQL"
]

CANDIDATE_PROFILES = [
    {
        "profile_id": 1,
        "user_id": 3,
        "name": "Priya Nair",
        "email": "priya@example.com",
        "resume_text": "Machine learning engineer with 3 years of experience building classification and recommendation models in Python and PyTorch. Deployed models as REST APIs and worked with SQL databases for feature pipelines.",
        "experience_years": 3,
        "location": "Bengaluru",
        "portfolio_url": "https://github.com/example-priya",
        "skills": ["Python", "SQL", "Machine Learning", "PyTorch", "REST APIs", "Git"]
    },
    {
        "profile_id": 2,
        "user_id": 4,
        "name": "Arjun Das",
        "email": "arjun@example.com",
        "resume_text": "Backend developer with 1 year of experience writing Java Spring services, REST APIs and SQL queries. Comfortable with Git, Docker and unit testing.",
        "experience_years": 1,
        "location": "Bengaluru",
        "portfolio_url": None,
        "skills": ["Java", "SQL", "REST APIs", "Git", "Docker"]
    },
    {
        "profile_id": 3,
        "user_id": 5,
        "name": "Meera Iyer",
        "email": "meera@example.com",
        "resume_text": "Data analyst with 2 years of experience creating dashboards in Tableau and Excel, writing SQL reports and doing statistical analysis for business teams.",
        "experience_years": 2,
        "location": "Hyderabad",
        "portfolio_url": None,
        "skills": ["SQL", "Excel", "Tableau", "Statistics", "Python"]
    },
    {
        "profile_id": 4,
        "user_id": 6,
        "name": "Karthik S",
        "email": "karthik@example.com",
        "resume_text": "NLP engineer with 4 years of experience in transformers, text classification and semantic search. Trained deep learning models in PyTorch and TensorFlow and built retrieval systems.",
        "experience_years": 4,
        "location": "Bengaluru",
        "portfolio_url": "https://github.com/example-karthik",
        "skills": ["Python", "NLP", "Deep Learning", "PyTorch", "TensorFlow", "Machine Learning"]
    },
    {
        "profile_id": 5,
        "user_id": 7,
        "name": "Neha Gupta",
        "email": "neha@example.com",
        "resume_text": "Fresher with a degree in statistics. Completed academic projects in Python and SQL, and built Excel and Tableau dashboards during an internship.",
        "experience_years": 0,
        "location": "Hyderabad",
        "portfolio_url": None,
        "skills": ["Python", "SQL", "Excel", "Tableau", "Statistics"]
    }
]

JOB_POSTINGS = [
    {
        "job_id": 1,
        "recruiter_id": 1,
        "recruiter_name": "Ananya Rao",
        "title": "Machine Learning Engineer",
        "description": "Build and deploy machine learning models for our recommendation platform. Work with Python, PyTorch and SQL data pipelines and expose models through REST APIs.",
        "min_experience": 2,
        "salary": 1200000,
        "location": "Bengaluru",
        "status": "open",
        "skills": ["Python", "Machine Learning", "PyTorch", "SQL"]
    },
    {
        "job_id": 2,
        "recruiter_id": 1,
        "recruiter_name": "Ananya Rao",
        "title": "Backend Developer",
        "description": "Develop and maintain Java microservices and REST APIs backed by SQL databases. Use Git and Docker in a CI workflow.",
        "min_experience": 1,
        "salary": 900000,
        "location": "Bengaluru",
        "status": "open",
        "skills": ["Java", "SQL", "REST APIs", "Git"]
    },
    {
        "job_id": 3,
        "recruiter_id": 2,
        "recruiter_name": "Rahul Mehta",
        "title": "Data Analyst",
        "description": "Analyse business data with SQL and Python, build Tableau dashboards and present insights using statistics and Excel.",
        "min_experience": 0,
        "salary": 600000,
        "location": "Hyderabad",
        "status": "open",
        "skills": ["SQL", "Python", "Tableau", "Statistics", "Excel"]
    },
    {
        "job_id": 4,
        "recruiter_id": 2,
        "recruiter_name": "Rahul Mehta",
        "title": "NLP Engineer",
        "description": "Design NLP systems including semantic search and text classification using transformers, PyTorch and Python. Remote-first team.",
        "min_experience": 2,
        "salary": 1500000,
        "location": "Remote",
        "status": "open",
        "skills": ["Python", "NLP", "PyTorch", "Machine Learning"]
    }
]

APPLICATIONS = [
    {"application_id": 1, "job_id": 1, "profile_id": 1, "match_score": 78.50, "status": "applied", "applied_at": "2026-09-28 10:00:00"},
    {"application_id": 2, "job_id": 1, "profile_id": 4, "match_score": 74.20, "status": "applied", "applied_at": "2026-09-28 10:15:00"},
    {"application_id": 3, "job_id": 2, "profile_id": 2, "match_score": 81.00, "status": "applied", "applied_at": "2026-09-28 11:30:00"},
    {"application_id": 4, "job_id": 3, "profile_id": 3, "match_score": 69.00, "status": "applied", "applied_at": "2026-09-28 12:45:00"},
    {"application_id": 5, "job_id": 3, "profile_id": 5, "match_score": 55.50, "status": "applied", "applied_at": "2026-09-28 14:00:00"},
    {"application_id": 6, "job_id": 4, "profile_id": 4, "match_score": 88.00, "status": "applied", "applied_at": "2026-09-28 15:20:00"},
]
