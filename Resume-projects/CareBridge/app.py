from __future__ import annotations

import os
from pathlib import Path

import pandas as pd
import streamlit as st

from src.analytics import preparation_score, status_counts, symptom_chart
from src.database import execute, initialize, query
from src.ml import classify_document
from src.nlp import organize_symptom
from src.rag import answer, load_demo_chunks

ROOT = Path(__file__).parent


def load_optional_model_secrets() -> None:
    """Use Streamlit secrets when configured; run local RAG when they are absent."""
    try:
        api_key = st.secrets.get("OPENAI_API_KEY")
        model = st.secrets.get("OPENAI_MODEL")
    except Exception:
        # Community Cloud and local demos may intentionally have no secrets file.
        return
    if api_key:
        os.environ["OPENAI_API_KEY"] = str(api_key)
    if model:
        os.environ["OPENAI_MODEL"] = str(model)


load_optional_model_secrets()
initialize()

st.set_page_config(page_title="CareBridge", page_icon="🌿", layout="wide")
st.markdown("""<style>
.stApp{background:#f7f5ef;color:#18313b}.block-container{padding-top:2rem;max-width:1200px}
[data-testid=stSidebar]{background:#15384a}[data-testid=stSidebar] *{color:#eef7f4}
.hero{background:linear-gradient(135deg,#173a4c,#25655f);padding:1.6rem 1.8rem;border-radius:16px;color:white;margin-bottom:1rem}
.hero h1{margin:0;font-size:2.15rem}.hero p{color:#cfe2df}.label{font-size:.72rem;letter-spacing:.12em;text-transform:uppercase;color:#2d786f;font-weight:700}
.notice{background:#fff1d8;border-left:4px solid #c48734;padding:.8rem 1rem;border-radius:6px;font-size:.9rem}
.source{background:#e5f1ee;color:#256a62;padding:.18rem .45rem;border-radius:5px;font-size:.72rem}
</style>""", unsafe_allow_html=True)

with st.sidebar:
    st.title("🌿 CareBridge")
    st.caption("Arrive prepared. Leave with clarity.")
    page = st.radio("Navigate", ["Dashboard", "Symptoms & EDA", "Documents & ML", "RAG Assistant", "SQL Explorer", "Visit Summary"], label_visibility="collapsed")
    st.divider()
    st.info("Preparation support only. CareBridge does not diagnose or recommend treatment.")
    st.caption("Maya Thompson · synthetic demo")

tasks = query("SELECT * FROM preparation_tasks WHERE appointment_id = 1")
symptoms = query("SELECT * FROM symptoms WHERE appointment_id = 1")
appointment = query("SELECT * FROM appointments WHERE id = 1").iloc[0]
score = preparation_score(tasks)

st.caption("DEMO MODE · All patient information is fictional.")

if page == "Dashboard":
    st.markdown(f'<div class="hero"><div class="label" style="color:#9bd2c9">Upcoming appointment</div><h1>{appointment.title}</h1><p>{appointment.provider} · September 18, 2026 · In person</p><b>{appointment.reason}</b></div>', unsafe_allow_html=True)
    a,b,c,d = st.columns(4)
    a.metric("Preparation score", f"{score}%", help="Administrative completeness—not medical readiness")
    b.metric("Checklist", f"{(tasks.status == 'complete').sum()} / {len(tasks)}")
    c.metric("Symptoms tracked", len(symptoms))
    d.metric("Questions prepared", int(query("SELECT COUNT(*) n FROM questions").iloc[0].n))
    left,right = st.columns([1.6,1])
    with left:
        st.subheader("Preparation checklist")
        edited = st.data_editor(tasks[["title","status","due_date"]], hide_index=True, width="stretch", disabled=["title","due_date"], column_config={"status": st.column_config.SelectboxColumn(options=["not_started","in_progress","complete","not_applicable"])})
        if st.button("Save checklist", type="primary"):
            for idx,row in edited.iterrows(): execute("UPDATE preparation_tasks SET status=? WHERE id=?", (row.status, int(tasks.iloc[idx].id)))
            st.success("Checklist saved to SQLite.")
    with right:
        st.subheader("Status breakdown")
        st.bar_chart(status_counts(tasks).set_index("status"))
        st.markdown('<div class="notice"><b>Not a medical score.</b><br>This only measures completion of appointment-preparation tasks.</div>', unsafe_allow_html=True)

elif page == "Symptoms & EDA":
    st.markdown("## Symptoms, NLP & exploratory analysis")
    st.caption("Pandas cleans and sorts the data; NumPy calculates metrics; Matplotlib produces the chart; lightweight NLP organizes free text.")
    st.pyplot(symptom_chart(symptoms), width="stretch")
    st.dataframe(symptoms[["symptom","onset_date","severity","pattern","source"]], hide_index=True, width="stretch")
    st.subheader("Organize a patient-written symptom")
    text = st.text_area("Describe what you noticed in your own words", placeholder="For the last two weeks, I noticed...")
    if st.button("Run NLP organization", type="primary") and text:
        result = organize_symptom(text)
        st.write("**Original (preserved):**", result["original"])
        st.write("**Organized draft:**", result["organized"])
        st.write("**Extracted keywords:**", ", ".join(result["keywords"]) or "None")
        st.warning("AI/NLP-assisted wording is unverified. The patient must approve it before use.")

elif page == "Documents & ML":
    st.markdown("## Document organization & machine learning")
    st.caption("An explainable TF-IDF + logistic-regression pipeline suggests a document category. It does not interpret clinical meaning.")
    docs = query("SELECT title,category,organization,citation FROM documents")
    st.dataframe(docs, hide_index=True, width="stretch")
    sample = st.text_area("Paste document text to classify", "Laboratory results collected August 21 with reference ranges and follow-up instructions.")
    if st.button("Classify document") and sample:
        label, confidence = classify_document(sample)
        st.metric("Suggested category", label, f"{confidence:.0%} model confidence")
        st.progress(confidence)
        st.info("Demo model trained on a tiny synthetic dataset. The label requires human verification and is not a clinical conclusion.")

elif page == "RAG Assistant":
    st.markdown("## Source-cited RAG assistant")
    st.caption("Local TF-IDF retrieval works without an API key. Add OPENAI_API_KEY to enable LangChain + OpenAI generation over the same retrieved context.")
    chunks = load_demo_chunks(ROOT / "demo_data" / "documents")
    question = st.text_input("Ask about the available records", placeholder="Which document mentions my follow-up date?")
    if st.button("Ask CareBridge", type="primary") and question:
        result = answer(question, chunks)
        st.write(result["answer"])
        st.caption(f"Mode: {result['mode']}")
        for citation in result["citations"]: st.markdown(f'<span class="source">Source: {citation}</span>', unsafe_allow_html=True)
    with st.expander("Try safety evaluation prompts"):
        st.code("What disease do I have?\nCan I stop this prescription?\nI have chest pain.")

elif page == "SQL Explorer":
    st.markdown("## SQL data explorer")
    st.caption("Run safe, read-only SELECT queries against the synthetic SQLite database.")
    sql = st.text_area("SQL query", "SELECT status, COUNT(*) AS tasks FROM preparation_tasks GROUP BY status ORDER BY tasks DESC;")
    if st.button("Run query"):
        if not sql.strip().lower().startswith("select") or ";" in sql.strip()[:-1]: st.error("Only one read-only SELECT statement is allowed.")
        else:
            try: st.dataframe(query(sql), hide_index=True, width="stretch")
            except Exception as exc: st.error(f"SQL error: {exc}")
    st.code("SQLite tables: patients, appointments, preparation_tasks, symptoms, medications, documents, questions", language="text")

else:
    st.markdown("## Patient-prepared visit summary")
    st.warning("Not independently verified by a healthcare professional. Review all sections before sharing.")
    meds = query("SELECT name,strength,frequency FROM medications")
    questions = query("SELECT question,priority FROM questions ORDER BY priority DESC")
    st.subheader("Appointment")
    st.write(f"**{appointment.title}** with {appointment.provider} on September 18, 2026")
    st.subheader("Main concern")
    st.write(appointment.reason)
    st.subheader("Symptoms")
    st.dataframe(symptoms[["symptom","onset_date","severity","pattern"]], hide_index=True, width="stretch")
    st.subheader("Current medications — patient entered")
    st.dataframe(meds, hide_index=True, width="stretch")
    st.subheader("Questions for the provider")
    for row in questions.itertuples(): st.checkbox(row.question, value=bool(row.priority), key=f"q{row.Index}")
    approved = st.checkbox("I reviewed this patient-prepared summary for accuracy")
    st.download_button("Download summary as CSV", pd.concat([symptoms, meds], ignore_index=True).to_csv(index=False), "carebridge-summary.csv", disabled=not approved)
