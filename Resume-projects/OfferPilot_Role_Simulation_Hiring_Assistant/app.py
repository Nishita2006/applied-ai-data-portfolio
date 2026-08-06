import io
import json
import re
from datetime import datetime

import pandas as pd
import streamlit as st

from src.job_parser import jd_skill_extractor
from src.resume_reader import extract_text_from_pdf
from src.llm_client import ask_llm, is_llm_available, transcribe_audio
from src.interview_analyzer import analyze_interview_transcript
from src.profile_verifier import (
    compare_resume_with_profiles,
    extract_profile_links,
    fetch_public_github_evidence,
)
from src.candidate_updates import (
    MILESTONES,
    STATUS_OPTIONS,
    build_status_message,
    extract_phone_number,
    extract_email_address,
    milestone_progress,
    send_twilio_sms,
    validate_phone_number,
)
from src.platform_services import (
    add_candidate_request,
    authenticate_user,
    create_portal_token,
    create_user,
    init_platform_db,
    list_audit_events,
    list_benchmarks,
    list_candidate_requests,
    list_candidates as list_persisted_candidates,
    list_interviews,
    list_jobs,
    list_users,
    log_communication,
    resolve_portal_token,
    save_benchmark,
    save_candidate,
    save_interview,
    save_job,
    send_smtp_email,
    user_count,
)

init_platform_db()
from src.llm_jd_analyzer import analyze_job_description_with_llm
from src.llm_simulation_generator import (
    generate_candidate_questions_with_llm,
    generate_simulation_task_with_llm,
)
from src.llm_rubric_scorer import score_simulation_response_with_llm
from src.llm_signal_card import generate_signal_card_with_llm
from src.semantic_matcher import (
    build_contextual_match_report,
    calculate_hybrid_candidate_score,
    find_jd_skills_in_resume_text,
    get_review_priority,
    normalize_skill_list,
    remove_negative_skill_sentences,
)


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Hiring Intelligence Workspace",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# DESIGN SYSTEM
# ============================================================

st.markdown(
    """
    <style>
        :root {
            color-scheme: light dark;
            --op-bg: #07111f;
            --op-panel: #0d1b2d;
            --op-panel-2: #11233a;
            --op-border: rgba(148, 163, 184, 0.18);
            --op-text: #f8fafc;
            --op-muted: #9fb0c7;
            --op-primary: #8b5cf6;
            --op-primary-2: #38bdf8;
            --op-success: #2dd4bf;
            --op-warning: #fbbf24;
            --op-danger: #fb7185;
        }

        @media (prefers-color-scheme: light) {
            :root {
                --op-bg: #f4f7fb; --op-panel: #ffffff; --op-panel-2: #edf3fa;
                --op-border: rgba(30, 41, 59, 0.16); --op-text: #172033;
                --op-muted: #53657b; --op-primary: #6d4aff; --op-primary-2: #087ea4;
                --op-success: #087f68; --op-warning: #a15c00; --op-danger: #be3455;
            }
            [data-testid="stHeader"] { background: rgba(244,247,251,.88) !important; }
            [data-testid="stSidebar"] { background: #fff !important; }
            .hero-title { color: #172033 !important; }
            .hero, .candidate-card, .section-card, .success-card, .role-header-card {
                background: rgba(255,255,255,.94) !important;
                box-shadow: 0 14px 35px rgba(31,41,55,.08) !important;
            }
            .mini-pill { color: #25344a !important; background: #f7f9fc !important; }
        }

        .stApp {
            background:
                radial-gradient(circle at 8% 0%, rgba(139, 92, 246, 0.18), transparent 28%),
                radial-gradient(circle at 95% 5%, rgba(56, 189, 248, 0.13), transparent 24%),
                var(--op-bg);
            color: var(--op-text);
        }

        [data-testid="stHeader"] {
            background: rgba(7, 17, 31, 0.72);
            backdrop-filter: blur(12px);
        }

        [data-testid="stSidebar"] {
            background: var(--op-panel);
            border-right: 1px solid var(--op-border);
        }

        .block-container {
            max-width: 1450px;
            padding-top: 1.6rem;
            padding-bottom: 3rem;
        }

        h1, h2, h3 {
            letter-spacing: -0.025em;
        }

        .hero {
            padding: 2rem 2.1rem;
            border: 1px solid var(--op-border);
            border-radius: 24px;
            background:
                linear-gradient(135deg, rgba(139, 92, 246, 0.15), rgba(56, 189, 248, 0.07)),
                rgba(13, 27, 45, 0.88);
            box-shadow: 0 24px 60px rgba(0, 0, 0, 0.28);
            margin-bottom: 1.2rem;
        }

        .eyebrow {
            color: #b9a7ff;
            font-size: 0.76rem;
            font-weight: 800;
            letter-spacing: 0.14em;
            text-transform: uppercase;
            margin-bottom: 0.6rem;
        }

        .hero-title {
            font-size: clamp(2.2rem, 4vw, 4.2rem);
            line-height: 0.98;
            font-weight: 850;
            margin: 0;
            color: white;
        }

        .gradient-text {
            background: linear-gradient(90deg, #c4b5fd, #7dd3fc);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .hero-copy {
            color: var(--op-muted);
            max-width: 850px;
            font-size: 1.04rem;
            line-height: 1.75;
            margin-top: 1rem;
            margin-bottom: 0;
        }

        .mini-pill {
            display: inline-block;
            padding: 0.38rem 0.72rem;
            margin: 0.9rem 0.35rem 0 0;
            border: 1px solid rgba(196, 181, 253, 0.22);
            border-radius: 999px;
            color: #dbeafe;
            background: rgba(15, 23, 42, 0.55);
            font-size: 0.78rem;
            font-weight: 650;
        }

        .section-card {
            padding: 1.35rem;
            border: 1px solid var(--op-border);
            border-radius: 18px;
            background: rgba(13, 27, 45, 0.82);
            margin-bottom: 1rem;
        }

        .role-header-card {
            padding: 1.35rem 1.5rem;
            border: 1px solid var(--op-border);
            border-radius: 18px;
            background:
                linear-gradient(135deg, rgba(139, 92, 246, 0.12), rgba(56, 189, 248, 0.06)),
                rgba(13, 27, 45, 0.86);
            margin-bottom: 1rem;
        }

        .role-title-large {
            color: white;
            font-size: 1.85rem;
            font-weight: 850;
            line-height: 1.2;
            margin-bottom: 0.35rem;
            overflow-wrap: anywhere;
        }

        .role-meta {
            color: var(--op-muted);
            font-size: 0.95rem;
            line-height: 1.6;
        }

        .skill-chip {
            display: inline-block;
            padding: 0.34rem 0.62rem;
            margin: 0.18rem 0.2rem 0.18rem 0;
            border-radius: 999px;
            font-size: 0.78rem;
            font-weight: 700;
            background: rgba(56, 189, 248, 0.10);
            border: 1px solid rgba(56, 189, 248, 0.22);
            color: #dbeafe;
        }

        .skill-chip-human {
            background: rgba(45, 212, 191, 0.10);
            border: 1px solid rgba(45, 212, 191, 0.22);
            color: #ccfbf1;
        }

        .skill-chip-preferred {
            background: rgba(139, 92, 246, 0.10);
            border: 1px solid rgba(139, 92, 246, 0.22);
            color: #ede9fe;
        }

        .success-card {
            padding: 1.25rem;
            border: 1px solid var(--op-border);
            border-radius: 16px;
            background: rgba(13, 27, 45, 0.82);
            min-height: 100%;
        }

        .success-card h4 {
            margin-top: 0;
            margin-bottom: 0.65rem;
            color: white;
        }

        .candidate-card {
            padding: 1rem 1.1rem;
            border: 1px solid var(--op-border);
            border-radius: 16px;
            background: linear-gradient(145deg, rgba(17, 35, 58, 0.88), rgba(9, 21, 36, 0.92));
            min-height: 176px;
        }

        .candidate-name {
            font-size: 1.05rem;
            font-weight: 800;
            color: white;
            margin-bottom: 0.15rem;
        }

        .candidate-rank {
            color: #a5b4fc;
            font-size: 0.78rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.08em;
        }

        .score-large {
            color: white;
            font-size: 2.15rem;
            font-weight: 850;
            line-height: 1;
            margin: 0.9rem 0 0.45rem;
        }

        .muted {
            color: var(--op-muted);
        }

        .status-chip {
            display: inline-block;
            padding: 0.28rem 0.58rem;
            border-radius: 999px;
            font-size: 0.72rem;
            font-weight: 800;
            margin-top: 0.25rem;
        }

        .chip-high {
            color: #99f6e4;
            background: rgba(45, 212, 191, 0.12);
            border: 1px solid rgba(45, 212, 191, 0.22);
        }

        .chip-medium {
            color: #fde68a;
            background: rgba(251, 191, 36, 0.12);
            border: 1px solid rgba(251, 191, 36, 0.22);
        }

        .chip-low {
            color: #fda4af;
            background: rgba(251, 113, 133, 0.12);
            border: 1px solid rgba(251, 113, 133, 0.22);
        }

        .step-number {
            display: inline-flex;
            width: 30px;
            height: 30px;
            align-items: center;
            justify-content: center;
            border-radius: 10px;
            margin-right: 0.5rem;
            font-weight: 850;
            background: linear-gradient(135deg, #8b5cf6, #38bdf8);
            color: white;
        }

        .signal-card {
            padding: 1.4rem;
            border: 1px solid rgba(139, 92, 246, 0.3);
            border-radius: 20px;
            background:
                radial-gradient(circle at 100% 0%, rgba(56, 189, 248, 0.12), transparent 28%),
                rgba(13, 27, 45, 0.92);
        }

        .disclaimer {
            padding: 0.8rem 1rem;
            border: 1px solid rgba(251, 191, 36, 0.18);
            border-radius: 12px;
            color: #cbd5e1;
            background: rgba(251, 191, 36, 0.05);
            font-size: 0.82rem;
        }

        div[data-testid="stMetric"] {
            background: rgba(13, 27, 45, 0.76);
            border: 1px solid var(--op-border);
            padding: 1rem;
            border-radius: 16px;
        }

        div[data-testid="stMetricValue"] {
            color: white;
        }

        .stButton > button,
        .stDownloadButton > button {
            border-radius: 11px;
            border: 1px solid rgba(139, 92, 246, 0.35);
            font-weight: 750;
            min-height: 2.75rem;
        }

        .stButton > button[kind="primary"] {
            background: linear-gradient(90deg, #7c3aed, #2563eb);
            border: none;
        }

        div[data-baseweb="tab-list"] {
            gap: 0.4rem;
            background: rgba(13, 27, 45, 0.68);
            border: 1px solid var(--op-border);
            border-radius: 14px;
            padding: 0.35rem;
        }

        button[data-baseweb="tab"] {
            border-radius: 10px;
            padding-left: 1rem;
            padding-right: 1rem;
        }

        [data-testid="stDataFrame"] {
            border: 1px solid var(--op-border);
            border-radius: 14px;
            overflow: hidden;
        }

        .footer {
            text-align: center;
            color: #718096;
            font-size: 0.78rem;
            margin-top: 2.5rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# DEMO DATA
# ============================================================

DEMO_JOB_DESCRIPTION = """
Software Engineering Intern — AI Hiring Tools

We are seeking a Software Engineering Intern to help build an AI-assisted hiring
workflow. The intern will work with Python, Streamlit, pandas, NLP, text matching,
APIs, Git, PDF parsing, and data analysis. Responsibilities include building
reliable user-facing features, testing scoring logic, documenting technical
decisions, collaborating with product and recruiting stakeholders, and presenting
results clearly.

Required qualifications:
- Python
- Streamlit
- pandas
- NLP
- APIs
- Git
- Data analysis
- Problem solving
- Communication
- Collaboration

Preferred qualifications:
- Resume parsing
- Embeddings or semantic search
- Machine learning
- Experience building LLM applications
- Familiarity with evaluation and responsible AI

The ideal candidate can translate ambiguous recruiting needs into a practical,
well-tested product and explain technical tradeoffs to nontechnical stakeholders.
""".strip()


DEMO_CANDIDATES = [
    {
        "Candidate": "Maya Patel",
        "Resume Text": """
        Computer Science student who built and deployed a Streamlit resume-screening
        application using Python, pandas, NLP, TF-IDF text matching, PDF parsing,
        REST APIs, and Git. Designed the candidate-ranking workflow, tested strong,
        medium, and weak resume cases, and improved ranking precision from 72% to 89%.
        Presented results to recruiting stakeholders and documented model limitations,
        fairness risks, and human-review requirements. Collaborated with two developers
        and owned the evaluation dashboard.
        """,
    },
    {
        "Candidate": "Jordan Lee",
        "Resume Text": """
        Data Science student experienced with Python, pandas, machine learning, SQL,
        Git, data analysis, and visualization. Built classification models and a
        dashboard for a student-services project in a four-person team. Supported API
        integration and presented the final project. Familiar with NLP concepts but has
        not independently deployed a Streamlit application. Interested in learning PDF
        parsing and LLM systems.
        """,
    },
    {
        "Candidate": "Alex Morgan",
        "Resume Text": """
        Business student with strong communication, presentation, customer service,
        and team coordination experience. Worked with project stakeholders and prepared
        weekly reports in Excel. Has limited classroom exposure to Python and has not
        built applications with Streamlit, pandas, NLP, APIs, or Git. Interested in
        recruiting operations and learning technical tools.
        """,
    },
]


DEMO_RESPONSES = {
    "Maya Patel": """
    I would begin by defining the decision the recruiter needs to make and the
    evidence the system should expose. I would create a pipeline with PDF text
    extraction, normalized skill detection, semantic similarity, and a transparent
    weighted score. I would keep resume fit and simulation performance separate so
    recruiters can see why a candidate ranked highly.

    For testing, I would build strong, medium, and weak candidate fixtures,
    including negative-skill sentences such as "limited Python experience." I would
    test parsing failures, empty files, duplicate resumes, and scoring stability.
    The interface would show matched evidence, missing skills, confidence, and a
    clear human-review warning.

    I would not use protected attributes, photographs, names, or inferred
    demographic information in scoring. I would evaluate false positives and false
    negatives across test cases, document limitations, and require the recruiter to
    make the final decision. I would release the feature in stages, collect
    recruiter feedback, and monitor whether rankings remain explainable and useful.
    """,
    "Jordan Lee": """
    I would build the application in Streamlit and use Python and pandas for the
    workflow. I would parse resumes, compare the text with the job description, and
    rank candidates. I would test several resumes and ask recruiters whether the
    rankings look correct. I would add a dashboard and document the project.
    """,
    "Alex Morgan": """
    I would upload resumes and let AI decide which candidate is best. The system
    should save recruiters time by automatically rejecting low-scoring candidates.
    I would focus on making the interface simple and visually appealing.
    """,
}


# ============================================================
# SESSION STATE
# ============================================================

DEFAULT_STATE = {
    "job_description": "",
    "jd_analysis": {},
    "category": "",
    "jd_role_skills": [],
    "jd_soft_skills": [],
    "candidate_df": pd.DataFrame(),
    "heatmap_df": pd.DataFrame(),
    "simulation_task": "",
    "candidate_responses": {},
    "candidate_rubric_scores": {},
    "candidate_signal_cards": {},
    "current_candidate_answer": "",
    "last_selected_candidate": "",
    "recruiter_notes": {},
    "recruiter_decisions": {},
    "follow_up_questions": {},
    "candidate_resume_texts": {},
    "candidate_skill_evidence": {},
    "skill_verification_results": {},
    "candidate_ats_reports": {},
    "interview_transcripts": {},
    "interview_analyses": {},
    "interview_consent": {},
    "profile_verifications": {},
    "candidate_contacts": {},
    "candidate_milestones": {},
    "candidate_sms_logs": {},
    "workspace_user": None,
    "active_job_id": None,
    "candidate_db_ids": {},
    "screening_completed": False,
    "demo_mode": False,
    "assistant_messages": [],
    "returning_candidate_alerts": [],
}

for key, default_value in DEFAULT_STATE.items():
    if key not in st.session_state:
        st.session_state[key] = default_value

AUTH_REQUIRED = True

portal_token = st.query_params.get("portal_token", "")
if portal_token:
    portal_candidate = resolve_portal_token(portal_token)
    st.markdown("## OfferPilot candidate portal")
    if not portal_candidate:
        st.error("This candidate portal link is invalid, expired, or revoked.")
        st.stop()
    try:
        portal_workflow = json.loads(portal_candidate.get("workflow_json") or "{}")
    except Exception:
        portal_workflow = {}
    portal_statuses = portal_workflow.get("milestones", {})
    if not portal_statuses:
        portal_statuses = {
            key: "Completed" if key == "application_received" else "Not started"
            for key, _ in MILESTONES
        }
    st.success(f'Welcome, {portal_candidate["name"]}.')
    portal_progress = milestone_progress(portal_statuses)
    st.progress(portal_progress, text=f"Application progress · {round(portal_progress * 100)}%")
    portal_rows = [
        {
            "Milestone": label,
            "Status": portal_statuses.get(key, "Not started"),
        }
        for key, label in MILESTONES
    ]
    st.dataframe(pd.DataFrame(portal_rows), use_container_width=True, hide_index=True)
    st.markdown("### Candidate request")
    with st.form("candidate_portal_request"):
        request_type = st.selectbox(
            "Request type",
            [
                "Update contact information",
                "Interview accommodation",
                "Withdraw application",
                "Delete my data",
                "Other question",
            ],
        )
        request_details = st.text_area("Details")
        request_submitted = st.form_submit_button("Submit request", type="primary")
    if request_submitted:
        add_candidate_request(portal_candidate["id"], request_type, request_details)
        st.success("Your request was submitted to the recruiting team.")
    st.caption("This page does not display internal scores, notes, or reviewer discussions.")
    st.stop()

if AUTH_REQUIRED and not st.session_state.workspace_user:
    st.markdown(
        """
        <div class="role-header-card" style="max-width:720px;margin:8vh auto 1rem;">
            <div class="eyebrow">Secure recruiter access</div>
            <div class="role-title-large">Hiring Intelligence Workspace</div>
            <p class="muted">Sign in to review roles, candidates, evidence, interviews, and decisions.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    _, login_column, _ = st.columns([1, 1.35, 1])
    with login_column:
        st.markdown("### Create workspace" if user_count() == 0 else "### Sign in")
    if user_count() == 0:
        with login_column:
            st.info("First visit: create the administrator who will manage recruiter accounts.")
            with st.form("first_admin_form"):
                admin_name = st.text_input("Full name")
                admin_email = st.text_input("Work email")
                admin_password = st.text_input("Password", type="password", help="Use at least 10 characters.")
                create_admin = st.form_submit_button("Create account and continue", type="primary", use_container_width=True)
            if create_admin:
                try:
                    create_user(admin_email, admin_name, "admin", admin_password)
                    st.session_state.workspace_user = authenticate_user(admin_email, admin_password)
                    st.rerun()
                except Exception as exc:
                    st.error(str(exc))
    else:
        with login_column:
            with st.form("workspace_login_form"):
                login_email = st.text_input("Work email")
                login_password = st.text_input("Password", type="password")
                login_clicked = st.form_submit_button("Sign in", type="primary", use_container_width=True)
            if login_clicked:
                user = authenticate_user(login_email, login_password)
                if user:
                    st.session_state.workspace_user = user
                    st.rerun()
                else:
                    st.error("The email or password is incorrect.")
    st.stop()


# ============================================================
# HELPERS
# ============================================================

def fallback_jd_analysis(job_description: str) -> dict:
    role_skills, soft_skills = jd_skill_extractor(job_description)
    title = "AI Hiring Tools Intern"
    lowered = job_description.lower()

    if "data analyst" in lowered:
        title = "Data Analyst"
    elif "software" in lowered:
        title = "Software Engineering Intern"
    elif "machine learning" in lowered:
        title = "Machine Learning Intern"

    return {
        "role_title": title,
        "role_category": "Software Engineering",
        "seniority_level": "Intern",
        "required_skills": normalize_skill_list(role_skills),
        "preferred_skills": [
            "resume parsing",
            "semantic search",
            "machine learning",
            "llm applications",
            "responsible ai",
        ],
        "soft_skills": normalize_skill_list(soft_skills),
        "responsibilities": [
            "Build and test user-facing hiring workflow features.",
            "Translate recruiter needs into product requirements.",
            "Evaluate scoring logic and communicate technical tradeoffs.",
            "Document limitations and collaborate with stakeholders.",
        ],
        "ideal_candidate_summary": (
            "A practical builder who combines Python and applied AI skills with "
            "clear communication, thoughtful testing, and responsible product judgment."
        ),
    }


def fallback_simulation_task(jd_analysis: dict) -> str:
    role_title = jd_analysis.get("role_title", "candidate")
    return f"""
### Business scenario
A recruiting team wants to introduce an AI-assisted resume screening workflow for
a high-volume {role_title} opening. Recruiters want faster review, but they are
concerned about unexplained scores, false matches, and over-automation.

### Candidate task
Propose a practical solution for the first working version of the product. Explain:

1. The workflow and core technical components.
2. How candidate fit should be scored and explained.
3. The test cases and evaluation metrics you would use.
4. How you would reduce bias and preserve human oversight.
5. How you would roll out the product and collect recruiter feedback.

### Expected response
Provide a structured response with architecture, scoring logic, validation,
responsible-AI safeguards, tradeoffs, and rollout steps.
""".strip()


def get_analysis(job_description: str) -> dict:
    try:
        analysis = analyze_job_description_with_llm(job_description)
        if analysis and analysis.get("required_skills"):
            if "intern" in job_description.lower():
                analysis["seniority_level"] = "Intern / Entry-level"
            return analysis
    except Exception:
        pass

    analysis = fallback_jd_analysis(job_description)
    if "intern" in job_description.lower():
        analysis["seniority_level"] = "Intern / Entry-level"
    return analysis


def get_simulation(job_description: str, jd_analysis: dict) -> str:
    try:
        task = generate_simulation_task_with_llm(job_description, jd_analysis)
        if task and str(task).strip():
            return task
    except Exception:
        pass
    return fallback_simulation_task(jd_analysis)


def fallback_rubric_score(response: str, category: str) -> dict:
    text = response.lower()
    word_count = len(response.split())

    dimensions = {
        "Technical Correctness": 8,
        "Reasoning Clarity": 8,
        "Role Relevance": 8,
        "Communication": 8,
        "Assumptions and Tradeoffs": 8,
    }

    technical_terms = [
        "python", "streamlit", "pipeline", "pdf", "semantic", "tf-idf",
        "api", "testing", "evaluation", "scoring", "dashboard",
    ]
    reasoning_terms = [
        "because", "first", "then", "tradeoff", "assumption", "evidence",
        "false positive", "false negative",
    ]
    role_terms = [
        "recruiter", "candidate", "resume", "hiring", "human review",
        "stakeholder", "workflow",
    ]
    responsibility_terms = [
        "bias", "protected", "fairness", "responsible", "human oversight",
        "limitation", "monitor",
    ]

    dimensions["Technical Correctness"] += min(
        12, sum(term in text for term in technical_terms)
    )
    dimensions["Reasoning Clarity"] += min(
        12, sum(term in text for term in reasoning_terms) * 2
    )
    dimensions["Role Relevance"] += min(
        12, sum(term in text for term in role_terms) * 2
    )
    dimensions["Communication"] += min(12, max(0, min(word_count // 25, 12)))
    dimensions["Assumptions and Tradeoffs"] += min(
        12, sum(term in text for term in responsibility_terms) * 2
    )

    dimensions = {key: min(value, 20) for key, value in dimensions.items()}
    dimensions["Simulation Score"] = sum(dimensions.values())
    return dimensions


def score_response(response: str, category: str, task: str) -> dict:
    try:
        scores = score_simulation_response_with_llm(response, category, task)
        if scores and "Simulation Score" in scores:
            return scores
    except Exception:
        pass
    return fallback_rubric_score(response, category)


def fallback_signal_card(
    candidate: str,
    resume_score: int,
    simulation_score: int,
    matched_skills: list,
    missing_skills: list,
) -> dict:
    final_numeric = round((0.60 * resume_score) + (0.40 * simulation_score))

    if final_numeric >= 75:
        confidence = "High"
        next_step = "Advance to structured interview"
    elif final_numeric >= 50:
        confidence = "Medium"
        next_step = "Conduct targeted recruiter screen"
    else:
        confidence = "Low"
        next_step = "Do not advance without additional evidence"

    strengths = [
        f"Demonstrated evidence across {min(len(matched_skills), 5)} relevant skills.",
        "Completed a role-relevant work simulation.",
    ]
    if simulation_score >= 75:
        strengths.append("Strong structured reasoning and practical judgment.")

    risks = []
    if missing_skills:
        risks.append("Missing or unclear evidence for: " + ", ".join(missing_skills[:4]))
    if resume_score < 50:
        risks.append("Resume evidence is below the preferred role-fit threshold.")
    if simulation_score < 50:
        risks.append("Simulation response needs deeper reasoning and validation detail.")
    if not risks:
        risks.append("Validate depth of ownership and execution during interview.")

    return {
        "Final Confidence": confidence,
        "Final Confidence Score": final_numeric,
        "Recommended Next Step": next_step,
        "Recruiter Summary": (
            f"{candidate} has a {resume_score}% resume match and a "
            f"{simulation_score}% simulation score. The combined evidence suggests "
            f"{confidence.lower()} confidence for the next stage."
        ),
        "Strengths": strengths,
        "Risks": risks,
        "Interview Focus Areas": [
            "Depth of ownership behind the strongest project evidence.",
            "Approach to testing, evaluation, and failure handling.",
            "Ability to explain tradeoffs to recruiting stakeholders.",
        ],
    }


def create_signal_card(
    candidate: str,
    resume_score: int,
    rubric_scores: dict,
    matched_skills: list,
    missing_skills: list,
) -> dict:
    simulation_score = rubric_scores.get("Simulation Score", 0)
    try:
        card = generate_signal_card_with_llm(
            candidate,
            resume_score,
            simulation_score,
            matched_skills,
            missing_skills,
            rubric_scores,
            st.session_state.category,
        )
        if card and card.get("Final Confidence"):
            if "Final Confidence Score" not in card:
                card["Final Confidence Score"] = round(
                    (0.60 * resume_score) + (0.40 * simulation_score)
                )
            return card
    except Exception:
        pass

    return fallback_signal_card(
        candidate,
        resume_score,
        simulation_score,
        matched_skills,
        missing_skills,
    )



def split_resume_into_sentences(resume_text: str) -> list[str]:
    """Create readable evidence snippets from resume text."""
    normalized = re.sub(r"\s+", " ", resume_text or "").strip()
    if not normalized:
        return []

    parts = re.split(r"(?<=[.!?])\s+|[\n\r•]+", normalized)
    return [part.strip(" -•\t") for part in parts if len(part.strip()) >= 18]


SKILL_ALIASES = {
    "python": ["python"],
    "streamlit": ["streamlit"],
    "pandas": ["pandas"],
    "nlp": ["nlp", "natural language processing", "text matching", "text analysis"],
    "apis": ["api", "apis", "rest api", "api integration"],
    "git": ["git", "github", "version control"],
    "data analysis": ["data analysis", "analytics", "analyzed", "analysis"],
    "problem solving": ["problem solving", "problem-solving", "debugged", "troubleshot"],
    "communication": ["communication", "presented", "explained", "stakeholders"],
    "collaboration": ["collaboration", "collaborated", "team", "teamwork"],
    "presentation": ["presentation", "presented", "demoed"],
}


def get_skill_aliases(skill: str) -> list[str]:
    normalized = skill.lower().strip()
    return list(dict.fromkeys([normalized] + SKILL_ALIASES.get(normalized, [])))


def find_skill_evidence(skill: str, sentences: list[str]) -> list[str]:
    aliases = get_skill_aliases(skill)
    matches = []

    for sentence in sentences:
        lowered = sentence.lower()
        if any(alias in lowered for alias in aliases):
            matches.append(sentence)

    return matches[:3]


def classify_skill_evidence(
    skill: str,
    evidence_lines: list[str],
) -> tuple[str, int]:
    if not evidence_lines:
        return "Not evidenced", 0

    combined = " ".join(evidence_lines).lower()

    action_signals = [
        "built", "created", "developed", "implemented", "designed",
        "deployed", "analyzed", "integrated", "trained", "evaluated",
        "tested", "debugged", "improved", "collaborated", "presented",
        "worked",
    ]
    project_signals = [
        "project", "application", "dashboard", "model", "pipeline",
        "system", "platform", "tool", "internship", "research",
        "team", "client",
    ]
    outcome_signals = [
        "%", "increased", "reduced", "improved", "accuracy",
        "users", "records", "deployed", "production", "result",
        "performance",
    ]

    score = 20
    score += min(35, 10 * sum(signal in combined for signal in action_signals))
    score += min(30, 8 * sum(signal in combined for signal in project_signals))
    score += min(15, 5 * sum(signal in combined for signal in outcome_signals))
    score = min(score, 100)

    if score >= 70:
        return "Strong project evidence", score
    if score >= 45:
        return "Some evidence — verify depth", score
    return "Keyword mention only", score


def build_skill_questions(
    skill: str,
    evidence_lines: list[str],
    evidence_strength: str,
) -> list[str]:
    if not evidence_lines:
        return [
            (
                f"The role requires **{skill}**, but the resume does not show where "
                "you used it. Describe the closest project, course, or work example."
            ),
            (
                f"What would you need to learn before using **{skill}** independently "
                "in this role?"
            ),
        ]

    evidence = evidence_lines[0]
    questions = [
        (
            f'Your resume says: "{evidence}" What did you personally build, '
            "implement, or own?"
        ),
        (
            f"Why did you choose **{skill}** for that work instead of another "
            "approach? What tradeoff did you make?"
        ),
        (
            f"What was the hardest bug, failure, or limitation while using "
            f"**{skill}**, and how did you diagnose it?"
        ),
        (
            f"What measurable result or test proves your use of **{skill}** "
            "was effective?"
        ),
    ]

    if evidence_strength == "Keyword mention only":
        questions.insert(
            1,
            (
                f"The resume mentions **{skill}** but gives little implementation "
                "detail. Describe the exact workflow, files, components, or "
                "deliverable you produced."
            ),
        )

    return questions


def build_skill_verification(
    candidate_name: str,
    resume_text: str,
    target_skills: list[str],
) -> list[dict]:
    sentences = split_resume_into_sentences(resume_text)
    verification_rows = []

    for skill in normalize_skill_list(target_skills):
        evidence_lines = find_skill_evidence(skill, sentences)
        evidence_strength, evidence_score = classify_skill_evidence(
            skill,
            evidence_lines,
        )

        verification_rows.append(
            {
                "Skill": skill,
                "Evidence Strength": evidence_strength,
                "Evidence Score": evidence_score,
                "Resume Evidence": (
                    " | ".join(evidence_lines)
                    if evidence_lines
                    else "No supporting resume evidence detected."
                ),
                "Questions": build_skill_questions(
                    skill,
                    evidence_lines,
                    evidence_strength,
                ),
            }
        )

    return verification_rows


def candidate_score_row(candidate_name: str, resume_text: str) -> tuple[dict, dict]:
    clean_resume_text = remove_negative_skill_sentences(resume_text)

    jd_technical_skills = normalize_skill_list(st.session_state.jd_role_skills)
    jd_soft_skills = normalize_skill_list(st.session_state.jd_soft_skills)
    jd_all_skills = normalize_skill_list(jd_technical_skills + jd_soft_skills)

    resume_role_skills, resume_soft_skills = jd_skill_extractor(clean_resume_text)
    direct_matches = find_jd_skills_in_resume_text(
        jd_technical_skills + jd_soft_skills,
        clean_resume_text,
    )
    resume_match_skills = normalize_skill_list(
        resume_role_skills + resume_soft_skills + direct_matches
    )

    technical_match = calculate_hybrid_candidate_score(
        st.session_state.job_description,
        clean_resume_text,
        jd_technical_skills,
        resume_match_skills,
    )
    soft_match = calculate_hybrid_candidate_score(
        st.session_state.job_description,
        clean_resume_text,
        jd_soft_skills,
        resume_match_skills,
    )

    technical_context = build_contextual_match_report(
        jd_technical_skills, clean_resume_text
    )
    soft_context = build_contextual_match_report(
        jd_soft_skills, clean_resume_text
    )

    final_score = round(
        (0.70 * technical_context["score"])
        + (0.20 * technical_match["text_similarity_score"])
        + (0.10 * soft_context["score"])
    )

    matched_skills = normalize_skill_list(
        technical_context["matched"] + soft_context["matched"]
    )
    missing_skills = normalize_skill_list(
        technical_context["missing"] + soft_context["missing"]
    )

    result = {
        "Candidate": candidate_name,
        "Match Score": final_score,
        "Technical Skill Score": technical_context["score"],
        "Text Similarity": technical_match["text_similarity_score"],
        "Soft Skill Score": soft_context["score"],
        "Related Skills": ", ".join(
            technical_context["partial"] + soft_context["partial"]
        ),
        "Review Priority": get_review_priority(final_score),
        "Matched Skills": ", ".join(matched_skills),
        "Missing Skills": ", ".join(missing_skills),
        "Resume Skills": ", ".join(resume_match_skills),
    }

    heatmap_row = {"Candidate": candidate_name}
    for skill in jd_all_skills:
        match_item = next(
            (
                item
                for item in technical_context["matches"] + soft_context["matches"]
                if item["skill"] == skill
            ),
            None,
        )
        heatmap_row[skill] = (
            match_item["status"] if match_item else "Missing evidence"
        )

    st.session_state.candidate_ats_reports[candidate_name] = {
        "technical": technical_context,
        "human": soft_context,
    }

    return result, heatmap_row


def build_candidate_tables(candidate_documents: list[dict]) -> None:
    candidate_results = []
    heatmap_results = []

    resume_texts = {}
    skill_evidence = {}

    prior_candidates = list_persisted_candidates()
    returning_alerts = []
    for candidate in candidate_documents:
        candidate_name = candidate["Candidate"]
        resume_text = candidate["Resume Text"]

        result, heatmap_row = candidate_score_row(
            candidate_name,
            resume_text,
        )
        candidate_results.append(result)
        heatmap_results.append(heatmap_row)

        target_skills = normalize_skill_list(
            st.session_state.jd_role_skills
            + st.session_state.jd_soft_skills
        )
        resume_texts[candidate_name] = resume_text
        profile_links = extract_profile_links(resume_text)
        if profile_links["github_username"]:
            try:
                github_evidence = fetch_public_github_evidence(
                    profile_links["github_username"]
                )
                profile_comparison = compare_resume_with_profiles(
                    resume_text, github_evidence
                )
                st.session_state.profile_verifications[candidate_name] = {
                    "github_url": profile_links["github_url"],
                    "linkedin_url": profile_links["linkedin_url"],
                    "github_evidence": github_evidence,
                    "github_error": "",
                    "comparison": profile_comparison,
                }
            except ValueError as exc:
                st.session_state.profile_verifications[candidate_name] = {
                    "github_url": profile_links["github_url"],
                    "linkedin_url": profile_links["linkedin_url"],
                    "github_evidence": None,
                    "github_error": str(exc),
                    "comparison": compare_resume_with_profiles(resume_text),
                }

        try:
            default_country_code = st.secrets.get("DEFAULT_PHONE_COUNTRY_CODE", "")
            application_consent = str(
                st.secrets.get("APPLICATION_SMS_CONSENT_CAPTURED", "false")
            ).strip().lower() in {"1", "true", "yes", "on"}
        except Exception:
            default_country_code = ""
            application_consent = False
        detected_phone = extract_phone_number(resume_text, default_country_code)
        detected_email = extract_email_address(resume_text)
        prior_matches = [
            row for row in prior_candidates
            if row.get("job_id") != st.session_state.active_job_id
            and (
                row.get("name", "").strip().lower() == candidate_name.strip().lower()
                or (detected_email and row.get("email", "").strip().lower() == detected_email.lower())
            )
        ]
        if prior_matches:
            returning_alerts.append(
                f"{candidate_name} appears in {len(prior_matches)} earlier application record(s). Review History before deciding."
            )
        existing_contact = st.session_state.candidate_contacts.get(candidate_name, {})
        st.session_state.candidate_contacts[candidate_name] = {
            "phone": existing_contact.get("phone") or detected_phone,
            "sms_consent": existing_contact.get("sms_consent", application_consent),
            "auto_updates": existing_contact.get("auto_updates", True),
            "consent_source": existing_contact.get(
                "consent_source",
                "Application form" if application_consent else "Not recorded",
            ),
            "email": existing_contact.get("email") or detected_email,
        }
        skill_evidence[candidate_name] = build_skill_verification(
            candidate_name,
            resume_text,
            target_skills,
        )

    candidate_df = pd.DataFrame(candidate_results)
    candidate_df = candidate_df.sort_values("Match Score", ascending=False).reset_index(drop=True)
    candidate_df.insert(0, "Rank", range(1, len(candidate_df) + 1))

    st.session_state.candidate_df = candidate_df
    st.session_state.heatmap_df = pd.DataFrame(heatmap_results)
    st.session_state.candidate_resume_texts = resume_texts
    st.session_state.candidate_skill_evidence = skill_evidence
    st.session_state.screening_completed = True
    st.session_state.returning_candidate_alerts = list(dict.fromkeys(returning_alerts))

    actor = (st.session_state.workspace_user or {}).get("email", "system")
    for candidate_name, resume_text in resume_texts.items():
        row = candidate_df[candidate_df["Candidate"] == candidate_name].iloc[0]
        contact = st.session_state.candidate_contacts.get(candidate_name, {})
        candidate_id = save_candidate(
            st.session_state.active_job_id,
            candidate_name,
            resume_text,
            workflow={
                "ats": row.to_dict(),
                "milestones": st.session_state.candidate_milestones.get(candidate_name, {}),
            },
            phone=contact.get("phone", ""),
            email=contact.get("email", ""),
            actor=actor,
        )
        st.session_state.candidate_db_ids[candidate_name] = candidate_id


def reset_workspace() -> None:
    for key, default_value in DEFAULT_STATE.items():
        st.session_state[key] = default_value
    st.rerun()


def analyze_job(job_description: str) -> None:
    with st.spinner("Analyzing the role and preparing the assessment workflow..."):
        analysis = get_analysis(job_description)
        role_skills = normalize_skill_list(analysis.get("required_skills", []))
        soft_skills = normalize_skill_list(analysis.get("soft_skills", []))
        category = analysis.get("role_category", "General")
        simulation = get_simulation(job_description, analysis)

        st.session_state.job_description = job_description
        st.session_state.jd_analysis = analysis
        st.session_state.jd_role_skills = role_skills
        st.session_state.jd_soft_skills = soft_skills
        st.session_state.category = category
        st.session_state.simulation_task = simulation
        actor = (st.session_state.workspace_user or {}).get("email", "system")
        st.session_state.active_job_id = save_job(
            analysis.get("role_title", "Untitled role"),
            job_description,
            analysis,
            actor,
        )


def load_demo() -> None:
    reset_keys = [
        "candidate_df",
        "heatmap_df",
        "candidate_responses",
        "candidate_rubric_scores",
        "candidate_signal_cards",
        "recruiter_notes",
        "recruiter_decisions",
        "follow_up_questions",
    ]
    for key in reset_keys:
        st.session_state[key] = DEFAULT_STATE[key].copy() if hasattr(DEFAULT_STATE[key], "copy") else DEFAULT_STATE[key]

    st.session_state.demo_mode = True
    analyze_job(DEMO_JOB_DESCRIPTION)
    build_candidate_tables(DEMO_CANDIDATES)

    for candidate_name, response in DEMO_RESPONSES.items():
        candidate_row = st.session_state.candidate_df[
            st.session_state.candidate_df["Candidate"] == candidate_name
        ].iloc[0]

        rubric = score_response(
            response,
            st.session_state.category,
            st.session_state.simulation_task,
        )

        matched = (
            candidate_row["Matched Skills"].split(", ")
            if candidate_row["Matched Skills"]
            else []
        )
        missing = (
            candidate_row["Missing Skills"].split(", ")
            if candidate_row["Missing Skills"]
            else []
        )

        card = create_signal_card(
            candidate_name,
            int(candidate_row["Match Score"]),
            rubric,
            matched,
            missing,
        )

        st.session_state.candidate_responses[candidate_name] = response
        st.session_state.candidate_rubric_scores[candidate_name] = rubric
        st.session_state.candidate_signal_cards[candidate_name] = card

    st.session_state.recruiter_decisions = {
        "Maya Patel": "Move Forward",
        "Jordan Lee": "Needs More Review",
        "Alex Morgan": "Hold",
    }
    st.session_state.recruiter_notes = {
        "Maya Patel": "Strong evidence of product thinking, testing, and responsible AI judgment.",
        "Jordan Lee": "Promising foundation; validate hands-on Streamlit and LLM application experience.",
        "Alex Morgan": "Communication is strong, but current technical evidence is limited.",
    }


def export_review_data() -> bytes:
    if st.session_state.candidate_df.empty:
        return b""

    export_df = st.session_state.candidate_df.copy()
    export_df["Simulation Score"] = export_df["Candidate"].map(
        lambda name: st.session_state.candidate_rubric_scores.get(name, {}).get(
            "Simulation Score", ""
        )
    )
    export_df["Final Confidence"] = export_df["Candidate"].map(
        lambda name: st.session_state.candidate_signal_cards.get(name, {}).get(
            "Final Confidence", ""
        )
    )
    export_df["Final Confidence Score"] = export_df["Candidate"].map(
        lambda name: st.session_state.candidate_signal_cards.get(name, {}).get(
            "Final Confidence Score", ""
        )
    )
    export_df["Recruiter Decision"] = export_df["Candidate"].map(
        lambda name: st.session_state.recruiter_decisions.get(
            name, "Needs More Review"
        )
    )
    export_df["Recruiter Notes"] = export_df["Candidate"].map(
        lambda name: st.session_state.recruiter_notes.get(name, "")
    )
    return export_df.to_csv(index=False).encode("utf-8")


def send_automatic_decision_update(candidate_name: str, decision: str) -> tuple[bool, str]:
    contact = st.session_state.candidate_contacts.get(candidate_name, {})
    if not contact.get("sms_consent") or not contact.get("auto_updates", True):
        return False, "Automatic SMS is not enabled for this candidate."
    phone = contact.get("phone", "")
    if not validate_phone_number(phone):
        return False, "The extracted phone number needs E.164 confirmation before SMS can be sent."

    decision_copy = {
        "Move Forward": "Your application is moving forward. The recruiting team will contact you with the next step.",
        "Needs More Review": "Your application remains under review. We will share another update when the review is complete.",
        "Hold": "Your application is still active and currently on hold. We will contact you when the status changes.",
        "Reject": "The team has completed its review and will not be moving forward with your application.",
    }
    first_name = candidate_name.strip().split()[0] if candidate_name.strip() else "Candidate"
    body = f"OfferPilot update for {first_name}: {decision_copy.get(decision, 'Your application status was updated.')}"
    try:
        account_sid = st.secrets["TWILIO_ACCOUNT_SID"]
        auth_token = st.secrets["TWILIO_AUTH_TOKEN"]
        from_number = st.secrets["TWILIO_FROM_NUMBER"]
        delivery = send_twilio_sms(
            account_sid, auth_token, from_number, phone, body
        )
    except Exception as exc:
        return False, str(exc)

    st.session_state.candidate_sms_logs.setdefault(candidate_name, []).append(
        {
            "Milestone": "Recruiter decision",
            "Status": decision,
            "Message": body,
            "Delivery": delivery["status"],
            "Sent at": delivery["sent_at"],
            "Message SID": delivery["sid"],
        }
    )
    statuses = st.session_state.candidate_milestones.setdefault(
        candidate_name,
        {key: "Not started" for key, _ in MILESTONES},
    )
    statuses["final_review"] = "Completed"
    if decision == "Reject":
        statuses["decision_shared"] = "Completed"
    return True, "Decision SMS queued by Twilio."


def confidence_chip(priority: str) -> tuple[str, str]:
    if "High" in priority:
        return "Strong fit", "chip-high"
    if "Medium" in priority:
        return "Review", "chip-medium"
    return "Limited fit", "chip-low"


def render_candidate_cards(df: pd.DataFrame) -> None:
    columns = st.columns(min(3, len(df)))

    for index, (_, row) in enumerate(df.head(3).iterrows()):
        label, css_class = confidence_chip(row["Review Priority"])
        matched_count = len(
            [skill for skill in str(row["Matched Skills"]).split(", ") if skill]
        )
        related_count = len(
            [skill for skill in str(row.get("Related Skills", "")).split(", ") if skill]
        )
        rank_label = (
            "Only candidate" if len(df) == 1 else f'Rank #{int(row["Rank"])}'
        )
        evidence_summary = f"{matched_count} matched competencies"
        if related_count:
            evidence_summary += f" · {related_count} related"

        with columns[index]:
            st.markdown(
                f"""
                <div class="candidate-card">
                    <div class="candidate-rank">{rank_label}</div>
                    <div class="candidate-name">{row["Candidate"]}</div>
                    <div class="score-large">{int(row["Match Score"])}%</div>
                    <div class="muted">{evidence_summary}</div>
                    <span class="status-chip {css_class}">{label}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )


def load_saved_workspace(saved_job: dict) -> None:
    """Switch the active recruiter workspace to a persisted role and its candidates."""
    try:
        saved_analysis = json.loads(saved_job.get("analysis_json") or "{}")
    except Exception:
        saved_analysis = {}
    st.session_state.active_job_id = saved_job["id"]
    st.session_state.job_description = saved_job["description"]
    st.session_state.jd_analysis = saved_analysis
    st.session_state.jd_role_skills = normalize_skill_list(saved_analysis.get("required_skills", []))
    st.session_state.jd_soft_skills = normalize_skill_list(saved_analysis.get("soft_skills", []))
    st.session_state.category = saved_analysis.get("role_category", "General")
    st.session_state.simulation_task = get_simulation(saved_job["description"], saved_analysis)
    saved_candidates = list_persisted_candidates(saved_job["id"])
    if saved_candidates:
        build_candidate_tables([
            {"Candidate": row["name"], "Resume Text": row["resume_text"]}
            for row in saved_candidates
        ])


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:
    st.markdown("## Recruiter workspace")
    st.caption("Hiring intelligence and candidate operations")
    current_workspace_user = st.session_state.workspace_user or {}
    st.caption(
        f'Signed in as {current_workspace_user.get("name", "Unknown")} · '
        f'{current_workspace_user.get("role", "unknown").replace("_", " ").title()}'
    )
    with st.popover("Open app guide", use_container_width=True):
        st.markdown(
            "**1. Role** — add or reopen a job.  \n"
            "**2. Screen** — upload resumes together.  \n"
            "**3. Compare** — audit evidence and ranking.  \n"
            "**4. Validate** — use tailored questions and practical review.  \n"
            "**5. Decide** — record the human decision and update the candidate."
        )
    saved_role_rows = list_jobs()
    if saved_role_rows:
        role_options = {f'{row["title"]} · {row["id"]}': row for row in saved_role_rows}
        selected_role_label = st.selectbox("Active role", list(role_options), key="sidebar_active_role")
        if st.button("Switch role workspace", use_container_width=True):
            load_saved_workspace(role_options[selected_role_label])
            st.rerun()
    if AUTH_REQUIRED and st.button("Sign out", use_container_width=True):
        st.session_state.workspace_user = None
        st.rerun()

    progress_steps = [
        ("1", "Role analyzed", bool(st.session_state.job_description)),
        ("2", "Candidates screened", not st.session_state.candidate_df.empty),
        ("3", "Simulation reviewed", bool(st.session_state.candidate_signal_cards)),
        ("4", "Decision documented", bool(st.session_state.recruiter_decisions)),
    ]

    st.markdown("### Workflow")
    for number, label, completed in progress_steps:
        icon = "✓" if completed else number
        st.markdown(f"**{icon}** &nbsp; {label}")

    st.divider()

    llm_status = is_llm_available()
    if llm_status:
        st.success("AI mode connected")
    else:
        st.info("Reliable fallback mode active")

    with st.expander("Connection details"):
        st.write(
            "OfferPilot uses the Groq-powered workflow when an API key is available "
            "and deterministic fallback logic when it is not."
        )
        if llm_status and st.button("Test AI connection", use_container_width=True):
            try:
                st.write(ask_llm("Reply with exactly: OfferPilot is ready."))
            except Exception as exc:
                st.error(f"Connection test failed: {exc}")

    st.divider()

    if st.button("Load demo: compare 3 candidates", type="primary", use_container_width=True):
        load_demo()
        st.rerun()

    if st.button("Reset workspace", use_container_width=True):
        reset_workspace()

    if not st.session_state.candidate_df.empty:
        st.download_button(
            "Download candidate review CSV",
            data=export_review_data(),
            file_name=f"offerpilot_review_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv",
            use_container_width=True,
        )


# ============================================================
# WORKSPACE HEADER
# ============================================================

active_role_name = st.session_state.jd_analysis.get("role_title", "No active role")
signed_in_name = (st.session_state.workspace_user or {}).get("name", "Recruiter")
st.markdown(
    f"""
    <div class="role-header-card">
        <div class="eyebrow">Recruiter dashboard</div>
        <div class="role-title-large">Welcome, {signed_in_name}</div>
        <div class="role-meta">Active role: {active_role_name} &nbsp;·&nbsp; Human-reviewed decision support</div>
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# MAIN NAVIGATION
# ============================================================

tab_overview, tab_role, tab_screening, tab_comparison, tab_verification, tab_simulation, tab_interview, tab_updates, tab_history, tab_assistant, tab_operations = st.tabs(
    [
        "Executive Overview",
        "1 · Role Intelligence",
        "2 · Advanced ATS Check",
        "3 · Evidence Comparison",
        "4 · Skill Verification",
        "5 · Simulation & Decision",
        "6 · Interview Evidence",
        "7 · Candidate Updates",
        "8 · History",
        "9 · AI Assistant",
        "10 · Settings",
    ]
)


# ============================================================
# EXECUTIVE OVERVIEW
# ============================================================

with tab_overview:
    st.markdown("## Hiring review at a glance")

    if st.session_state.candidate_df.empty:
        left, right = st.columns([1.35, 1])

        with left:
            st.markdown(
                """
                <div class="section-card">
                    <h3>Built for a credible live demo</h3>
                    <p class="muted">
                        Start with a real job description and uploaded resumes, or
                        load the complete HR demo from the sidebar to show the full
                        workflow immediately.
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )

            step_cols = st.columns(3)
            steps = [
                ("1", "Understand the role", "Extract skills, seniority, responsibilities, and candidate expectations."),
                ("2", "Compare evidence", "Rank candidates with technical fit, text similarity, and soft-skill evidence."),
                ("3", "Validate capability", "Score a practical work simulation and document the recruiter decision."),
            ]
            for col, (number, title, copy) in zip(step_cols, steps):
                with col:
                    st.markdown(
                        f"""
                        <div class="candidate-card">
                            <span class="step-number">{number}</span>
                            <strong>{title}</strong>
                            <p class="muted" style="margin-top:0.8rem;">{copy}</p>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

        with right:
            st.markdown("### Demo-ready in one click")
            st.write(
                "The sample workflow includes one role, three candidate profiles, "
                "three simulation responses, rubric scores, signal cards, and saved "
                "recruiter decisions."
            )
            if st.button(
                "Load demo: compare 3 candidates",
                type="primary",
                use_container_width=True,
                key="overview_demo_button",
            ):
                load_demo()
                st.rerun()

    else:
        df = st.session_state.candidate_df
        reviewed_count = len(st.session_state.candidate_signal_cards)
        move_forward_count = sum(
            decision == "Move Forward"
            for decision in st.session_state.recruiter_decisions.values()
        )

        metric_cols = st.columns(4)
        metric_cols[0].metric("Candidates", len(df))
        metric_cols[1].metric("Top resume match", f"{int(df['Match Score'].max())}%")
        metric_cols[2].metric("Simulations reviewed", reviewed_count)
        metric_cols[3].metric("Move forward", move_forward_count)

        st.markdown("### Leading candidates")
        render_candidate_cards(df)

        st.markdown("### Pipeline view")
        pipeline_df = df[
            ["Rank", "Candidate", "Match Score", "Review Priority", "Matched Skills", "Missing Skills"]
        ].copy()
        pipeline_df["Decision"] = pipeline_df["Candidate"].map(
            lambda name: st.session_state.recruiter_decisions.get(
                name, "Needs More Review"
            )
        )
        st.dataframe(
            pipeline_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Match Score": st.column_config.ProgressColumn(
                    "Resume Match",
                    min_value=0,
                    max_value=100,
                    format="%d%%",
                ),
                "Matched Skills": st.column_config.TextColumn(width="large"),
                "Missing Skills": st.column_config.TextColumn(width="large"),
            },
        )


# ============================================================
# ROLE INTELLIGENCE
# ============================================================

with tab_role:
    st.markdown("## Role intelligence")
    st.caption(
        "Turn an unstructured job description into a concise, readable assessment blueprint."
    )

    if not st.session_state.jd_analysis:
        input_left, input_right = st.columns([3, 1])

        with input_right:
            if st.button("Use sample role", use_container_width=True):
                st.session_state.job_description = DEMO_JOB_DESCRIPTION
                st.rerun()

        job_description = st.text_area(
            "Job description",
            height=300,
            value=st.session_state.job_description,
            placeholder="Paste the full job description here...",
        )

        if st.button(
            "Analyze role and build assessment",
            type="primary",
            use_container_width=True,
        ):
            if not job_description.strip():
                st.warning("Paste a job description before running the analysis.")
            else:
                analyze_job(job_description)
                st.success("Role intelligence and simulation blueprint created.")
                st.rerun()

    else:
        analysis = st.session_state.jd_analysis
        role_title = analysis.get("role_title", "Not identified")
        category = analysis.get(
            "role_category",
            st.session_state.category or "Not identified",
        )
        seniority = analysis.get("seniority_level", "Not identified")
        required_count = len(st.session_state.jd_role_skills)
        human_count = len(st.session_state.jd_soft_skills)

        st.markdown(
            f"""
            <div class="role-header-card">
                <div class="eyebrow">Role summary</div>
                <div class="role-title-large">{role_title}</div>
                <div class="role-meta">
                    {category} &nbsp;·&nbsp; {seniority}
                    &nbsp;·&nbsp; {required_count} technical competencies
                    &nbsp;·&nbsp; {human_count} human competencies
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        left, middle, right = st.columns(3)

        with left:
            st.markdown("### Required")
            chips = "".join(
                f'<span class="skill-chip">{skill}</span>'
                for skill in st.session_state.jd_role_skills
            )
            st.markdown(chips or "No required skills identified.", unsafe_allow_html=True)

        with middle:
            st.markdown("### Human")
            chips = "".join(
                f'<span class="skill-chip skill-chip-human">{skill}</span>'
                for skill in st.session_state.jd_soft_skills
            )
            st.markdown(chips or "No human skills identified.", unsafe_allow_html=True)

        with right:
            st.markdown("### Preferred")
            preferred = analysis.get("preferred_skills", [])
            chips = "".join(
                f'<span class="skill-chip skill-chip-preferred">{skill}</span>'
                for skill in preferred
            )
            st.markdown(chips or "No preferred skills identified.", unsafe_allow_html=True)

        st.markdown("### Success profile")
        success_left, success_right = st.columns([1.15, 1])

        with success_left:
            st.markdown(
                f"""
                <div class="success-card">
                    <h4>Ideal candidate</h4>
                    <p class="muted">
                        {analysis.get("ideal_candidate_summary", "")}
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with success_right:
            responsibilities = analysis.get("responsibilities", [])
            top_responsibilities = responsibilities[:4]
            responsibility_html = "".join(
                f"<li>{item}</li>" for item in top_responsibilities
            )
            st.markdown(
                f"""
                <div class="success-card">
                    <h4>Core outcomes</h4>
                    <ul class="muted">
                        {responsibility_html}
                    </ul>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with st.expander("View original job description"):
            st.text(st.session_state.job_description)

        if st.button("Analyze a different role"):
            st.session_state.jd_analysis = {}
            st.session_state.job_description = ""
            st.session_state.candidate_df = pd.DataFrame()
            st.session_state.heatmap_df = pd.DataFrame()
            st.session_state.candidate_skill_evidence = {}
            st.rerun()


# ============================================================
# CANDIDATE SCREENING
# ============================================================

with tab_screening:
    st.markdown("## Advanced ATS resume check")
    st.caption(
        "Run an explainable ATS check using exact skills, synonyms, related "
        "wording, context, negation handling, and whole-document similarity."
    )

    st.info(
        "Start here after defining the role. Upload one or more resumes, run the "
        "check, then select a candidate to inspect every matched, partial, and "
        "missing requirement."
    )
    for alert in st.session_state.returning_candidate_alerts:
        st.warning(alert)

    if not st.session_state.job_description:
        st.info("Analyze a role in the Role Intelligence tab before screening resumes.")
    else:
        source = st.radio(
            "Candidate source",
            ["Upload resume PDFs", "Use sample candidate set"],
            horizontal=True,
        )

        if source == "Upload resume PDFs":
            uploaded_resumes = st.file_uploader(
                "Upload candidate resumes",
                type=["pdf"],
                accept_multiple_files=True,
                help="Text-based PDFs work best. Scanned PDFs may require OCR.",
            )

            if st.button(
                "Screen uploaded candidates",
                type="primary",
                disabled=not uploaded_resumes,
            ):
                documents = []
                extraction_errors = []

                with st.spinner("Extracting resume evidence and calculating scores..."):
                    for resume in uploaded_resumes or []:
                        try:
                            text = extract_text_from_pdf(resume)
                            if not text or not text.strip():
                                extraction_errors.append(
                                    f"{resume.name}: no readable text found."
                                )
                                continue
                            documents.append(
                                {
                                    "Candidate": resume.name.rsplit(".", 1)[0],
                                    "Resume Text": text,
                                }
                            )
                        except Exception as exc:
                            extraction_errors.append(f"{resume.name}: {exc}")

                    if documents:
                        build_candidate_tables(documents)
                        st.success(f"Screened {len(documents)} candidates.")

                for error in extraction_errors:
                    st.warning(error)

        else:
            st.write(
                "Use the included strong, developing, and limited-fit profiles to "
                "demonstrate how the scoring model separates different evidence levels."
            )
            if st.button("Screen sample candidates", type="primary"):
                build_candidate_tables(DEMO_CANDIDATES)
                st.session_state.demo_mode = True
                st.success("Sample candidate set screened.")

        if not st.session_state.candidate_df.empty:
            df = st.session_state.candidate_df

            st.markdown("### Ranked shortlist")
            render_candidate_cards(df)
            if len(df) > 3:
                with st.expander(f"Show all {len(df)} ranked candidates"):
                    st.dataframe(
                        df[["Rank", "Candidate", "Match Score", "Review Priority"]],
                        use_container_width=True,
                        hide_index=True,
                    )

            with st.expander("How the ATS score is calculated"):
                st.write(
                    "The match score combines 70% required technical evidence, 20% whole-resume "
                    "semantic similarity, and 10% human-skill evidence. Exact terms, accepted "
                    "synonyms, contextual/related wording, and negation are evaluated separately. "
                    "The score supports review; it never automatically rejects a candidate."
                )

            threshold = st.slider(
                "Shortlist threshold",
                min_value=0,
                max_value=100,
                value=60,
                help="This is a review filter, not an automatic rejection rule.",
            )

            filtered_df = df[df["Match Score"] >= threshold].copy()

            st.dataframe(
                filtered_df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Match Score": st.column_config.ProgressColumn(
                        "Match Score",
                        min_value=0,
                        max_value=100,
                        format="%d%%",
                    ),
                    "Technical Skill Score": st.column_config.ProgressColumn(
                        "Technical",
                        min_value=0,
                        max_value=100,
                        format="%d%%",
                    ),
                    "Text Similarity": st.column_config.ProgressColumn(
                        "Similarity",
                        min_value=0,
                        max_value=100,
                        format="%d%%",
                    ),
                    "Soft Skill Score": st.column_config.ProgressColumn(
                        "Human Skills",
                        min_value=0,
                        max_value=100,
                        format="%d%%",
                    ),
                    "Matched Skills": st.column_config.TextColumn(width="large"),
                    "Missing Skills": st.column_config.TextColumn(width="large"),
                },
            )

            selected_explanation = st.selectbox(
                "Inspect candidate evidence",
                df["Candidate"].tolist(),
            )

            explanation_row = df[df["Candidate"] == selected_explanation].iloc[0]
            with st.expander("View evidence summary", expanded=False):
                exp_left, exp_middle, exp_right = st.columns(3)

            with exp_left:
                st.markdown("#### Evidence found")
                matched = [
                    skill
                    for skill in explanation_row["Matched Skills"].split(", ")
                    if skill
                ]
                if matched:
                    for skill in matched:
                        st.success(skill)
                else:
                    st.info("No direct matched skills were identified.")

            with exp_middle:
                st.markdown("#### Related evidence")
                related = [
                    skill
                    for skill in explanation_row.get("Related Skills", "").split(", ")
                    if skill
                ]
                if related:
                    for skill in related:
                        st.info(f"{skill} — partial credit")
                else:
                    st.caption("No partial matches were detected.")

            with exp_right:
                st.markdown("#### Evidence to validate")
                missing = [
                    skill
                    for skill in explanation_row["Missing Skills"].split(", ")
                    if skill
                ]
                if missing:
                    for skill in missing:
                        st.warning(skill)
                else:
                    st.success("No required skill gaps were identified.")

            ats_report = st.session_state.candidate_ats_reports.get(
                selected_explanation, {}
            )
            report_items = (
                ats_report.get("technical", {}).get("matches", [])
                + ats_report.get("human", {}).get("matches", [])
            )
            if report_items:
                st.markdown("#### Contextual ATS evidence report")
                st.caption(
                    "Exact terms, accepted synonyms, related wording, and missing "
                    "evidence are shown separately so a recruiter can audit the score."
                )
                st.dataframe(
                    pd.DataFrame(
                        [
                            {
                                "Requirement": item["skill"],
                                "Status": item["status"],
                                "Match basis": item["match_type"],
                                "Detected term": item["matched_term"],
                                "Confidence": item["confidence"],
                                "Resume evidence": item["evidence"],
                            }
                            for item in report_items
                        ]
                    ),
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "Confidence": st.column_config.ProgressColumn(
                            min_value=0, max_value=100, format="%d%%"
                        ),
                        "Resume evidence": st.column_config.TextColumn(width="large"),
                    },
                )


# ============================================================
# EVIDENCE COMPARISON
# ============================================================

with tab_comparison:
    st.markdown("## Evidence comparison")
    st.caption("See exactly which role competencies appear in each candidate profile.")

    if st.session_state.heatmap_df.empty:
        st.info("Screen candidates first to generate the competency comparison.")
    else:
        heatmap_df = st.session_state.heatmap_df.copy()
        def evidence_color(value):
            colors = {
                "Matched": "background-color: #d1fae5; color: #065f46; font-weight: 700",
                "Partial": "background-color: #fef3c7; color: #92400e; font-weight: 700",
                "Missing evidence": "background-color: #ffe4e6; color: #9f1239; font-weight: 700",
            }
            return colors.get(value, "")

        st.dataframe(
            heatmap_df.style.map(evidence_color),
            use_container_width=True,
            hide_index=True,
        )

        st.markdown("### Comparison insights")
        candidate_df = st.session_state.candidate_df

        top_candidate = candidate_df.iloc[0]
        lowest_candidate = candidate_df.iloc[-1]

        insight_cols = st.columns(3)
        insight_cols[0].metric(
            "Strongest evidence",
            top_candidate["Candidate"],
            f"{int(top_candidate['Match Score'])}% match",
        )
        insight_cols[1].metric(
            "Score spread",
            (
                f"{int(top_candidate['Match Score'] - lowest_candidate['Match Score'])} pts"
                if len(candidate_df) > 1
                else "Not applicable"
            ),
        )
        insight_cols[2].metric(
            "Competencies assessed",
            max(len(heatmap_df.columns) - 1, 0),
        )

        st.markdown(
            """
            <div class="disclaimer">
                A missing match means the evidence was not detected in the supplied
                resume text. It does not prove that the candidate lacks the skill.
                Recruiters should validate important gaps through structured questions.
            </div>
            """,
            unsafe_allow_html=True,
        )



# ============================================================
# SKILL VERIFICATION
# ============================================================

with tab_verification:
    st.markdown("## Skill claim verification")
    st.caption(
        "See whether each candidate supports a skill with project evidence, "
        "then record the interviewer's verdict."
    )

    if st.session_state.candidate_df.empty:
        st.info("Screen candidates first to generate skill verification.")
    else:
        candidate_names = st.session_state.candidate_df["Candidate"].tolist()

        st.markdown("### Public profile claim verification")
        st.caption(
            "Compare resume claims with candidate-provided public profile evidence. "
            "Missing public evidence is never treated as proof that a claim is false."
        )
        profile_candidate = st.selectbox(
            "Candidate profile to verify",
            candidate_names,
            key="profile_verification_candidate",
        )
        profile_resume_text = st.session_state.candidate_resume_texts.get(
            profile_candidate, ""
        )
        detected_links = extract_profile_links(profile_resume_text)
        github_url = detected_links["github_url"]
        linkedin_url = detected_links["linkedin_url"]
        detected_col, linkedin_col = st.columns(2)
        with detected_col:
            st.markdown("#### GitHub")
            if github_url:
                st.success("GitHub URL extracted from the resume.")
                st.link_button("Open extracted GitHub profile", github_url)
            else:
                st.warning("No GitHub URL was found in this resume.")
        with linkedin_col:
            st.markdown("#### LinkedIn")
            if linkedin_url:
                st.success("LinkedIn URL extracted from the resume.")
                st.link_button("Open extracted LinkedIn profile", linkedin_url)
            else:
                st.warning("No LinkedIn URL was found in this resume.")

        with st.expander(
            "Manual correction — only when a PDF link could not be extracted",
            expanded=False,
        ):
            github_url = st.text_input(
                "Correct GitHub profile URL",
                value=github_url,
                key=f"github_url_{profile_candidate}",
                placeholder="https://github.com/username",
            )
            linkedin_url = st.text_input(
                "Correct LinkedIn profile URL",
                value=linkedin_url,
                key=f"linkedin_url_{profile_candidate}",
                placeholder="https://www.linkedin.com/in/profile",
            )

        with st.expander("Authorized LinkedIn evidence", expanded=False):
            st.caption(
                "Until approved LinkedIn Profile API access is configured, use an "
                "authorized candidate export for work-history comparison."
            )
            linkedin_profile_text = st.text_area(
                "LinkedIn profile text or export",
                height=130,
                key=f"linkedin_text_{profile_candidate}",
                placeholder="Paste the relevant Experience, Projects, and Skills sections.",
            )

        if st.button(
            "Refresh public profile evidence",
            type="primary",
            disabled=not github_url and not linkedin_profile_text.strip(),
            key=f"verify_profiles_{profile_candidate}",
        ):
            github_evidence = None
            github_error = ""
            github_username = extract_profile_links(github_url)["github_username"]
            if github_url and not github_username:
                github_error = "Enter a valid github.com/username profile URL."
            elif github_username:
                try:
                    with st.spinner("Reading public GitHub repository metadata..."):
                        github_evidence = fetch_public_github_evidence(github_username)
                except ValueError as exc:
                    github_error = str(exc)

            comparison = compare_resume_with_profiles(
                profile_resume_text,
                github_evidence,
                linkedin_profile_text,
            )
            st.session_state.profile_verifications[profile_candidate] = {
                "github_url": github_url,
                "linkedin_url": linkedin_url,
                "github_evidence": github_evidence,
                "github_error": github_error,
                "comparison": comparison,
            }

        profile_result = st.session_state.profile_verifications.get(
            profile_candidate
        )
        if profile_result:
            if profile_result["github_error"]:
                st.warning(profile_result["github_error"])
            github_evidence = profile_result["github_evidence"]
            comparison = profile_result["comparison"]

            if github_evidence:
                github_metrics = st.columns(3)
                github_metrics[0].metric(
                    "Public repositories", github_evidence["public_repo_count"]
                )
                github_metrics[1].metric(
                    "Resume/GitHub overlap", f'{comparison["github_overlap"]}%'
                )
                github_metrics[2].metric(
                    "Shared evidence terms",
                    len(comparison["github_shared_terms"]),
                )
                repo_rows = github_evidence["repos"][:20]
                if repo_rows:
                    st.dataframe(
                        pd.DataFrame(repo_rows),
                        use_container_width=True,
                        hide_index=True,
                        column_config={
                            "url": st.column_config.LinkColumn("Repository"),
                        },
                    )

            if linkedin_profile_text:
                st.metric(
                    "Resume/LinkedIn text overlap",
                    f'{comparison["linkedin_overlap"]}%',
                )
            for signal in comparison["review_signals"]:
                st.info(signal)
            st.caption(comparison["limitations"])

        st.divider()

        st.markdown("### Candidate evidence summary")

        summary_rows = []
        for candidate_name in candidate_names:
            rows = st.session_state.candidate_skill_evidence.get(
                candidate_name,
                [],
            )
            summary_rows.append(
                {
                    "Candidate": candidate_name,
                    "Strong Evidence": sum(
                        row["Evidence Strength"] == "Strong project evidence"
                        for row in rows
                    ),
                    "Needs Verification": sum(
                        row["Evidence Strength"]
                        in {
                            "Some evidence — verify depth",
                            "Keyword mention only",
                        }
                        for row in rows
                    ),
                    "Not Evidenced": sum(
                        row["Evidence Strength"] == "Not evidenced"
                        for row in rows
                    ),
                    "Evidence Quality": round(
                        sum(row["Evidence Score"] for row in rows)
                        / max(len(rows), 1)
                    ),
                }
            )

        summary_df = pd.DataFrame(summary_rows).sort_values(
            "Evidence Quality",
            ascending=False,
        )

        st.dataframe(
            summary_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Evidence Quality": st.column_config.ProgressColumn(
                    "Evidence Quality",
                    min_value=0,
                    max_value=100,
                    format="%d%%",
                )
            },
        )

        st.markdown("### Compare role competencies")

        target_skills = normalize_skill_list(
            st.session_state.jd_role_skills
            + st.session_state.jd_soft_skills
        )
        matrix_rows = []

        for skill in target_skills:
            row = {"Role Competency": skill}

            for candidate_name in candidate_names:
                evidence_rows = st.session_state.candidate_skill_evidence.get(
                    candidate_name,
                    [],
                )
                skill_row = next(
                    (
                        item
                        for item in evidence_rows
                        if item["Skill"] == skill
                    ),
                    None,
                )

                if not skill_row:
                    symbol = "🔴 Not evidenced"
                elif skill_row["Evidence Strength"] == "Strong project evidence":
                    symbol = "🟢 Strong"
                elif skill_row["Evidence Strength"] == "Some evidence — verify depth":
                    symbol = "🟡 Verify depth"
                elif skill_row["Evidence Strength"] == "Keyword mention only":
                    symbol = "🟠 Mention only"
                else:
                    symbol = "🔴 Not evidenced"

                row[candidate_name] = symbol

            matrix_rows.append(row)

        st.dataframe(
            pd.DataFrame(matrix_rows),
            use_container_width=True,
            hide_index=True,
        )

        st.divider()
        st.markdown("### Verify one candidate in depth")

        verification_candidate = st.selectbox(
            "Candidate",
            candidate_names,
            key="verification_candidate",
        )

        evidence_rows = st.session_state.candidate_skill_evidence.get(
            verification_candidate,
            [],
        )

        if not evidence_rows:
            st.warning(
                "No verification evidence is available. Rerun Candidate Screening "
                "or reload the demo."
            )
        else:
            selected_skill = st.selectbox(
                "Skill to test",
                [row["Skill"] for row in evidence_rows],
                key=f"skill_to_verify_{verification_candidate}",
            )

            selected_row = next(
                row
                for row in evidence_rows
                if row["Skill"] == selected_skill
            )

            left, right = st.columns([1, 1.2])

            with left:
                st.markdown("### Resume evidence")
                st.info(selected_row["Resume Evidence"])
                st.metric(
                    "Evidence quality",
                    f'{selected_row["Evidence Score"]}%',
                    selected_row["Evidence Strength"],
                )

            with right:
                st.markdown("### Questions based on this resume")
                for number, question in enumerate(
                    selected_row["Questions"],
                    start=1,
                ):
                    st.markdown(
                        f"""
                        <div class="section-card">
                            <strong>Question {number}</strong>
                            <p class="muted" style="margin-bottom:0;">
                                {question}
                            </p>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

            st.markdown("### Editable recruiter verification record")

            editable_rows = []
            for row in evidence_rows:
                key = f"{verification_candidate}::{row['Skill']}"
                saved = st.session_state.skill_verification_results.get(
                    key,
                    {"Verdict": "Not assessed", "Notes": ""},
                )
                editable_rows.append(
                    {
                        "Skill": row["Skill"],
                        "Resume Evidence Strength": row["Evidence Strength"],
                        "Interviewer Verdict": saved["Verdict"],
                        "Interview Evidence": saved["Notes"],
                    }
                )

            edited_df = st.data_editor(
                pd.DataFrame(editable_rows),
                use_container_width=True,
                hide_index=True,
                num_rows="fixed",
                disabled=["Skill", "Resume Evidence Strength"],
                column_config={
                    "Interviewer Verdict": st.column_config.SelectboxColumn(
                        "Interviewer Verdict",
                        options=[
                            "Not assessed",
                            "Proven",
                            "Partially proven",
                            "Not proven",
                        ],
                        required=True,
                    ),
                    "Interview Evidence": st.column_config.TextColumn(
                        "Interview Evidence",
                        width="large",
                    ),
                },
                key=f"verification_editor_{verification_candidate}",
            )

            if st.button(
                "Save recruiter verification record",
                key=f"save_record_{verification_candidate}",
            ):
                for _, edited_row in edited_df.iterrows():
                    key = (
                        f"{verification_candidate}::"
                        f"{edited_row['Skill']}"
                    )
                    st.session_state.skill_verification_results[key] = {
                        "Verdict": edited_row["Interviewer Verdict"],
                        "Notes": edited_row["Interview Evidence"],
                    }

                st.success("Recruiter verification record saved.")


# ============================================================
# SIMULATION & DECISION
# ============================================================

with tab_simulation:
    st.markdown("## Simulation and recruiter decision")
    st.caption(
        "Validate how candidates think through realistic work—not only how their "
        "resume is written."
    )

    if st.session_state.candidate_df.empty:
        st.info("Complete candidate screening before reviewing simulations.")
    else:
        with st.expander("View role simulation task", expanded=True):
            st.markdown(st.session_state.simulation_task)

        candidate_names = st.session_state.candidate_df["Candidate"].tolist()
        selected_candidate = st.selectbox(
            "Candidate",
            candidate_names,
            key="selected_candidate_for_simulation",
        )

        if st.session_state.last_selected_candidate != selected_candidate:
            st.session_state.current_candidate_answer = (
                st.session_state.candidate_responses.get(selected_candidate, "")
            )
            st.session_state.last_selected_candidate = selected_candidate

        button_cols = st.columns([1, 1, 2])

        with button_cols[0]:
            if (
                st.session_state.demo_mode
                and selected_candidate in DEMO_RESPONSES
                and st.button("Load sample response", use_container_width=True)
            ):
                st.session_state.current_candidate_answer = DEMO_RESPONSES[
                    selected_candidate
                ]
                st.rerun()

        with button_cols[1]:
            if st.button("Clear response", use_container_width=True):
                st.session_state.current_candidate_answer = ""
                st.rerun()

        st.text_area(
            "Candidate response",
            height=260,
            key="current_candidate_answer",
            placeholder="Paste the candidate's work simulation response...",
        )

        if st.button(
            "Score response and generate signal card",
            type="primary",
            use_container_width=True,
        ):
            response = st.session_state.current_candidate_answer.strip()

            if not response:
                st.warning("Add a candidate response before scoring.")
            else:
                with st.spinner("Evaluating the response and building the signal card..."):
                    rubric_scores = score_response(
                        response,
                        st.session_state.category,
                        st.session_state.simulation_task,
                    )

                    selected_row = st.session_state.candidate_df[
                        st.session_state.candidate_df["Candidate"] == selected_candidate
                    ].iloc[0]

                    matched_skills = (
                        selected_row["Matched Skills"].split(", ")
                        if selected_row["Matched Skills"]
                        else []
                    )
                    missing_skills = (
                        selected_row["Missing Skills"].split(", ")
                        if selected_row["Missing Skills"]
                        else []
                    )

                    signal_card = create_signal_card(
                        selected_candidate,
                        int(selected_row["Match Score"]),
                        rubric_scores,
                        matched_skills,
                        missing_skills,
                    )

                    st.session_state.candidate_responses[selected_candidate] = response
                    st.session_state.candidate_rubric_scores[
                        selected_candidate
                    ] = rubric_scores
                    st.session_state.candidate_signal_cards[
                        selected_candidate
                    ] = signal_card

                st.success("Simulation review saved.")

        if selected_candidate in st.session_state.candidate_signal_cards:
            selected_row = st.session_state.candidate_df[
                st.session_state.candidate_df["Candidate"] == selected_candidate
            ].iloc[0]
            rubric = st.session_state.candidate_rubric_scores[selected_candidate]
            card = st.session_state.candidate_signal_cards[selected_candidate]

            metric_cols = st.columns([1, 1, 1, 1, 1.4])
            metric_cols[0].metric(
                "Resume match",
                f"{int(selected_row['Match Score'])}%",
            )
            metric_cols[1].metric(
                "Simulation",
                f"{int(rubric.get('Simulation Score', 0))}%",
            )
            metric_cols[2].metric(
                "Combined evidence",
                f"{int(card.get('Final Confidence Score', 0))}%",
            )
            metric_cols[3].metric(
                "Confidence",
                card.get("Final Confidence", ""),
            )
            with metric_cols[4]:
                st.info(
                    "Scoring context\n\nResume evidence: 60%\n\nPractical response: 40%\n\n"
                    "Each response rubric has five 20-point dimensions. Scores inform human review only."
                )

            st.markdown(
                f"""
                <div class="signal-card">
                    <div class="eyebrow">Candidate signal card</div>
                    <h2 style="margin-top:0;">{selected_candidate}</h2>
                    <p><strong>Recommended next step:</strong>
                    {card.get("Recommended Next Step", "")}</p>
                    <p class="muted">{card.get("Recruiter Summary", "")}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

            st.markdown("### Structured evidence")
            evidence_cols = st.columns(3)

            with evidence_cols[0]:
                st.markdown("#### Strengths")
                for item in card.get("Strengths", []):
                    st.success(item)

            with evidence_cols[1]:
                st.markdown("#### Risks")
                for item in card.get("Risks", []):
                    st.warning(item)

            with evidence_cols[2]:
                st.markdown("#### Interview focus")
                for item in card.get("Interview Focus Areas", []):
                    st.info(item)

            rubric_df = pd.DataFrame(
                [
                    {"Rubric Area": key, "Score": value}
                    for key, value in rubric.items()
                    if key != "Simulation Score"
                ]
            )
            st.dataframe(
                rubric_df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Score": st.column_config.ProgressColumn(
                        "Score",
                        min_value=0,
                        max_value=20,
                        format="%d/20",
                    )
                },
            )

        st.divider()
        st.markdown("### Recruiter decision record")

        decision_options = [
            "Move Forward",
            "Needs More Review",
            "Hold",
            "Reject",
        ]
        saved_decision = st.session_state.recruiter_decisions.get(
            selected_candidate,
            "Needs More Review",
        )

        decision_col, notes_col = st.columns([1, 2])

        with decision_col:
            recruiter_decision = st.selectbox(
                "Decision",
                decision_options,
                index=decision_options.index(saved_decision),
                key=f"decision_{selected_candidate}",
            )

        with notes_col:
            recruiter_notes = st.text_area(
                "Evidence-based notes",
                value=st.session_state.recruiter_notes.get(selected_candidate, ""),
                height=120,
                key=f"notes_{selected_candidate}",
                placeholder="Record the evidence behind the decision...",
            )

        if st.button("Generate profile-specific interview questions", use_container_width=True):
            st.session_state.follow_up_questions[selected_candidate] = (
                generate_candidate_questions_with_llm(
                    st.session_state.job_description,
                    st.session_state.jd_analysis,
                    selected_candidate,
                    st.session_state.candidate_resume_texts.get(selected_candidate, ""),
                    st.session_state.candidate_skill_evidence.get(selected_candidate, []),
                )
            )
            st.rerun()

        follow_up_questions = st.text_area(
            "Structured interview questions",
            value=st.session_state.follow_up_questions.get(selected_candidate, ""),
            height=100,
            key=f"questions_{selected_candidate}",
            placeholder="Add questions that validate missing or uncertain evidence...",
        )

        if st.button("Save recruiter decision"):
            previous_decision = st.session_state.recruiter_decisions.get(
                selected_candidate
            )
            st.session_state.recruiter_decisions[
                selected_candidate
            ] = recruiter_decision
            st.session_state.recruiter_notes[selected_candidate] = recruiter_notes
            st.session_state.follow_up_questions[
                selected_candidate
            ] = follow_up_questions
            selected_resume_text = st.session_state.candidate_resume_texts.get(
                selected_candidate, ""
            )
            selected_contact = st.session_state.candidate_contacts.get(
                selected_candidate, {}
            )
            persisted_candidate_id = save_candidate(
                st.session_state.active_job_id,
                selected_candidate,
                selected_resume_text,
                workflow={
                    "decision": recruiter_decision,
                    "notes": recruiter_notes,
                    "follow_up_questions": follow_up_questions,
                    "rubric": st.session_state.candidate_rubric_scores.get(
                        selected_candidate, {}
                    ),
                    "signal_card": st.session_state.candidate_signal_cards.get(
                        selected_candidate, {}
                    ),
                    "milestones": st.session_state.candidate_milestones.get(
                        selected_candidate, {}
                    ),
                },
                phone=selected_contact.get("phone", ""),
                email=selected_contact.get("email", ""),
                actor=(st.session_state.workspace_user or {}).get("email", "system"),
            )
            st.session_state.candidate_db_ids[selected_candidate] = persisted_candidate_id
            if previous_decision != recruiter_decision:
                sent, update_message = send_automatic_decision_update(
                    selected_candidate, recruiter_decision
                )
                if sent:
                    st.success(f"Recruiter decision saved. {update_message}")
                else:
                    st.success("Recruiter decision saved.")
                    st.info(update_message)
            else:
                st.success("Recruiter decision saved. The status did not change, so no SMS was sent.")

        if st.session_state.candidate_signal_cards:
            st.markdown("### Review summary")
            summary_rows = []

            for candidate_name in candidate_names:
                row = st.session_state.candidate_df[
                    st.session_state.candidate_df["Candidate"] == candidate_name
                ].iloc[0]
                rubric_data = st.session_state.candidate_rubric_scores.get(
                    candidate_name, {}
                )
                signal_data = st.session_state.candidate_signal_cards.get(
                    candidate_name, {}
                )

                summary_rows.append(
                    {
                        "Candidate": candidate_name,
                        "Resume Match": row["Match Score"],
                        "Simulation Score": rubric_data.get("Simulation Score", ""),
                        "Confidence": signal_data.get("Final Confidence", "Not reviewed"),
                        "Decision": st.session_state.recruiter_decisions.get(
                            candidate_name, "Needs More Review"
                        ),
                    }
                )

            st.dataframe(
                pd.DataFrame(summary_rows),
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Resume Match": st.column_config.ProgressColumn(
                        min_value=0,
                        max_value=100,
                        format="%d%%",
                    ),
                    "Simulation Score": st.column_config.ProgressColumn(
                        min_value=0,
                        max_value=100,
                        format="%d%%",
                    ),
                },
            )


with tab_interview:
    st.markdown("## Interview evidence workspace")
    st.caption(
        "Capture a consented interview transcript, review answer evidence, and "
        "generate structured follow-ups. This workspace does not infer deception, "
        "emotion, personality, or AI use."
    )

    if st.session_state.candidate_df.empty:
        st.info("Screen candidates before creating an interview evidence record.")
    else:
        interview_candidates = st.session_state.candidate_df["Candidate"].tolist()
        interview_candidate = st.selectbox(
            "Candidate",
            interview_candidates,
            key="interview_candidate",
        )

        st.markdown("### Recording and privacy consent")
        consent = st.checkbox(
            "The candidate has been informed and explicitly consented to recording and transcription.",
            value=st.session_state.interview_consent.get(interview_candidate, False),
            key=f"consent_{interview_candidate}",
        )
        st.session_state.interview_consent[interview_candidate] = consent
        st.caption(
            "Audio is processed only after consent. OfferPilot stores the transcript "
            "in the current app session; configure approved retention and deletion "
            "controls before production use."
        )

        capture_col, upload_col = st.columns(2)
        with capture_col:
            recorded_audio = st.audio_input(
                "Record interview audio",
                disabled=not consent,
                key=f"recorded_audio_{interview_candidate}",
            )
        with upload_col:
            uploaded_audio = st.file_uploader(
                "Or upload a recorded interview",
                type=["wav", "mp3", "m4a", "mp4", "webm", "ogg"],
                disabled=not consent,
                key=f"uploaded_audio_{interview_candidate}",
            )

        audio_source = recorded_audio or uploaded_audio
        if st.button(
            "Transcribe consented audio",
            type="primary",
            disabled=not consent or audio_source is None,
            key=f"transcribe_{interview_candidate}",
        ):
            if not is_llm_available():
                st.warning(
                    "Audio transcription requires a configured GROQ_API_KEY. "
                    "You can paste or edit the transcript below instead."
                )
            else:
                try:
                    with st.spinner("Transcribing interview audio..."):
                        transcript = transcribe_audio(
                            audio_source.getvalue(),
                            getattr(audio_source, "name", "interview.wav"),
                        )
                    st.session_state.interview_transcripts[interview_candidate] = (
                        transcript or ""
                    )
                    st.success("Transcript created. Review and correct it before analysis.")
                    st.rerun()
                except Exception as exc:
                    st.error(f"Transcription failed: {exc}")

        transcript_text = st.text_area(
            "Reviewed interview transcript",
            value=st.session_state.interview_transcripts.get(interview_candidate, ""),
            height=300,
            key=f"transcript_editor_{interview_candidate}",
            placeholder=(
                "Paste the phone/video interview transcript here, or record/upload "
                "audio above. Remove unrelated sensitive personal information."
            ),
        )

        analyze_col, clear_col = st.columns([1, 1])
        with analyze_col:
            analyze_clicked = st.button(
                "Analyze answer evidence",
                type="primary",
                disabled=not transcript_text.strip(),
                key=f"analyze_interview_{interview_candidate}",
            )
        with clear_col:
            if st.button(
                "Delete session transcript",
                disabled=not transcript_text.strip(),
                key=f"clear_interview_{interview_candidate}",
            ):
                st.session_state.interview_transcripts.pop(interview_candidate, None)
                st.session_state.interview_analyses.pop(interview_candidate, None)
                st.rerun()

        if analyze_clicked:
            st.session_state.interview_transcripts[interview_candidate] = transcript_text
            st.session_state.interview_analyses[interview_candidate] = (
                analyze_interview_transcript(
                    transcript_text,
                    st.session_state.candidate_resume_texts.get(interview_candidate, ""),
                    normalize_skill_list(
                        st.session_state.jd_role_skills
                        + st.session_state.jd_soft_skills
                    ),
                )
            )
            st.success("Interview evidence review created.")

        interview_analysis = st.session_state.interview_analyses.get(
            interview_candidate
        )
        if interview_analysis:
            st.markdown("### Objective answer signals")
            metrics = st.columns(4)
            metrics[0].metric("Transcript words", interview_analysis["word_count"])
            metrics[1].metric(
                "Concrete evidence", f'{interview_analysis["evidence_score"]}%'
            )
            metrics[2].metric(
                "Answer specificity", f'{interview_analysis["specificity_score"]}%'
            )
            metrics[3].metric(
                "Resume topic overlap", f'{interview_analysis["resume_similarity"]}%'
            )
            st.caption(
                "These are content-review aids, not candidate quality, honesty, "
                "personality, or employment-decision scores."
            )

            if interview_analysis["supported_skills"]:
                st.markdown("#### Role topics discussed")
                st.write(", ".join(interview_analysis["supported_skills"]))

            st.markdown("#### Items requiring verification")
            if interview_analysis["review_flags"]:
                for flag in interview_analysis["review_flags"]:
                    st.warning(flag)
            else:
                st.success("The transcript contains multiple concrete evidence signals.")

            st.markdown("#### Adaptive follow-up questions")
            for number, question in enumerate(
                interview_analysis["follow_ups"], start=1
            ):
                st.info(f"{number}. {question}")

            st.download_button(
                "Download reviewed transcript",
                data=st.session_state.interview_transcripts.get(interview_candidate, ""),
                file_name=f"{interview_candidate}_reviewed_transcript.txt",
                mime="text/plain",
                key=f"download_transcript_{interview_candidate}",
            )


with tab_updates:
    st.markdown("## Candidate milestone updates")
    st.caption(
        "Give candidates a clear view of their application progress and send "
        "consented status updates by SMS. Milestone messages are previewed; changed "
        "recruiter decisions can be sent automatically after opt-in."
    )

    if st.session_state.candidate_df.empty:
        st.info("Screen candidates before creating milestone updates.")
    else:
        update_candidates = st.session_state.candidate_df["Candidate"].tolist()
        update_candidate = st.selectbox(
            "Candidate",
            update_candidates,
            key="candidate_update_candidate",
        )
        contact = st.session_state.candidate_contacts.get(
            update_candidate,
            {
                "phone": "",
                "sms_consent": False,
                "auto_updates": True,
                "consent_source": "Not recorded",
            },
        )
        st.markdown("### Hiring workflow")
        workflow_stages = [
            ("Application", lambda n: True),
            ("Screened", lambda n: n in st.session_state.candidate_resume_texts),
            ("Practical review", lambda n: n in st.session_state.candidate_rubric_scores),
            ("Decision recorded", lambda n: n in st.session_state.recruiter_decisions),
        ]
        total_candidates = max(len(df), 1)
        for stage_name, stage_filter in workflow_stages:
            stage_names = [name for name in df["Candidate"].tolist() if stage_filter(name)]
            with st.expander(f"{stage_name} · {len(stage_names)}/{total_candidates} ({round(100 * len(stage_names) / total_candidates)}%)"):
                if stage_names:
                    stage_rows = df[df["Candidate"].isin(stage_names)][["Rank", "Candidate", "Match Score"]]
                    st.dataframe(stage_rows, use_container_width=True, hide_index=True)
                else:
                    st.caption("No candidates are at this step yet.")
        st.caption(
            "Diversity ratios are shown only when HR supplies an approved, consented audit dataset. "
            "The app never infers demographic attributes from names or resumes."
        )
        phone_col, consent_col = st.columns([1, 1.4])
        with phone_col:
            phone_number = st.text_input(
                "Candidate phone number",
                value=contact.get("phone", ""),
                placeholder="+15551234567",
                key=f"candidate_phone_{update_candidate}",
                help="Use international E.164 format.",
            )
        with consent_col:
            sms_consent = st.checkbox(
                "Candidate has opted in to application-status SMS updates.",
                value=contact.get("sms_consent", False),
                key=f"sms_consent_{update_candidate}",
            )
            st.caption(f'Consent source: {contact.get("consent_source", "Not recorded")}')
            auto_updates = st.checkbox(
                "Automatically send an SMS when the saved recruiter decision changes.",
                value=contact.get("auto_updates", True),
                disabled=not sms_consent,
                key=f"auto_updates_{update_candidate}",
            )
        st.session_state.candidate_contacts[update_candidate] = {
            "phone": phone_number.strip(),
            "email": contact.get("email", ""),
            "sms_consent": sms_consent,
            "auto_updates": auto_updates,
            "consent_source": (
                contact.get("consent_source", "Not recorded")
                if sms_consent == contact.get("sms_consent", False)
                else "Recruiter confirmation in OfferPilot"
            ),
        }

        default_statuses = {
            key: (
                "Completed"
                if key in {"application_received", "resume_review"}
                else "Not started"
            )
            for key, _ in MILESTONES
        }
        statuses = st.session_state.candidate_milestones.setdefault(
            update_candidate, default_statuses
        )

        st.markdown("### Candidate-facing progress")
        progress = milestone_progress(statuses)
        st.progress(progress, text=f"Application progress · {round(progress * 100)}%")

        milestone_rows = []
        for position, (milestone_key, milestone_label) in enumerate(MILESTONES, start=1):
            current_status = statuses.get(milestone_key, "Not started")
            marker = {
                "Completed": "✓",
                "In progress": "●",
                "Not started": "○",
            }[current_status]
            milestone_rows.append(
                {
                    "Step": position,
                    "Milestone": f"{marker} {milestone_label}",
                    "Status": current_status,
                }
            )
        st.dataframe(
            pd.DataFrame(milestone_rows),
            use_container_width=True,
            hide_index=True,
        )

        st.markdown("### Update a milestone")
        selected_milestone_label = st.selectbox(
            "Milestone",
            [label for _, label in MILESTONES],
            key=f"update_milestone_{update_candidate}",
        )
        selected_milestone_key = next(
            key for key, label in MILESTONES if label == selected_milestone_label
        )
        selected_status = st.selectbox(
            "New status",
            STATUS_OPTIONS,
            index=STATUS_OPTIONS.index(
                statuses.get(selected_milestone_key, "Not started")
            ),
            key=f"update_status_{update_candidate}",
        )
        next_step = st.text_input(
            "Candidate-facing next step",
            key=f"candidate_next_step_{update_candidate}",
            placeholder="Example: We will contact you within three business days.",
        )
        default_message = build_status_message(
            update_candidate,
            selected_milestone_label,
            selected_status,
            next_step,
        )
        message_body = st.text_area(
            "SMS preview",
            value=default_message,
            height=120,
            key=f"sms_preview_{update_candidate}_{selected_milestone_key}_{selected_status}",
            help="Keep messages factual and do not include private evaluation details.",
        )

        save_col, send_col = st.columns(2)
        with save_col:
            if st.button(
                "Save milestone without SMS",
                use_container_width=True,
                key=f"save_milestone_{update_candidate}",
            ):
                statuses[selected_milestone_key] = selected_status
                st.success("Milestone saved. No message was sent.")
                st.rerun()

        with send_col:
            send_clicked = st.button(
                "Save milestone and send SMS",
                type="primary",
                use_container_width=True,
                disabled=not sms_consent or not validate_phone_number(phone_number),
                key=f"send_milestone_{update_candidate}",
            )

        if phone_number and not validate_phone_number(phone_number):
            st.warning("Enter the phone number in E.164 format, such as +15551234567.")
        if not sms_consent:
            st.caption("SMS sending remains disabled until candidate opt-in is recorded.")

        if send_clicked:
            try:
                account_sid = st.secrets["TWILIO_ACCOUNT_SID"]
                auth_token = st.secrets["TWILIO_AUTH_TOKEN"]
                from_number = st.secrets["TWILIO_FROM_NUMBER"]
            except Exception:
                account_sid = auth_token = from_number = ""

            if not all([account_sid, auth_token, from_number]):
                st.error(
                    "Twilio is not configured. Add TWILIO_ACCOUNT_SID, "
                    "TWILIO_AUTH_TOKEN, and TWILIO_FROM_NUMBER to Streamlit secrets."
                )
            else:
                try:
                    with st.spinner("Sending candidate update..."):
                        delivery = send_twilio_sms(
                            account_sid,
                            auth_token,
                            from_number,
                            phone_number,
                            message_body,
                        )
                    statuses[selected_milestone_key] = selected_status
                    st.session_state.candidate_sms_logs.setdefault(
                        update_candidate, []
                    ).append(
                        {
                            "Milestone": selected_milestone_label,
                            "Status": selected_status,
                            "Message": message_body,
                            "Delivery": delivery["status"],
                            "Sent at": delivery["sent_at"],
                            "Message SID": delivery["sid"],
                        }
                    )
                    st.success("Milestone saved and SMS queued by Twilio.")
                    st.rerun()
                except ValueError as exc:
                    st.error(str(exc))

        sms_logs = st.session_state.candidate_sms_logs.get(update_candidate, [])
        if sms_logs:
            st.markdown("### Update history")
            st.dataframe(
                pd.DataFrame(sms_logs),
                use_container_width=True,
                hide_index=True,
                column_config={"Message": st.column_config.TextColumn(width="large")},
            )


with tab_history:
    st.markdown("## Application and change history")
    st.caption("Reopen earlier profiles, spot repeat applicants, and review who changed what.")
    history_candidates = list_persisted_candidates()
    history_jobs = {row["id"]: row for row in list_jobs()}
    if history_candidates:
        history_labels = {
            f'{row["name"]} · {history_jobs.get(row["job_id"], {}).get("title", "Unassigned role")} · {row["updated_at"][:10]}': row
            for row in history_candidates
        }
        history_choice = st.selectbox("Candidate application", list(history_labels))
        history_row = history_labels[history_choice]
        prior_for_person = [
            row for row in history_candidates
            if row["name"].strip().lower() == history_row["name"].strip().lower()
            or (history_row.get("email") and row.get("email") == history_row.get("email"))
        ]
        if len(prior_for_person) > 1:
            st.warning(f"Returning applicant: {len(prior_for_person)} application records found.")
        st.dataframe(
            pd.DataFrame([{
                "Role": history_jobs.get(row["job_id"], {}).get("title", "Unassigned"),
                "Candidate": row["name"], "Email": row["email"], "Updated": row["updated_at"]
            } for row in prior_for_person]),
            use_container_width=True, hide_index=True,
        )
        with st.expander("View saved application details"):
            try:
                saved_history_workflow = json.loads(history_row.get("workflow_json") or "{}")
            except Exception:
                saved_history_workflow = {}
            st.json(saved_history_workflow)
    else:
        st.info("History appears after a role or candidate is saved.")
    history_events = list_audit_events(100)
    if history_events:
        st.markdown("### Recent changes")
        st.dataframe(
            pd.DataFrame(history_events)[["created_at", "actor", "action", "entity_type", "entity_id"]],
            use_container_width=True, hide_index=True,
        )


with tab_assistant:
    st.markdown("## Recruiter AI assistant")
    st.caption("Ask about the active role, candidates, evidence, workflow, or next review steps.")
    if not is_llm_available():
        st.info("Connect a Groq API key in Settings to use the conversational assistant. It does not use scripted replies.")
    for message in st.session_state.assistant_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    assistant_prompt = st.chat_input("Ask a question about this hiring workspace", disabled=not is_llm_available())
    if assistant_prompt:
        st.session_state.assistant_messages.append({"role": "user", "content": assistant_prompt})
        candidate_context = st.session_state.candidate_df.to_dict(orient="records") if not st.session_state.candidate_df.empty else []
        assistant_context = f"""
You are a conversational hiring decision-support assistant. Answer the recruiter's question
using semantic context and careful judgment, not acronym or keyword rules. Cite the supplied
candidate evidence in plain language. Never make an autonomous hiring decision, infer protected
attributes, or treat missing resume evidence as proof of missing ability. Flag uncertainty.
Active role analysis: {json.dumps(st.session_state.jd_analysis, default=str)[:7000]}
Candidate rankings: {json.dumps(candidate_context, default=str)[:9000]}
Recruiter question: {assistant_prompt}
"""
        try:
            assistant_answer = ask_llm(assistant_context, temperature=0.25)
        except Exception as exc:
            assistant_answer = f"The assistant could not complete that request: {exc}"
        st.session_state.assistant_messages.append({"role": "assistant", "content": assistant_answer})
        st.rerun()


with tab_operations:
    st.markdown("## Platform operations")
    st.caption(
        "Persistent records, workspace access, candidate portal links, audit history, "
        "ATS evaluation, scheduling, and email."
    )
    ops_user = st.session_state.workspace_user or {}
    ops_tabs = st.tabs(
        ["Records", "Users", "Candidate portal", "Audit", "ATS evaluation", "Scheduling"]
    )

    with ops_tabs[0]:
        persisted_jobs = list_jobs()
        persisted_candidates = list_persisted_candidates()
        st.metric("Persistent jobs", len(persisted_jobs))
        st.metric("Persistent candidate records", len(persisted_candidates))
        if persisted_jobs:
            job_labels = {
                f'{row["title"]} · job {row["id"]}': row for row in persisted_jobs
            }
            load_job_choice = st.selectbox(
                "Saved workspace",
                list(job_labels),
                key="saved_workspace_job",
            )
            if st.button("Load saved workspace"):
                saved_job = job_labels[load_job_choice]
                try:
                    saved_analysis = json.loads(saved_job["analysis_json"] or "{}")
                except Exception:
                    saved_analysis = {}
                st.session_state.active_job_id = saved_job["id"]
                st.session_state.job_description = saved_job["description"]
                st.session_state.jd_analysis = saved_analysis
                st.session_state.jd_role_skills = normalize_skill_list(
                    saved_analysis.get("required_skills", [])
                )
                st.session_state.jd_soft_skills = normalize_skill_list(
                    saved_analysis.get("soft_skills", [])
                )
                st.session_state.category = saved_analysis.get(
                    "role_category", "General"
                )
                st.session_state.simulation_task = get_simulation(
                    saved_job["description"], saved_analysis
                )
                saved_candidates = list_persisted_candidates(saved_job["id"])
                if saved_candidates:
                    build_candidate_tables(
                        [
                            {"Candidate": row["name"], "Resume Text": row["resume_text"]}
                            for row in saved_candidates
                        ]
                    )
                    for row in saved_candidates:
                        try:
                            saved_workflow = json.loads(row["workflow_json"] or "{}")
                        except Exception:
                            saved_workflow = {}
                        candidate_name = row["name"]
                        if saved_workflow.get("decision"):
                            st.session_state.recruiter_decisions[candidate_name] = saved_workflow["decision"]
                        if saved_workflow.get("notes"):
                            st.session_state.recruiter_notes[candidate_name] = saved_workflow["notes"]
                        if saved_workflow.get("rubric"):
                            st.session_state.candidate_rubric_scores[candidate_name] = saved_workflow["rubric"]
                        if saved_workflow.get("signal_card"):
                            st.session_state.candidate_signal_cards[candidate_name] = saved_workflow["signal_card"]
                        if saved_workflow.get("milestones"):
                            st.session_state.candidate_milestones[candidate_name] = saved_workflow["milestones"]
                st.success("Saved workspace loaded.")
                st.rerun()
        if persisted_candidates:
            st.dataframe(
                pd.DataFrame(
                    [
                        {
                            "ID": row["id"],
                            "Job ID": row["job_id"],
                            "Candidate": row["name"],
                            "Email": row["email"],
                            "Phone": row["phone"],
                            "Updated": row["updated_at"],
                        }
                        for row in persisted_candidates
                    ]
                ),
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.info("Analyze a role and screen candidates to create persistent records.")

    with ops_tabs[1]:
        if ops_user.get("role") != "admin":
            st.warning("Only administrators can manage workspace users.")
        else:
            users = list_users()
            if users:
                st.dataframe(pd.DataFrame(users), use_container_width=True, hide_index=True)
            with st.form("create_workspace_user"):
                new_user_name = st.text_input("Name")
                new_user_email = st.text_input("Email")
                new_user_role = st.selectbox(
                    "Role", ["recruiter", "hiring_manager", "admin"]
                )
                new_user_password = st.text_input("Temporary password", type="password")
                create_user_clicked = st.form_submit_button("Create user")
            if create_user_clicked:
                try:
                    create_user(
                        new_user_email,
                        new_user_name,
                        new_user_role,
                        new_user_password,
                    )
                    st.success("Workspace user created.")
                    st.rerun()
                except Exception as exc:
                    st.error(str(exc))

    with ops_tabs[2]:
        portal_candidates = list_persisted_candidates()
        if not portal_candidates:
            st.info("No persistent candidates are available yet.")
        else:
            portal_labels = {
                f'{row["name"]} · record {row["id"]}': row for row in portal_candidates
            }
            portal_choice = st.selectbox(
                "Candidate",
                list(portal_labels),
                key="portal_candidate_record",
            )
            if st.button("Generate secure candidate portal link"):
                token = create_portal_token(portal_labels[portal_choice]["id"])
                st.session_state["last_portal_link"] = f"?portal_token={token}"
            if st.session_state.get("last_portal_link"):
                st.code(st.session_state["last_portal_link"])
                st.caption(
                    "Add this query string to the deployed OfferPilot URL. Treat it "
                    "as a password and send it only to the selected candidate."
                )
        requests = list_candidate_requests()
        if requests:
            st.markdown("### Candidate requests")
            st.dataframe(pd.DataFrame(requests), use_container_width=True, hide_index=True)

    with ops_tabs[3]:
        events = list_audit_events()
        if events:
            audit_df = pd.DataFrame(events)
            st.dataframe(
                audit_df[["created_at", "actor", "action", "entity_type", "entity_id"]],
                use_container_width=True,
                hide_index=True,
            )
            with st.expander("Inspect raw audit details"):
                st.dataframe(audit_df, use_container_width=True, hide_index=True)
        else:
            st.info("Audit events appear after persistent workflow actions.")

    with ops_tabs[4]:
        st.write(
            "Upload a validation CSV with `expected_label` (0 or 1), "
            "`predicted_score` (0–100), and optional `audit_group`."
        )
        benchmark_file = st.file_uploader(
            "ATS validation dataset",
            type=["csv"],
            key="ats_benchmark_file",
        )
        benchmark_threshold = st.slider(
            "Evaluation threshold", 0, 100, 60, key="benchmark_threshold"
        )
        if benchmark_file is not None:
            benchmark_df = pd.read_csv(benchmark_file)
            required_columns = {"expected_label", "predicted_score"}
            if not required_columns.issubset(benchmark_df.columns):
                st.error("The CSV must contain expected_label and predicted_score.")
            else:
                expected = benchmark_df["expected_label"].astype(int)
                predicted = (
                    benchmark_df["predicted_score"].astype(float)
                    >= benchmark_threshold
                ).astype(int)
                tp = int(((expected == 1) & (predicted == 1)).sum())
                fp = int(((expected == 0) & (predicted == 1)).sum())
                fn = int(((expected == 1) & (predicted == 0)).sum())
                tn = int(((expected == 0) & (predicted == 0)).sum())
                metrics = {
                    "threshold": benchmark_threshold,
                    "rows": len(benchmark_df),
                    "precision": round(tp / max(tp + fp, 1), 3),
                    "recall": round(tp / max(tp + fn, 1), 3),
                    "accuracy": round((tp + tn) / max(len(benchmark_df), 1), 3),
                    "false_positive_rate": round(fp / max(fp + tn, 1), 3),
                    "false_negative_rate": round(fn / max(fn + tp, 1), 3),
                }
                metric_cols = st.columns(4)
                metric_cols[0].metric("Precision", metrics["precision"])
                metric_cols[1].metric("Recall", metrics["recall"])
                metric_cols[2].metric("False-positive rate", metrics["false_positive_rate"])
                metric_cols[3].metric("False-negative rate", metrics["false_negative_rate"])
                benchmark_df["predicted_label"] = predicted
                if "audit_group" in benchmark_df.columns:
                    group_rates = (
                        benchmark_df.groupby("audit_group", dropna=False)["predicted_label"]
                        .agg(["count", "mean"])
                        .reset_index()
                        .rename(columns={"mean": "selection_rate"})
                    )
                    st.markdown("### Aggregate selection-rate monitoring")
                    st.dataframe(group_rates, use_container_width=True, hide_index=True)
                if st.button("Save benchmark run"):
                    save_benchmark(
                        f"ATS validation · {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                        metrics,
                        benchmark_df.to_dict(orient="records"),
                        ops_user.get("email", "system"),
                    )
                    st.success("Benchmark run saved with an audit event.")
        saved_benchmarks = list_benchmarks()
        if saved_benchmarks:
            st.markdown("### Saved benchmark runs")
            st.dataframe(
                pd.DataFrame(
                    [
                        {
                            "ID": row["id"],
                            "Name": row["name"],
                            "Created by": row["created_by"],
                            "Created": row["created_at"],
                            "Metrics": row["metrics_json"],
                        }
                        for row in saved_benchmarks
                    ]
                ),
                use_container_width=True,
                hide_index=True,
            )

    with ops_tabs[5]:
        schedule_candidates = list_persisted_candidates()
        created_ics = None
        if not schedule_candidates:
            st.info("No persistent candidates are available for scheduling.")
        else:
            schedule_labels = {
                f'{row["name"]} · {row["email"] or "email missing"}': row
                for row in schedule_candidates
            }
            with st.form("schedule_interview_form"):
                schedule_choice = st.selectbox("Candidate", list(schedule_labels))
                schedule_date = st.date_input("Interview date")
                schedule_time = st.time_input("Interview time")
                schedule_timezone = st.text_input("Timezone", value="America/Chicago")
                schedule_duration = st.number_input(
                    "Duration in minutes", min_value=15, max_value=240, value=45, step=15
                )
                schedule_meeting_url = st.text_input("Meeting URL")
                schedule_notes = st.text_area("Candidate-facing notes")
                send_email_invite = st.checkbox("Send schedule email after saving")
                schedule_clicked = st.form_submit_button("Schedule interview", type="primary")
            if schedule_clicked:
                schedule_candidate = schedule_labels[schedule_choice]
                starts_at = datetime.combine(schedule_date, schedule_time).isoformat()
                save_interview(
                    schedule_candidate["id"],
                    starts_at,
                    int(schedule_duration),
                    schedule_timezone,
                    schedule_meeting_url,
                    schedule_notes,
                    ops_user.get("email", "system"),
                )
                end_time = datetime.combine(schedule_date, schedule_time) + pd.Timedelta(minutes=int(schedule_duration))
                created_ics = (
                    "BEGIN:VCALENDAR\r\nVERSION:2.0\r\nPRODID:-//OfferPilot//Interview//EN\r\n"
                    "BEGIN:VEVENT\r\n"
                    f"DTSTART:{datetime.combine(schedule_date, schedule_time).strftime('%Y%m%dT%H%M%S')}\r\n"
                    f"DTEND:{end_time.strftime('%Y%m%dT%H%M%S')}\r\n"
                    f"SUMMARY:Interview with {schedule_candidate['name']}\r\n"
                    f"LOCATION:{schedule_meeting_url}\r\nDESCRIPTION:{schedule_notes}\r\n"
                    "END:VEVENT\r\nEND:VCALENDAR\r\n"
                )
                st.session_state["last_interview_ics"] = created_ics
                if send_email_invite:
                    if not schedule_candidate["email"]:
                        st.warning("Interview saved, but the candidate email is missing.")
                    else:
                        try:
                            smtp_config = {
                                "host": st.secrets["SMTP_HOST"],
                                "port": st.secrets.get("SMTP_PORT", 587),
                                "username": st.secrets["SMTP_USERNAME"],
                                "password": st.secrets["SMTP_PASSWORD"],
                                "from_email": st.secrets["SMTP_FROM_EMAIL"],
                                "ssl": str(st.secrets.get("SMTP_SSL", "false")).lower() == "true",
                            }
                            email_body = (
                                f"Hello {schedule_candidate['name']},\n\nYour interview is scheduled for "
                                f"{starts_at} ({schedule_timezone}).\nMeeting: {schedule_meeting_url}\n\n"
                                f"{schedule_notes}"
                            )
                            delivery = send_smtp_email(
                                smtp_config,
                                schedule_candidate["email"],
                                "Your OfferPilot interview schedule",
                                email_body,
                            )
                            log_communication(
                                schedule_candidate["id"], "email", schedule_candidate["email"],
                                "Your OfferPilot interview schedule", email_body, delivery["status"]
                            )
                            st.success("Interview saved and schedule email sent.")
                        except Exception as exc:
                            st.warning(f"Interview saved, but email failed: {exc}")
                else:
                    st.success("Interview saved.")
        if st.session_state.get("last_interview_ics"):
            st.download_button(
                "Download calendar invitation (.ics)",
                data=st.session_state["last_interview_ics"],
                file_name="offerpilot_interview.ics",
                mime="text/calendar",
            )
        scheduled = list_interviews()
        if scheduled:
            st.markdown("### Scheduled interviews")
            st.dataframe(pd.DataFrame(scheduled), use_container_width=True, hide_index=True)


st.markdown('<div class="footer">Human-reviewed hiring intelligence</div>', unsafe_allow_html=True)
