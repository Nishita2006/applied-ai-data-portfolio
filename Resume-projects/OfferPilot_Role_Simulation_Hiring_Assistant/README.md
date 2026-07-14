# OfferPilot — Evidence-Led Hiring Intelligence

OfferPilot is an AI-assisted hiring decision-support application that helps recruiters analyze job descriptions, compare resume evidence, validate candidates through role-specific work simulations, and document structured hiring decisions.

> OfferPilot supports recruiter judgment. It does not autonomously select or reject candidates and should not use protected attributes.

## Live Demo

**Streamlit app:** https://offerpilot-hiring-assistant.streamlit.app/

## Why OfferPilot

Traditional resume screening can over-reward keyword-heavy resumes while providing limited evidence that a candidate can perform the work. OfferPilot combines multiple role-relevant signals:

- Structured job-description analysis
- Explainable resume-to-role matching
- Negative-skill sentence handling
- Candidate competency comparison
- Role-specific work simulations
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