# OfferPilot: LLM-Powered Role Simulation Hiring Assistant

OfferPilot is an LLM-powered hiring assistant that helps recruiters analyze job descriptions, screen resumes, generate role-specific work simulation tasks, score candidate responses, and create recruiter-ready signal cards.

The project is designed to support an end-to-end candidate review workflow, combining resume matching, LLM reasoning, simulation-based assessment, and recruiter decision tracking.

## Live Demo

https://offerpilot-hiring-assistant.streamlit.app/


## Project Overview

Traditional resume screening often relies on manual review or simple keyword matching. OfferPilot improves this process by helping recruiters understand candidate fit from multiple signals:

* Job description analysis
* Resume skill matching
* Text similarity scoring
* Role-specific simulation tasks
* LLM-based rubric scoring
* Candidate signal cards
* Recruiter notes and decision tracking

The goal is not to replace recruiters, but to give them a clearer and more structured way to compare candidates.

## Key Features

### 1. Job Description Analysis

Recruiters can paste a job description, and the app extracts:

* Role title
* Role category
* Required technical skills
* Preferred skills
* Soft skills
* Responsibilities
* Seniority level
* Ideal candidate summary

The app uses an LLM when available and falls back to rule-based logic if the API key is not configured.

### 2. Candidate Resume Screening

Recruiters can upload multiple resume PDFs. The app extracts resume text and ranks candidates using a hybrid matching approach.

The scoring includes:

* Technical skill match
* Resume and job description text similarity
* Soft skill match

This helps identify strong, medium, and weak candidate fits.

### 3. Negative Skill Sentence Handling

OfferPilot removes misleading negative skill sentences such as:

> Limited experience with Python, Streamlit, Pandas, NLP, APIs, and Git.

This prevents weak resumes from falsely matching technical skills just because those skills are mentioned in a negative context.

### 4. Skill Heatmap

The app generates a candidate skill heatmap showing which required skills each candidate matches or misses.

This makes it easier for recruiters to compare candidates side by side.

### 5. Role Simulation Task Generator

OfferPilot generates a realistic work simulation task based on the job description and role category.

The task includes:

* Business scenario
* Candidate task
* Expected response elements
* Evaluation focus

This helps recruiters evaluate how candidates think through practical role-specific problems.

### 6. LLM Rubric Scoring

Recruiters can paste a candidate's simulation response. The app scores the response using a structured rubric:

* Technical correctness
* Reasoning clarity
* Role relevance
* Communication
* Assumptions and tradeoffs

The final simulation score is calculated out of 100.

### 7. Candidate Signal Card

OfferPilot combines resume match score and simulation score to generate a final candidate signal card.

The signal card includes:

* Final confidence
* Recommended next step
* Recruiter summary
* Strengths
* Risks
* Interview focus areas

Final confidence is calculated using a deterministic scoring formula so that the LLM does not overrate weak candidates.

### 8. Recruiter Notes and Decision Tracking

Recruiters can save additional review information for each candidate:

* Recruiter decision
* Recruiter notes
* Follow-up questions

This makes the app closer to a real hiring review workflow.

## Tech Stack

* Python
* Streamlit
* Pandas
* scikit-learn
* pypdf
* Groq API
* Llama 3.1
* TF-IDF text similarity
* Rule-based skill extraction
* LLM-powered scoring and summarization

## Project Structure

```text
OfferPilot_Role_Simulation_Hiring_Assistant/
│
├── app.py
├── requirements.txt
├── README.md
│
├── src/
│   ├── resume_reader.py
│   ├── job_parser.py
│   ├── semantic_matcher.py
│   ├── simulation_generator.py
│   ├── rubric_scorer.py
│   ├── signal_card.py
│   ├── llm_client.py
│   ├── llm_jd_analyzer.py
│   ├── llm_simulation_generator.py
│   ├── llm_rubric_scorer.py
│   └── llm_signal_card.py
│
└── .streamlit/
    └── secrets.toml
```

Note: `.streamlit/secrets.toml` is used locally for API keys and should not be pushed to GitHub.

## How It Works

### Step 1: Analyze Job Description

The recruiter pastes a job description. OfferPilot extracts role information, required skills, soft skills, and responsibilities.

### Step 2: Upload Resumes

The recruiter uploads resume PDFs. The app extracts text from each resume.

### Step 3: Match Candidates

The app compares each resume against the job description using:

* Direct skill matching
* Text similarity
* Soft skill matching
* Negative skill sentence filtering

Candidates are ranked by match score.

### Step 4: Generate Simulation Task

The app creates a role-specific work simulation task using the job description.

### Step 5: Score Candidate Response

The recruiter pastes the candidate's simulation response. The app scores it using an LLM rubric.

### Step 6: Create Signal Card

The app generates a recruiter-ready candidate signal card with strengths, risks, final confidence, and recommended next steps.

### Step 7: Save Recruiter Notes

The recruiter can save final notes, decisions, and follow-up questions for each candidate.

## Scoring Logic

### Resume Match Score

The final resume match score combines:

* 70% technical skill match
* 20% text similarity
* 10% soft skill match

This prevents soft skills from overpowering technical fit.

### Final Confidence Score

Final confidence combines resume match and simulation performance:

* 60% resume match score
* 40% simulation score

Confidence levels:

* High: 75 and above
* Medium: 40 to 74
* Low: below 40

This makes final candidate recommendations more consistent and less dependent on LLM wording.

## Example Results

In testing, OfferPilot correctly ranked candidates as:

| Candidate Type   | Resume Match | Simulation Score | Final Confidence |
| ---------------- | -----------: | ---------------: | ---------------- |
| Strong candidate |          84% |              76% | High             |
| Medium candidate |          43% |              76% | Medium           |
| Weak candidate   |           5% |              22% | Low              |

## Local Setup

Clone the repository and install dependencies:

```bash
pip install -r requirements.txt
```

Run the Streamlit app:

```bash
streamlit run app.py
```

If running from the root repository folder:

```bash
streamlit run "Resume-projects/OfferPilot_Role_Simulation_Hiring_Assistant/app.py"
```

## Environment Variables

Create a local secrets file:

```text
.streamlit/secrets.toml
```

Add your Groq API key:

```toml
GROQ_API_KEY = "your_api_key_here"
```

Important: Do not push `secrets.toml` to GitHub.

Recommended `.gitignore` entries:

```text
**/.streamlit/
**/secrets.toml
.env
__pycache__/
*.pyc
```

## Deployment

The app is deployed using Streamlit Cloud.

For deployment, add the Groq API key in:

```text
Streamlit Cloud → App Settings → Secrets
```

Use this format:

```toml
GROQ_API_KEY = "your_api_key_here"
```

## Limitations

* Resume parsing depends on PDF text quality.
* Skill extraction is partly rule-based and may miss uncommon wording.
* LLM-generated feedback may vary slightly across runs.
* The app is designed as a decision-support tool, not an automated hiring decision system.
* The current version does not include authentication or a database for long-term candidate storage.

## Future Improvements

Potential future improvements include:

* Add embeddings for deeper semantic resume matching
* Store candidate reviews in a database
* Add export to CSV or PDF
* Add authentication for recruiters
* Improve resume parsing for complex PDF layouts
* Add bias and fairness checks
* Add batch comparison across multiple job descriptions

## Resume Bullet

Built OfferPilot, an LLM-powered hiring assistant that analyzes job descriptions, screens resumes using hybrid skill and text similarity matching, generates role-specific simulations, scores candidate responses with an LLM rubric, and produces recruiter-ready signal cards with decision tracking.

## Author

Nishita Reddy Yaduguri
