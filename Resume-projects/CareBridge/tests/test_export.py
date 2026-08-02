from src.database import initialize, query
from src.export import build_visit_pdf


def test_visit_brief_is_a_real_pdf():
    initialize()
    appointment = query("SELECT * FROM appointments WHERE id=1").iloc[0]
    symptoms = query("SELECT * FROM symptoms WHERE appointment_id=1")
    medications = query("SELECT * FROM medications WHERE patient_id=1")
    questions = query("SELECT * FROM questions WHERE appointment_id=1")
    result = build_visit_pdf(appointment, symptoms, medications, questions)
    assert result.startswith(b"%PDF")
    assert len(result) > 5_000
