from __future__ import annotations
import json, logging, os
from datetime import date, time
from html import escape
from urllib.parse import urlsplit, urlunsplit
import streamlit as st
from src.auth import AuthUser, SupabaseAuth, clear_user_session
from src.config import load_config
from src.database import DB_PATH, initialize
from src.documents import DocumentError, extract_text
from src.export import build_visit_pdf
from src.ml import classify_document_details
from src.rag import Chunk, answer
from src.routing import AUTHENTICATED_NO_VISITS, AUTHENTICATED_WITH_VISIT, PUBLIC, resolve_app_state
from src.store import LocalStore, SupabaseStore, friendly_data_error
from ui.auth import auth_screen
from ui.components import bento_features, empty_state, final_cta, hero_copy, marketing_nav, page_header, product_preview, progress_card, records_story, responsible_ai, section_header, summary_card, topbar, wordmark, workflow_story
from ui.styles import apply_styles

try:
    for key in ("GROQ_API_KEY","GROQ_MODEL"):
        if st.secrets.get(key): os.environ[key]=str(st.secrets[key])
except Exception: pass
st.set_page_config(page_title="CareBridge",page_icon="CB",layout="wide",initial_sidebar_state="expanded")
apply_styles()
logger=logging.getLogger("carebridge")
WORKING_TIMES=[time(hour,minute) for hour in range(8,19) for minute in (0,30) if not (hour==18 and minute==30)]

class SafeStore:
    def __init__(self,wrapped): self.wrapped=wrapped
    def __getattr__(self,name):
        value=getattr(self.wrapped,name)
        if not callable(value): return value
        def guarded(*args,**kwargs):
            try: return value(*args,**kwargs)
            except Exception as exc:
                logger.exception("Store operation failed: %s",name)
                st.error(friendly_data_error(exc)); st.stop()
        return guarded

def appointment_time_input(container,key: str):
    return container.selectbox("Appointment time *",WORKING_TIMES,index=2,key=key,format_func=lambda value:value.strftime("%I:%M %p"))

def table(name: str):
    return store.list_items(name,st.session_state.active_visit_id)
def refresh(): st.rerun()
@st.dialog("Create another visit")
def create_visit_dialog() -> None:
    with st.form("additional-visit"):
        a,b=st.columns(2); appt_date=a.date_input("Appointment date *",min_value=date.today()); appt_time=appointment_time_input(b,"additional_visit_time")
        provider=st.text_input("Provider or clinic *",max_chars=120); specialty=st.text_input("Appointment type or specialty *",max_chars=120); reason=st.text_area("Main reason for visit *",max_chars=1000); location=st.text_input("Location (optional)"); notes=st.text_area("Preparation notes (optional)"); submitted=st.form_submit_button("Create Visit",type="primary",width="stretch")
    if submitted:
        if not all(value.strip() for value in (provider,specialty,reason)): st.error("Complete all required fields.")
        else:
            try:
                new_id=store.create_visit({"appointment_date":str(appt_date),"appointment_time":appt_time.strftime("%H:%M"),"provider":provider.strip(),"specialty":specialty.strip(),"reason":reason.strip(),"location":location.strip(),"notes":notes.strip()})
                st.session_state.active_visit_id=str(new_id); st.session_state.nav_target="Overview"; st.session_state.creating_visit=False; st.toast("Visit created · Overview opened"); refresh()
            except Exception as exc: st.error(friendly_data_error(exc))
def move_question(items: list[dict],index: int,direction: int) -> None:
    target=index+direction
    if target<0 or target>=len(items): return
    current,other=items[index],items[target]
    current_position,other_position=current["position"],other["position"]
    if current_position==other_position: current_position,other_position=index,target
    store.update("questions",current["id"],{"position":other_position})
    store.update("questions",other["id"],{"position":current_position})
    refresh()

config=load_config(st.secrets)
current_user=st.session_state.get("auth_user")
auth=None
if config.local_mode:
    initialize(); store=SafeStore(LocalStore(DB_PATH)); current_user=AuthUser("local","local@carebridge")
elif config.supabase_ready:
    if "supabase_client" not in st.session_state:
        from supabase import create_client
        st.session_state.supabase_client=create_client(config.supabase_url,config.supabase_anon_key)
    auth=SupabaseAuth(st.session_state.supabase_client)
    recovery_token=st.query_params.get("token_hash") if st.query_params.get("type")=="recovery" else None
    if not current_user and recovery_token:
        try:
            auth.verify_recovery(recovery_token); st.session_state.auth_mode="reset"; st.query_params.clear(); refresh()
        except Exception as exc:
            st.session_state.auth_error=str(exc); st.session_state.auth_mode="forgot"; st.query_params.clear(); refresh()
    if not current_user and (st.query_params.get("start")=="1" or st.query_params.get("auth") or st.session_state.get("auth_mode")):
        mode=st.query_params.get("auth") or st.session_state.get("auth_mode","signup")
        parts=urlsplit(str(st.context.url)); app_url=urlunsplit((parts.scheme,parts.netloc,parts.path,"",""))
        if st.session_state.pop("auth_error",None): st.error("That password-reset link is invalid or expired. Request a new one.")
        result=auth_screen(auth,mode,app_url)
        if result:
            kind,value=result
            if kind=="mode": st.session_state.auth_mode=value; st.query_params.clear(); refresh()
            else: st.session_state.auth_user=value; st.session_state.auth_mode="signin"; st.query_params.clear(); refresh()
        st.stop()
    if current_user: store=SafeStore(SupabaseStore(st.session_state.supabase_client,current_user.id))
else:
    auth=None

if not current_user:
    visits=[]
else:
    try: visits=store.list_visits()
    except Exception as exc:
        st.error(friendly_data_error(exc))
        st.info("Setup path: Supabase Dashboard → SQL Editor → New query → paste the complete sql/supabase_schema.sql file → Run.")
        if st.button("Sign Out",width="stretch"):
            if auth: auth.sign_out()
            clear_user_session(st.session_state)
            st.query_params.clear(); refresh()
        st.stop()

app_state=resolve_app_state(current_user,visits)

if current_user and visits:
    valid_ids={str(v["id"]) for v in visits}
    candidate=str(st.session_state.get("active_visit_id") or store.get_active_visit() or "")
    st.session_state.active_visit_id=candidate if candidate in valid_ids else str(visits[0]["id"])
    if candidate not in valid_ids: store.set_active_visit(st.session_state.active_visit_id)

if app_state!=AUTHENTICATED_WITH_VISIT:
    step=st.session_state.get("onboarding_step",-1 if app_state==AUTHENTICATED_NO_VISITS else 0)
    if step==0:
        marketing_nav()
        if (st.query_params.get("start")=="1" or st.query_params.get("auth")) and not config.supabase_ready:
            st.error("Account setup requires SUPABASE_URL and SUPABASE_ANON_KEY. Add them to Streamlit secrets, then restart CareBridge.")
            st.query_params.clear()
        hero_left,hero_right=st.columns([1.02,.98],gap="large")
        with hero_left: hero_copy()
        with hero_right: product_preview()
        bento_features(); records_story(); workflow_story(); responsible_ai(); final_cta()
    elif step==-1:
        wordmark(); page_header("Your workspace","Prepare for your first visit","No visits exist in your account yet. Create one to open the private preparation workspace.")
        empty_state("V","No visits yet","Create your first visit using appointment information you enter.")
        if st.button("Create Visit",type="primary"): st.session_state.onboarding_step=1; refresh()
    elif step==1:
        wordmark()
        st.markdown('<div class="cb-form-shell"><div class="cb-step">Step 1 of 2</div><div class="cb-step-track"><div class="cb-step-fill" style="width:50%"></div></div><h1>Tell us about your upcoming visit</h1><p class="cb-lede">Start with the essentials. You can organize everything else inside the workspace.</p></div>',unsafe_allow_html=True)
        with st.form("visit-step-one"):
            a,b=st.columns(2); appt_date=a.date_input("Appointment date *",min_value=date.today()); appt_time=appointment_time_input(b,"first_visit_time")
            provider=st.text_input("Provider or clinic *",max_chars=120); specialty=st.text_input("Appointment type or specialty *",max_chars=120); reason=st.text_area("Main reason for visit *",max_chars=1000)
            back,forward=st.columns(2); back_clicked=back.form_submit_button("Back",width="stretch"); submitted=forward.form_submit_button("Continue",type="primary",width="stretch")
        if back_clicked: st.session_state.onboarding_step=-1 if app_state==AUTHENTICATED_NO_VISITS else 0; refresh()
        if submitted:
            if not all(x.strip() for x in (provider,specialty,reason)): st.error("Complete all required fields before continuing.")
            else: st.session_state.visit_draft={"appointment_date":str(appt_date),"appointment_time":appt_time.strftime("%H:%M"),"provider":provider.strip(),"specialty":specialty.strip(),"reason":reason.strip()}; st.session_state.onboarding_step=2; refresh()
    else:
        wordmark()
        st.markdown('<div class="cb-form-shell"><div class="cb-step">Step 2 of 2</div><div class="cb-step-track"><div class="cb-step-fill" style="width:100%"></div></div><h1>Add the finishing details</h1><p class="cb-lede">Both fields are optional.</p></div>',unsafe_allow_html=True)
        with st.form("visit-step-two"):
            location=st.text_input("Location (optional)"); notes=st.text_area("Preparation notes (optional)"); back,finish=st.columns(2); back_clicked=back.form_submit_button("Back",width="stretch"); submitted=finish.form_submit_button("Create Visit Workspace",type="primary",width="stretch")
        if back_clicked: st.session_state.onboarding_step=1; refresh()
        if submitted:
            draft={**st.session_state.visit_draft,"location":location.strip(),"notes":notes.strip()}
            try:
                new_id=store.create_visit(draft); st.session_state.active_visit_id=str(new_id); st.session_state.nav="Overview"; st.session_state.onboarding_step=-1; st.toast("Visit created · Your workspace is ready"); refresh()
            except Exception as exc: st.error(friendly_data_error(exc))
    st.stop()

if st.session_state.pop("nav_target",None): st.session_state.nav="Overview"
with st.sidebar:
    wordmark()
    selected=st.selectbox("Active visit",visits,index=next((i for i,v in enumerate(visits) if str(v["id"])==str(st.session_state.active_visit_id)),0),format_func=lambda v:f"{v['appointment_date']} · {v['provider']}")
    if str(selected["id"])!=str(st.session_state.active_visit_id): st.session_state.active_visit_id=str(selected["id"]); store.set_active_visit(str(selected["id"])); refresh()
    if st.button("Create another visit",width="stretch"): st.session_state.creating_visit=True
    page=st.radio("Workspace",["Overview","Visit Readiness","Symptoms","Medications","Records","Records Assistant","Questions","Visit Brief"],label_visibility="collapsed",key="nav")
    st.markdown("---"); st.caption("Privacy"); st.caption("About CareBridge")
    if not config.local_mode:
        st.caption(current_user.email)
        if st.button("Sign Out",width="stretch"):
            auth.sign_out();
            clear_user_session(st.session_state)
            st.query_params.clear(); refresh()
    st.markdown('<div class="cb-privacy">Preparation and communication support only. CareBridge does not diagnose or recommend treatment.</div>',unsafe_allow_html=True)

if st.session_state.get("creating_visit"): create_visit_dialog()
visit=store.get_visit(st.session_state.active_visit_id); tasks=table("preparation_tasks")
score=round(100*sum(t["completed"] for t in tasks)/len(tasks)) if tasks else 0
topbar(visit,score)

if page=="Overview":
    page_header("Workspace overview","Your upcoming visit","Everything you have prepared, organized around this appointment.")
    st.markdown(f'<div class="cb-card"><span class="cb-pill">Upcoming</span><div class="cb-card-value">{escape(visit["specialty"])}</div><div class="cb-card-copy">{escape(visit["appointment_date"])} at {escape(visit["appointment_time"])} · {escape(visit["provider"])}</div><p>{escape(visit["reason"])}</p></div>',unsafe_allow_html=True)
    symptoms,meds,docs,questions=map(table,("symptoms","medications","documents","questions")); complete=sum(t["completed"] for t in tasks)
    st.markdown("<br>",unsafe_allow_html=True); progress_card(score,complete,len(tasks)); section_header("Your visit at a glance","Each area reflects information you have actually saved.")
    cols=st.columns(4)
    for col,label,data,zero in zip(cols,["Symptoms","Medications","Records","Questions"],[symptoms,meds,docs,questions],["None added","None recorded","None uploaded","None prepared"]):
        with col: summary_card(label,len(data),zero)
    pending=[t["title"] for t in tasks if not t["completed"]]; section_header("Continue preparing","Your next step is based on the readiness checklist.")
    if pending: st.markdown(f'<div class="cb-card"><span class="cb-pill pending">Next best action</span><div class="cb-card-value" style="font-size:1.3rem">{escape(pending[0])}</div><div class="cb-card-copy">Open Visit Readiness to complete this item or add a note.</div></div>',unsafe_allow_html=True)
    else: st.success("All preparation checklist items are complete.",icon="✓")

elif page=="Visit Readiness":
    page_header("Preparation checklist","Visit Readiness","Mark items complete or reopen them. Notes and progress are saved to this visit."); progress_card(score,sum(t["completed"] for t in tasks),len(tasks))
    groups={"Appointment":tasks[:1],"Health information":tasks[3:6],"Records":tasks[1:3]+tasks[6:7],"Visit planning":tasks[7:]}
    for group,items in groups.items():
        section_header(group)
        for task in items:
            with st.container(border=True):
                c1,c2=st.columns([1.1,1]); done=c1.checkbox(task["title"],value=bool(task["completed"]),key=f"t{task['id']}"); notes=c2.text_input("Optional note",task["notes"],key=f"tn{task['id']}",placeholder="Add a note")
                if done!=bool(task["completed"]) or notes!=task["notes"]: store.update("preparation_tasks",task["id"],{"completed":bool(done),"notes":notes})

elif page=="Symptoms":
    page_header("Health information","Symptoms & Timeline","Document what you want to remember to discuss with your provider. Your wording is preserved."); symptoms=table("symptoms")
    if not symptoms: empty_state("S","No symptoms added yet","Add symptoms you want to remember to discuss during your appointment.")
    for x in symptoms:
        severity=f'{x["severity"]} / 10' if x.get("severity") is not None else "Not entered"
        st.markdown(f'<div class="cb-card"><div class="cb-card-title">{escape(x["name"])}</div><div class="cb-card-copy">Started: {escape(x.get("onset") or "Not entered")} · Patient-reported severity: {severity} · Frequency: {escape(x.get("frequency") or "Not entered")}</div></div>',unsafe_allow_html=True)
        with st.expander("Edit symptom details"):
            edit_name=st.text_input("Symptom",x["name"],key=f"sn{x['id']}"); edit_onset=st.text_input("Onset",x.get("onset") or "",key=f"so{x['id']}"); edit_description=st.text_area("Description in your own words",x.get("description") or "",key=f"sd{x['id']}"); c1,c2=st.columns(2)
            if c1.button("Save changes",key=f"ss{x['id']}") and edit_name.strip(): store.update("symptoms",x["id"],{"name":edit_name.strip(),"onset":edit_onset.strip(),"description":edit_description}); refresh()
            if c2.button("Delete symptom",key=f"ds{x['id']}"): store.delete("symptoms",x["id"]); refresh()
    section_header("Add a symptom","Start with the essentials; additional detail is optional.")
    with st.form("symptom"):
        a,b=st.columns(2); name=a.text_input("Symptom or short description *"); onset=b.text_input("Onset date or approximate onset"); severity=st.slider("Patient-reported severity (optional)",0,10,value=None)
        with st.expander("Add more details"): frequency=st.text_input("Frequency"); pattern=st.text_input("Pattern"); triggers=st.text_input("Triggers you noticed"); relief=st.text_input("Relieving factors you noticed"); description=st.text_area("Description in your own words")
        submitted=st.form_submit_button("Add symptom",type="primary")
    if submitted:
        if not name.strip(): st.error("Enter a symptom description.")
        else: store.insert("symptoms",{"visit_id":visit["id"],"name":name.strip(),"onset":onset.strip(),"severity":severity,"frequency":frequency.strip(),"pattern":pattern.strip(),"triggers":triggers.strip(),"relief":relief.strip(),"description":description}); st.toast("Symptom saved"); refresh()

elif page=="Medications":
    page_header("Health information","Medications & Allergies","Keep an accurate list in your own words. CareBridge does not recommend medication or dosage changes.")
    a,b=st.columns(2,gap="large")
    with a:
        section_header("Medications"); meds=table("medications")
        if not meds: empty_state("M","No medications recorded","Add medication information you want available for the visit.")
        for x in meds:
            st.markdown(f'<div class="cb-card"><div class="cb-card-title">{escape(x["name"])}</div><div class="cb-card-copy">{escape(x.get("dose") or "Dose not entered")} · {escape(x.get("frequency") or "Frequency not entered")}</div></div>',unsafe_allow_html=True)
            with st.expander("Edit medication"):
                ename=st.text_input("Medication name",x["name"],key=f"emn{x['id']}"); edose=st.text_input("Dose",x.get("dose") or "",key=f"emd{x['id']}"); efreq=st.text_input("Frequency",x.get("frequency") or "",key=f"emf{x['id']}"); c1,c2=st.columns(2)
                if c1.button("Save changes",key=f"sm{x['id']}") and ename.strip(): store.update("medications",x["id"],{"name":ename.strip(),"dose":edose,"frequency":efreq}); refresh()
                if c2.button("Delete medication",key=f"dm{x['id']}"): store.delete("medications",x["id"]); refresh()
        with st.expander("Add medication",expanded=not meds):
            with st.form("med"): name=st.text_input("Medication name *"); dose=st.text_input("Dose as entered"); freq=st.text_input("Frequency"); notes=st.text_input("Notes"); add=st.form_submit_button("Save medication",type="primary")
            if add and name.strip(): store.insert("medications",{"visit_id":visit["id"],"name":name.strip(),"dose":dose,"frequency":freq,"notes":notes}); st.toast("Medication saved"); refresh()
    with b:
        section_header("Reported Allergies"); allergies=table("allergies")
        if not allergies: empty_state("A","No allergies recorded","Add allergies and reported reactions as you understand them.")
        for x in allergies:
            st.markdown(f'<div class="cb-card"><div class="cb-card-title">{escape(x["allergy"])}</div><div class="cb-card-copy">Reported reaction: {escape(x.get("reaction") or "Not entered")}</div></div>',unsafe_allow_html=True)
            with st.expander("Edit allergy"):
                eallergy=st.text_input("Allergy",x["allergy"],key=f"ean{x['id']}"); ereaction=st.text_input("Reported reaction",x.get("reaction") or "",key=f"ear{x['id']}"); c1,c2=st.columns(2)
                if c1.button("Save changes",key=f"sa{x['id']}") and eallergy.strip(): store.update("allergies",x["id"],{"allergy":eallergy.strip(),"reaction":ereaction}); refresh()
                if c2.button("Delete allergy",key=f"da{x['id']}"): store.delete("allergies",x["id"]); refresh()
        with st.expander("Add allergy",expanded=not allergies):
            with st.form("allergy"): allergy=st.text_input("Allergy *"); reaction=st.text_input("Reported reaction"); anotes=st.text_input("Notes"); adda=st.form_submit_button("Save allergy",type="primary")
            if adda and allergy.strip(): store.insert("allergies",{"visit_id":visit["id"],"allergy":allergy.strip(),"reaction":reaction,"notes":anotes}); st.toast("Allergy saved"); refresh()

elif page=="Records":
    page_header("Document workspace","Your Records","Upload and organize the records you want available while preparing for your visit."); docs=table("documents")
    st.markdown('<div class="cb-empty"><div class="cb-empty-icon">PDF</div><div class="cb-empty-title">Drop records here or browse files</div><div class="cb-empty-copy">PDF and TXT supported · maximum 10 MB · selectable text required</div></div>',unsafe_allow_html=True)
    tab1,tab2=st.tabs(["Upload a file","Add text manually"])
    with tab1: uploaded=st.file_uploader("Choose a PDF or TXT record",type=["txt","pdf"],label_visibility="collapsed"); upload_title=st.text_input("Record title",key="ut"); save_upload=st.button("Add record",type="primary")
    with tab2: manual_title=st.text_input("Record title",key="mt"); manual_text=st.text_area("Record text"); save_manual=st.button("Add text record",type="primary")
    if save_upload and uploaded:
        try:
            with st.status("Adding record...",expanded=False) as status:
                status.update(label="Extracting readable text..."); text,mime=extract_text(uploaded.getvalue(),uploaded.name)
                status.update(label="Organizing record..."); title=upload_title.strip() or uploaded.name; pred=classify_document_details(text); store.upload_document(visit["id"],title,uploaded.name,mime,uploaded.getvalue(),text,pred); status.update(label="Record ready",state="complete")
            st.toast("Record added · Text extraction complete"); refresh()
        except DocumentError as exc: st.error(str(exc))
    if save_manual:
        if not manual_title.strip() or not manual_text.strip(): st.error("Enter both a title and record text.")
        else: pred=classify_document_details(manual_text); filename=f'{manual_title.strip()}.txt'; store.upload_document(visit["id"],manual_title.strip(),filename,"text/plain",manual_text.strip().encode(),manual_text.strip(),pred); st.toast("Record added successfully"); refresh()
    section_header("Saved records")
    if not docs: empty_state("R","No records added yet","Add records you want available while preparing for your appointment.")
    categories=["Referral","Lab result","Insurance","Visit note","Imaging","Instructions","Other"]
    for x in docs:
        status="Category confirmed" if x["category_confirmed"] else "Review category"
        st.markdown(f'<div class="cb-file"><div class="cb-file-icon">{("PDF" if x.get("mime_type")=="application/pdf" else "TXT")}</div><div class="cb-file-main"><div class="cb-file-name">{escape(x["title"])}</div><div class="cb-file-meta">{escape(x.get("category") or "Uncategorized")} · Text extracted successfully · {escape(x.get("created_at") or "")}</div></div><span class="cb-pill">{status}</span></div>',unsafe_allow_html=True)
        with st.expander("View record & document intelligence"):
            main,intel=st.columns([1.5,1],gap="large")
            with main:
                st.markdown("#### Extracted content"); st.text_area("Record content",x["extracted_text"][:10000],height=280,disabled=True,key=f"text{x['id']}")
            with intel:
                explanation=classify_document_details(x["extracted_text"])
                terms=" · ".join(explanation["features"]) or "No strong category terms"
                st.markdown("#### Document Intelligence"); renamed=st.text_input("Record title",x["title"],key=f"rn{x['id']}"); st.markdown(f'<div class="cb-card"><div class="cb-card-copy">Suggested category</div><div class="cb-card-title">{escape(x.get("suggested_category") or "Uncertain")}</div><span class="cb-pill">{x.get("confidence") or 0:.0%} classifier confidence</span><div class="cb-card-copy" style="margin-top:.7rem"><b>Influential terms</b><br>{escape(terms)}</div></div>',unsafe_allow_html=True); st.caption("This describes document routing, not medical confidence.")
                cat=st.selectbox("Confirm or change category",categories,index=categories.index(x["category"]) if x.get("category") in categories else len(categories)-1,key=f"cat{x['id']}")
                if st.button("Save document details",key=f"cc{x['id']}") and renamed.strip(): store.update("documents",x["id"],{"title":renamed.strip(),"category":cat,"category_confirmed":True}); refresh()
                if st.button("Delete record",key=f"dd{x['id']}"): store.delete("documents",x["id"]); refresh()

elif page=="Records Assistant":
    page_header("Grounded record search","Ask Your Records","Ask questions about information contained in the records you have added. Answers always show their evidence."); docs=table("documents")
    if not docs: empty_state("Q","No records available","Add at least one record before asking questions about it.")
    else:
        st.markdown('<div class="cb-card"><div class="cb-card-title">Evidence-first answers</div><div class="cb-card-copy">Local retrieval selects relevant excerpts first. Groq may compose from only those excerpts; it never receives your full database or all records.</div></div>',unsafe_allow_html=True)
        chips=st.columns(3)
        suggestions=["Where is the appointment date mentioned?","Which record contains referral information?","What medications are mentioned?"]
        for col,suggestion in zip(chips,suggestions):
            if col.button(suggestion,key=f"chip-{suggestion}",width="stretch"): st.session_state.record_question=suggestion
        question=st.text_input("Ask about your records...",key="record_question")
        if st.button("Search my records",type="primary") and question.strip():
            chunks=[Chunk(p.strip(),d["title"],f"passage {i+1}") for d in docs for i,p in enumerate(d["extracted_text"].split("\n\n")) if len(p.strip())>15]
            with st.status("Searching your records...",expanded=False) as status:
                result=answer(question,chunks); status.update(label="Evidence retrieved",state="complete")
            st.markdown(f'<div class="cb-message-user">{escape(question)}</div><br><div class="cb-message-ai"><div class="cb-kicker">CareBridge</div>{escape(result["answer"])}</div>',unsafe_allow_html=True)
            if result["evidence"]: section_header("Sources","Expand each source to inspect the retrieved evidence.")
            for e in result["evidence"]:
                level="High" if e["score"]>=.45 else "Moderate" if e["score"]>=.2 else "Low"
                with st.expander(f'{e["source"]} · Relevance: {level}'):
                    st.markdown(f'<div class="cb-evidence"><span class="cb-pill">{escape(e["section"])}</span><blockquote>{escape(e["excerpt"])}</blockquote><div class="cb-fine">Retrieval score: {e["score"]:.0%}</div></div>',unsafe_allow_html=True)

elif page=="Questions":
    page_header("Visit planning","Questions for Your Provider","Build a focused list you can bring into the appointment."); questions=table("questions")
    if not questions: empty_state("?","No questions prepared yet","Add questions you want to remember during your appointment.")
    for index,x in enumerate(questions,1):
        st.markdown(f'<div class="cb-card"><span class="cb-pill">{index}</span> '+('<span class="cb-pill pending">Priority</span>' if x["priority"] else '')+'</div>',unsafe_allow_html=True)
        c1,c2,c3,c4=st.columns([4,1,1,1]); edited_q=c1.text_input("Question",x["question"],key=f"eq{x['id']}",label_visibility="collapsed")
        if c2.button("Save",key=f"sq{x['id']}") and edited_q.strip(): store.update("questions",x["id"],{"question":edited_q.strip()}); refresh()
        if c3.button("Priority",key=f"pq{x['id']}"): store.update("questions",x["id"],{"priority":not bool(x["priority"])}); refresh()
        if c4.button("Delete",key=f"dq{x['id']}"): store.delete("questions",x["id"]); refresh()
        up,down=st.columns(2)
        up.button("Move up",key=f"uq{x['id']}",disabled=index==1,on_click=move_question,args=(questions,index-1,-1),width="stretch")
        down.button("Move down",key=f"nq{x['id']}",disabled=index==len(questions),on_click=move_question,args=(questions,index-1,1),width="stretch")
    with st.expander("Add question",expanded=not questions):
        with st.form("question"): q=st.text_input("Question *"); priority=st.checkbox("Mark as priority"); addq=st.form_submit_button("Save question",type="primary")
        if addq and q.strip(): store.insert("questions",{"visit_id":visit["id"],"question":q.strip(),"priority":bool(priority),"position":len(questions)}); st.toast("Question saved"); refresh()

else:
    page_header("Review and export","Visit Brief","Review the information you entered before creating a portable visit brief."); symptoms,meds,allergies,docs,questions=map(table,("symptoms","medications","allergies","documents","questions"))
    def items(data,key): return "".join(f'<li>{escape(str(x[key]))}</li>' for x in data) or '<li class="cb-card-copy">Nothing entered</li>'
    st.markdown(f'''<div class="cb-paper"><div class="cb-paper-brand">CareBridge · Patient-prepared visit brief</div><h1>{escape(visit["specialty"])}</h1><div class="cb-card-copy">{escape(visit["appointment_date"])} at {escape(visit["appointment_time"])} · {escape(visit["provider"])}</div><h2>Appointment</h2><p><b>Main concern</b><br>{escape(visit["reason"])}</p><h2>Symptoms</h2><ul>{items(symptoms,"name")}</ul><h2>Medications</h2><ul>{items(meds,"name")}</ul><h2>Allergies</h2><ul>{items(allergies,"allergy")}</ul><h2>Relevant records</h2><ul>{items(docs,"title")}</ul><h2>Questions for provider</h2><ul>{items(questions,"question")}</ul></div>''',unsafe_allow_html=True)
    section_header("Review confirmation"); progress_card(score,sum(t["completed"] for t in tasks),len(tasks)); approved=st.checkbox("I reviewed this brief and confirm that it reflects the information I entered.",value=bool(visit["brief_confirmed"]))
    if approved!=bool(visit["brief_confirmed"]): store.confirm_brief(visit["id"],approved)
    if approved:
        try:
            pdf=build_visit_pdf(visit,symptoms,meds,allergies,docs,questions); payload=json.dumps({"visit":visit,"symptoms":symptoms,"medications":meds,"allergies":allergies,"documents":[{k:v for k,v in d.items() if k!="extracted_text"} for d in docs],"questions":questions},indent=2); a,b=st.columns(2); a.download_button("Download Visit Brief",pdf,"carebridge-visit-brief.pdf","application/pdf",type="primary",width="stretch"); b.download_button("Download Structured Data",payload,"carebridge-visit-data.json","application/json",width="stretch")
        except Exception:
            logger.exception("Visit brief export failed"); st.error("CareBridge could not generate the visit brief. Review the saved information and try again.")
    else: st.info("Review and confirm the brief to enable downloads.")
