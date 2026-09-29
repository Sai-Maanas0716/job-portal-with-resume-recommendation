"""Database connector and query manager with dual-mode support:
1. Live Oracle Database (via oracledb)
2. Interactive Demo Mode (in-memory SQLite preloaded with 3NF schema and sample data)
"""
import os
import sqlite3
from typing import Any, Dict, List, Optional
from dotenv import load_dotenv

from src.matcher import calculate_skill_match_pct, calculate_hybrid_score
from src.sample_data import USERS, SKILLS, CANDIDATE_PROFILES, JOB_POSTINGS, APPLICATIONS

load_dotenv()

# Track active mode
_ACTIVE_MODE = None
_SQLITE_CONN = None


def _init_sqlite_demo_db() -> sqlite3.Connection:
    """Initialize an in-memory SQLite mirror representing the 3NF Oracle schema."""
    conn = sqlite3.connect(":memory:", check_same_thread=False)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.executescript("""
    CREATE TABLE users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL,
        user_role TEXT NOT NULL CHECK (user_role IN ('candidate', 'recruiter')),
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE candidate_profiles (
        profile_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL UNIQUE REFERENCES users(user_id) ON DELETE CASCADE,
        resume_text TEXT NOT NULL,
        experience_years INTEGER NOT NULL DEFAULT 0,
        location TEXT NOT NULL DEFAULT 'Bengaluru',
        portfolio_url TEXT,
        summary_embedding TEXT,
        last_updated TEXT DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE job_postings (
        job_id INTEGER PRIMARY KEY AUTOINCREMENT,
        recruiter_id INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
        title TEXT NOT NULL,
        description TEXT NOT NULL,
        min_experience INTEGER NOT NULL DEFAULT 0,
        salary INTEGER NOT NULL,
        location TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'open' CHECK (status IN ('open', 'closed')),
        job_embedding TEXT,
        posted_at TEXT DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE skills (
        skill_id INTEGER PRIMARY KEY AUTOINCREMENT,
        skill_name TEXT NOT NULL UNIQUE
    );

    CREATE TABLE candidate_skills (
        profile_id INTEGER NOT NULL REFERENCES candidate_profiles(profile_id) ON DELETE CASCADE,
        skill_id INTEGER NOT NULL REFERENCES skills(skill_id) ON DELETE CASCADE,
        PRIMARY KEY (profile_id, skill_id)
    );

    CREATE TABLE job_skills (
        job_id INTEGER NOT NULL REFERENCES job_postings(job_id) ON DELETE CASCADE,
        skill_id INTEGER NOT NULL REFERENCES skills(skill_id) ON DELETE CASCADE,
        PRIMARY KEY (job_id, skill_id)
    );

    CREATE TABLE applications (
        application_id INTEGER PRIMARY KEY AUTOINCREMENT,
        job_id INTEGER NOT NULL REFERENCES job_postings(job_id) ON DELETE CASCADE,
        profile_id INTEGER NOT NULL REFERENCES candidate_profiles(profile_id) ON DELETE CASCADE,
        match_score REAL NOT NULL DEFAULT 0.0,
        status TEXT NOT NULL DEFAULT 'applied' CHECK (status IN ('applied', 'shortlisted', 'rejected')),
        applied_at TEXT DEFAULT CURRENT_TIMESTAMP,
        UNIQUE (job_id, profile_id)
    );

    CREATE TABLE audit_log (
        log_id INTEGER PRIMARY KEY AUTOINCREMENT,
        table_name TEXT NOT NULL,
        action TEXT NOT NULL,
        details TEXT,
        logged_at TEXT DEFAULT CURRENT_TIMESTAMP
    );
    """)

    for u in USERS:
        cur.execute(
            "INSERT INTO users (user_id, name, email, password_hash, user_role) VALUES (?, ?, ?, ?, ?)",
            (u["user_id"], u["name"], u["email"], u["password_hash"], u["user_role"])
        )

    skill_map = {}
    for idx, skill in enumerate(SKILLS, start=1):
        cur.execute("INSERT INTO skills (skill_id, skill_name) VALUES (?, ?)", (idx, skill))
        skill_map[skill.lower()] = idx

    for cp in CANDIDATE_PROFILES:
        cur.execute(
            """INSERT INTO candidate_profiles
               (profile_id, user_id, resume_text, experience_years, location, portfolio_url, summary_embedding)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (cp["profile_id"], cp["user_id"], cp["resume_text"], cp["experience_years"], cp["location"], cp["portfolio_url"], "[EMBEDDING_VECTOR]")
        )
        for s in cp["skills"]:
            s_id = skill_map.get(s.lower())
            if s_id:
                cur.execute("INSERT INTO candidate_skills (profile_id, skill_id) VALUES (?, ?)", (cp["profile_id"], s_id))

    for jp in JOB_POSTINGS:
        cur.execute(
            """INSERT INTO job_postings
               (job_id, recruiter_id, title, description, min_experience, salary, location, status, job_embedding)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (jp["job_id"], jp["recruiter_id"], jp["title"], jp["description"], jp["min_experience"], jp["salary"], jp["location"], jp["status"], "[EMBEDDING_VECTOR]")
        )
        for s in jp["skills"]:
            s_id = skill_map.get(s.lower())
            if s_id:
                cur.execute("INSERT INTO job_skills (job_id, skill_id) VALUES (?, ?)", (jp["job_id"], s_id))

    for app in APPLICATIONS:
        cur.execute(
            """INSERT INTO applications (application_id, job_id, profile_id, match_score, status, applied_at)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (app["application_id"], app["job_id"], app["profile_id"], app["match_score"], app["status"], app["applied_at"])
        )

    conn.commit()
    return conn


def _check_oracle_available() -> bool:
    """Checks if Oracle credentials are configured and reachable."""
    user = os.getenv("ORACLE_USER")
    pwd = os.getenv("ORACLE_PASSWORD")
    dsn = os.getenv("ORACLE_DSN")
    if not (user and pwd and dsn) or os.getenv("DEMO_MODE", "").lower() == "true":
        return False
    try:
        import oracledb
        oracledb.defaults.fetch_lobs = False
        conn = oracledb.connect(user=user, password=pwd, dsn=dsn)
        conn.close()
        return True
    except Exception:
        return False


def get_mode() -> str:
    """Returns whether the system is connected to live Oracle or Demo Mode."""
    global _ACTIVE_MODE
    if _ACTIVE_MODE is None:
        if _check_oracle_available():
            _ACTIVE_MODE = "ORACLE"
        else:
            _ACTIVE_MODE = "DEMO"
    return _ACTIVE_MODE


def query(sql: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """Runs a SELECT query and returns a list of dictionaries with lowercase keys."""
    global _SQLITE_CONN
    if get_mode() == "ORACLE":
        import oracledb
        with oracledb.connect(
            user=os.getenv("ORACLE_USER"),
            password=os.getenv("ORACLE_PASSWORD"),
            dsn=os.getenv("ORACLE_DSN"),
        ) as conn:
            with conn.cursor() as cur:
                cur.execute(sql, params or {})
                cols = [c[0].lower() for c in cur.description]
                return [dict(zip(cols, row)) for row in cur.fetchall()]
    else:
        if _SQLITE_CONN is None:
            _SQLITE_CONN = _init_sqlite_demo_db()
        cur = _SQLITE_CONN.cursor()
        cur.execute(sql, params or {})
        rows = cur.fetchall()
        return [dict(r) for r in rows]


def execute(sql: str, params: Optional[Dict[str, Any]] = None) -> None:
    """Runs an INSERT / UPDATE / DELETE command."""
    global _SQLITE_CONN
    if get_mode() == "ORACLE":
        import oracledb
        with oracledb.connect(
            user=os.getenv("ORACLE_USER"),
            password=os.getenv("ORACLE_PASSWORD"),
            dsn=os.getenv("ORACLE_DSN"),
        ) as conn:
            with conn.cursor() as cur:
                cur.execute(sql, params or {})
            conn.commit()
    else:
        if _SQLITE_CONN is None:
            _SQLITE_CONN = _init_sqlite_demo_db()
        cur = _SQLITE_CONN.cursor()
        cur.execute(sql, params or {})
        _SQLITE_CONN.commit()


def get_all_jobs() -> List[Dict[str, Any]]:
    """Returns all jobs with recruiter name and required skill tags."""
    sql = """
        SELECT j.job_id, j.title, j.description, j.min_experience,
               j.salary, j.location, j.status, j.posted_at,
               u.name AS recruiter_name, u.user_id AS recruiter_id
        FROM job_postings j
        JOIN users u ON u.user_id = j.recruiter_id
        ORDER BY j.job_id DESC
    """
    jobs = query(sql)
    for j in jobs:
        s_sql = """
            SELECT s.skill_name
            FROM skills s
            JOIN job_skills js ON js.skill_id = s.skill_id
            WHERE js.job_id = :job_id
            ORDER BY s.skill_name
        """
        s_rows = query(s_sql, {"job_id": j["job_id"]})
        j["skills"] = [r["skill_name"] for r in s_rows]
    return jobs


def get_all_candidates() -> List[Dict[str, Any]]:
    """Returns all candidate profiles with their possessed skills."""
    sql = """
        SELECT cp.profile_id, cp.user_id, u.name, u.email,
               cp.resume_text, cp.experience_years, cp.location,
               cp.portfolio_url, cp.last_updated
        FROM candidate_profiles cp
        JOIN users u ON u.user_id = cp.user_id
        ORDER BY cp.profile_id
    """
    candidates = query(sql)
    for c in candidates:
        s_sql = """
            SELECT s.skill_name
            FROM skills s
            JOIN candidate_skills cs ON cs.skill_id = s.skill_id
            WHERE cs.profile_id = :profile_id
            ORDER BY s.skill_name
        """
        s_rows = query(s_sql, {"profile_id": c["profile_id"]})
        c["skills"] = [r["skill_name"] for r in s_rows]
    return candidates


def get_eligible_candidates_for_job(job_id: int) -> List[Dict[str, Any]]:
    """
    Executes relational pre-filtering mirroring Oracle PL/SQL procedure:
    sp_get_eligible_candidates(job_id, ref_cursor)
    """
    job_rows = query("SELECT min_experience, location FROM job_postings WHERE job_id = :job_id", {"job_id": job_id})
    if not job_rows:
        return []
    min_exp = job_rows[0]["min_experience"]
    loc = job_rows[0]["location"]

    candidates = get_all_candidates()
    eligible = []
    for c in candidates:
        if c["experience_years"] >= min_exp and (loc == "Remote" or c["location"] == loc):
            eligible.append(c)
    return eligible


def apply_job(job_id: int, profile_id: int, semantic_score: float) -> float:
    """
    Applies candidate to a job, mirroring PL/SQL:
    - trg_app_before_insert (verifies job is 'open')
    - sp_apply_job (calculates final match score: 60% semantic + 40% skill match)
    """
    j_rows = query("SELECT status FROM job_postings WHERE job_id = :job_id", {"job_id": job_id})
    if not j_rows or j_rows[0]["status"] != "open":
        raise ValueError("Cannot apply: This job is closed.")

    j_skills = [r["skill_name"] for r in query(
        "SELECT s.skill_name FROM skills s JOIN job_skills js ON js.skill_id = s.skill_id WHERE js.job_id = :j",
        {"j": job_id}
    )]
    c_skills = [r["skill_name"] for r in query(
        "SELECT s.skill_name FROM skills s JOIN candidate_skills cs ON cs.skill_id = s.skill_id WHERE cs.profile_id = :c",
        {"c": profile_id}
    )]
    skill_pct = calculate_skill_match_pct(c_skills, j_skills)
    final_score = calculate_hybrid_score(skill_pct, semantic_score)

    existing = query(
        "SELECT application_id, status FROM applications WHERE job_id = :j AND profile_id = :p",
        {"j": job_id, "p": profile_id}
    )
    if existing:
        execute(
            """
            UPDATE applications
            SET match_score = :match_score, status = 'applied'
            WHERE application_id = :id
            """,
            {"match_score": final_score, "id": existing[0]["application_id"]}
        )
    else:
        execute(
            """
            INSERT INTO applications (job_id, profile_id, match_score, status)
            VALUES (:job_id, :profile_id, :match_score, 'applied')
            """,
            {"job_id": job_id, "profile_id": profile_id, "match_score": final_score}
        )
    return final_score


def update_job_status(job_id: int, new_status: str) -> None:
    """Updates job status and triggers trg_job_status_audit logging to audit_log."""
    old_rows = query("SELECT status FROM job_postings WHERE job_id = :job_id", {"job_id": job_id})
    old_status = old_rows[0]["status"] if old_rows else "unknown"

    execute("UPDATE job_postings SET status = :status WHERE job_id = :job_id", {"status": new_status, "job_id": job_id})

    execute(
        """
        INSERT INTO audit_log (table_name, action, details)
        VALUES ('JOB_POSTINGS', 'STATUS_CHANGE', :details)
        """,
        {"details": f"Job {job_id}: {old_status} -> {new_status}"}
    )


def shortlist_applications(job_id: int, threshold: float) -> int:
    """Shortlists applications above threshold mirroring PL/SQL sp_shortlist_applications."""
    apps = query("SELECT application_id, match_score FROM applications WHERE job_id = :j AND status = 'applied'", {"j": job_id})
    count = 0
    for a in apps:
        if a["match_score"] >= threshold:
            execute("UPDATE applications SET status = 'shortlisted' WHERE application_id = :id", {"id": a["application_id"]})
            count += 1
    return count


def get_ranked_applications(job_id: int) -> List[Dict[str, Any]]:
    """Fetches ranked applicants mirroring Oracle view: vw_ranked_applicants."""
    sql = """
        SELECT a.application_id, a.job_id, cp.profile_id,
               u.name AS candidate_name, u.email AS candidate_email,
               cp.experience_years, cp.location,
               a.match_score, a.status, a.applied_at
        FROM applications a
        JOIN candidate_profiles cp ON cp.profile_id = a.profile_id
        JOIN users u ON u.user_id = cp.user_id
        WHERE a.job_id = :job_id
        ORDER BY a.match_score DESC
    """
    apps = query(sql, {"job_id": job_id})
    for rank, a in enumerate(apps, start=1):
        a["rank_position"] = rank
    return apps


def get_audit_logs() -> List[Dict[str, Any]]:
    """Returns all audit log records."""
    return query("SELECT * FROM audit_log ORDER BY log_id DESC")
