from src.llm_client import ask_llm, is_llm_available
from src.simulation_generator import generate_simulation_task


def generate_candidate_questions_with_llm(job_description, jd_analysis, candidate_name, resume_text, evidence_rows):
    """Create profile- and level-specific technical plus scenario questions."""
    strengths = [row["Skill"] for row in evidence_rows if row.get("Evidence Score", 0) >= 45][:5]
    gaps = [row["Skill"] for row in evidence_rows if row.get("Evidence Score", 0) < 45][:5]
    seniority = jd_analysis.get("seniority_level", "Not specified")
    if is_llm_available():
        prompt = f"""
Create six structured interview questions for {candidate_name}, applying for the role below.
Return only a numbered list. Tailor difficulty to the stated seniority. Ask three technical
questions grounded in the candidate's actual experience and three realistic scenario questions.
Each scenario must ask what they would do, why, tradeoffs, and how they would verify the result.
Do not assume missing evidence means missing ability. Do not ask about protected attributes.

Role: {jd_analysis.get('role_title', '')} ({seniority})
Required capabilities: {jd_analysis.get('required_skills', [])}
Responsibilities: {jd_analysis.get('responsibilities', [])}
Resume evidence strengths: {strengths}
Evidence to validate: {gaps}
Resume: {str(resume_text)[:7000]}
Job description: {str(job_description)[:5000]}
"""
        try:
            response = ask_llm(prompt)
            if response and response.strip():
                return response.strip()
        except Exception:
            pass

    anchor = strengths[0] if strengths else "the candidate's strongest project"
    gap = gaps[0] if gaps else "a key role requirement"
    return "\n".join([
        f"1. Walk me through your work involving {anchor}. What did you personally own and how did you validate it?",
        f"2. Explain a difficult technical decision in that work. What alternatives and tradeoffs did you consider?",
        f"3. The resume provides limited evidence for {gap}. Describe the closest relevant experience and the depth of your contribution.",
        f"4. Scenario: a production result for {anchor} is inconsistent. How would you diagnose it, communicate risk, and verify the fix?",
        "5. Scenario: requirements change midway through delivery. How would you reprioritize, align stakeholders, and measure success?",
        "6. Scenario: your preferred approach creates a quality-versus-speed tradeoff. What would you choose, why, and what safeguards would you add?",
    ])


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
