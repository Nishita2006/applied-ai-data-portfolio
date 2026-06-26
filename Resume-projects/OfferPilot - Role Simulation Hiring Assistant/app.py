import streamlit as st
import pandas as pd

from src.job_parser import jd_skill_extractor, role_category
from src.resume_reader import extract_text_from_pdf
from src.match_engine import calculate_match_score
from src.simulation_generator import generate_simulation_task
from src.rubric_scorer import score_simulation_response
from src.signal_card import generate_signal_card


# -----------------------------
# Page setup
# -----------------------------
st.set_page_config(
    page_title="OfferPilot",
    page_icon="🎯",
    layout="wide"
)


# -----------------------------
# Custom styling
# -----------------------------
st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(135deg, #eef4ff 0%, #f8f7ff 45%, #f7fbff 100%);
        color: #1f2937;
    }

    .main-title {
        font-size: 46px;
        font-weight: 800;
        color: #243b6b;
        margin-bottom: 4px;
        letter-spacing: -0.5px;
    }

    .subtitle {
        font-size: 18px;
        color: #64748b;
        margin-bottom: 30px;
        max-width: 950px;
    }

    .section-card {
        background: rgba(255, 255, 255, 0.88);
        padding: 26px;
        border-radius: 20px;
        box-shadow: 0px 8px 24px rgba(99, 102, 241, 0.10);
        margin-bottom: 24px;
        border: 1px solid #dbeafe;
    }

    .card-title {
        font-size: 23px;
        font-weight: 750;
        color: #1e3a8a;
        margin-bottom: 8px;
    }

    .card-text {
        font-size: 15px;
        color: #64748b;
        margin-bottom: 8px;
        line-height: 1.6;
    }

    div[data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.9);
        border: 1px solid #dbeafe;
        padding: 18px;
        border-radius: 18px;
        box-shadow: 0px 6px 18px rgba(37, 99, 235, 0.08);
    }

    div[data-testid="stMetricLabel"] {
        color: #64748b;
        font-weight: 600;
    }

    div[data-testid="stMetricValue"] {
        color: #1e3a8a;
        font-weight: 800;
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background-color: rgba(255, 255, 255, 0.55);
        padding: 8px;
        border-radius: 16px;
    }

    .stTabs [data-baseweb="tab"] {
        background-color: #ffffff;
        border-radius: 12px;
        color: #475569;
        padding: 10px 18px;
        border: 1px solid #dbeafe;
        font-weight: 600;
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #dbeafe 0%, #ede9fe 100%);
        color: #1e3a8a;
        border: 1px solid #bfdbfe;
    }

    div.stButton > button {
        background: linear-gradient(135deg, #3b82f6 0%, #6366f1 100%);
        color: white;
        border-radius: 12px;
        padding: 0.65rem 1.25rem;
        border: none;
        font-weight: 700;
        box-shadow: 0px 6px 16px rgba(59, 130, 246, 0.25);
    }

    div.stButton > button:hover {
        background: linear-gradient(135deg, #2563eb 0%, #4f46e5 100%);
        color: white;
        border: none;
    }

    textarea, input {
        border-radius: 12px !important;
    }

    div[data-testid="stDataFrame"] {
        border-radius: 16px;
        overflow: hidden;
        border: 1px solid #dbeafe;
        box-shadow: 0px 6px 18px rgba(37, 99, 235, 0.08);
    }

    .stAlert {
        border-radius: 14px;
    }

    div[data-testid="stExpander"] {
        background-color: rgba(255, 255, 255, 0.8);
        border-radius: 14px;
        border: 1px solid #dbeafe;
    }
    </style>
    """,
    unsafe_allow_html=True
)


# -----------------------------
# App header
# -----------------------------
st.markdown(
    '<div class="main-title">OfferPilot</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">A role simulation hiring assistant that helps recruiters screen resumes, compare candidate fit, and evaluate responses with structured rubrics.</div>',
    unsafe_allow_html=True
)


# -----------------------------
# Store values across tabs
# -----------------------------
if "job_description" not in st.session_state:
    st.session_state.job_description = ""

if "category" not in st.session_state:
    st.session_state.category = ""

if "jd_role_skills" not in st.session_state:
    st.session_state.jd_role_skills = []

if "jd_soft_skills" not in st.session_state:
    st.session_state.jd_soft_skills = []

if "candidate_df" not in st.session_state:
    st.session_state.candidate_df = pd.DataFrame()

if "heatmap_df" not in st.session_state:
    st.session_state.heatmap_df = pd.DataFrame()

if "simulation_task" not in st.session_state:
    st.session_state.simulation_task = ""


# -----------------------------
# App tabs
# -----------------------------
tab1, tab2, tab3, tab4 = st.tabs([
    "Job Setup",
    "Candidate Screening",
    "Skill Heatmap",
    "Simulation Review"
])


# -----------------------------
# Tab 1: Job Setup
# -----------------------------
with tab1:
    st.markdown(
        """
        <div class="section-card">
            <div class="card-title">Job Description Setup</div>
            <div class="card-text">
                Paste the job description. OfferPilot will extract role skills, soft skills, and role category.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    job_description = st.text_area(
        "Paste the job description here",
        height=280,
        value=st.session_state.job_description
    )

    analyze_jd = st.button("Analyze Job Description")

    if analyze_jd:
        if job_description.strip() == "":
            st.warning("Please paste a job description first.")
        else:
            role_skills, soft_skills = jd_skill_extractor(job_description)
            category = role_category(job_description)
            simulation_task = generate_simulation_task(category)

            st.session_state.job_description = job_description
            st.session_state.jd_role_skills = role_skills
            st.session_state.jd_soft_skills = soft_skills
            st.session_state.category = category
            st.session_state.simulation_task = simulation_task

            st.success("Job description analyzed successfully.")

    if st.session_state.job_description:
        col1, col2, col3 = st.columns(3)

        col1.metric("Role Category", st.session_state.category)
        col2.metric("Role Skills Found", len(st.session_state.jd_role_skills))
        col3.metric("Soft Skills Found", len(st.session_state.jd_soft_skills))

        st.subheader("Job Description Analysis")
        st.write("**Role Category:**", st.session_state.category)
        st.write("**Role Skills Found:**", st.session_state.jd_role_skills)
        st.write("**Soft Skills Found:**", st.session_state.jd_soft_skills)


# -----------------------------
# Tab 2: Candidate Screening
# -----------------------------
with tab2:
    st.markdown(
        """
        <div class="section-card">
            <div class="card-title">Candidate Screening</div>
            <div class="card-text">
                Upload multiple resume PDFs. The app extracts resume skills, compares them to the job description, and ranks candidates.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    uploaded_resumes = st.file_uploader(
        "Upload candidate resume PDFs",
        type=["pdf"],
        accept_multiple_files=True
    )

    if uploaded_resumes:
        if st.session_state.job_description.strip() == "":
            st.warning("Please analyze a job description first in the Job Setup tab.")
        else:
            candidate_results = []
            heatmap_results = []

            for resume in uploaded_resumes:
                resume_text = extract_text_from_pdf(resume)
                resume_role_skills, resume_soft_skills = jd_skill_extractor(resume_text)

                # Match resume skills against JD skills
                matched_skills, missing_skills, match_score = calculate_match_score(
                    st.session_state.jd_role_skills,
                    resume_role_skills
                )

                if match_score >= 75:
                    review_priority = "High Review"
                elif match_score >= 50:
                    review_priority = "Medium Review"
                else:
                    review_priority = "Low Review"

                candidate_results.append({
                    "Candidate": resume.name,
                    "Match Score": match_score,
                    "Review Priority": review_priority,
                    "Matched Skills": ", ".join(matched_skills),
                    "Missing Skills": ", ".join(missing_skills),
                    "Resume Skills": ", ".join(resume_role_skills)
                })

                # Build heatmap row
                heatmap_row = {"Candidate": resume.name}

                for skill in st.session_state.jd_role_skills:
                    if skill in resume_role_skills:
                        heatmap_row[skill] = "Yes"
                    else:
                        heatmap_row[skill] = "No"

                heatmap_results.append(heatmap_row)

                with st.expander(f"View Extracted Resume Text - {resume.name}"):
                    st.write(resume_text[:3000])

            candidate_df = pd.DataFrame(candidate_results)

            candidate_df = candidate_df.sort_values(
                by="Match Score",
                ascending=False
            )

            candidate_df.insert(0, "Rank", range(1, len(candidate_df) + 1))

            heatmap_df = pd.DataFrame(heatmap_results)

            st.session_state.candidate_df = candidate_df
            st.session_state.heatmap_df = heatmap_df

            st.success("Candidate screening completed.")

    if not st.session_state.candidate_df.empty:
        st.subheader("Candidate Ranking Results")

        total_candidates = len(st.session_state.candidate_df)
        top_score = st.session_state.candidate_df["Match Score"].max()
        high_review_count = len(
            st.session_state.candidate_df[
                st.session_state.candidate_df["Review Priority"] == "High Review"
            ]
        )

        col1, col2, col3, col4 = st.columns(4)

        col1.metric("Total Candidates", total_candidates)
        col2.metric("Top Match Score", str(top_score) + "%")
        col3.metric("High Review", high_review_count)
        col4.metric("Role Category", st.session_state.category)

        st.dataframe(st.session_state.candidate_df, use_container_width=True)


# -----------------------------
# Tab 3: Skill Heatmap
# -----------------------------
with tab3:
    st.markdown(
        """
        <div class="section-card">
            <div class="card-title">Skill Heatmap</div>
            <div class="card-text">
                Compare candidates against the required skills from the job description.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    if st.session_state.heatmap_df.empty:
        st.info("Upload resumes in the Candidate Screening tab to view the heatmap.")
    else:
        st.dataframe(st.session_state.heatmap_df, use_container_width=True)


# -----------------------------
# Tab 4: Simulation Review
# -----------------------------
with tab4:
    st.markdown(
        """
        <div class="section-card">
            <div class="card-title">Simulation Review</div>
            <div class="card-text">
                Generate a role-specific task, paste a candidate response, score it with a rubric, and create a final signal card.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    if st.session_state.candidate_df.empty:
        st.info("Complete candidate screening first.")
    else:
        st.subheader("Role Simulation Task")

        st.write("**Role Category:**", st.session_state.category)
        st.write(st.session_state.simulation_task)

        st.subheader("Candidate Simulation Response")

        candidate_names = st.session_state.candidate_df["Candidate"].tolist()

        selected_candidate = st.selectbox(
            "Select candidate",
            candidate_names
        )

        candidate_answer = st.text_area(
            "Paste the candidate's simulation response here",
            height=220
        )

        if st.button("Score Candidate Response"):
            if candidate_answer.strip() == "":
                st.warning("Please paste the candidate's response first.")
            else:
                rubric_scores = score_simulation_response(
                    candidate_answer,
                    st.session_state.category
                )

                selected_candidate_row = st.session_state.candidate_df[
                    st.session_state.candidate_df["Candidate"] == selected_candidate
                ].iloc[0]

                matched_skills_list = (
                    selected_candidate_row["Matched Skills"].split(", ")
                    if selected_candidate_row["Matched Skills"]
                    else []
                )

                missing_skills_list = (
                    selected_candidate_row["Missing Skills"].split(", ")
                    if selected_candidate_row["Missing Skills"]
                    else []
                )

                signal_card = generate_signal_card(
                    selected_candidate_row["Match Score"],
                    rubric_scores["Simulation Score"],
                    matched_skills_list,
                    missing_skills_list
                )

                st.success("Candidate response scored successfully.")

                col1, col2, col3 = st.columns(3)

                col1.metric(
                    "Resume Match",
                    str(selected_candidate_row["Match Score"]) + "%"
                )

                col2.metric(
                    "Simulation Score",
                    str(rubric_scores["Simulation Score"]) + "%"
                )

                col3.metric(
                    "Final Confidence",
                    signal_card["Final Confidence"]
                )

                with st.expander("View Submitted Response"):
                    st.write(candidate_answer)

                st.subheader("Rubric Score")

                score_df = pd.DataFrame(
                    list(rubric_scores.items()),
                    columns=["Rubric Area", "Score"]
                )

                st.dataframe(score_df, use_container_width=True)

                st.subheader("Candidate Signal Card")

                st.markdown(
                    f"""
                    <div class="section-card">
                        <div class="card-title">{selected_candidate}</div>
                        <div class="card-text"><b>Final Confidence:</b> {signal_card["Final Confidence"]}</div>
                        <div class="card-text"><b>Recommended Next Step:</b> {signal_card["Recommended Next Step"]}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                card_col1, card_col2 = st.columns(2)

                with card_col1:
                    st.markdown("### Strengths")
                    for strength in signal_card["Strengths"]:
                        st.success(strength)

                with card_col2:
                    st.markdown("### Risks")
                    for risk in signal_card["Risks"]:
                        st.warning(risk)