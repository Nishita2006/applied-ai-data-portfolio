import json

from src.llm_client import ask_llm, is_llm_available
from src.rubric_scorer import score_simulation_response


def score_simulation_response_with_llm(candidate_response, role_category, simulation_task):
    """
    Uses LLM to score a candidate response.
    Falls back to rule-based scorer if LLM is unavailable or fails.
    """

    if not is_llm_available():
        return score_simulation_response(candidate_response, role_category)

    prompt = f"""
You are scoring a candidate's response for a recruiter-facing hiring assistant.

Return ONLY valid JSON.
Do not include markdown.
Do not include explanations outside the JSON.

Use this exact JSON structure:

{{
  "Technical Correctness": 0,
  "Reasoning Clarity": 0,
  "Role Relevance": 0,
  "Communication": 0,
  "Assumptions / Tradeoffs": 0,
  "Simulation Score": 0,
  "Overall Feedback": ""
}}

Scoring rules:
- Each rubric area should be scored from 0 to 20.
- Simulation Score should be the sum of the five rubric areas, from 0 to 100.
- Be fair but not overly generous.
- Reward specific, practical, role-relevant answers.
- Penalize vague answers that only say generic things.
- Overall Feedback should be 2 to 4 sentences in recruiter-friendly language.

Role Category:
{role_category}

Simulation Task:
{simulation_task}

Candidate Response:
{candidate_response}
"""

    try:
        response = ask_llm(prompt)
        parsed_response = json.loads(response)

        rubric_keys = [
            "Technical Correctness",
            "Reasoning Clarity",
            "Role Relevance",
            "Communication",
            "Assumptions / Tradeoffs"
        ]

        total_score = 0

        for key in rubric_keys:
            parsed_response[key] = int(parsed_response.get(key, 0))
            total_score += parsed_response[key]

        parsed_response["Simulation Score"] = int(parsed_response.get("Simulation Score", total_score))

        return parsed_response

    except Exception:
        return score_simulation_response(candidate_response, role_category)