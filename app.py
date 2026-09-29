"""Smart Job Portal & AI Resume Matching Engine
DBMS Course Project - Review 1 Demo Application
"""
import streamlit as st
import pandas as pd
from src import db
from src.matcher import (
    compute_semantic_similarity,
    calculate_skill_match_pct,
    calculate_hybrid_score,
)

st.set_page_config(
    page_title="Smart Job Portal - AI & DBMS",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    .badge {
        display: inline-block;
        padding: 3px 8px;
        border-radius: 4px;
        font-size: 12px;
        font-weight: bold;
        margin-right: 5px;
        margin-bottom: 5px;
    }
    .badge-skill { background-color: #e3f2fd; color: #1565c0; border: 1px solid #bbdefb; }
    .badge-score { background-color: #e8f5e9; color: #2e7d32; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# Sidebar
st.sidebar.title("💼 Smart Job Portal")
st.sidebar.caption("AI-Driven Hybrid Candidate-Job Matching")

mode = db.get_mode()
if mode == "ORACLE":
    st.sidebar.success("🟢 Connected: Oracle Database (XE/19c)")
else:
    st.sidebar.info("💡 Mode: Interactive Demo (3NF Relational Mirror)")

navigation = st.sidebar.radio(
    "Navigation",
    [
        "📋 Overview & Architecture",
        "👔 Recruiter Portal (Filter & Rank)",
        "👤 Candidate Portal (Apply & Match)",
        "🔍 DBMS Lab Evaluation & SQL Runner",
        "📝 Review 1 Feedback & Next Steps",
    ],
)

st.sidebar.markdown("---")
st.sidebar.markdown("**Course:** DBMS Semester Mini-Project (20 Marks)")
st.sidebar.markdown("**Architecture:** Hybrid SQL + Dense Embeddings")

# ==============================================================================
# 1. OVERVIEW & ARCHITECTURE
# ==============================================================================
if navigation == "📋 Overview & Architecture":
    st.title("Smart Job Portal & AI-Driven Resume Matching")
    st.subheader("DBMS Mini-Project — Review 1 Prototype")

    st.markdown("""
    Welcome to the **Review 1 Demonstration** of the Smart Job Portal. This system bridges a **strictly normalized 3NF Relational Database** with an **Applied AI Semantic Retrieval Engine**.
    """)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Database Schema", "3NF Normalized", "Oracle SQL / PL-SQL")
    col2.metric("Retrieval Paradigm", "Hybrid Retrieval", "SQL + Cosine Similarity")
    col3.metric("Semantic Model", "Sentence-Transformers", "all-MiniLM-L6-v2")
    col4.metric("Matching Formula", "60% AI + 40% SQL", "Balanced Weighting")

    st.markdown("---")

    st.header("1. Core Problem & Solution")
    c1, c2 = st.columns(2)
    with c1:
        st.error("❌ Problem with Traditional Systems")
        st.write("""
        - Relies on simple `LIKE` string searches or keyword counts.
        - Fails when candidates use valid synonyms or different phrasing.
        - Inefficient full-table scans on non-indexed columns.
        - Ignores relational constraints (experience, location) during AI ranking.
        """)
    with c2:
        st.success("✅ Hybrid Retrieval Solution")
        st.write("""
        - **Step 1 (SQL Pre-Filtering):** Relational engine filters candidate pool by hard criteria (experience >= required, location match).
        - **Step 2 (Semantic Vector Search):** NLP model computes cosine similarity between resume text and job description.
        - **Step 3 (Dynamic Re-Ranking):** Composite score calculated and stored transactionally via PL/SQL stored procedure.
        """)

    st.header("2. Chen ER Model & Relational Mapping")
    st.markdown("""
    The conceptual design consists of **5 Entities** and **6 Relationships**:
    - **USER** (`user_id` [PK], `name`, `email`, `password_hash`, `user_role`, `created_at`)
    - **CANDIDATE_PROFILES** (`profile_id` [PK], `user_id` [FK], `resume_text`, `experience_years`, `location`, `portfolio_url`)
    - **JOB_POSTINGS** (`job_id` [PK], `recruiter_id` [FK], `title`, `description`, `min_experience`, `salary`, `location`, `status`)
    - **SKILLS** (`skill_id` [PK], `skill_name`)
    - **APPLICATIONS** (`application_id` [PK], `job_id` [FK], `profile_id` [FK], `match_score`, `status`, `applied_at`)
    
    **Relationships:**
    - `HAS`: USER <-> CANDIDATE (1:1)
    - `POSTS`: USER <-> JOB_POSTING (1:N)
    - `POSSESSES`: CANDIDATE <-> SKILL (M:N -> `candidate_skills` table)
    - `REQUIRES`: JOB_POSTING <-> SKILL (M:N -> `job_skills` table)
    - `SUBMITS`: CANDIDATE <-> APPLICATION (1:N)
    - `RECEIVES`: JOB_POSTING <-> APPLICATION (1:N)
    """)

    st.header("3. Matching Formula (PL/SQL sp_apply_job)")
    st.latex(r"\text{Final Match Score} = (0.60 \times \text{Semantic Score}) + (0.40 \times \text{Skill Overlap \%})")

# ==============================================================================
# 2. RECRUITER PORTAL
# ==============================================================================
elif navigation == "👔 Recruiter Portal (Filter & Rank)":
    st.title("👔 Recruiter Dashboard")
    st.caption("Perform SQL Pre-Filtering, View AI Compatibility, and Run PL/SQL Batch Shortlisting")

    jobs = db.get_all_jobs()
    job_options = {f"Job #{j['job_id']}: {j['title']} ({j['location']})": j for j in jobs}
    selected_job_label = st.selectbox("Select a Job Posting to inspect:", list(job_options.keys()))
    selected_job = job_options[selected_job_label]

    st.markdown(f"""
    **Job Details:** {selected_job['description']}  
    **Requirements:** Min Experience: `{selected_job['min_experience']} yrs` | Location: `{selected_job['location']}` | Salary: `₹{selected_job['salary']:,}` | Status: `{selected_job['status'].upper()}`
    """)
    st.write("**Required Skills:** " + " ".join([f"<span class='badge badge-skill'>{s}</span>" for s in selected_job["skills"]]), unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["📊 Candidate Pool (SQL Pre-Filter & AI Match)", "📑 Current Applications (Ranked View)", "⚙️ PL/SQL Batch Shortlist"])

    with tab1:
        st.subheader("Step 1 & 2: SQL Pre-Filter + Semantic Vector Scoring")
        st.info("Demonstrates Oracle PL/SQL `sp_get_eligible_candidates`: Candidate pool pre-filtered by hard constraints before running semantic inference.")

        eligible = db.get_eligible_candidates_for_job(selected_job["job_id"])
        if not eligible:
            st.warning("No candidates meet the hard constraints for this job.")
        else:
            scored_candidates = []
            for c in eligible:
                skill_pct = calculate_skill_match_pct(c["skills"], selected_job["skills"])
                sem_score = compute_semantic_similarity(c["resume_text"], selected_job["description"])
                final_score = calculate_hybrid_score(skill_pct, sem_score)
                scored_candidates.append({
                    "Profile ID": c["profile_id"],
                    "Name": c["name"],
                    "Exp (Yrs)": c["experience_years"],
                    "Location": c["location"],
                    "Skill Match %": f"{skill_pct:.1f}%",
                    "Semantic Similarity %": f"{sem_score:.1f}%",
                    "Hybrid Match Score": final_score,
                    "Candidate Skills": ", ".join(c["skills"]),
                })

            df_scores = pd.DataFrame(scored_candidates).sort_values(by="Hybrid Match Score", ascending=False)
            st.dataframe(df_scores, use_container_width=True)

    with tab2:
        st.subheader("Ranked Applicants (Oracle View: vw_ranked_applicants)")
        apps = db.get_ranked_applications(selected_job["job_id"])
        if not apps:
            st.write("No submitted applications yet for this job.")
        else:
            df_apps = pd.DataFrame(apps)[["rank_position", "candidate_name", "candidate_email", "experience_years", "location", "match_score", "status", "applied_at"]]
            df_apps.columns = ["Rank", "Candidate Name", "Email", "Exp (Yrs)", "Location", "Match Score", "Status", "Applied At"]
            st.dataframe(df_apps, use_container_width=True)

    with tab3:
        st.subheader("PL/SQL Procedure: sp_shortlist_applications")
        st.write("This executes an explicit PL/SQL cursor with `FOR UPDATE` to transition applications above a match threshold from `applied` -> `shortlisted`.")
        col_thresh, col_btn = st.columns([2, 1])
        with col_thresh:
            threshold = st.slider("Match Score Threshold for Shortlisting", 50, 100, 75)
        with col_btn:
            st.write("")
            st.write("")
            if st.button("Run Batch Shortlist"):
                count = db.shortlist_applications(selected_job["job_id"], float(threshold))
                st.success(f"Shortlisted {count} applicant(s) scoring >= {threshold}%!")
                st.rerun()

# ==============================================================================
# 3. CANDIDATE PORTAL
# ==============================================================================
elif navigation == "👤 Candidate Portal (Apply & Match)":
    st.title("👤 Candidate Portal")
    st.caption("Browse Jobs with Live Semantic Match Scores and Submit Applications")

    candidates = db.get_all_candidates()
    cand_options = {f"{c['name']} ({c['experience_years']} yrs exp, {c['location']})": c for c in candidates}
    selected_cand_label = st.selectbox("Select Candidate Persona to test with:", list(cand_options.keys()))
    selected_cand = cand_options[selected_cand_label]

    st.markdown(f"""
    **Candidate Summary:** {selected_cand['resume_text']}  
    **Skills:** {" ".join([f"<span class='badge badge-skill'>{s}</span>" for s in selected_cand["skills"]])}
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("Active Job Feed with Real-Time Hybrid Compatibility")

    all_jobs = [j for j in db.get_all_jobs() if j["status"] == "open"]
    for j in all_jobs:
        skill_pct = calculate_skill_match_pct(selected_cand["skills"], j["skills"])
        sem_score = compute_semantic_similarity(selected_cand["resume_text"], j["description"])
        hybrid_score = calculate_hybrid_score(skill_pct, sem_score)
        eligible = (selected_cand["experience_years"] >= j["min_experience"]) and (j["location"] == "Remote" or selected_cand["location"] == j["location"])

        with st.container():
            st.markdown(f"### {j['title']} — {j['recruiter_name']}")
            c1, c2, c3, c4 = st.columns([3, 1, 1, 1])
            with c1:
                st.write(f"📍 **{j['location']}** | Min Experience: **{j['min_experience']} yrs** | Salary: **₹{j['salary']:,}**")
                st.caption(j["description"])
                st.write("Skills Required: " + " ".join([f"<span class='badge badge-skill'>{s}</span>" for s in j["skills"]]), unsafe_allow_html=True)
            with c2:
                st.metric("Skill Overlap", f"{skill_pct:.1f}%")
            with c3:
                st.metric("Semantic Match", f"{sem_score:.1f}%")
            with c4:
                st.metric("Final Hybrid Score", f"{hybrid_score:.1f}%")

            col_btn, col_note = st.columns([1, 4])
            with col_btn:
                btn_key = f"apply_{j['job_id']}_{selected_cand['profile_id']}"
                if st.button("Apply Now", key=btn_key):
                    try:
                        final = db.apply_job(j["job_id"], selected_cand["profile_id"], sem_score)
                        st.success(f"Application recorded transactionally! Score: {final:.1f}%")
                    except Exception as e:
                        st.error(f"Error: {e}")
            with col_note:
                if not eligible:
                    st.caption("⚠️ Note: You do not meet the hard constraints (experience or location), but application can still be evaluated.")
            st.markdown("---")

# ==============================================================================
# 4. DBMS LAB EVALUATION & SQL RUNNER
# ==============================================================================
elif navigation == "🔍 DBMS Lab Evaluation & SQL Runner":
    st.title("🔍 DBMS Evaluation & Viva Showcase")
    st.caption("Interactive Inspector for 3NF Tables, Triggers, and Demo SQL Queries")

    tab1, tab2, tab3 = st.tabs(["📋 3NF Database Tables", "⚡ 9 Viva Demo Queries", "🛡️ PL/SQL Trigger Audit Log"])

    with tab1:
        st.subheader("Browse 3NF Relational Tables")
        table_name = st.selectbox("Select Table:", ["users", "candidate_profiles", "job_postings", "skills", "applications", "audit_log"])
        data = db.query(f"SELECT * FROM {table_name}")
        if data:
            st.dataframe(pd.DataFrame(data), use_container_width=True)
        else:
            st.info(f"Table '{table_name}' is currently empty.")

    with tab2:
        st.subheader("Run Viva Showcase Queries (from sql/04_demo_queries.sql)")
        queries = {
            "1. Multi-table INNER JOIN (Jobs with Recruiters)": (
                "SELECT j.job_id, j.title, j.location, u.name AS recruiter FROM job_postings j JOIN users u ON u.user_id = j.recruiter_id WHERE j.status = 'open'"
            ),
            "2. M:N Junction JOIN (Skills required per job)": (
                "SELECT j.title, s.skill_name FROM job_postings j JOIN job_skills js ON js.job_id = j.job_id JOIN skills s ON s.skill_id = js.skill_id ORDER BY j.title, s.skill_name"
            ),
            "3. GROUP BY + HAVING (Jobs with at least 2 applications)": (
                "SELECT j.title, COUNT(*) AS applicants, ROUND(AVG(a.match_score), 2) AS avg_score FROM applications a JOIN job_postings j ON j.job_id = a.job_id GROUP BY j.title HAVING COUNT(*) >= 2"
            ),
            "4. Subquery (Candidates who have not applied to any job)": (
                "SELECT u.name, cp.location FROM candidate_profiles cp JOIN users u ON u.user_id = cp.user_id WHERE cp.profile_id NOT IN (SELECT profile_id FROM applications)"
            ),
            "5. Ranked Applicants View (Analytic Window Ranking)": (
                "SELECT a.job_id, cp.profile_id, u.name AS candidate_name, a.match_score, a.status FROM applications a JOIN candidate_profiles cp ON cp.profile_id = a.profile_id JOIN users u ON u.user_id = cp.user_id ORDER BY a.job_id, a.match_score DESC"
            ),
        }

        selected_query_label = st.selectbox("Select Viva Demo Query:", list(queries.keys()))
        selected_sql = queries[selected_query_label]
        st.code(selected_sql, language="sql")

        if st.button("Execute Query"):
            res = db.query(selected_sql)
            if res:
                st.dataframe(pd.DataFrame(res), use_container_width=True)
            else:
                st.info("Query returned 0 rows.")

    with tab3:
        st.subheader("Trigger 2: Audit Logging on Status Changes (trg_job_status_audit)")
        st.write("Demonstrates automated logging whenever a job's status changes from 'open' <-> 'closed'.")
        col_j, col_s, col_b = st.columns(3)
        with col_j:
            j_id = st.number_input("Job ID", min_value=1, max_value=10, value=2)
        with col_s:
            new_st = st.selectbox("New Status", ["closed", "open"])
        with col_b:
            st.write("")
            st.write("")
            if st.button("Update Status (Trigger Test)"):
                db.update_job_status(int(j_id), new_st)
                st.success(f"Job {j_id} updated to '{new_st}'. Trigger executed!")

        st.markdown("**Live Audit Log Table:**")
        logs = db.get_audit_logs()
        if logs:
            st.dataframe(pd.DataFrame(logs), use_container_width=True)
        else:
            st.info("Audit log is currently empty.")

# ==============================================================================
# 5. REVIEW 1 FEEDBACK & NEXT STEPS
# ==============================================================================
elif navigation == "📝 Review 1 Feedback & Next Steps":
    st.title("📝 Review 1 Notes & Professor Feedback Tracker")
    st.markdown("""
    This section is designed to capture feedback and suggestions from the professor during **Review 1 tomorrow**.
    
    ### Scope of Review 1 (What We Are Presenting):
    1. **Project Architecture:** Hybrid combination of Oracle SQL/PL-SQL and Sentence-Transformers vector matching.
    2. **Database Design:** 5 Entities (Users, Candidate Profiles, Job Postings, Skills, Applications) in strict 3NF.
    3. **PL/SQL Features:** 
       - `fn_skill_match_pct` (Calculates keyword overlap percentage)
       - `sp_apply_job` (Calculates 60% semantic + 40% skill composite score)
       - `sp_get_eligible_candidates` (Pre-filtering with REF CURSOR)
       - `sp_shortlist_applications` (Batch update with explicit cursor)
       - 3 Automated Triggers (`trg_app_before_insert`, `trg_job_status_audit`, `trg_profile_touch`)
    4. **Working Demo Prototype:** Real-time pre-filtering, similarity scoring, application persistence, and SQL inspection.

    ### Questions & Potential Additions for Review 2:
    - *Does the instructor want custom PL/SQL packages?*
    - *Should we add MongoDB (NoSQL) for raw resume JSON storage (leveraging Lab 8–11)?*
    - *Are additional constraints or complex triggers needed?*
    """)
    st.info("All notes and adjustments discussed tomorrow can be directly appended into `PROJECT_CONTEXT.md`.")
