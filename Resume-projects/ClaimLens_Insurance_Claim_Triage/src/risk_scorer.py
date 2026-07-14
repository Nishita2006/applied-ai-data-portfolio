def calculate_risk_score(
    claim_type,
    claim_amount,
    evidence_uploaded,
    police_report_available,
    photos_available,
    injury_involved,
    conflicting_statements,
    previous_claims
):
    risk_score = 0
    red_flags = []

    if claim_amount > 10000:
        risk_score += 3
        red_flags.append("High claim amount")
    elif claim_amount >= 3000:
        risk_score += 2
        red_flags.append("Moderate claim amount")
    else:
        risk_score += 1

    if injury_involved:
        risk_score += 3
        red_flags.append("Injury involved")

    if claim_type in ["Auto", "Theft"] and not police_report_available:
        risk_score += 2
        red_flags.append("Police report missing")

    if not photos_available:
        risk_score += 1
        red_flags.append("Photos missing")

    if not evidence_uploaded:
        risk_score += 2
        red_flags.append("Evidence missing")

    if conflicting_statements:
        risk_score += 3
        red_flags.append("Conflicting statements")

    if previous_claims:
        risk_score += 2
        red_flags.append("Previous claims")

    if risk_score <= 4:
        risk_level = "Low Risk"
    elif risk_score <= 8:
        risk_level = "Medium Risk"
    else:
        risk_level = "High Risk"

    return risk_score, risk_level, red_flags

