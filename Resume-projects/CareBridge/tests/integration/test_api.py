from fastapi.testclient import TestClient
from apps.api.main import app

client = TestClient(app)


def test_demo_workflow_and_score():
    response = client.get("/api/demo")
    assert response.status_code == 200
    body = response.json()
    assert body["patient"]["synthetic"] is True
    assert body["preparationScore"] == 67


def test_cited_follow_up_answer():
    response = client.post("/api/assistant", json={"question": "Which report mentioned my follow-up date?"})
    assert response.status_code == 200
    assert response.json()["citations"]


def test_unsafe_question_refused():
    response = client.post("/api/assistant", json={"question": "What medication should I take?"})
    assert response.json()["allowed"] is False


def test_document_upload_validation():
    assert client.post("/api/documents", files={"file": ("lab.txt", b"synthetic result")}).status_code == 200
    assert client.post("/api/documents", files={"file": ("bad.exe", b"x")}).status_code == 400

