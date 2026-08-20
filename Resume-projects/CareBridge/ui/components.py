from __future__ import annotations
from html import escape
import streamlit as st

def wordmark() -> None:
    st.markdown('<div class="cb-wordmark"><span class="cb-mark">C</span><span class="cb-word">CareBridge</span></div>',unsafe_allow_html=True)

def page_header(kicker: str,title: str,copy: str="") -> None:
    st.markdown(f'<div class="cb-kicker">{escape(kicker)}</div><h1>{escape(title)}</h1>'+ (f'<p class="cb-lede">{escape(copy)}</p>' if copy else ""),unsafe_allow_html=True)

def topbar(visit: dict,score: int) -> None:
    st.markdown(f'<div class="cb-topbar"><div><div class="cb-topbar-title">{escape(visit["specialty"])}</div><div class="cb-topbar-meta">{escape(visit["appointment_date"])} · {escape(visit["appointment_time"])} · {escape(visit["provider"])}</div></div><div class="cb-topbar-status">{score}% prepared</div></div>',unsafe_allow_html=True)

def empty_state(symbol: str,title: str,copy: str) -> None:
    st.markdown(f'<div class="cb-empty"><div class="cb-empty-icon">{escape(symbol)}</div><div class="cb-empty-title">{escape(title)}</div><div class="cb-empty-copy">{escape(copy)}</div></div>',unsafe_allow_html=True)

def summary_card(label: str,count: int,empty_label: str) -> None:
    value=f'{count} recorded' if count else empty_label
    st.markdown(f'<div class="cb-card"><div class="cb-card-title">{escape(label)}</div><div class="cb-card-value">{escape(value)}</div><div class="cb-card-copy">Saved for this visit</div></div>',unsafe_allow_html=True)

def progress_card(score: int,complete: int,total: int) -> None:
    st.markdown(f'<div class="cb-progress"><div class="cb-progress-head"><div><div class="cb-kicker">Visit preparation</div><div class="cb-progress-value">{score}%</div></div><span class="cb-pill">{complete} of {total} complete</span></div><div class="cb-track"><div class="cb-fill" style="width:{score}%"></div></div><div class="cb-fine">Administrative preparation only — not a health, urgency, risk, or medical readiness score.</div></div>',unsafe_allow_html=True)

def section_header(title: str,copy: str="") -> None:
    st.markdown(f'<div class="cb-section"><div><h2>{escape(title)}</h2>'+ (f'<p>{escape(copy)}</p>' if copy else "")+'</div></div>',unsafe_allow_html=True)

def marketing_nav() -> None:
    st.markdown('''<nav class="mk-nav"><div class="mk-brand"><span class="cb-mark">C</span><span>CareBridge</span></div><div class="mk-links"><a href="#how-it-works">How it works</a><a href="#features">Features</a><a href="#responsible-ai">Responsible AI</a></div><div class="mk-nav-actions"><a href="?auth=signin">Sign In</a><a class="mk-nav-cta" href="?start=1">Get Started →</a></div></nav>''',unsafe_allow_html=True)

def hero_copy() -> None:
    st.markdown('''<div class="mk-hero-copy"><div class="mk-badge"><i></i> Patient visit preparation</div><h1>Walk into your next appointment prepared.</h1><p>Bring symptoms, medications, records, questions, and preparation into one calm workspace—then create a brief you have reviewed.</p><div class="mk-actions"><a class="mk-primary" href="?start=1">Get Started →</a><a class="mk-secondary" href="#how-it-works">See How It Works</a></div></div>''',unsafe_allow_html=True)

def final_cta() -> None:
    st.markdown('''<section class="final-cta"><div class="mk-eyebrow">Prepare with clarity</div><h2>Your appointment is short.<br>Your preparation does not have to be.</h2><p>Create an organized workspace using only the information you choose to add.</p><a class="mk-primary light" href="?start=1">Prepare for a Visit →</a></section>''',unsafe_allow_html=True)

def product_preview() -> None:
    st.markdown('''<div class="product-stage">
      <div class="stage-glow"></div>
      <div class="product-window">
        <div class="window-top"><div class="window-brand"><span class="mini-mark">C</span> CareBridge</div><span class="window-chip">Visit workspace</span></div>
        <div class="window-body"><div class="mini-sidebar"><span class="mini-nav active">Overview</span><span class="mini-nav">Readiness</span><span class="mini-nav">Records</span><span class="mini-nav">Ask records</span><span class="mini-nav">Visit brief</span></div>
        <div class="mini-main"><div class="mini-eyebrow">Visit preparation</div><div class="mini-title">Everything for your visit, together.</div><div class="mini-progress"><i></i></div>
          <div class="mini-grid"><div class="mini-panel"><b>Preparation</b><span><i class="status done"></i> Appointment details</span><span><i class="status open"></i> Medication review</span><span><i class="status ready"></i> Records ready</span></div><div class="mini-panel accent"><b>Ask your records</b><span class="mini-search">Search with evidence <strong>→</strong></span><small>Sources stay attached</small></div></div>
          <div class="mini-bottom"><span class="doc-icon">DOC</span><div><b>Visit brief</b><small>Review before export</small></div><span class="window-chip">You confirm</span></div>
        </div></div>
      </div><div class="float-card float-record"><span class="doc-icon">PDF</span><div><b>Records</b><small>Text ready</small></div></div><div class="float-card float-source"><span class="source-dot"></span><div><b>Evidence shown</b><small>Grounded retrieval</small></div></div>
    </div>''',unsafe_allow_html=True)

def bento_features() -> None:
    st.markdown('''<section id="features" class="mk-section"><div class="mk-eyebrow">One calm workspace</div><h2>Visit information is scattered.<br>CareBridge brings it together.</h2><div class="bento">
      <article class="bento-card bento-wide dark"><div class="feature-icon">01</div><h3>Everything in one place</h3><p>Organize the information you choose to bring into the appointment.</p><div class="capability-row"><span>Symptoms</span><span>Medications</span><span>Records</span><span>Questions</span></div></article>
      <article class="bento-card mint"><div class="feature-icon">02</div><h3>Visit preparation</h3><p>A deterministic checklist shows what is complete and what needs attention next.</p><div class="micro-check"><i></i><span>Preparation areas</span><b>Clear status</b></div><div class="micro-check"><i class="open"></i><span>Next action</span><b>Always visible</b></div></article>
      <article class="bento-card blue"><div class="feature-icon">03</div><h3>Ask your records</h3><p>Local retrieval finds relevant excerpts first and keeps citations visible.</p><div class="citation-mini"><span class="source-dot"></span><div><b>Source attached</b><small>Relevant excerpt available</small></div></div></article>
      <article class="bento-card bento-wide paper-card"><div><div class="feature-icon">04</div><h3>Take a reviewed brief with you</h3><p>Your entries become a clear visit brief only after you review and confirm them.</p></div><div class="paper-mini"><div>CAREBRIDGE</div><b>Visit brief</b><span></span><span></span><span class="short"></span><small>Patient reviewed</small></div></article>
    </div></section>''',unsafe_allow_html=True)

def records_story() -> None:
    st.markdown('''<section class="ai-story"><div class="ai-copy"><div class="mk-eyebrow">Grounded records assistant</div><h2>Ask your records,<br>not the internet.</h2><p>CareBridge retrieves from records you added and makes the supporting source a first-class part of every answer.</p><div class="ai-points"><span>Local retrieval first</span><span>Supporting excerpts shown</span><span>Clear insufficient-evidence response</span></div></div><div class="ai-demo"><div class="ask-field">Where is the appointment date mentioned?<span>⌕</span></div><div class="answer-card"><div class="answer-brand"><span class="mini-mark">C</span> CareBridge</div><p>I found the appointment information in a record you added.</p><div class="source-card"><div><span class="source-dot"></span><b>Source</b></div><strong>Uploaded record</strong><small>Relevant excerpt available · citation preserved</small></div></div></div></section>''',unsafe_allow_html=True)

def workflow_story() -> None:
    steps=[("01","Create your visit"),("02","Organize what matters"),("03","Add records and questions"),("04","Review your visit brief"),("05","Bring it with you")]
    cards="".join(f'<div class="flow-step"><span>{number}</span><b>{title}</b></div>' for number,title in steps)
    st.markdown(f'<section id="how-it-works" class="mk-section flow-section"><div class="mk-eyebrow">How it works</div><h2>From scattered details to one reviewed brief.</h2><div class="flow-grid">{cards}</div></section>',unsafe_allow_html=True)

def responsible_ai() -> None:
    principles=[("Your wording stays yours","Symptoms are stored as entered."),("Answers stay grounded","Retrieved sources remain visible."),("No clinical recommendations","No diagnosis, treatment, or medication changes."),("You review before export","The visit brief requires confirmation.")]
    cards="".join(f'<div class="principle"><span>✓</span><div><b>{title}</b><small>{copy}</small></div></div>' for title,copy in principles)
    st.markdown(f'<section id="responsible-ai" class="responsible"><div><div class="mk-eyebrow">Responsible by design</div><h2>Built around preparation,<br>not diagnosis.</h2><p>Safety is part of the product architecture, not a disclaimer added afterward.</p></div><div class="principle-grid">{cards}</div><div class="privacy-line"><b>Privacy boundary</b> · This public portfolio deployment is not certified for protected health information. Avoid entering sensitive identifying or health information.</div></section>',unsafe_allow_html=True)
