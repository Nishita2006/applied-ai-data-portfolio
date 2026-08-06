# OfferPilot — Evidence-Led Hiring Intelligence

OfferPilot is an AI-assisted hiring decision-support application that helps recruiters analyze job descriptions, compare resume evidence, validate candidates through role-specific work simulations, and document structured hiring decisions.

The current workflow also includes a contextual ATS evidence report and a consent-based interview evidence workspace. Interview analysis is limited to objective answer content and never attempts to infer deception, emotion, personality, or AI use.

OfferPilot now includes a persistent SQLite platform layer, optional enforced workspace authentication, secure candidate portal links, audit history, ATS benchmark runs, interview scheduling, calendar downloads, and SMTP email delivery.

## Platform configuration

Recruiter authentication is enabled by default. To explicitly disable it for an isolated local demo, add:

```toml
ENABLE_AUTH = false
```

On the first authenticated launch, OfferPilot asks you to create the initial administrator. Administrators can add recruiter and hiring-manager accounts from **8 · Platform Operations**.

Jobs, candidates, ATS snapshots, decisions, portal tokens, requests, interviews, communications, audit events, and benchmark runs are stored in `data/applications.db`. Saved workspaces can be reopened from **Platform Operations → Records**.

Candidate portal links are generated under **Platform Operations → Candidate portal**. Append the generated query string to the deployed app URL. Candidates can view milestones and submit contact, accommodation, withdrawal, or deletion requests without seeing internal scores or notes.

To enable scheduling email delivery, configure:

```toml
SMTP_HOST = "smtp.example.com"
SMTP_PORT = 587
SMTP_USERNAME = "your-smtp-user"
SMTP_PASSWORD = "your-smtp-password"
SMTP_FROM_EMAIL = "recruiting@example.com"
SMTP_SSL = false
```

Scheduling works without SMTP and always provides a downloadable `.ics` calendar invitation.

The ATS evaluation page accepts CSV files with `expected_label`, `predicted_score`, and optional `audit_group` columns. It reports precision, recall, error rates, and aggregate selection rates. Group labels must come from an approved audit dataset and must never be inferred from resumes.

> OfferPilot supports recruiter judgment. It does not autonomously select or reject candidates and should not use protected attributes.

## Live Demo

**Streamlit app:** https://offerpilot-hiring-assistant.streamlit.app/

## Why OfferPilot

Traditional resume screening can over-reward keyword-heavy resumes while providing limited evidence that a candidate can perform the work. OfferPilot combines multiple role-relevant signals:

- Structured job-description analysis
- Explainable resume-to-role matching
- Exact, synonym, related-wording, and negation-aware ATS evidence
- Negative-skill sentence handling
- Candidate competency comparison
- Role-specific work simulations
- Consented audio capture/upload, editable transcription, and structured follow-ups
- Public GitHub evidence and candidate-provided LinkedIn claim verification
- Candidate-facing milestone progress and opt-in SMS status updates
- Structured rubric scoring
- Recruiter-ready signal cards
- Human decision and notes tracking
- Exportable candidate review results

## HR Demo Mode

The application includes a one-click demo workflow with:

- One sample software-engineering internship
- Three sample candidate profiles
- Strong, developing, and limited-fit examples
- Completed simulation responses
- Candidate signal cards
- Recruiter decisions and evidence-based notes

Use **Load complete HR demo** in the sidebar to present the complete workflow without uploading files.

## Core Workflow

The recruiter workspace also includes multi-role switching, returning-applicant alerts,
application and audit history, a guided workflow, profile-specific technical and scenario
questions, and an LLM-backed conversational assistant. The assistant is available only when
`GROQ_API_KEY` is configured and does not use scripted responses.

### 1. Role Intelligence

OfferPilot converts an unstructured job description into an assessment blueprint containing:

- Role title and category
- Seniority level
- Required competencies
- Preferred competencies
- Human or workplace competencies
- Responsibilities
- Ideal-candidate summary

### 2. Candidate Screening

Recruiters can upload multiple text-based PDF resumes or use the sample candidate set.

The resume-match score combines:

- **70%** technical or role-specific competency match
- **20%** resume-to-job text similarity
- **10%** human competency match

The interface shows matched evidence, missing evidence, review priority, candidate ranking, and a configurable shortlist review threshold.

Each contextual ATS requirement is labeled as matched, partial, or missing evidence and includes the detected term, confidence, and supporting resume passage. Synonyms are accepted through an auditable local alias map; close lexical variants receive only conservative partial credit.

## Interview evidence workflow

After screening, recruiters can select a candidate in **Interview Evidence**, confirm recording consent, record or upload interview audio, and transcribe it with Groq Whisper when an API key is configured. A transcript can always be pasted and edited manually.

The review identifies concrete examples, ownership language, measurable outcomes, role topics, and vague claims that need follow-up. These are review aids—not honesty, personality, cheating, or candidate-quality scores. Transcripts remain in Streamlit session state in this prototype and can be deleted from the workspace; production deployments must add organization-approved storage, access, retention, and deletion controls.

## Public profile verification

The **Skill Verification** stage detects GitHub and LinkedIn profile URLs when they are readable in resume text. Recruiters can correct or enter a URL when a PDF stores it only as a hidden hyperlink. OfferPilot retrieves public GitHub account and repository metadata and compares project technologies and topics with the resume.

Profile URLs stored as PDF hyperlink annotations are included during resume extraction. When a GitHub URL is present, the public GitHub comparison runs automatically after screening.

LinkedIn is not scraped automatically. Recruiters can use candidate-provided profile text or an export of the relevant Experience, Projects, and Skills sections. Profile overlap is supporting evidence only: it cannot prove authorship or ownership, and missing or private public evidence must not be treated as proof that a resume claim is false.

## Candidate milestone updates

The **Candidate Updates** stage presents a seven-step candidate-facing timeline from application receipt through decision sharing. Recruiters can update a milestone without sending a message or preview and manually send an SMS after recording candidate opt-in. Phone numbers must use E.164 format, and SMS delivery history is kept in the current Streamlit session.

To enable Twilio SMS delivery, add these values to `.streamlit/secrets.toml`:

```toml
TWILIO_ACCOUNT_SID = "AC..."
TWILIO_AUTH_TOKEN = "..."
TWILIO_FROM_NUMBER = "+15551234567"
```

Phone numbers are extracted from resume text. International numbers are normalized automatically; national numbers require an explicitly configured default country code, for example:

```toml
DEFAULT_PHONE_COUNTRY_CODE = "+1"
APPLICATION_SMS_CONSENT_CAPTURED = true
```

Set `APPLICATION_SMS_CONSENT_CAPTURED` only when the application form records status-message consent and that record is transferred with every imported application. Candidates then initialize as opted in, the UI records **Application form** as the consent source, and automatic decision updates are enabled by default. Production deployments must implement the organization's consent records, opt-out handling, retention controls, messaging compliance, and access restrictions.

### 3. Evidence Comparison

A competency matrix compares candidates side by side and makes the detected evidence visible to the recruiter.

A missing match means that evidence was not detected in the supplied resume. It does not prove the candidate lacks that competency.

### 4. Work Simulation

OfferPilot generates a role-specific practical scenario designed to evaluate reasoning, technical judgment, communication, assumptions, and tradeoffs.

### 5. Candidate Signal Card

Resume evidence and simulation performance are combined into a structured signal card containing:

- Final confidence
- Combined evidence score
- Recommended next step
- Recruiter summary
- Strengths
- Risks
- Interview focus areas

The combined evidence score uses:

- **60%** resume-match score
- **40%** simulation score

### 6. Recruiter Decision Record

Recruiters can save:

- Move Forward, Needs More Review, Hold, or Reject
- Evidence-based notes
- Structured interview questions
- Candidate review results as CSV

## Responsible-AI Design

OfferPilot is designed as a human-in-the-loop decision-support tool.

The intended safeguards include:

- No autonomous employment decisions
- No protected-attribute scoring
- Explainable matched and missing evidence
- Clear distinction between absent evidence and absent ability
- Human review before every final decision
- Structured validation through work simulations
- Documented recruiter reasoning

## Technology

- Python
- Streamlit
- pandas
- pypdf
- scikit-learn
- TF-IDF and cosine similarity
- Groq API
- Llama-based job analysis, simulation generation, scoring, and summaries
- Deterministic fallback logic when the API is unavailable

## Project Structure

```text
OfferPilot_Role_Simulation_Hiring_Assistant/
├── app.py
├── README.md
├── requirements.txt
├── .gitignore
└── src/
    ├── job_parser.py
    ├── llm_client.py
    ├── llm_jd_analyzer.py
    ├── llm_rubric_scorer.py
    ├── llm_signal_card.py
    ├── llm_simulation_generator.py
    ├── resume_reader.py
    ├── rubric_scorer.py
    ├── semantic_matcher.py
    ├── signal_card.py
    └── simulation_generator.py
```

The current `src` directory remains compatible with the redesigned application.

## Local Setup

From the OfferPilot directory:

```bash
python -m venv .venv
```

Activate the virtual environment.

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

macOS or Linux:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the application:

```bash
streamlit run app.py
```

From the root portfolio repository:

```bash
streamlit run "Resume-projects/OfferPilot_Role_Simulation_Hiring_Assistant/app.py"
```

## Groq Configuration

Create this local file:

```text
.streamlit/secrets.toml
```

Add:

```toml
GROQ_API_KEY = "your_groq_api_key"
```

Do not commit this file.

For Streamlit Community Cloud, add the same key under:

```text
App settings → Secrets
```

The application remains usable in fallback mode when the key is unavailable.

## Limitations

- PDF extraction works best with text-based resumes.
- Scanned PDFs may require OCR.
- Rule-based skill extraction may miss uncommon synonyms.
- LLM output can vary between runs.
- The current MVP does not provide authentication or persistent database storage.
- Production hiring use would require formal fairness testing, governance, security controls, accessibility review, and legal validation.

## Resume Bullet

Built OfferPilot, an explainable AI-assisted hiring workflow that analyzes job descriptions, ranks resumes using hybrid competency and TF-IDF matching, generates role-specific simulations, evaluates responses with structured rubrics, and produces recruiter-ready signal cards with human decision tracking.

## Author

**Nishita Reddy Yaduguri**  
Computer Science and Data Science, University of Wisconsin–Madison
