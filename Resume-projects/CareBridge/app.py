from __future__ import annotations

import os
from html import escape
from pathlib import Path

import pandas as pd
import streamlit as st

from src.analytics import preparation_score, symptom_chart
from src.database import execute, initialize, query
from src.export import build_visit_pdf
from src.ml import classify_document_details
from src.nlp import organize_symptom
from src.rag import answer, load_record_chunks
from src.records import RECORD_TEXT

ROOT = Path(__file__).parent


def load_optional_model_secrets() -> None:
    """Use a configured model when available; keep local record search as the fallback."""
    try:
        api_key = st.secrets.get("OPENAI_API_KEY")
        model = st.secrets.get("OPENAI_MODEL")
    except Exception:
        return
    if api_key:
        os.environ["OPENAI_API_KEY"] = str(api_key)
    if model:
        os.environ["OPENAI_MODEL"] = str(model)


load_optional_model_secrets()
initialize()
st.set_page_config(page_title="CareBridge", page_icon="🌿", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
:root{--navy:#14384a;--teal:#277b73;--mint:#e7f2ef;--cream:#f8f6f1;--ink:#18313b;--muted:#687b82;--line:#dbe4e1;--amber:#c3832f}
.stApp{background:var(--cream);color:var(--ink)}.block-container{padding:2rem 2.5rem 4rem;max-width:1180px}
[data-testid=stSidebar]{background:var(--navy)}[data-testid=stSidebar] *{color:#eef7f4}
[data-testid=stSidebar] .safe,[data-testid=stSidebar] .safe *{color:#16384a!important}
[data-testid=stSidebar] [role=radiogroup] label{padding:.42rem .55rem;border-radius:8px;margin:.08rem 0}
[data-testid=stSidebar] [role=radiogroup] label:hover{background:rgba(255,255,255,.08)}
h1,h2,h3{color:#16384a;letter-spacing:-.02em}.hero{background:linear-gradient(135deg,#173a4c,#24655f);padding:1.7rem 1.9rem;border-radius:18px;color:white;margin:.5rem 0 1.2rem;box-shadow:0 14px 35px rgba(20,56,74,.13)}
.hero h1{color:white;margin:.25rem 0;font-size:2.15rem}.hero p{color:#d4e7e3;margin:.4rem 0}.eyebrow{font-size:.7rem;letter-spacing:.14em;text-transform:uppercase;color:#7bd0c3;font-weight:700}
.welcome{font-size:.76rem;color:var(--teal);font-weight:700;letter-spacing:.1em;text-transform:uppercase}.lede{font-size:1.05rem;color:var(--muted);margin-top:-.5rem}
.soft-card{background:white;border:1px solid var(--line);padding:1rem 1.1rem;border-radius:13px;margin:.55rem 0;box-shadow:0 4px 18px rgba(24,49,59,.04)}
.attention{background:#fff2d9;border-left:4px solid var(--amber);padding:.85rem 1rem;border-radius:7px;font-size:.9rem}.safe{background:#e8f3f0;border-left:4px solid var(--teal);padding:.85rem 1rem;border-radius:7px;font-size:.9rem}
.source{display:inline-block;background:#e5f1ee;color:#256a62;padding:.2rem .48rem;border-radius:5px;font-size:.72rem;margin:.15rem .25rem .15rem 0}
.record-page{background:#fff;border:1px solid #d5dfdc;border-radius:10px;padding:1.35rem 1.5rem;margin:.7rem 0;box-shadow:0 8px 24px rgba(24,49,59,.06);white-space:pre-wrap;line-height:1.65;color:#263c45}
.step{width:30px;height:30px;border-radius:50%;background:#dcece8;color:#246c64;display:inline-grid;place-items:center;font-weight:700;margin-right:.5rem}
div[data-testid=stMetric]{background:white;border:1px solid var(--line);padding:1rem;border-radius:13px;box-shadow:0 4px 18px rgba(24,49,59,.04)}
.stButton>button,.stDownloadButton>button{border-radius:9px;font-weight:650}.stButton>button[kind=primary]{background:var(--teal);border-color:var(--teal)}
@media(max-width:700px){.block-container{padding:1.2rem}.hero{padding:1.3rem}.hero h1{font-size:1.7rem}}
</style>
""", unsafe_allow_html=True)

PAGES = ["Overview", "Visit Readiness", "Symptoms & Timeline", "Document Intelligence", "Records Assistant", "Visit Brief"]
with st.sidebar:
    st.markdown("## 🌿 CareBridge")
    st.caption("Arrive prepared. Leave with clarity.")
    st.markdown("---")
    page = st.radio("Your workspace", PAGES, label_visibility="collapsed", key="nav")
    st.markdown("---")
    st.markdown("**Maya Thompson**")
    st.caption("Cardiology visit workspace")
    st.markdown('<div class="safe"><b>Preparation support only</b><br>CareBridge does not diagnose or recommend treatment.</div>', unsafe_allow_html=True)
    st.caption("Fictional patient information is used in this public workspace.")

tasks = query("SELECT * FROM preparation_tasks WHERE appointment_id = 1")
symptoms = query("SELECT * FROM symptoms WHERE appointment_id = 1")
appointment = query("SELECT * FROM appointments WHERE id = 1").iloc[0]
medications = query("SELECT name,strength,frequency,status FROM medications WHERE patient_id = 1")
documents = query("SELECT title,category,organization,citation FROM documents WHERE appointment_id = 1")
questions = query("SELECT id,question,priority FROM questions WHERE appointment_id = 1 ORDER BY priority DESC, id")
score = preparation_score(tasks)
open_tasks = tasks.loc[tasks.status != "complete"]

if page == "Overview":
    st.markdown('<div class="welcome">Patient visit preparation</div>', unsafe_allow_html=True)
    st.markdown("# Welcome back, Maya")
    st.markdown('<p class="lede">Continue preparing for your upcoming cardiology appointment.</p>', unsafe_allow_html=True)
    st.markdown(f'''<div class="hero"><div class="eyebrow">Next appointment · September 18</div><h1>{appointment.title}</h1><p>{appointment.provider} · 10:30 AM · In person</p><b>{appointment.reason}</b></div>''', unsafe_allow_html=True)
    a,b,c,d = st.columns(4)
    a.metric("Visit preparation", f"{score}%", help="Measures completed preparation tasks only")
    b.metric("Items remaining", len(open_tasks))
    c.metric("Symptoms added", len(symptoms))
    d.metric("Questions ready", len(questions))
    left,right = st.columns([1.45,1], gap="large")
    with left:
        st.subheader("What to do next")
        for row in open_tasks.itertuples():
            label = "In progress" if row.status == "in_progress" else "Not started"
            st.markdown(f'<div class="soft-card"><b>{row.title}</b><br><small>{label} · Due {row.due_date}</small></div>', unsafe_allow_html=True)
        st.button("Continue preparation", type="primary", on_click=lambda: st.session_state.update(nav="Visit Readiness"))
    with right:
        st.subheader("Your visit at a glance")
        st.markdown(f"**Main reason**  \n{appointment.reason}")
        st.markdown("**Records ready**  \n4 documents organized")
        st.markdown("**Top priorities**  \n3 questions marked important")
        st.markdown('<div class="attention"><b>This is a preparation score.</b><br>It does not measure health, urgency, or medical safety.</div>', unsafe_allow_html=True)

elif page == "Visit Readiness":
    st.markdown('<div class="welcome">Appointment preparation</div>', unsafe_allow_html=True)
    st.markdown("# Get ready for your visit")
    st.markdown('<p class="lede">Complete what you can. You may mark an item not applicable if it does not apply to this visit.</p>', unsafe_allow_html=True)
    progress,details = st.columns([1.5,1], gap="large")
    with progress:
        st.progress(score / 100, text=f"{score}% prepared")
        edited = st.data_editor(
            tasks[["title", "status", "due_date"]], hide_index=True, width="stretch",
            disabled=["title", "due_date"],
            column_config={
                "title": st.column_config.TextColumn("Preparation item"),
                "status": st.column_config.SelectboxColumn("Status", options=["not_started", "in_progress", "complete", "not_applicable"]),
                "due_date": st.column_config.DateColumn("Due"),
            },
        )
        if st.button("Save progress", type="primary"):
            for idx,row in edited.iterrows():
                execute("UPDATE preparation_tasks SET status=? WHERE id=?", (row.status, int(tasks.iloc[idx].id)))
            st.success("Your preparation progress was saved.")
    with details:
        st.markdown("### Appointment details")
        st.markdown(f'<div class="soft-card"><b>{appointment.title}</b><br>{appointment.provider}<br><small>September 18, 2026 · 10:30 AM<br>In person</small></div>', unsafe_allow_html=True)
        st.markdown("### Before you go")
        st.markdown("- Bring a photo ID and insurance card\n- Keep your medication list current\n- Bring the questions most important to you")

elif page == "Symptoms & Timeline":
    st.markdown('<div class="welcome">Your health information</div>', unsafe_allow_html=True)
    st.markdown("# Symptoms and medications")
    st.markdown('<p class="lede">Keep the facts in your own words so you can explain what has been happening.</p>', unsafe_allow_html=True)
    symptom_tab,medicine_tab = st.tabs(["Symptoms", "Medications & allergies"])
    with symptom_tab:
        chart_col,list_col = st.columns([1,1], gap="large")
        with chart_col:
            st.markdown("### What you have tracked")
            st.pyplot(symptom_chart(symptoms), width="stretch")
            st.caption("Severity is patient-reported and does not represent a clinical assessment.")
        with list_col:
            st.markdown("### Current entries")
            for row in symptoms.itertuples():
                st.markdown(f'<div class="soft-card"><b>{row.symptom}</b> · {row.severity}/10<br><small>Started {row.onset_date} · {row.pattern}</small></div>', unsafe_allow_html=True)
        st.markdown("### Add what you noticed")
        symptom_text = st.text_area("Describe the symptom in your own words", placeholder="When did it begin? What does it feel like? What makes it better or worse?")
        if st.button("Organize my description", type="primary") and symptom_text:
            result = organize_symptom(symptom_text)
            st.markdown('<div class="safe"><b>Draft organized for review</b><br>Your original wording is preserved below.</div>', unsafe_allow_html=True)
            st.text_area("Original entry", result["original"], disabled=True)
            st.text_area("Clearer draft", result["organized"])
            st.caption("Review and edit this wording before including it in your visit packet.")
    with medicine_tab:
        st.markdown("### Current medications")
        st.dataframe(medications, hide_index=True, width="stretch", column_config={"name":"Medication","strength":"Strength","frequency":"How often","status":"Status"})
        st.markdown("### Reported allergies")
        st.markdown('<div class="soft-card"><b>Penicillin</b><br>Reported reaction: rash · Moderate</div><div class="soft-card"><b>Latex</b><br>Reported reaction: skin irritation · Mild</div>', unsafe_allow_html=True)
        st.markdown('<div class="attention">Do not start, stop, or change medication based on CareBridge. Confirm medication questions with a qualified healthcare professional.</div>', unsafe_allow_html=True)

elif page == "Document Intelligence":
    st.markdown('<div class="welcome">Document intelligence</div>', unsafe_allow_html=True)
    st.markdown("# Organize appointment records")
    st.markdown('<p class="lede">CareBridge suggests a folder for each record. You remain in control of the final category.</p>', unsafe_allow_html=True)
    for row in documents.itertuples():
        with st.expander(f"{row.title} · {row.category}"):
            st.markdown(f'<div class="soft-card"><b>{row.title}</b><br><small>{row.category} · {row.organization}</small><br><span class="source">Source: {row.citation}</span></div>', unsafe_allow_html=True)
            st.caption("Fictional document metadata for this public patient workspace.")
            record_text = RECORD_TEXT.get(row.title, "A source preview is not available for this record.")
            if st.toggle(f"View source — {row.citation}", key=f"preview-{row.Index}"):
                st.markdown(f'<div class="record-page">{escape(record_text)}</div>', unsafe_allow_html=True)
                st.download_button(
                    "Download record",
                    record_text,
                    file_name=f"{row.title.lower().replace(' ', '-')}.txt",
                    mime="text/plain",
                    key=f"download-record-{row.Index}",
                )
    st.markdown("### Add a record")
    st.button("Use example record", on_click=lambda: st.session_state.update(document_text="Laboratory blood results. Specimen collected August 21. Values include reference ranges and a follow-up instruction."))
    uploaded = st.file_uploader("Choose a text record", type=["txt"], help="This MVP reads TXT files and does not permanently save uploads.")
    pasted = st.text_area("Or paste the document text", placeholder="Paste administrative instructions or report text here...", key="document_text")
    record_text = uploaded.getvalue().decode("utf-8", errors="ignore") if uploaded else pasted
    if st.button("Review record", type="primary") and record_text:
        prediction = classify_document_details(record_text)
        col1,col2 = st.columns(2)
        col1.metric("Suggested category", prediction["category"])
        col2.metric("Model confidence", f'{prediction["confidence"]:.0%}')
        st.progress(prediction["confidence"])
        st.markdown("**Words that influenced this prediction:** " + (" · ".join(prediction["features"]) or "No strong features found"))
        st.caption("Confirm the suggested category before using it. Document organization is not a clinical interpretation.")

elif page == "Records Assistant":
    st.markdown('<div class="welcome">Source-cited record search</div>', unsafe_allow_html=True)
    st.markdown("# Ask CareBridge about your records")
    st.markdown('<p class="lede">Answers are grounded in the available documents and show the supporting evidence.</p>', unsafe_allow_html=True)
    st.info("CareBridge is using private local record search. Source search and citations remain available without an external AI service.")
    left,right = st.columns([1,1], gap="large")
    with left:
        st.markdown("### Questions for your provider")
        for row in questions.itertuples():
            st.checkbox(row.question, value=bool(row.priority), key=f"question-{row.id}", help="Checked questions are marked as priorities")
        new_question = st.text_input("Add another question", placeholder="What do you want to remember to ask?")
        if st.button("Add to my list") and new_question:
            execute("INSERT INTO questions (appointment_id,question,priority) VALUES (1,?,0)", (new_question,))
            st.success("Question added to your list.")
    with right:
        st.markdown("### Suggested questions")
        suggestion_cols = st.columns(2)
        suggestions = ["Which record mentions my follow-up date?", "What preparation instructions are available?"]
        for index,suggestion in enumerate(suggestions):
            suggestion_cols[index].button(suggestion, key=f"suggest-{index}", on_click=lambda value=suggestion: st.session_state.__setitem__("record-question", value), width="stretch")
        question = st.text_input("What would you like to find?", placeholder="Which record mentions my follow-up date?", key="record-question")
        if st.button("Find the answer", type="primary") and question:
            result = answer(question, load_record_chunks(ROOT / "sample_records"))
            st.markdown(f'<div class="soft-card">{result["answer"]}</div>', unsafe_allow_html=True)
            if result["evidence"]:
                st.markdown("#### Supporting evidence")
                for item in result["evidence"]:
                    st.markdown(f'<div class="soft-card"><b>{item["source"]}</b> · {item["section"]}<br><span class="source">Retrieval score: {item["score"]:.0%}</span><br><small>{item["excerpt"]}</small></div>', unsafe_allow_html=True)
            else:
                st.caption("No source was cited because sufficient evidence was not found.")
        st.markdown('<div class="safe"><b>What CareBridge can help with</b><br>Finding dates, instructions, prepared questions, and missing records. It cannot diagnose or recommend treatment.</div>', unsafe_allow_html=True)

else:
    st.markdown('<div class="welcome">Review and share</div>', unsafe_allow_html=True)
    st.markdown("# Your visit brief")
    st.markdown('<p class="lede">A concise summary you control. Review every section before downloading or sharing.</p>', unsafe_allow_html=True)
    st.markdown('<div class="attention"><b>Patient-prepared and not independently verified.</b><br>This packet does not replace clinic intake or professional medical review.</div>', unsafe_allow_html=True)
    st.markdown("### Appointment")
    st.markdown(f'<div class="soft-card"><b>{appointment.title}</b> with {appointment.provider}<br>September 18, 2026 at 10:30 AM · In person<br><br><b>Main reason:</b> {appointment.reason}</div>', unsafe_allow_html=True)
    st.markdown("### Symptoms")
    st.dataframe(symptoms[["symptom","onset_date","severity","pattern"]], hide_index=True, width="stretch", column_config={"symptom":"Symptom","onset_date":"Started","severity":"Severity (0–10)","pattern":"Pattern"})
    st.markdown("### Current medications")
    st.dataframe(medications[["name","strength","frequency"]], hide_index=True, width="stretch", column_config={"name":"Medication","strength":"Strength","frequency":"How often"})
    st.markdown("### Priority questions")
    for row in questions.loc[questions.priority == 1].itertuples():
        st.markdown(f"- {row.question}")
    approved = st.checkbox("I reviewed this brief and confirm it reflects the information I entered")
    pdf = build_visit_pdf(appointment, symptoms, medications, questions)
    csv_data = pd.concat([symptoms.assign(section="symptoms"), medications.assign(section="medications")], ignore_index=True).to_csv(index=False)
    download_a,download_b = st.columns(2)
    download_a.download_button("Download visit brief (PDF)", pdf, "carebridge-visit-brief.pdf", mime="application/pdf", disabled=not approved, type="primary", width="stretch")
    download_b.download_button("Download summary data (CSV)", csv_data, "carebridge-summary-data.csv", mime="text/csv", disabled=not approved, width="stretch")
