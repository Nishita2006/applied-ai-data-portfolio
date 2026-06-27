import json

from src.llm_client import ask_llm, is_llm_available
from src.job_parser import jd_skill_extractor, role_category


def analyze_job_description_with_llm(job_description):
    """
    Uses LLM to analyze a job description.
    Falls back to rule-based parser if LLM is unavailable or fails.
    """

    if not is_llm_available():
        return analyze_job_description_fallback(job_description)

    prompt = f"""
You are analyzing a job description for a recruiter-facing hiring assistant.

Return ONLY valid JSON.
Do not include markdown.
Do not include explanations outside the JSON.

Return this exact JSON structure:

{{
  "role_title": "",
  "role_category": "",
  "required_skills": [],
  "preferred_skills": [],
  "responsibilities": [],
  "soft_skills": [],
  "seniority_level": "",
  "ideal_candidate_summary": ""
}}

Rules:
- Keep skills short and clean.
- Do not duplicate skills.
- Use plain language.
- If something is missing, use an empty list or empty string.
- required_skills should include technical or role-specific skills such as tools, programming languages, methods, frameworks, and domain skills.
- soft_skills should include human/workplace skills such as communication, collaboration, teamwork, presentation, problem solving, stakeholder management, organization, and adaptability.
- If the job description mentions working with teams, collaborating, presenting, explaining results, or communicating with non-technical users, include those as soft_skills.
- Do not put the same skill in both required_skills and soft_skills.

Job Description:
{job_description}
"""

    try:
        response = ask_llm(prompt)
        parsed_response = json.loads(response)
        return parsed_response

    except Exception:
        return analyze_job_description_fallback(job_description)


def analyze_job_description_fallback(job_description):
    """
    Rule-based fallback.
    """

    role_skills, soft_skills = jd_skill_extractor(job_description)
    category = role_category(job_description)

    return {
        "role_title": "",
        "role_category": category,
        "required_skills": role_skills,
        "preferred_skills": [],
        "responsibilities": [],
        "soft_skills": soft_skills,
        "seniority_level": "",
        "ideal_candidate_summary": ""
    }