def generate_signal_card(match_score, simulation_score, matched_skills, missing_skills):
    strengths = []
    risks = []

    # Resume match summary
    if match_score >= 75:
        strengths.append("Strong resume match with the job requirements.")
    elif match_score >= 50:
        strengths.append("Moderate resume match with some relevant skills.")
    else:
        risks.append("Resume has low overlap with the job requirements.")

    # Simulation score summary
    if simulation_score >= 75:
        strengths.append("Strong simulation response based on the rubric.")
    elif simulation_score >= 50:
        strengths.append("Moderate simulation response with room for improvement.")
    else:
        risks.append("Simulation response scored low on the rubric.")

    if len(matched_skills) > 0:
        strengths.append("Matched skills: " + ", ".join(matched_skills))

    if len(missing_skills) > 0:
        risks.append("Missing or unclear skills: " + ", ".join(missing_skills))

    # Final decision-support label
    if match_score >= 75 and simulation_score >= 75:
        final_confidence = "High"
        recommended_next_step = "Move to technical screen."
    elif match_score >= 50 and simulation_score >= 50:
        final_confidence = "Medium"
        recommended_next_step = "Review manually and ask targeted follow-up questions."
    else:
        final_confidence = "Low"
        recommended_next_step = "Lower review priority unless there is other strong evidence."

    return {
        "Final Confidence": final_confidence,
        "Strengths": strengths,
        "Risks": risks,
        "Recommended Next Step": recommended_next_step
    }