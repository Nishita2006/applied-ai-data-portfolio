from pathlib import Path
from src.ml import classify_document, classify_document_details
from src.nlp import organize_symptom, safety_check
from src.rag import answer, load_demo_chunks


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


def test_rag_answer_has_citation():
    chunks = load_demo_chunks(Path("demo_data/documents"))
    result = answer("When is the follow-up appointment?", chunks)
    assert result["citations"]
    assert result["evidence"][0]["excerpt"]
    assert 0 <= result["evidence"][0]["score"] <= 1


def test_rag_reports_insufficient_evidence():
    chunks = load_demo_chunks(Path("demo_data/documents"))
    result = answer("What is the parking garage color?", chunks)
    assert "not find enough evidence" in result["answer"]
    assert result["evidence"] == []
