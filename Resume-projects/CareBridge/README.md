# CareBridge

## AI Patient Visit Preparation Assistant

**Arrive prepared. Leave with clarity.**

🌐 **Live Demo:** (https://carebridge-ai.streamlit.app/)

CareBridge is an applied AI healthcare administration project that helps patients prepare for medical appointments by organizing symptoms, medications, documents, provider questions, and follow-up information in one place.

The application uses synthetic patient data and demonstrates Python, data analysis, machine learning, NLP, SQL, and retrieval-augmented generation through a Streamlit interface.

> CareBridge is an educational portfolio project. It is not a medical device, diagnostic tool, emergency service, or substitute for professional medical care.

---

## Project Overview

Patients often prepare for healthcare appointments using information spread across:

* Their memory
* Medication lists
* Lab reports
* Referral documents
* Previous appointment notes
* Insurance paperwork
* Patient portals

This makes it easy to forget important details such as:

* When a symptom started
* How a symptom changed
* Which medications are currently being taken
* Which records are still missing
* Which questions should be asked during the appointment
* What follow-up instructions were provided

CareBridge brings this information into one structured appointment-preparation workflow.

---

## Main Features

### Appointment Dashboard

The dashboard shows:

* Upcoming appointment details
* Provider information
* Appointment date
* Visit type
* Main reason for the visit
* Appointment preparation score
* Checklist progress
* Number of symptoms tracked
* Number of questions prepared

The preparation score measures administrative readiness only. It is not a medical-risk or clinical-safety score.

---

### Preparation Checklist

Patients can update preparation tasks such as:

* Uploading referral documents
* Reviewing insurance information
* Adding medications
* Recording allergies
* Preparing provider questions
* Reviewing appointment instructions

Checklist changes are saved in SQLite.

Task statuses include:

* Not started
* In progress
* Complete
* Not applicable

---

### Symptom Tracking and Data Analysis

The symptoms section displays:

* Symptom name
* Onset date
* Severity
* Pattern
* Source

The page also includes:

* Pandas-based data analysis
* NumPy calculations
* Matplotlib visualization
* Symptom severity charts
* Structured symptom tables

---

### Symptom Text Organizer

Patients can enter a symptom description in their own words.

CareBridge then creates:

* The original patient text
* An organized version
* Extracted keywords
* A verification warning

The original patient wording is always preserved.

The organized version must be reviewed before it is used.

---

### Document Classification

CareBridge includes a machine-learning model that suggests a category for pasted healthcare document text.

The classifier uses:

* TF-IDF vectorization
* Logistic regression
* Synthetic training examples
* Prediction confidence
* Influential feature words for each prediction

Possible categories may include:

* Referral
* Lab result
* Visit note
* Insurance document
* Procedure instructions
* Other healthcare document

The model only classifies the document type. It does not interpret the document medically.

---

### RAG Assistant

The RAG assistant allows users to ask questions about the available synthetic records.

Example questions:

* Which document mentions my follow-up date?
* What preparation instructions are available?
* Which report mentions the provider?
* What information is available about the appointment?

The assistant includes:

* Local TF-IDF retrieval
* Source citations
* Relevant source excerpts
* Retrieval scores
* An explicit insufficient-evidence response
* Low-information fallback
* Medical-safety checks
* Optional LangChain and OpenAI generation
* Local operation without an API key

The assistant does not diagnose conditions or provide treatment advice.

---

### SQL Explorer

CareBridge includes a read-only SQL workspace connected to the synthetic SQLite database.

Users can run `SELECT` queries on tables such as:

* `patients`
* `appointments`
* `preparation_tasks`
* `symptoms`
* `medications`
* `documents`
* `questions`

Example query:

```sql
SELECT
    status,
    COUNT(*) AS task_count
FROM preparation_tasks
GROUP BY status
ORDER BY task_count DESC;
```

The SQL explorer blocks:

* Database modifications
* Multiple SQL statements
* Non-`SELECT` commands

---

### Visit Summary

The visit summary brings together:

* Appointment details
* Main concern
* Symptoms
* Current medications
* Prepared questions

The summary is clearly labeled as patient-prepared and not medically verified.

The patient must confirm that the summary has been reviewed before downloading it.

The visit brief exports as a polished PDF. The underlying summary data can also be downloaded as CSV.

---

## Application Pages

CareBridge includes the following pages:

### Home

Introduces the project, technical stack, synthetic-data policy, appointment details, and preparation progress.

### Visit Readiness

Provides an editable appointment-preparation checklist backed by SQLite.

### Symptoms & Timeline

Displays symptom history, severity visualization, medications, allergies, and patient-reviewed text organization.

### Document Intelligence

Provides explainable document classification with confidence and influential feature words.

### Records Assistant

Returns grounded answers with source documents, excerpts, retrieval scores, and insufficient-evidence behavior.

### Data Explorer

Allows users to explore the synthetic SQLite database using safe read-only SQL queries.

### Visit Brief

Combines appointment information, symptoms, medications, and provider questions into downloadable PDF and CSV formats.

---

## Demo Workflow

CareBridge uses a fictional patient named **Maya Thompson**.

All patient information is synthetic.

A complete demo can follow these steps:

1. Open the dashboard.
2. Review the upcoming cardiology appointment.
3. View the appointment preparation score.
4. Update a checklist item.
5. Save the changes.
6. Open the Symptoms & Timeline page.
7. Review the symptom severity chart.
8. Enter a symptom description.
9. Organize the symptom text.
10. Compare the original and organized versions.
11. Open Document Intelligence.
12. Select **Try sample document**.
13. Run the document classifier.
14. Review the category, confidence, and influential feature words.
15. Open Records Assistant.
16. Ask which document mentions a follow-up date.
17. Review the answer, cited excerpt, and retrieval score.
18. Test a restricted question such as `What disease do I have?`
19. Open Data Explorer.
20. Run a read-only SQL query.
21. Open Visit Brief.
22. Review the appointment information.
23. Confirm the summary.
24. Download the PDF visit brief or CSV summary data.

---

## Technology Stack

### Application

* Python
* Streamlit

### Data Analysis

* Pandas
* NumPy
* Matplotlib

### Database

* SQLite
* SQL

### Machine Learning

* scikit-learn
* TF-IDF vectorization
* Logistic regression

### NLP

* Text cleaning
* Keyword extraction
* Rule-based text organization
* Safety-intent detection

### Retrieval and AI

* Local TF-IDF retrieval
* LangChain
* Optional OpenAI integration
* Source citations
* Safety refusals

### Testing

* pytest

---

## Project Structure

```text
CareBridge/
│
├── .streamlit/
│
├── demo_data/
│   └── documents/
│
├── docs/
│   ├── architecture.md
│   ├── ai_safety.md
│   └── privacy_design.md
│
├── notebooks/
│   └── carebridge_eda.ipynb
│
├── sql/
│
├── src/
│   ├── analytics.py
│   ├── database.py
│   ├── ml.py
│   ├── nlp.py
│   ├── rag.py
│   └── supporting modules
│
├── tests/
│
├── .env.example
├── .gitignore
├── app.py
├── README.md
└── requirements.txt
```

---

## How It Works

```text
Synthetic Patient Data
        ↓
SQLite Database
        ↓
Pandas and NumPy Processing
        ↓
Machine Learning and NLP
        ↓
Local Record Retrieval
        ↓
Source-Cited Answers
        ↓
Patient Review
        ↓
Visit Summary Export
```

---

## Machine Learning

CareBridge uses a document-classification model.

The workflow is:

```text
Document Text
      ↓
TF-IDF Vectorization
      ↓
Logistic Regression
      ↓
Suggested Category
      ↓
Confidence Score
      ↓
Human Review
```

The classifier is trained on synthetic examples.

Its predictions are for demonstration only.

---

## Natural Language Processing

The symptom organizer demonstrates lightweight NLP.

It can:

* Preserve the original patient statement
* Clean and normalize text
* Extract keywords
* Create a more organized draft
* Detect restricted medical requests
* Show the original and organized versions together

This allows the patient to review the result before accepting it.

---

## Retrieval-Augmented Generation

CareBridge supports local retrieval and optional model-backed generation.

### Local Mode

Local mode works without an API key.

It uses:

* Synthetic healthcare documents
* TF-IDF similarity
* Relevant record selection
* Source citations
* Safety checks

### Optional OpenAI Mode

When an OpenAI API key is available, LangChain and OpenAI can generate answers using the retrieved records.

The assistant still follows the same safety restrictions.

---

## Safety Boundaries

CareBridge does not:

* Diagnose diseases
* Predict diagnoses
* Recommend treatments
* Recommend medications
* Recommend dosage changes
* Recommend stopping prescriptions
* Interpret test results as final medical conclusions
* Replace healthcare professionals
* Replace emergency services

The application also:

* Preserves original patient input
* Displays source citations
* Requires human review
* Uses synthetic data
* Blocks unsafe medical requests
* Treats uploaded content as untrusted

---

## Run Locally

### Requirements

* Python 3.10 or later
* Git

### Clone the Repository

```bash
git clone https://github.com/Nishita2006/applied-ai-data-portfolio.git
cd applied-ai-data-portfolio/Resume-projects/CareBridge
```

### Create a Virtual Environment

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

macOS or Linux:

```bash
source .venv/bin/activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Create the Environment File

Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

macOS or Linux:

```bash
cp .env.example .env
```

### Start the Application

```bash
streamlit run app.py
```

The app will usually open at:

```text
http://localhost:8501
```

---

## Optional OpenAI Setup

CareBridge works without an OpenAI API key.

To enable optional model-backed generation, add:

```env
OPENAI_API_KEY=your-api-key
OPENAI_MODEL=gpt-4o-mini
```

Never commit API keys or secret files to GitHub.

---

## Testing

Run all tests:

```bash
pytest
```

The test suite covers areas such as:

* Preparation-score calculations
* Database behavior
* SQL safety
* NLP organization
* Document classification
* Retrieval
* Citations
* Medical-safety refusals

---

## Deployment

CareBridge can be deployed on Streamlit Community Cloud.

Use:

```text
Repository:
Nishita2006/applied-ai-data-portfolio
```

```text
Branch:
main
```

```text
Main file path:
Resume-projects/CareBridge/app.py
```

After deployment, replace the live demo line at the top of this README with the actual Streamlit URL.

---

## Current Limitations

* The project uses synthetic patient data.
* The document classifier uses a small synthetic dataset.
* Classification confidence is not medical certainty.
* The local retriever is not a clinical knowledge system.
* AI-generated answers may contain errors.
* PDF generation uses a concise single-page portfolio template.
* The application does not include production authentication.
* The application is not designed to store real patient data.
* The project has not undergone clinical, legal, regulatory, or security validation.

---

## Future Improvements

* Add user authentication
* Add secure patient accounts
* Add patient-level data isolation
* Add caregiver sharing
* Add multi-format document upload
* Add stronger document extraction
* Add semantic vector retrieval
* Add multilingual support
* Add voice-based symptom entry
* Add calendar integration
* Add mobile support
* Add accessibility testing
* Add audit logs
* Add secure cloud storage

---

## Skills Demonstrated

CareBridge demonstrates:

* Python development
* Streamlit application development
* Pandas data analysis
* NumPy calculations
* Matplotlib visualization
* SQLite database design
* SQL querying
* Machine learning
* TF-IDF vectorization
* Logistic regression
* NLP text processing
* Retrieval-augmented generation
* LangChain integration
* Optional OpenAI integration
* Source citations
* Responsible AI
* Human-in-the-loop design
* Safety guardrails
* Testing
* Git and GitHub workflows
* Technical documentation

---

## Resume Description

### CareBridge — AI Patient Visit Preparation Assistant

* Built a Streamlit-based healthcare administration assistant that organizes appointment tasks, patient-reported symptoms, medications, documents, provider questions, and patient-reviewed visit summaries using synthetic data.
* Developed a TF-IDF and logistic-regression document classifier, NLP symptom organizer, SQLite data layer, Pandas and NumPy analytics, Matplotlib visualizations, and a safe read-only SQL explorer.
* Implemented a source-cited retrieval workflow with optional LangChain and OpenAI generation, human verification, low-information fallback, and safety refusals for diagnostic, treatment, and medication-related requests.

---

## Author

**Nishita Reddy Yaduguri**

Computer Science and Data Science
University of Wisconsin–Madison

GitHub: https://github.com/Nishita2006

---

## Disclaimer

CareBridge is an educational and portfolio project.

It is not intended to:

* Diagnose medical conditions
* Provide medical advice
* Recommend medication
* Recommend treatment
* Replace a doctor
* Replace emergency care
* Store real patient information

All patient information used in the project is fictional and synthetic.

Always consult a qualified healthcare professional for medical concerns.
