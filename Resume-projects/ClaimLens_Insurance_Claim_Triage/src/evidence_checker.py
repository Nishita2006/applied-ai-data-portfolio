def check_missing_evidence(
    claim_type,
    evidence_uploaded,
    police_report_available,
    photos_available,
    injury_involved):
    missing_evidence = []
    if not evidence_uploaded:
        missing_evidence.append("General claim evidence is missing")
    if not photos_available:
        missing_evidence.append("Photos of damage or incident are missing")
    if claim_type in ["Auto", "Theft"] and not police_report_available:
        missing_evidence.append("Police report is missing")
    if injury_involved:
        missing_evidence.append("Medical documentation may be required")
    return missing_evidence
