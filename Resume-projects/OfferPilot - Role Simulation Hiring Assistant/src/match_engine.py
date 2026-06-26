def calculate_match_score(jd_skills, resume_skills):
    matched_skills = []
    missing_skills = []

    # Find which JD skills are present or missing in the resume
    for skill in jd_skills:
        if skill in resume_skills:
            matched_skills.append(skill)
        else:
            missing_skills.append(skill)

    if len(jd_skills) == 0:
        match_score = 0
    else:
        match_score = round((len(matched_skills) / len(jd_skills)) * 100, 2)

    return matched_skills, missing_skills, match_score