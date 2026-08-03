# CareBridge — Patient Visit Preparation Assistant

CareBridge is an AI-assisted patient visit preparation application that helps patients organize appointment requirements, symptoms, medications, records, provider questions, and a patient-reviewed visit brief in one workspace.

The application is designed as a student-built MVP. It supports preparation and communication; it does not diagnose conditions, recommend treatment, advise medication changes, or replace a healthcare professional.

## Live Application

**Streamlit app:** https://carebridge-ai.streamlit.app/

The public workspace uses a fictional patient and fictional records. No real patient information is included.

## Why CareBridge

Patients often prepare for appointments using information spread across memory, medication lists, referrals, reports, insurance documents, and patient portals. Important details can be missed during a short visit.

CareBridge brings the preparation process into one structured workflow:

- Track appointment requirements
- Record symptoms in the patient's own words
- Review medications and reported allergies
- Organize appointment records
- Prepare questions for the provider
- Find cited information in available records
- Export a concise visit brief

## Core Workflow

### 1. Appointment Overview

The overview shows the next appointment, its main purpose, preparation progress, incomplete items, symptoms entered, and questions prepared.

The **Visit Preparation** percentage measures administrative completeness only. It is not a health, urgency, or medical-safety score.

### 2. Visit Readiness

Patients can review and update preparation items such as:

- Confirming appointment details
- Adding insurance and referral information
- Reviewing medication and allergy information
- Completing symptom history
- Uploading requested records
- Confirming transportation

Progress is saved in SQLite.

### 3. Symptoms and Timeline

Patients can review symptom onset, severity, and patterns, then enter a new description in their own words.

CareBridge can organize the wording into a clearer draft while preserving the original entry. The patient must review the draft before using it.

Medication and allergy information remains visible alongside symptom preparation. CareBridge never recommends starting, stopping, or changing medication.

### 4. Document Intelligence

Patients can review existing appointment records or add text from a new record.

CareBridge suggests a document category and shows:

- Suggested category
- Confidence
- Words that influenced the suggestion
- A reminder that the category requires confirmation

The classifier organizes document types only. It does not interpret medical meaning or produce clinical conclusions.

### 5. Records Assistant

Patients can ask administrative questions about the records available in their workspace.

Answers include:

- The retrieved answer
- Source document
- Relevant excerpt
- Retrieval score
- A clear response when there is not enough evidence

The assistant works without an external model key by using local record retrieval. An optional model-backed response layer can be enabled, but it uses the same retrieved sources and safety restrictions.

### 6. Visit Brief

The visit brief combines:

- Appointment details
- Main concern
- Symptoms and timeline information
- Current medications
- Priority questions

The patient must confirm that the brief reflects their information before downloading it. The application provides a printable PDF and a CSV data export.

## Responsible-AI Design

CareBridge is designed as preparation support with a human-review boundary.

Safeguards include:

- No diagnosis or disease prediction
- No treatment recommendations
- No medication or dosage advice
- Emergency-language redirection
- Original patient wording preserved
- Sources and excerpts displayed with retrieved answers
- Insufficient-evidence responses instead of unsupported answers
- Patient confirmation before summary export
- Fictional information in the public application

## Data and Application Design

Appointments, preparation tasks, symptoms, medications, records, and questions are stored in a normalized SQLite database. Pandas and NumPy support preparation metrics and data processing. Matplotlib displays patient-entered symptom severity. A small TF-IDF and logistic-regression model suggests document categories. Local TF-IDF retrieval supplies source-cited record answers, with optional LangChain and OpenAI generation when configured.

The technical implementation remains intentionally compact so the workflow can be reviewed and run as a student MVP.

## Project Structure

```text
CareBridge/
├── app.py
├── requirements.txt
├── sql/
│   ├── schema.sql
│   └── seed.sql
├── src/
│   ├── analytics.py
│   ├── database.py
│   ├── export.py
│   ├── ml.py
│   ├── nlp.py
│   └── rag.py
├── sample_records/
├── notebooks/
│   └── carebridge_eda.ipynb
├── tests/
└── docs/
```

## Local Setup

From the CareBridge directory:

```bash
python -m venv .venv
```

Activate the environment.

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

macOS or Linux:

```bash
source .venv/bin/activate
```

Install dependencies and start the application:

```bash
pip install -r requirements.txt
streamlit run app.py
```

Run the tests:

```bash
pytest
```

## Optional Model Configuration

CareBridge remains usable without an API key. To enable the optional model-backed response layer, add these values to Streamlit secrets or environment variables:

```toml
OPENAI_API_KEY = "your-api-key"
OPENAI_MODEL = "gpt-4o-mini"
```

Do not commit secret files or API keys.

## Limitations

- The public application uses fictional patient information.
- The document classifier is trained on a small synthetic dataset.
- Classification confidence is not medical certainty.
- Local retrieval is limited to records available in the workspace.
- Text uploads are limited to TXT files in the current MVP.
- Authentication and patient-level production access controls are not implemented.
- The application is not certified to store protected health information.
- Clinical, legal, security, and accessibility validation would be required before real healthcare use.

## Resume Bullet

Built CareBridge, an AI-assisted patient visit preparation MVP that organizes appointment readiness, symptom timelines, medications, records, provider questions, source-cited document retrieval, and patient-reviewed PDF visit briefs using a compact Python and SQLite workflow.

## Author

**Nishita Reddy Yaduguri**  
Computer Science and Data Science, University of Wisconsin–Madison  
GitHub: https://github.com/Nishita2006
