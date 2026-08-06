import re

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


VAGUE_PHRASES = [
    "we did", "helped with", "worked on", "various tasks", "responsible for",
    "used ai", "used tools", "best practices", "etc",
]
OWNERSHIP_TERMS = [
    "i built", "i designed", "i implemented", "i decided", "i tested",
    "i measured", "i fixed", "my responsibility", "i owned",
]
EVIDENCE_TERMS = [
    "because", "for example", "result", "increased", "reduced", "measured",
    "tradeoff", "failed", "debugged", "%", "users", "records",
]


def _similarity(first, second):
    if not str(first or "").strip() or not str(second or "").strip():
        return 0
    vectors = TfidfVectorizer(stop_words="english", ngram_range=(1, 2)).fit_transform(
        [str(first), str(second)]
    )
    return round(cosine_similarity(vectors[0:1], vectors[1:2])[0][0] * 100)


def analyze_interview_transcript(transcript, resume_text="", role_skills=None):
    """Create review signals from objective answer content, never a deception verdict."""
    text = re.sub(r"\s+", " ", str(transcript or "")).strip()
    lowered = text.lower()
    word_count = len(text.split())
    ownership_hits = sum(term in lowered for term in OWNERSHIP_TERMS)
    evidence_hits = sum(term in lowered for term in EVIDENCE_TERMS)
    vague_hits = [term for term in VAGUE_PHRASES if term in lowered]
    number_hits = len(re.findall(r"\b\d+(?:\.\d+)?%?\b", text))
    role_skills = role_skills or []
    supported_skills = [skill for skill in role_skills if skill.lower() in lowered]

    review_flags = []
    if word_count < 40:
        review_flags.append("Transcript is too short for meaningful evidence review.")
    if vague_hits:
        review_flags.append("Some answers use broad wording that needs concrete follow-up.")
    if ownership_hits == 0:
        review_flags.append("Individual ownership is unclear; ask what the candidate personally did.")
    if evidence_hits + number_hits < 2:
        review_flags.append("Few examples, outcomes, or tradeoffs were detected.")

    evidence_score = min(100, 20 + ownership_hits * 12 + evidence_hits * 7 + number_hits * 5)
    specificity_score = max(0, min(100, 35 + evidence_hits * 8 + number_hits * 7 - len(vague_hits) * 8))
    return {
        "word_count": word_count,
        "resume_similarity": _similarity(text, resume_text),
        "evidence_score": evidence_score,
        "specificity_score": specificity_score,
        "supported_skills": supported_skills,
        "review_flags": review_flags,
        "follow_ups": build_follow_up_questions(review_flags, supported_skills),
    }


def build_follow_up_questions(review_flags, supported_skills):
    questions = [
        "Choose one claim you made and walk through exactly what you personally implemented.",
        "What failed the first time, and what evidence led you to the fix?",
        "What measurable result changed because of your work, and how was it measured?",
        "If one project constraint changed today, what would you do differently and why?",
    ]
    if supported_skills:
        questions.insert(0, f"Sketch the workflow where you used {supported_skills[0]} and explain each decision.")
    return questions[:5]
