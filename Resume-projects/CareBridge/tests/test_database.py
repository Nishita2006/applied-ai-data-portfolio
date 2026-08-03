from pathlib import Path
from src.database import execute, initialize, query


def test_sqlite_seed_and_patient_is_synthetic(tmp_path: Path):
    database = tmp_path / "test.db"
    initialize(database)
    patients = query("SELECT * FROM patients", path=database)
    assert len(patients) == 1
    assert patients.iloc[0].synthetic == 1
    documents = query("SELECT title FROM documents", path=database)
    assert "Demo insurance card" not in documents.title.tolist()
    assert {"Cardiology referral", "Blood panel report", "Primary care visit summary", "Insurance card"} == set(documents.title)


def test_symptom_response_is_saved_without_rewriting(tmp_path: Path):
    database = tmp_path / "test.db"
    initialize(database)
    response = "this moening i didnt feel good"
    execute(
        "INSERT INTO symptom_responses (appointment_id,response_text) VALUES (?,?)",
        (1, response),
        path=database,
    )
    saved = query("SELECT response_text FROM symptom_responses", path=database)
    assert saved.iloc[0].response_text == response
