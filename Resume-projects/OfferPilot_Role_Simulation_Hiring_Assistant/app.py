import io
import json
from datetime import datetime

import pandas as pd
import streamlit as st

from src.job_parser import jd_skill_extractor
from src.resume_reader import extract_text_from_pdf
from src.llm_client import ask_llm, is_llm_available
from src.llm_jd_analyzer import analyze_job_description_with_llm
from src.llm_simulation_generator import generate_simulation_task_with_llm
from src.llm_rubric_scorer import score_simulation_response_with_llm
from src.llm_signal_card import generate_signal_card_with_llm
from src.semantic_matcher import (
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
    page_title="OfferPilot | Hiring Intelligence",
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
            background: #091524;
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
        Computer Science student with experience building Python and Streamlit
        applications. Built an NLP resume analyzer using pandas, PDF parsing,
        TF-IDF text matching, REST APIs, Git, and evaluation dashboards. Worked
        with recruiters to convert feedback into product improvements. Presented
        results to nontechnical stakeholders and documented assumptions,
        limitations, and model tradeoffs. Strong collaboration, communication,
        and problem-solving experience.
        """,
    },
    {
        "Candidate": "Jordan Lee",
        "Resume Text": """
        Data Science student experienced with Python, pandas, machine learning,
        SQL, Git, data analysis, and visualization. Built classification models
        and a dashboard for student services. Familiar with NLP concepts and
        API integration. Collaborated in a four-person team and presented a final
        project. Interested in learning Streamlit, PDF parsing, and LLM systems.
        """,
    },
    {
        "Candidate": "Alex Morgan",
        "Resume Text": """
        Business student with Excel, presentation, customer service, and project
        coordination experience. Strong communication and teamwork. Limited
        experience with Python, Streamlit, pandas, NLP, APIs, and Git. Interested
        in technology and recruiting operations.
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
    "screening_completed": False,
    "demo_mode": False,
}

for key, default_value in DEFAULT_STATE.items():
    if key not in st.session_state:
        st.session_state[key] = default_value


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
            return analysis
    except Exception:
        pass
    return fallback_jd_analysis(job_description)


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

    final_score = round(
        (0.70 * technical_match["skill_score"])
        + (0.20 * technical_match["text_similarity_score"])
        + (0.10 * soft_match["skill_score"])
    )

    matched_skills = normalize_skill_list(
        technical_match["matched_skills"] + soft_match["matched_skills"]
    )
    missing_skills = normalize_skill_list(
        technical_match["missing_skills"] + soft_match["missing_skills"]
    )

    result = {
        "Candidate": candidate_name,
        "Match Score": final_score,
        "Technical Skill Score": technical_match["skill_score"],
        "Text Similarity": technical_match["text_similarity_score"],
        "Soft Skill Score": soft_match["skill_score"],
        "Review Priority": get_review_priority(final_score),
        "Matched Skills": ", ".join(matched_skills),
        "Missing Skills": ", ".join(missing_skills),
        "Resume Skills": ", ".join(resume_match_skills),
    }

    heatmap_row = {"Candidate": candidate_name}
    for skill in jd_all_skills:
        heatmap_row[skill] = "✓" if skill in resume_match_skills else "—"

    return result, heatmap_row


def build_candidate_tables(candidate_documents: list[dict]) -> None:
    candidate_results = []
    heatmap_results = []

    for candidate in candidate_documents:
        result, heatmap_row = candidate_score_row(
            candidate["Candidate"],
            candidate["Resume Text"],
        )
        candidate_results.append(result)
        heatmap_results.append(heatmap_row)

    candidate_df = pd.DataFrame(candidate_results)
    candidate_df = candidate_df.sort_values("Match Score", ascending=False).reset_index(drop=True)
    candidate_df.insert(0, "Rank", range(1, len(candidate_df) + 1))

    st.session_state.candidate_df = candidate_df
    st.session_state.heatmap_df = pd.DataFrame(heatmap_results)
    st.session_state.screening_completed = True


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

        with columns[index]:
            st.markdown(
                f"""
                <div class="candidate-card">
                    <div class="candidate-rank">Rank #{int(row["Rank"])}</div>
                    <div class="candidate-name">{row["Candidate"]}</div>
                    <div class="score-large">{int(row["Match Score"])}%</div>
                    <div class="muted">{matched_count} matched competencies</div>
                    <span class="status-chip {css_class}">{label}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:
    st.markdown("## ✦ OfferPilot")
    st.caption("Evidence-led hiring intelligence")

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

    if st.button("Load complete HR demo", type="primary", use_container_width=True):
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
# HERO
# ============================================================

st.markdown(
    """
    <div class="hero">
        <div class="eyebrow">Hiring intelligence · Human decision support</div>
        <h1 class="hero-title">
            Find stronger candidates with
            <span class="gradient-text">evidence, not just keywords.</span>
        </h1>
        <p class="hero-copy">
            OfferPilot combines job analysis, explainable resume matching,
            role-specific work simulations, structured scoring, and recruiter
            decision tracking in one review workspace.
        </p>
        <span class="mini-pill">Explainable matching</span>
        <span class="mini-pill">Role simulations</span>
        <span class="mini-pill">Human-in-the-loop decisions</span>
        <span class="mini-pill">Exportable review evidence</span>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="disclaimer">
        <strong>Responsible use:</strong> OfferPilot supports recruiter review. It
        should not make autonomous employment decisions or use protected attributes.
        Final decisions require qualified human judgment and role-relevant evidence.
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# MAIN NAVIGATION
# ============================================================

tab_overview, tab_role, tab_screening, tab_comparison, tab_simulation = st.tabs(
    [
        "Executive Overview",
        "1 · Role Intelligence",
        "2 · Candidate Screening",
        "3 · Evidence Comparison",
        "4 · Simulation & Decision",
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
                "Launch sample hiring review",
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
        "Turn an unstructured job description into a transparent assessment blueprint."
    )

    action_col, sample_col = st.columns([3, 1])

    with sample_col:
        if st.button("Use sample role", use_container_width=True):
            st.session_state.job_description = DEMO_JOB_DESCRIPTION
            st.rerun()

    job_description = st.text_area(
        "Job description",
        height=310,
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

    if st.session_state.jd_analysis:
        analysis = st.session_state.jd_analysis

        metric_cols = st.columns(4)
        metric_cols[0].metric(
            "Role",
            analysis.get("role_title", "Not identified"),
        )
        metric_cols[1].metric(
            "Category",
            analysis.get("role_category", st.session_state.category),
        )
        metric_cols[2].metric(
            "Required skills",
            len(st.session_state.jd_role_skills),
        )
        metric_cols[3].metric(
            "Seniority",
            analysis.get("seniority_level", "Not identified"),
        )

        left, right = st.columns([1.15, 1])

        with left:
            st.markdown("### Assessment blueprint")

            st.markdown("**Required competencies**")
            st.write(
                " · ".join(st.session_state.jd_role_skills)
                if st.session_state.jd_role_skills
                else "No required skills identified."
            )

            st.markdown("**Preferred competencies**")
            preferred = analysis.get("preferred_skills", [])
            st.write(" · ".join(preferred) if preferred else "None identified.")

            st.markdown("**Human competencies**")
            st.write(
                " · ".join(st.session_state.jd_soft_skills)
                if st.session_state.jd_soft_skills
                else "No soft skills identified."
            )

        with right:
            st.markdown("### What success looks like")
            st.write(analysis.get("ideal_candidate_summary", ""))

            st.markdown("**Core responsibilities**")
            for responsibility in analysis.get("responsibilities", []):
                st.write(f"• {responsibility}")


# ============================================================
# CANDIDATE SCREENING
# ============================================================

with tab_screening:
    st.markdown("## Candidate screening")
    st.caption(
        "Compare resume evidence using a transparent weighted model: "
        "70% technical skills, 20% text similarity, and 10% soft skills."
    )

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
            exp_left, exp_right = st.columns(2)

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
        st.dataframe(
            heatmap_df,
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
            f"{int(top_candidate['Match Score'] - lowest_candidate['Match Score'])} pts",
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

            metric_cols = st.columns(4)
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

        follow_up_questions = st.text_area(
            "Structured interview questions",
            value=st.session_state.follow_up_questions.get(selected_candidate, ""),
            height=100,
            key=f"questions_{selected_candidate}",
            placeholder="Add questions that validate missing or uncertain evidence...",
        )

        if st.button("Save recruiter decision"):
            st.session_state.recruiter_decisions[
                selected_candidate
            ] = recruiter_decision
            st.session_state.recruiter_notes[selected_candidate] = recruiter_notes
            st.session_state.follow_up_questions[
                selected_candidate
            ] = follow_up_questions
            st.success("Recruiter decision saved.")

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


st.markdown(
    """
    <div class="footer">
        OfferPilot · Built by Nishita Reddy Yaduguri · Applied AI for transparent,
        human-centered hiring workflows
    </div>
    """,
    unsafe_allow_html=True,
)
