import streamlit as st
from src.risk_scorer import calculate_risk_score
from src.evidence_checker import check_missing_evidence
from src.next_steps import generate_next_steps
from src.claim_summary import generate_claim_summary

st.set_page_config(
    page_title="ClaimLens",
    page_icon="🛡️",
    layout="wide"
)

st.title("ClaimLens")
st.write("Insurance claim triage assistant for risk scoring and evidence review.")

claim_type = st.selectbox(
    "Claim Type",
    ["Auto", "Theft", "Property", "Health", "Other"]
)

claim_amount = st.number_input(
    "Claim Amount",
    min_value=0
)

incident_description = st.text_area(
    "Incident Description"
)

evidence_uploaded = st.checkbox("Evidence uploaded")
police_report_available = st.checkbox("Police report available")
photos_available = st.checkbox("Photos available")
injury_involved = st.checkbox("Injury involved")
conflicting_statements = st.checkbox("Conflicting statements")
previous_claims = st.checkbox("Previous claims")

if st.button("Analyze Claim"):
    risk_score, risk_level, red_flags = calculate_risk_score(
        claim_type,
        claim_amount,
        evidence_uploaded,
        police_report_available,
        photos_available,
        injury_involved,
        conflicting_statements,
        previous_claims
    )

    st.subheader("Risk Assessment")

    st.metric("Risk Score", risk_score)
    st.metric("Risk Level", risk_level)

    st.subheader("Red Flags")

    if red_flags:
        for flag in red_flags:
            st.warning(flag)
    else:
        st.success("No major red flags detected.")
    
    missing_evidence = check_missing_evidence(
        claim_type,
        evidence_uploaded,
        police_report_available,
        photos_available,
        injury_involved
    )
    st.subheader("Missing Evidence")

    if missing_evidence:
        for missing in missing_evidence:
            st.warning(missing)
    else:
        st.success("No missing evidence detected")

    next_steps = generate_next_steps(
        risk_level,
        red_flags,
        missing_evidence
    )
    st.subheader("Next steps")
    if next_steps:
        for steps in next_steps:
            st.info(steps)
    else:
        st.success("No further steps to take")

    claim_summary = generate_claim_summary(
    claim_type,
    claim_amount,
    incident_description,
    risk_score,
    risk_level,
    red_flags,
    missing_evidence,
    next_steps
    )

    st.subheader("Claim Summary")
    st.write(claim_summary)