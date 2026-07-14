def generate_next_steps(risk_level, red_flags, missing_evidence):
    next_steps_list = []
    if risk_level == "High Risk":
        next_steps_list.append("Escalate claim for senior adjuster review")
    elif risk_level == "Medium Risk":
        next_steps_list.append("Review claim details and request any missing evidence")
    elif risk_level == "Low Risk":
        next_steps_list.append("Proceed with standard claim review")
    if missing_evidence:
        next_steps_list.append("Request missing evidence from claimant")
    if "Conflicting statements" in red_flags:
        next_steps_list.append("Review claimant and witness statements for inconsistencies")
    if "Injury involved" in red_flags:
        next_steps_list.append("Review medical documentation and injury details")
    if "Police report missing" in red_flags:
        next_steps_list.append("Request police report before final decision")
    return next_steps_list



    