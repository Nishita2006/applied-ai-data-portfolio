import re
from difflib import SequenceMatcher
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


SKILL_ALIASES = {
    "apis": ["api", "rest api", "restful services", "web services", "endpoint development"],
    "api": ["apis", "rest api", "restful services", "web services", "endpoint development"],
    "machine learning": ["ml", "predictive modeling", "statistical learning", "model training"],
    "natural language processing": ["nlp", "text analytics", "language models", "text mining"],
    "nlp": ["natural language processing", "text analytics", "language models", "text mining"],
    "data analysis": ["analytics", "data analytics", "analyzed data", "exploratory analysis", "eda"],
    "problem solving": ["troubleshooting", "root cause analysis", "debugging", "resolved issues"],
    "communication": ["presented", "stakeholder communication", "technical writing", "explained"],
    "collaboration": ["teamwork", "cross-functional", "partnered", "worked with"],
    "teamwork": ["collaboration", "cross-functional", "partnered", "worked with"],
    "leadership": ["led", "mentored", "managed", "owned", "coordinated"],
    "recruitment": ["recruiting", "talent acquisition", "candidate sourcing", "hiring"],
    "human resources": ["hr", "people operations", "people ops", "employee relations"],
    "power bi": ["powerbi", "microsoft power bi", "business intelligence dashboards"],
    "javascript": ["js", "ecmascript", "node.js", "nodejs"],
    "git": ["github", "gitlab", "version control", "source control"],
    "aws": ["amazon web services", "ec2", "s3", "lambda"],
    "azure": ["microsoft azure", "azure functions", "azure devops"],
    "docker": ["containers", "containerization", "containerised", "containerized"],
}

SKILL_CANONICAL = {
    "apis": "api",
}

RELATED_EVIDENCE = {
    "data analysis": [
        "analyzing prediction",
        "analysing prediction",
        "measuring accuracy",
        "evaluated detection performance",
        "evaluation metrics",
        "data science",
        "analyzed confidence",
        "analysed confidence",
    ],
}

NEGATION_PATTERNS = [
    r"\bno experience (?:with|in)\b",
    r"\bnot (?:experienced|familiar|proficient) (?:with|in)\b",
    r"\b(?:limited|little) experience (?:with|in)\b",
    r"\bcurrently learning\b",
]


def split_evidence_sentences(text):
    return [
        part.strip(" -•\t")
        for part in re.split(r"(?<=[.!?])\s+|[\r\n•]+", str(text or ""))
        if len(part.strip()) >= 8
    ]


def get_skill_aliases(skill):
    normalized = normalize_skill(skill)
    aliases = [normalized] + SKILL_ALIASES.get(normalized, [])
    return list(dict.fromkeys(normalize_text(alias) for alias in aliases if alias))


def _phrase_present(phrase, text):
    return re.search(r"(?<![a-z0-9])" + re.escape(phrase) + r"(?![a-z0-9])", text) is not None


def _is_negated(sentence, phrase):
    lowered = normalize_text(sentence)
    if not _phrase_present(phrase, lowered):
        return False
    phrase_start = lowered.find(phrase)
    prefix = lowered[max(0, phrase_start - 55):phrase_start]
    return any(re.search(pattern, prefix + phrase) for pattern in NEGATION_PATTERNS)


def match_skill_to_resume(skill, resume_text):
    """Return an explainable exact, synonym, related-term, or missing match."""
    normalized_skill = normalize_skill(skill)
    aliases = get_skill_aliases(skill)
    sentences = split_evidence_sentences(resume_text)

    for sentence in sentences:
        normalized_sentence = normalize_text(sentence)
        for alias in aliases:
            if _phrase_present(alias, normalized_sentence) and not _is_negated(sentence, alias):
                match_type = "Exact" if alias == normalized_skill else "Synonym"
                return {
                    "skill": normalized_skill,
                    "status": "Matched",
                    "match_type": match_type,
                    "matched_term": alias,
                    "confidence": 100 if match_type == "Exact" else 90,
                    "evidence": sentence,
                }

    for related_phrase in RELATED_EVIDENCE.get(normalized_skill, []):
        for sentence in sentences:
            if related_phrase in normalize_text(sentence):
                return {
                    "skill": normalized_skill,
                    "status": "Partial",
                    "match_type": "Contextual evidence",
                    "matched_term": related_phrase,
                    "confidence": 70,
                    "evidence": sentence,
                }

    # Conservative lexical matching catches close variants such as analyse/analyzed.
    affirmative_text = " ".join(
        sentence
        for sentence in sentences
        if not any(
            re.search(pattern, normalize_text(sentence))
            for pattern in NEGATION_PATTERNS
        )
    )
    resume_tokens = set(normalize_text(affirmative_text).split())
    skill_tokens = normalized_skill.split()
    best_term, best_ratio = "", 0.0
    for token in resume_tokens:
        if len(token) < 5:
            continue
        for skill_token in skill_tokens:
            ratio = SequenceMatcher(None, token, skill_token).ratio()
            if ratio > best_ratio:
                best_term, best_ratio = token, ratio
    if best_ratio >= 0.84:
        evidence = next(
            (
                sentence
                for sentence in sentences
                if best_term in normalize_text(sentence)
                and not any(
                    re.search(pattern, normalize_text(sentence))
                    for pattern in NEGATION_PATTERNS
                )
            ),
            "Related wording detected in the resume.",
        )
        return {
            "skill": normalized_skill,
            "status": "Partial",
            "match_type": "Related wording",
            "matched_term": best_term,
            "confidence": round(best_ratio * 80),
            "evidence": evidence,
        }

    return {
        "skill": normalized_skill,
        "status": "Missing evidence",
        "match_type": "None",
        "matched_term": "",
        "confidence": 0,
        "evidence": "No role-relevant evidence detected. Validate during structured review.",
    }


def build_contextual_match_report(skills, resume_text):
    matches = [match_skill_to_resume(skill, resume_text) for skill in normalize_skill_list(skills)]
    if not matches:
        return {"score": 0, "matches": [], "matched": [], "partial": [], "missing": []}
    weights = {"Matched": 1.0, "Partial": 0.5, "Missing evidence": 0.0}
    score = round(100 * sum(weights[item["status"]] for item in matches) / len(matches))
    return {
        "score": score,
        "matches": matches,
        "matched": [item["skill"] for item in matches if item["status"] == "Matched"],
        "partial": [item["skill"] for item in matches if item["status"] == "Partial"],
        "missing": [item["skill"] for item in matches if item["status"] == "Missing evidence"],
    }


def normalize_text(text):
    if text is None:
        return ""

    text = str(text).lower()
    text = re.sub(r"[^a-z0-9+#.\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()

    return text


def normalize_skill(skill):
    normalized = normalize_text(skill)
    return SKILL_CANONICAL.get(normalized, normalized)


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
