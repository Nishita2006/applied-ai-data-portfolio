from src.llm_client import ask_llm, is_llm_available
from src.simulation_generator import generate_simulation_task


def generate_simulation_task_with_llm(job_description, jd_analysis):
    """
    Uses LLM to generate a custom simulation task from the actual JD.
    Falls back to rule-based task if LLM fails.
    """

    role_category = jd_analysis.get("role_category", "")
    role_title = jd_analysis.get("role_title", "")
    required_skills = jd_analysis.get("required_skills", [])
    responsibilities = jd_analysis.get("responsibilities", [])

    if not is_llm_available():
        return generate_simulation_task(role_category)

    prompt = f"""
You are creating a role-specific work simulation task for a recruiter-facing hiring assistant.

Return ONLY the task text.
Do not include markdown fences.
Do not include extra commentary.

Job Information:
Role Title: {role_title}
Role Category: {role_category}
Required Skills: {required_skills}
Responsibilities: {responsibilities}

Original Job Description:
{job_description}

Create a realistic work simulation task with this structure:

Work Simulation Task:
Business Scenario:
Candidate Task:
What the Response Should Include:
Evaluation Focus:

Rules:
- Keep the task concise.
- Do not repeat the full job description.
- Do not ask the candidate to build a full production app.
- Make the task answerable in 20 to 30 minutes.
- Focus on reasoning, design choices, tradeoffs, and practical implementation thinking.
- Include a reminder that the candidate should explain assumptions and tradeoffs.
"""

    try:
        response = ask_llm(prompt)

        if response is None or response.strip() == "":
            return generate_simulation_task(role_category)

        return response.strip()

    except Exception:
        return generate_simulation_task(role_category)