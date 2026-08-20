from pathlib import Path
import sys
from types import SimpleNamespace
from src.ml import classify_document, classify_document_details
from src.nlp import organize_symptom, safety_check
from src.rag import answer, load_record_chunks


def test_ml_document_classifier():
    label, confidence = classify_document("laboratory blood result specimen collected")
    assert label == "Lab result"
    assert 0 <= confidence <= 1


def test_ml_prediction_explains_relevant_features():
    result = classify_document_details("laboratory blood result specimen collected")
    assert result["category"] == "Lab result"
    assert result["features"]


def test_nlp_preserves_original():
    result = organize_symptom("  Felt   tired in afternoons ")
    assert result["original"] == "  Felt   tired in afternoons "
    assert result["verified"] is False


def test_medical_advice_is_refused():
    assert safety_check("Can I stop this prescription?")[0] is False

def test_emergency_language_redirects_without_triage():
    allowed,message=safety_check("I cannot breathe")
    assert allowed is False
    assert "emergency services" in message


def test_rag_answer_has_citation(monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    chunks = load_record_chunks(Path("sample_records"))
    result = answer("When is the follow-up appointment?", chunks)
    assert result["citations"]
    assert result["evidence"][0]["excerpt"]
    assert 0 <= result["evidence"][0]["score"] <= 1


def test_rag_reports_insufficient_evidence(monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    chunks = load_record_chunks(Path("sample_records"))
    result = answer("What is the parking garage color?", chunks)
    assert "not find enough evidence" in result["answer"]
    assert result["evidence"] == []


def test_rag_uses_configured_groq_model_with_grounded_context(monkeypatch):
    captured = {}

    class FakeCompletions:
        def create(self, **kwargs):
            captured["request"] = kwargs
            return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content="The follow-up is documented in the record [1]."))])

    class FakeGroq:
        def __init__(self, **kwargs):
            captured["config"] = kwargs
            self.chat = SimpleNamespace(completions=FakeCompletions())

    monkeypatch.setenv("GROQ_API_KEY", "test-key")
    monkeypatch.setenv("GROQ_MODEL", "test-model")
    monkeypatch.setitem(sys.modules, "groq", SimpleNamespace(Groq=FakeGroq))

    chunks = load_record_chunks(Path("sample_records"))
    result = answer("When is the follow-up appointment?", chunks)

    assert result["mode"] == "Groq grounded composition"
    assert captured["request"]["model"] == "test-model"
    prompt = captured["request"]["messages"][0]["content"]
    assert "Use only the numbered record excerpts" in prompt
    assert "When is the follow-up appointment?" in prompt
    assert "[1]" in result["answer"]

def test_rag_uses_default_groq_model(monkeypatch):
    captured = {}
    class Completions:
        def create(self, **kwargs):
            captured.update(kwargs)
            return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content="Supported [1]."))])
    class FakeGroq:
        def __init__(self, **kwargs): self.chat=SimpleNamespace(completions=Completions())
    monkeypatch.setenv("GROQ_API_KEY", "test-key")
    monkeypatch.delenv("GROQ_MODEL", raising=False)
    monkeypatch.setitem(sys.modules, "groq", SimpleNamespace(Groq=FakeGroq))
    answer("When is the follow-up appointment?", load_record_chunks(Path("sample_records")))
    assert captured["model"] == "llama-3.1-8b-instant"

def test_groq_error_falls_back_to_local_retrieval(monkeypatch):
    class FailingGroq:
        def __init__(self, **kwargs): raise RuntimeError("rate limited")
    monkeypatch.setenv("GROQ_API_KEY", "bad-key")
    monkeypatch.setitem(sys.modules, "groq", SimpleNamespace(Groq=FailingGroq))
    result=answer("When is the follow-up appointment?",load_record_chunks(Path("sample_records")))
    assert result["mode"] == "local TF-IDF retrieval"
    assert result["evidence"]
