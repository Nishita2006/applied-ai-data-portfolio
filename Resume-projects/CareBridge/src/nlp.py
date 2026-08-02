from __future__ import annotations

import re
from collections import Counter

STOPWORDS = {"about", "after", "again", "been", "during", "from", "have", "into", "most", "that", "their", "this", "when", "with", "would"}
BLOCKED = (r"what (?:disease|condition|illness) do i have", r"(?:what|which) medication should i take", r"(?:can|should) i stop", r"do i need surgery", r"is (?:this|my) symptom harmless")
EMERGENCY = (r"chest pain", r"cannot breathe", r"can't breathe", r"unconscious", r"suicid")


def keywords(text: str, limit: int = 6) -> list[str]:
    tokens = re.findall(r"[a-zA-Z][a-zA-Z-]{3,}", text.lower())
    return [word for word, _ in Counter(t for t in tokens if t not in STOPWORDS).most_common(limit)]


def organize_symptom(text: str) -> dict:
    clean = " ".join(text.split())
    return {"original": text, "organized": clean[:1].upper() + clean[1:] if clean else "", "keywords": keywords(text), "verified": False}


def safety_check(question: str) -> tuple[bool, str]:
    lowered = question.lower()
    if any(re.search(pattern, lowered) for pattern in EMERGENCY):
        return False, "CareBridge cannot assess emergencies. Contact local emergency services or seek immediate professional help now."
    if any(re.search(pattern, lowered) for pattern in BLOCKED):
        return False, "I can organize records and prepare questions, but I cannot diagnose, recommend treatment, or advise medication changes. Please ask a qualified healthcare professional."
    return True, ""

