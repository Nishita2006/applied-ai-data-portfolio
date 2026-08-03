from pathlib import Path
from src.database import initialize, query


def test_sqlite_seed_and_patient_is_synthetic(tmp_path: Path):
    database = tmp_path / "test.db"
    initialize(database)
    patients = query("SELECT * FROM patients", path=database)
    assert len(patients) == 1
    assert patients.iloc[0].synthetic == 1
    documents = query("SELECT title FROM documents", path=database)
    assert "Demo insurance card" not in documents.title.tolist()
    assert {"Cardiology referral", "Blood panel report", "Primary care visit summary", "Insurance card"} == set(documents.title)
