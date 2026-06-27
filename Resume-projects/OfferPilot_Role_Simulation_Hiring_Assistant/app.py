import streamlit as st
import pandas as pd

from src.job_parser import jd_skill_extractor
from src.resume_reader import extract_text_from_pdf
from src.llm_client import ask_llm, is_llm_available
from src.llm_jd_analyzer import analyze_job_description_with_llm
from src.llm_simulation_generator import generate_simulation_task_with_llm
from src.llm_rubric_scorer import score_simulation_response_with_llm
from src.llm_signal_card import generate_signal_card_with_llm
from src.semantic_matcher import (
    normalize_skill_list,
    calculate_hybrid_candidate_score,
    get_review_priority,
    remove_negative_skill_sentences,
    find_jd_skills_in_resume_text
)

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
# Header
# -----------------------------
st.markdown(
    '<div class="main-title">OfferPilot</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">An LLM-powered role simulation hiring assistant that helps recruiters analyze jobs, screen resumes, generate work simulations, score responses, and create candidate signal cards.</div>',
    unsafe_allow_html=True
)


# -----------------------------
# LLM status
# -----------------------------
with st.expander("LLM Mode Status"):
    if is_llm_available():
        st.success("Groq API key found. LLM mode is available.")

        if st.button("Test LLM"):
            test_response = ask_llm("Reply with exactly: OfferPilot LLM connection is working.")
            st.write(test_response)
    else:
        st.warning("No Groq API key found. App is running in fallback mode.")


# -----------------------------
# Session State
# -----------------------------
if "job_description" not in st.session_state:
    st.session_state.job_description = ""

if "jd_analysis" not in st.session_state:
    st.session_state.jd_analysis = {}

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

if "candidate_responses" not in st.session_state:
    st.session_state.candidate_responses = {}

if "candidate_rubric_scores" not in st.session_state:
    st.session_state.candidate_rubric_scores = {}

if "candidate_signal_cards" not in st.session_state:
    st.session_state.candidate_signal_cards = {}

if "current_candidate_answer" not in st.session_state:
    st.session_state.current_candidate_answer = ""

if "last_selected_candidate" not in st.session_state:
    st.session_state.last_selected_candidate = ""

if "recruiter_notes" not in st.session_state:
    st.session_state.recruiter_notes = {}

if "recruiter_decisions" not in st.session_state:
    st.session_state.recruiter_decisions = {}

if "follow_up_questions" not in st.session_state:
    st.session_state.follow_up_questions = {}


# -----------------------------
# Tabs
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
            <div class="card-title">LLM Job Description Setup</div>
            <div class="card-text">
                Paste the job description. OfferPilot will use the LLM to extract role details, skills, responsibilities, and candidate expectations.
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
            with st.spinner("Analyzing job description with LLM..."):
                jd_analysis = analyze_job_description_with_llm(job_description)

                role_skills = normalize_skill_list(jd_analysis.get("required_skills", []))
                soft_skills = normalize_skill_list(jd_analysis.get("soft_skills", []))
                category = jd_analysis.get("role_category", "")

                simulation_task = generate_simulation_task_with_llm(
                    job_description,
                    jd_analysis
                )

                st.session_state.job_description = job_description
                st.session_state.jd_analysis = jd_analysis
                st.session_state.jd_role_skills = role_skills
                st.session_state.jd_soft_skills = soft_skills
                st.session_state.category = category
                st.session_state.simulation_task = simulation_task

            st.success("Job description analyzed successfully.")

    if st.session_state.job_description:
        col1, col2, col3 = st.columns(3)

        col1.metric("Role Category", st.session_state.category)
        col2.metric("Required Skills", len(st.session_state.jd_role_skills))
        col3.metric("Soft Skills", len(st.session_state.jd_soft_skills))

        st.subheader("Job Description Analysis")

        jd_analysis = st.session_state.jd_analysis

        st.write("**Role Title:**", jd_analysis.get("role_title", ""))
        st.write("**Role Category:**", jd_analysis.get("role_category", st.session_state.category))
        st.write("**Seniority Level:**", jd_analysis.get("seniority_level", ""))

        st.write("**Required Skills:**", st.session_state.jd_role_skills)
        st.write("**Preferred Skills:**", jd_analysis.get("preferred_skills", []))
        st.write("**Soft Skills:**", st.session_state.jd_soft_skills)

        st.write("**Responsibilities:**")
        for responsibility in jd_analysis.get("responsibilities", []):
            st.write("- " + responsibility)

        st.write("**Ideal Candidate Summary:**")
        st.write(jd_analysis.get("ideal_candidate_summary", ""))

# -----------------------------
# Tab 2: Candidate Screening
# -----------------------------
with tab2:
    st.markdown(
        """
        <div class="section-card">
            <div class="card-title">Candidate Screening</div>
            <div class="card-text">
                Upload resume PDFs. OfferPilot extracts resume text, compares resumes to the job description, and ranks candidates using weighted technical skill, soft skill, and text similarity scoring.
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

            # Separate technical skills and soft skills
            jd_technical_skills = normalize_skill_list(
                st.session_state.jd_role_skills
            )

            jd_soft_skills = normalize_skill_list(
                st.session_state.jd_soft_skills
            )

            # Used only for the heatmap display
            jd_all_skills = normalize_skill_list(
                jd_technical_skills + jd_soft_skills
            )

            for resume in uploaded_resumes:
                resume_text = extract_text_from_pdf(resume)

                # Removes sentences like "limited experience with Python..."
                # so weak resumes do not falsely match technical skills.
                clean_resume_text = remove_negative_skill_sentences(resume_text)

                resume_role_skills, resume_soft_skills = jd_skill_extractor(
                    clean_resume_text
                )

                direct_jd_skill_matches = find_jd_skills_in_resume_text(
                    jd_technical_skills + jd_soft_skills,
                    clean_resume_text
                )

                resume_match_skills = normalize_skill_list(
                    resume_role_skills + resume_soft_skills + direct_jd_skill_matches
                )

                # Technical match: most important part of resume screening
                technical_match = calculate_hybrid_candidate_score(
                    st.session_state.job_description,
                    clean_resume_text,
                    jd_technical_skills,
                    resume_match_skills
                )

                # Soft skill match: useful, but weighted lower
                soft_match = calculate_hybrid_candidate_score(
                    st.session_state.job_description,
                    clean_resume_text,
                    jd_soft_skills,
                    resume_match_skills
                )

                # Weighted final score
                # 70% technical skill match
                # 20% resume/JD text similarity
                # 10% soft skill match
                final_score = round(
                    (0.70 * technical_match["skill_score"]) +
                    (0.20 * technical_match["text_similarity_score"]) +
                    (0.10 * soft_match["skill_score"])
                )

                matched_skills = normalize_skill_list(
                    technical_match["matched_skills"] +
                    soft_match["matched_skills"]
                )

                missing_skills = normalize_skill_list(
                    technical_match["missing_skills"] +
                    soft_match["missing_skills"]
                )

                skill_score = technical_match["skill_score"]
                text_similarity_score = technical_match["text_similarity_score"]

                review_priority = get_review_priority(final_score)

                candidate_results.append({
                    "Candidate": resume.name,
                    "Match Score": final_score,
                    "Skill Score": skill_score,
                    "Text Similarity": text_similarity_score,
                    "Review Priority": review_priority,
                    "Matched Skills": ", ".join(matched_skills),
                    "Missing Skills": ", ".join(missing_skills),
                    "Resume Skills": ", ".join(resume_match_skills)
                })

                # Build heatmap row
                heatmap_row = {"Candidate": resume.name}

                for skill in jd_all_skills:
                    if skill in resume_match_skills:
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

            # Remove saved reviews for candidates no longer uploaded
            current_candidates = set(candidate_df["Candidate"].tolist())

            st.session_state.candidate_responses = {
                candidate: response
                for candidate, response in st.session_state.candidate_responses.items()
                if candidate in current_candidates
            }

            st.session_state.candidate_rubric_scores = {
                candidate: scores
                for candidate, scores in st.session_state.candidate_rubric_scores.items()
                if candidate in current_candidates
            }

            st.session_state.candidate_signal_cards = {
                candidate: card
                for candidate, card in st.session_state.candidate_signal_cards.items()
                if candidate in current_candidates
            }

            st.session_state.recruiter_notes = {
                candidate: notes
                for candidate, notes in st.session_state.recruiter_notes.items()
                if candidate in current_candidates
            }

            st.session_state.recruiter_decisions = {
                candidate: decision
                for candidate, decision in st.session_state.recruiter_decisions.items()
                if candidate in current_candidates
            }

            st.session_state.follow_up_questions = {
                candidate: questions
                for candidate, questions in st.session_state.follow_up_questions.items()
                if candidate in current_candidates
            }

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
                Compare each candidate against the required role and soft skills from the job description.
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
            <div class="card-title">LLM Simulation Review</div>
            <div class="card-text">
                Review a role-specific simulation task, paste a candidate response, score it with an LLM rubric, and generate a candidate signal card.
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
            candidate_names,
            key="selected_candidate_for_simulation"
        )

        if st.session_state.last_selected_candidate != selected_candidate:
            st.session_state.current_candidate_answer = st.session_state.candidate_responses.get(
                selected_candidate,
                ""
            )
            st.session_state.last_selected_candidate = selected_candidate

        st.text_area(
            "Paste the candidate's simulation response here",
            height=220,
            key="current_candidate_answer"
        )

        col_save, col_clear = st.columns(2)

        with col_save:
            save_clicked = st.button("Score Response and Save Review")

        with col_clear:
            clear_clicked = st.button("Clear Current Response")

        if clear_clicked:
            st.session_state.current_candidate_answer = ""
            st.rerun()

        if save_clicked:
            if st.session_state.current_candidate_answer.strip() == "":
                st.warning("Please paste the candidate's response first.")
            else:
                with st.spinner("Scoring response and generating signal card..."):
                    rubric_scores = score_simulation_response_with_llm(
                        st.session_state.current_candidate_answer,
                        st.session_state.category,
                        st.session_state.simulation_task
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

                    signal_card = generate_signal_card_with_llm(
                        selected_candidate,
                        selected_candidate_row["Match Score"],
                        rubric_scores["Simulation Score"],
                        matched_skills_list,
                        missing_skills_list,
                        rubric_scores,
                        st.session_state.category
                    )

                    st.session_state.candidate_responses[selected_candidate] = (
                        st.session_state.current_candidate_answer
                    )
                    st.session_state.candidate_rubric_scores[selected_candidate] = rubric_scores
                    st.session_state.candidate_signal_cards[selected_candidate] = signal_card

                st.success(
                    f"Saved response, rubric score, and signal card for {selected_candidate}."
                )

        if selected_candidate in st.session_state.candidate_signal_cards:
            selected_candidate_row = st.session_state.candidate_df[
                st.session_state.candidate_df["Candidate"] == selected_candidate
            ].iloc[0]

            saved_rubric_scores = st.session_state.candidate_rubric_scores[selected_candidate]
            saved_signal_card = st.session_state.candidate_signal_cards[selected_candidate]
            saved_response = st.session_state.candidate_responses[selected_candidate]

            col1, col2, col3 = st.columns(3)

            col1.metric(
                "Resume Match",
                str(selected_candidate_row["Match Score"]) + "%"
            )

            col2.metric(
                "Simulation Score",
                str(saved_rubric_scores["Simulation Score"]) + "%"
            )

            col3.metric(
                "Final Confidence",
                saved_signal_card["Final Confidence"]
            )

            with st.expander("View Saved Submitted Response"):
                st.write(saved_response)

            st.subheader("Rubric Score")

            score_df = pd.DataFrame(
                list(saved_rubric_scores.items()),
                columns=["Rubric Area", "Score"]
            )

            st.dataframe(score_df, use_container_width=True)

            st.subheader("Candidate Signal Card")

            st.markdown(
                f"""
                <div class="section-card">
                    <div class="card-title">{selected_candidate}</div>
                    <div class="card-text"><b>Final Confidence:</b> {saved_signal_card.get("Final Confidence", "")}</div>
                    <div class="card-text"><b>Recommended Next Step:</b> {saved_signal_card.get("Recommended Next Step", "")}</div>
                    <div class="card-text"><b>Recruiter Summary:</b> {saved_signal_card.get("Recruiter Summary", "")}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

            card_col1, card_col2, card_col3 = st.columns(3)

            with card_col1:
                st.markdown("### Strengths")
                for strength in saved_signal_card.get("Strengths", []):
                    st.success(strength)

            with card_col2:
                st.markdown("### Risks")
                for risk in saved_signal_card.get("Risks", []):
                    st.warning(risk)

            with card_col3:
                st.markdown("### Interview Focus")
                for focus_area in saved_signal_card.get("Interview Focus Areas", []):
                    st.info(focus_area)
        else:
             st.info("No saved simulation review for this candidate yet.")

        st.divider()

        st.subheader("Recruiter Notes and Decision")

        saved_decision = st.session_state.recruiter_decisions.get(
            selected_candidate,
            "Needs More Review"
        )

        decision_options = [
            "Move Forward",
            "Hold",
            "Reject",
            "Needs More Review"
        ]

        recruiter_decision = st.selectbox(
            "Recruiter Decision",
            decision_options,
            index=decision_options.index(saved_decision),
            key=f"decision_{selected_candidate}"
        )

        saved_notes = st.session_state.recruiter_notes.get(
            selected_candidate,
            ""
        )

        recruiter_notes = st.text_area(
            "Recruiter Notes",
            value=saved_notes,
            height=120,
            key=f"notes_{selected_candidate}"
        )

        saved_questions = st.session_state.follow_up_questions.get(
            selected_candidate,
            ""
        )

        follow_up_questions = st.text_area(
            "Follow-up Questions",
            value=saved_questions,
            height=120,
            key=f"questions_{selected_candidate}"
        )

        if st.button("Save Recruiter Notes"):
            st.session_state.recruiter_decisions[selected_candidate] = recruiter_decision
            st.session_state.recruiter_notes[selected_candidate] = recruiter_notes
            st.session_state.follow_up_questions[selected_candidate] = follow_up_questions

            st.success(f"Recruiter notes saved for {selected_candidate}.")

        st.divider()

        st.subheader("Saved Candidate Reviews")
        if len(st.session_state.candidate_signal_cards) == 0:
            st.info("No candidate reviews saved yet.")
        else:
            for candidate_name, signal_card in st.session_state.candidate_signal_cards.items():
                rubric_scores = st.session_state.candidate_rubric_scores[candidate_name]
                response = st.session_state.candidate_responses[candidate_name]

                with st.expander(candidate_name):
                    review_row = st.session_state.candidate_df[
                        st.session_state.candidate_df["Candidate"] == candidate_name
                    ].iloc[0]

                    col1, col2, col3 = st.columns(3)

                    col1.metric(
                        "Resume Match",
                        str(review_row["Match Score"]) + "%"
                    )

                    col2.metric(
                        "Simulation Score",
                        str(rubric_scores["Simulation Score"]) + "%"
                    )

                    col3.metric(
                        "Final Confidence",
                        signal_card.get("Final Confidence", "")
                    )

                    st.write(
                        "**Recommended Next Step:**",
                        signal_card.get("Recommended Next Step", "")
                    )

                    st.write(
                        "**Recruiter Summary:**",
                        signal_card.get("Recruiter Summary", "")
                    )

                    st.write(
                        "**Recruiter Decision:**",
                        st.session_state.recruiter_decisions.get(
                            candidate_name,
                            "Not saved"
                        )
                    )

                    st.write(
                        "**Recruiter Notes:**",
                        st.session_state.recruiter_notes.get(
                            candidate_name,
                            "No notes saved."
                        )
                    )

                    st.write(
                        "**Follow-up Questions:**",
                        st.session_state.follow_up_questions.get(
                            candidate_name,
                            "No follow-up questions saved."
                        )
                    )

                    st.write("**Saved Response:**")
                    st.write(response)

                    st.write("**Rubric Scores:**")
                    st.dataframe(
                        pd.DataFrame(
                            list(rubric_scores.items()),
                            columns=["Rubric Area", "Score"]
                        ),
                        use_container_width=True
                    )

                    review_col1, review_col2, review_col3 = st.columns(3)

                    with review_col1:
                        st.markdown("**Strengths**")
                        for strength in signal_card.get("Strengths", []):
                            st.success(strength)

                    with review_col2:
                        st.markdown("**Risks**")
                        for risk in signal_card.get("Risks", []):
                            st.warning(risk)

                    with review_col3:
                        st.markdown("**Interview Focus Areas**")
                        for focus_area in signal_card.get("Interview Focus Areas", []):
                            st.info(focus_area)