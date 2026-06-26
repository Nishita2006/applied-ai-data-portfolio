# OfferPilot: Role Simulation Hiring Assistant

OfferPilot is a recruiter-facing resume screening and role simulation tool. It helps recruiters compare candidates against a job description, rank resumes by role fit, generate role-specific simulation tasks, score candidate responses using a structured rubric, and create a final candidate signal card.

The project is designed to go beyond a basic resume matcher. Instead of only showing a resume match score, it combines resume-job fit with a practical simulation response to give recruiters a clearer view of candidate readiness.

## Problem

Recruiters often review many resumes for the same role, and resumes can look very similar or overly polished. A simple keyword match does not always show whether a candidate can actually reason through role-specific tasks.

OfferPilot helps by combining:

* Resume and job description skill matching
* Candidate ranking
* Skill gap visibility
* Role-specific work simulation
* Rubric-based response scoring
* Final candidate signal card

## Features

### Job Description Analysis

Recruiters can paste a job description, and the app extracts:

* Role category
* Role-specific skills
* Soft skills

Supported role categories include:

* Data / Analytics
* AI / ML
* Software Engineering
* Finance / Risk
* HR / People Operations
* Product / Business
* General Internship

### Candidate Resume Screening

Recruiters can upload multiple resume PDFs. The app:

* Extracts text from each resume
* Finds role-specific skills in each resume
* Compares resume skills to job description skills
* Calculates a match score
* Ranks candidates by fit
* Labels candidates as High Review, Medium Review, or Low Review

### Skill Heatmap

The app creates a skill heatmap showing which candidates match each required job skill.

This helps recruiters quickly compare candidates across the same role requirements.

### Role Simulation Task

Based on the detected role category, OfferPilot generates a small role-specific task.

Examples:

* Data role: analyze a small dataset and explain insights
* ML role: choose model evaluation metrics
* SWE role: debug a performance issue
* Finance/Risk role: review suspicious transactions
* HR role: improve a recruiting process
* Product role: choose feature launch metrics

### Rubric-Based Response Scoring

Recruiters can paste a candidate’s simulation response. The app scores the response using a structured rubric:

* Technical Correctness
* Reasoning Clarity
* Role Relevance
* Communication
* Assumptions / Tradeoffs

The final simulation score is calculated as a percentage.

### Candidate Signal Card

OfferPilot combines resume match and simulation performance into a final candidate signal card.

The signal card includes:

* Resume match score
* Simulation score
* Final confidence level
* Strengths
* Risks
* Recommended next step

## Tech Stack

* Python
* Streamlit
* Pandas
* pypdf
* Rule-based NLP/text matching
* Rubric-based scoring logic

## Project Structure

```text
OfferPilot/
│
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
│
└── src/
    ├── job_parser.py
    ├── resume_reader.py
    ├── match_engine.py
    ├── simulation_generator.py
    ├── rubric_scorer.py
    └── signal_card.py
```

## How to Run

Clone the repository:

```bash
git clone <your-repo-link>
cd OfferPilot
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the Streamlit app:

```bash
streamlit run app.py
```

## Sample Workflow

1. Paste a job description in the Job Setup tab.
2. Click Analyze Job Description.
3. Upload multiple resume PDFs in the Candidate Screening tab.
4. Review the ranked candidate table.
5. Open the Skill Heatmap tab to compare candidate skills.
6. Go to the Simulation Review tab.
7. Select a candidate and paste their simulation response.
8. View rubric scores and the final Candidate Signal Card.

## Limitations

This project uses rule-based text matching and scoring. It is designed to be explainable and easy to understand, but it does not replace human hiring judgment.

Current limitations:

* Resume text extraction works best with text-based PDFs, not scanned image resumes.
* Skill extraction depends on predefined skill lists.
* Match scores are based on keyword overlap, not deep semantic understanding.
* Rubric scoring is rule-based and may not fully capture answer quality.
* The app supports recruiter decision-making but should not be used as an automatic hiring decision system.

## Future Improvements

Possible next upgrades:

* Add semantic similarity using embeddings
* Support scanned resumes using OCR
* Add LLM-generated simulation tasks
* Add LLM-assisted rubric scoring with explanations
* Store screening sessions in a database
* Export candidate signal cards as PDF reports
* Add authentication and recruiter workspace history
* Improve skill extraction with a larger skill taxonomy

## Project Goal

The goal of OfferPilot is to create a more explainable and practical hiring support tool by combining resume screening with role-specific simulation evaluation.
