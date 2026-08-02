from datetime import datetime, timedelta, timezone

from services.core import can_access, extract_tasks, guard_assistant, readiness_score, structure_symptom, validate_upload


def test_readiness_excludes_not_applicable():
    assert readiness_score([{"status": "complete"}, {"status": "not_started"}, {"status": "not_applicable"}]) == 50


def test_upload_validation():
    assert validate_upload("record.pdf", 1024)[0]
    assert not validate_upload("malware.exe", 10)[0]
    assert not validate_upload("huge.pdf", 11 * 1024 * 1024)[0]


def test_diagnostic_and_medication_requests_are_refused():
    assert guard_assistant("What disease do I have?")["kind"] == "clinical_limit"
    assert guard_assistant("Can I stop this prescription?")["allowed"] is False


def test_emergency_language_is_redirected():
    assert guard_assistant("I have chest pain")["kind"] == "emergency"


def test_administrative_question_is_allowed():
    assert guard_assistant("What documents am I missing?")["allowed"]


def test_symptom_original_is_preserved_and_unverified():
    result = structure_symptom("  heartbeat   felt fast ")
    assert result["original"] == "  heartbeat   felt fast "
    assert result["verified"] is False


def test_sharing_revocation_and_expiration():
    active = {"recipient_user_id": "caregiver", "expires_at": (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()}
    assert can_access(owner_id="patient", actor_id="caregiver", role="caregiver", permission=active)
    active["revoked_at"] = datetime.now(timezone.utc).isoformat()
    assert not can_access(owner_id="patient", actor_id="caregiver", role="caregiver", permission=active)


def test_task_extraction_requires_verification():
    tasks = extract_tasks("Call clinic. Bring insurance card.")
    assert len(tasks) == 2
    assert all(task["verified"] is False for task in tasks)

