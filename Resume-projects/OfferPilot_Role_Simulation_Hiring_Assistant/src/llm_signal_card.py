import json

from src.llm_client import ask_llm, is_llm_available
from src.signal_card import generate_signal_card


def calculate_final_confidence(resume_match_score, simulation_score):
    """
    Calculates final confidence using a deterministic weighted score.
    This prevents the LLM from being too generous or inconsistent.
    """

    overall_score = round(
        (0.60 * resume_match_score) + (0.40 * simulation_score)
    )

    if overall_score >= 75:
        final_confidence = "High"
    elif overall_score >= 40:
        final_confidence = "Medium"
    else:
        final_confidence = "Low"

    return final_confidence, overall_score


def get_recommended_next_step(final_confidence):
    """
    Gives a consistent recruiter next step based on final confidence.
    """

    if final_confidence == "High":
        return "Move forward to a technical interview or next-round review."
    elif final_confidence == "Medium":
        return "Consider a follow-up screen to verify technical depth and role fit."
    else:
        return "Do not move forward unless there is additional evidence of role-relevant skills."


def generate_signal_card_with_llm(
    candidate_name,
    resume_match_score,
    simulation_score,
    matched_skills,
    missing_skills,
    rubric_scores,
    role_category
):
    """
    Uses LLM to generate recruiter-friendly explanation fields.
    Final Confidence is calculated by code, not decided by the LLM.
    """

    final_confidence, overall_score = calculate_final_confidence(
        resume_match_score,
        simulation_score
    )

    recommended_next_step = get_recommended_next_step(final_confidence)

    fallback_card = generate_signal_card(
        resume_match_score,
        simulation_score,
        matched_skills,
        missing_skills
    )

    if not is_llm_available():
        fallback_card["Final Confidence"] = final_confidence
        fallback_card["Overall Score"] = overall_score
        fallback_card["Recommended Next Step"] = recommended_next_step
        return fallback_card

    prompt = f"""
You are creating a recruiter-friendly candidate signal card.

Return ONLY valid JSON.
Do not include markdown.
Do not include explanations outside the JSON.

Use this exact JSON structure:

{{
  "Recruiter Summary": "",
  "Strengths": [],
  "Risks": [],
  "Interview Focus Areas": []
}}

Candidate:
{candidate_name}

Role Category:
{role_category}

Resume Match Score:
{resume_match_score}

Simulation Score:
{simulation_score}

Final Confidence:
{final_confidence}

Overall Score:
{overall_score}

Matched Skills:
{matched_skills}

Missing Skills:
{missing_skills}

Rubric Scores:
{rubric_scores}

Rules:
- Do not change Final Confidence.
- Be honest and fair.
- If resume match and simulation score are both low, clearly state that the candidate is not a strong fit.
- Strengths should be based only on evidence from the resume match and simulation response.
- Do not invent technical skills that are not shown.
- Risks should be practical and specific.
- Interview Focus Areas should tell the recruiter what to verify next.
- If Final Confidence is Low, do not describe the candidate as technically strong.
- If Simulation Score is below 40, do not say the candidate has a good understanding of technical requirements.
- For Low confidence candidates, keep Strengths limited to general positives only, such as communication or understanding the basic goal.
- Do not list a skill as a risk if it appears in Matched Skills.
- Do not say the candidate lacks communication or teamwork if those are matched skills.
- Be stricter with weak candidates. Do not make the recommendation sound like they should continue unless the scores support it.
"""

    try:
        response = ask_llm(prompt)
        parsed_response = json.loads(response)

        signal_card = {
            "Final Confidence": final_confidence,
            "Overall Score": overall_score,
            "Recommended Next Step": recommended_next_step,
            "Recruiter Summary": parsed_response.get("Recruiter Summary", ""),
            "Strengths": parsed_response.get("Strengths", []),
            "Risks": parsed_response.get("Risks", []),
            "Interview Focus Areas": parsed_response.get("Interview Focus Areas", [])
        }

        return signal_card

    except Exception:
        fallback_card["Final Confidence"] = final_confidence
        fallback_card["Overall Score"] = overall_score
        fallback_card["Recommended Next Step"] = recommended_next_step
        return fallback_card