# Applied AI & Data Portfolio

A portfolio of applied AI, machine learning, and data science projects focused on real-world workflow automation and decision support.

This repository documents my work in Python, data analysis, NLP, machine learning, and applied AI. The main focus is building practical tools that solve realistic problems across hiring, campus services, insurance, civic compliance, and healthcare administration.

## Featured Projects

| Project                                                                                                     | Focus Area                                                 | Status    |
| ----------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------- | --------- |
| [Campus Lost & Found AI Matcher](Resume-projects/campus-lost-found-ai-matcher)                              | NLP, text similarity, matching system                      | Completed |
| [OfferPilot: Role Simulation Hiring Assistant](Resume-projects/OfferPilot_Role_Simulation_Hiring_Assistant) | LLM apps, resume screening, scoring workflows              | Completed |
| [ClaimLens: Insurance Claim Triage Assistant](Resume-projects/claimlens-insurance-claim-triage)             | Risk scoring, evidence review, document intelligence       | Completed |
| [PermitPal: City Permit Compliance Assistant](Resume-projects/permitpal-city-permit-compliance)             | Rule-based reasoning, civic tech, compliance support       | Completed |
| [CareBridge: Patient Visit Prep Assistant](Resume-projects/CareBridge)                                      | Healthcare admin, ML, NLP, and source-cited retrieval       | [Live MVP](https://carebridge-ai.streamlit.app/) |
| [Job Portal: Full-Stack Recruiting Platform](Resume-projects/job-portal)                                    | Java, Spring Boot, REST APIs, PostgreSQL, JWT               | Completed |

## Repository Structure

```text
applied-ai-data-portfolio/
│
├── 01-python-basics/
│   └── Python fundamentals and mini projects
│
├── pandas-numpy-practice-projects/
│   └── Data analysis and EDA practice
│
├── nlp-practice-projects/
│   └── NLP practice projects and text processing exercises
│
├── Resume-projects/
│   ├── campus-lost-found-ai-matcher/
│   ├── OfferPilot_Role_Simulation_Hiring_Assistant/
│   ├── claimlens-insurance-claim-triage/
│   ├── permitpal-city-permit-compliance/
│   ├── CareBridge/
│   └── job-portal/
│
├── requirements.txt
├── runtime.txt
└── README.md
```

## Skills Demonstrated

* Python programming
* Data cleaning and analysis
* NLP and text similarity
* Streamlit app development
* Rule-based scoring systems
* LLM-assisted workflows
* Resume and document parsing
* Risk and decision-support logic
* Git and GitHub project organization
* Java and object-oriented programming
* Spring Boot REST API development
* Relational database design with PostgreSQL and JPA
* Spring Security, BCrypt, and JWT authorization

## Project Theme

The projects in this repository focus on AI and data tools that support real decision-making workflows. Each project is designed around a practical problem, including matching lost items, evaluating candidate fit, triaging insurance claims, simplifying permit requirements, and preparing healthcare visit summaries.

## Projects Overview

### Campus Lost & Found AI Matcher

An NLP-powered matching tool that helps students find lost items by comparing lost-item descriptions with found-item reports and ranking the most relevant matches.

**Highlights:**

* Text similarity-based matching
* Match confidence scoring
* Explainable match reasons
* Streamlit app interface

---

### OfferPilot: Role Simulation Hiring Assistant

A hiring workflow assistant that analyzes job descriptions, compares resumes, generates role-specific simulation tasks, and evaluates candidate responses using structured scoring.

**Highlights:**

* Job description analysis
* Resume screening and ranking
* Role-specific simulation generation
* Candidate response scoring
* Recruiter-style signal card

---

### ClaimLens: Insurance Claim Triage Assistant

An insurance claim review tool that organizes claim details, identifies missing evidence, calculates a basic risk score, and suggests next steps for claim handlers.

**Highlights:**

* Claim intake workflow
* Rule-based risk scoring
* Missing evidence detection
* Review recommendation logic
* Future RAG-ready structure

---

### PermitPal: City Permit Compliance Assistant

A civic-tech assistant that helps users understand possible permit requirements, required documents, and next steps for city or housing-related projects.

**Highlights:**

* Permit requirement guidance
* Document checklist generation
* Rule-based compliance logic
* Simplified user-facing explanations
* Future RAG-ready structure

---

### [CareBridge: Patient Visit Prep Assistant](Resume-projects/CareBridge)

A deployed patient visit preparation MVP that brings appointment readiness, patient-entered symptoms, medications, records, provider questions, and a downloadable visit brief into one accessible workspace. The public application uses only fictional patient information.

**[Open the live application](https://carebridge-ai.streamlit.app/)**

**Highlights:**

* Appointment readiness tracking with SQLite-backed storage
* Patient responses saved exactly as entered
* Explainable TF-IDF and logistic-regression document classification
* Source-cited record retrieval with insufficient-evidence handling
* Provider question preparation and PDF/CSV visit-brief export
* Automated tests and deployment on Streamlit Community Cloud

---

### [Job Portal: Full-Stack Recruiting Platform](Resume-projects/job-portal)

A production-style recruiting application with separate candidate and recruiter workspaces, secure authentication, persistent relational data, and a responsive frontend.

**Highlights:**

* Candidate profiles, resume uploads, job search, applications, and status tracking
* Company profiles, job publishing, applicant filtering, hiring stages, and analytics
* Layered Spring Boot architecture with controllers, services, repositories, entities, and DTOs
* BCrypt password hashing, signed JWT authentication, and role-based API authorization
* PostgreSQL-ready JPA model with validation, pagination, sorting, and search filters
* Swagger/OpenAPI docs, Postman collection, Docker deployment, and automated tests

## Current Focus

These projects are completed MVPs that demonstrate applied AI, data processing, workflow design, and decision-support logic. Current work focuses on stronger model evaluation, expanded datasets, responsible source-grounded retrieval, and production-minded application design.

## Author

Nishita Reddy Yaduguri
Computer Science and Data Science student at the University of Wisconsin–Madison
