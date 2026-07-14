def generate_claim_summary(
    claim_type,
    claim_amount,
    incident_description,
    risk_score,
    risk_level,
    red_flags,
    missing_evidence,
    next_steps
):
    summary = (
        f"This {claim_type} claim has a reported claim amount of ${claim_amount} "
        f"and is classified as {risk_level} with a risk score of {risk_score}. "
    )

    if incident_description:
        summary += f"The claimant reported: {incident_description}. "

    if red_flags:
        summary += "Key red flags include " + ", ".join(red_flags) + ". "
    else:
        summary += "No major red flags were detected. "

    if missing_evidence:
        summary += "Missing evidence includes " + ", ".join(missing_evidence) + ". "
    else:
        summary += "No missing evidence was detected. "

    if next_steps:
        summary += "Recommended next steps include " + ", ".join(next_steps) + ". "

    return summary