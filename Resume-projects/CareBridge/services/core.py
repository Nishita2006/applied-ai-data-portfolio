"""Deterministic domain services used by the API and tests.

The demo deliberately does not call a model. These helpers show the guardrails,
source labelling, permission checks, and human-verification boundary expected of
the production AI integration.
"""
from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Iterable

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt", ".jpg", ".jpeg", ".png", ".csv"}
BLOCKED_PATTERNS = (
    r"what (?:disease|condition|illness) do i have",
    r"(?:what|which) medication should i take",
    r"(?:can|should) i stop",
    r"do i need surgery",
    r"is (?:this|my) symptom harmless",
)
EMERGENCY_PATTERNS = (r"chest pain", r"can't breathe", r"cannot breathe", r"suicid", r"unconscious")


def readiness_score(items: Iterable[dict]) -> int:
    """Return completed applicable items as a percentage, never a health score."""
    applicable = [item for item in items if item.get("status") != "not_applicable"]
    if not applicable:
        return 0
    complete = sum(item.get("status") == "complete" for item in applicable)
    return round(complete / len(applicable) * 100)


def validate_upload(filename: str, size: int, max_mb: int = 10) -> tuple[bool, str]:
    suffix = "." + filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if suffix not in ALLOWED_EXTENSIONS:
        return False, "Unsupported file type"
    if size > max_mb * 1024 * 1024:
        return False, f"File exceeds {max_mb} MB"
    return True, "accepted"


def can_access(*, owner_id: str, actor_id: str, role: str, permission: dict | None = None) -> bool:
    if role == "admin":
        return True
    if actor_id == owner_id:
        return True
    if not permission or permission.get("revoked_at"):
        return False
    expires = permission.get("expires_at")
    if expires and datetime.fromisoformat(expires) < datetime.now(timezone.utc):
        return False
    return permission.get("recipient_user_id") == actor_id


def guard_assistant(question: str) -> dict:
    normalized = question.lower().strip()
    if any(re.search(pattern, normalized) for pattern in EMERGENCY_PATTERNS):
        return {
            "allowed": False,
            "kind": "emergency",
            "answer": "CareBridge cannot assess emergencies. Contact local emergency services or seek immediate professional help now.",
        }
    if any(re.search(pattern, normalized) for pattern in BLOCKED_PATTERNS):
        return {
            "allowed": False,
            "kind": "clinical_limit",
            "answer": "I can organize your records and help prepare questions, but I cannot diagnose, recommend treatment, or advise medication changes. Please ask a qualified healthcare professional.",
        }
    return {"allowed": True, "kind": "administrative"}


def structure_symptom(text: str) -> dict:
    """Demo-only organization: preserves original and requires patient approval."""
    cleaned = " ".join(text.strip().split())
    return {
        "original": text,
        "ai_organized": cleaned[:1].upper() + cleaned[1:] if cleaned else "",
        "source_type": "ai_organized",
        "verified": False,
        "notice": "AI-assisted wording. Compare with your original entry before approving.",
    }


def extract_tasks(instructions: str) -> list[dict]:
    sentences = [s.strip(" -\n") for s in re.split(r"[.;\n]+", instructions) if s.strip()]
    return [
        {"title": sentence, "status": "not_started", "source": "provider_instruction", "verified": False}
        for sentence in sentences
    ]

