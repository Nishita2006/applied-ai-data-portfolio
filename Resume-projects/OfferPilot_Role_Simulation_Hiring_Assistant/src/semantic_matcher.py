import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def normalize_text(text):
    if text is None:
        return ""

    text = str(text).lower()
    text = re.sub(r"[^a-z0-9+#.\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()

    return text


def normalize_skill(skill):
    return normalize_text(skill)


def normalize_skill_list(skills):
    cleaned = []

    for skill in skills:
        normalized = normalize_skill(skill)

        if normalized and normalized not in cleaned:
            cleaned.append(normalized)

    return cleaned


def calculate_skill_overlap_score(jd_skills, resume_skills):
    """
    Calculates exact normalized skill overlap.
    """

    jd_skills = normalize_skill_list(jd_skills)
    resume_skills = normalize_skill_list(resume_skills)

    if len(jd_skills) == 0:
        return [], [], 0

    matched_skills = []

    for skill in jd_skills:
        if skill in resume_skills:
            matched_skills.append(skill)

    missing_skills = []

    for skill in jd_skills:
        if skill not in matched_skills:
            missing_skills.append(skill)

    score = round((len(matched_skills) / len(jd_skills)) * 100)

    return matched_skills, missing_skills, score


def calculate_text_similarity_score(job_description, resume_text):
    """
    Calculates text similarity between JD and resume using TF-IDF.
    This behaves like a lightweight local embedding-style similarity.
    """

    job_description = normalize_text(job_description)
    resume_text = normalize_text(resume_text)

    if job_description == "" or resume_text == "":
        return 0

    vectorizer = TfidfVectorizer(stop_words="english")
    vectors = vectorizer.fit_transform([job_description, resume_text])

    similarity = cosine_similarity(vectors[0:1], vectors[1:2])[0][0]

    return round(similarity * 100)


def calculate_hybrid_candidate_score(
    job_description,
    resume_text,
    jd_skills,
    resume_skills
):
    """
    Combines skill overlap and text similarity.
    This gives fairer scores than exact skill matching alone.
    """

    matched_skills, missing_skills, skill_score = calculate_skill_overlap_score(
        jd_skills,
        resume_skills
    )

    text_similarity_score = calculate_text_similarity_score(
        job_description,
        resume_text
    )

    final_score = round((0.65 * skill_score) + (0.35 * text_similarity_score))

    return {
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "skill_score": skill_score,
        "text_similarity_score": text_similarity_score,
        "final_score": final_score
    }


def get_review_priority(score):
    if score >= 75:
        return "High Review"
    elif score >= 40:
        return "Medium Review"
    else:
        return "Low Review"
    

def remove_negative_skill_sentences(text):
    """
    Removes sentences where the candidate is saying they do NOT have
    or have limited experience with certain skills.
    This prevents weak resumes from falsely matching required skills.
    """

    if text is None:
        return ""

    negative_phrases = [
        "limited experience",
        "limited technical experience",
        "no experience",
        "little experience",
        "lack experience",
        "lacks experience",
        "not experienced",
        "not familiar",
        "unfamiliar",
        "weak in",
        "missing experience",
        "does not have experience",
        "do not have experience"
    ]

    sentences = re.split(r"(?<=[.!?])\s+", str(text))

    cleaned_sentences = []

    for sentence in sentences:
        sentence_lower = sentence.lower()

        has_negative_phrase = any(
            phrase in sentence_lower for phrase in negative_phrases
        )

        if not has_negative_phrase:
            cleaned_sentences.append(sentence)

    return " ".join(cleaned_sentences)

def find_jd_skills_in_resume_text(jd_skills, resume_text):
    """
    Directly checks whether JD skills appear in the resume text.
    This helps catch skills that the rule-based extractor may miss.
    """

    resume_text = normalize_text(resume_text)
    found_skills = []

    for skill in jd_skills:
        normalized_skill = normalize_skill(skill)

        if normalized_skill in resume_text:
            found_skills.append(normalized_skill)

    return normalize_skill_list(found_skills)