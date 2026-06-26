ROLE_SKILLS = [
    # Software / technical skills
    "python", "sql", "java", "javascript", "c++", "git", "github",
    "excel", "tableau", "power bi", "machine learning", "data analysis",
    "pandas", "numpy", "streamlit", "sqlite", "apis", "api",
    "aws", "azure", "docker",

    # HR / people operations skills
    "human resources", "hr", "recruitment", "workforce development",
    "employee relations", "performance management", "talent acquisition",
    "training", "onboarding", "continuous improvement", "quality",

    # Product / business skills
    "product", "strategy", "customer", "market research",
    "business analytics", "dashboard", "metrics",

    # Finance / risk skills
    "risk", "fraud", "financial", "credit", "compliance"
]


SOFT_SKILLS = [
    "communication", "collaboration", "teamwork", "leadership",
    "problem solving", "analytical thinking", "critical thinking",
    "attention to detail", "presentation", "adaptability",
    "empowerment", "management", "employee-oriented",
    "high performance culture", "development"
]


def jd_skill_extractor(description):
    text = description.lower()

    found_role_skills = []
    found_soft_skills = []

    # Find role-specific skills
    for skill in ROLE_SKILLS:
        if skill in text:
            found_role_skills.append(skill)

    # Find soft skills
    for skill in SOFT_SKILLS:
        if skill in text:
            found_soft_skills.append(skill)

    return found_role_skills, found_soft_skills


def role_category(description):
    job_description = description.lower()

    if (
        "machine learning" in job_description
        or "data science" in job_description
        or "model" in job_description
        or "nlp" in job_description
    ):
        category = "AI / ML"

    elif (
        "sql" in job_description
        or "dashboard" in job_description
        or "analytics" in job_description
        or "tableau" in job_description
        or "power bi" in job_description
        or "data analysis" in job_description
    ):
        category = "Data / Analytics"

    elif (
        "software" in job_description
        or "backend" in job_description
        or "frontend" in job_description
        or "api" in job_description
        or "java" in job_description
        or "developer" in job_description
    ):
        category = "Software Engineering"

    elif (
        "risk" in job_description
        or "fraud" in job_description
        or "financial" in job_description
        or "credit" in job_description
        or "compliance" in job_description
    ):
        category = "Finance / Risk"

    elif (
        "human resources" in job_description
        or "hr" in job_description
        or "recruitment" in job_description
        or "employee relations" in job_description
        or "workforce" in job_description
        or "talent acquisition" in job_description
    ):
        category = "HR / People Operations"

    elif (
        "product" in job_description
        or "strategy" in job_description
        or "customer" in job_description
        or "market research" in job_description
    ):
        category = "Product / Business"

    else:
        category = "General Internship"

    return category