from pathlib import Path
from streamlit.testing.v1 import AppTest
from src.database import create_visit, delete_item, execute, initialize

def test_app_renders_without_runtime_errors():
    initialize(); app=AppTest.from_file(str(Path(__file__).parents[1]/"app.py"),default_timeout=30).run(); assert not app.exception; assert not app.error
    if not app.radio:
        copy=" ".join(item.value for item in app.markdown)
        assert "Ask your records" in copy
        assert "Built around preparation" in copy
        assert "From scattered details" in copy

def test_all_redesigned_pages_render_with_populated_long_content(monkeypatch):
    monkeypatch.setenv("CAREBRIDGE_LOCAL_MODE","true")
    initialize()
    visit_id=create_visit({"appointment_date":"0001-01-01","appointment_time":"09:00","provider":"A provider or clinic with a deliberately long display name","specialty":"Specialty visit","reason":"A long user-entered reason "*20,"location":"","notes":""})
    execute("INSERT INTO symptoms(visit_id,name,onset,severity,frequency,description) VALUES(?,?,?,?,?,?)",(visit_id,"A long symptom description "*5,"Recently",4,"Intermittent","User wording "*40))
    execute("INSERT INTO medications(visit_id,name,dose,frequency) VALUES(?,?,?,?)",(visit_id,"Medication entered by user","10 mg","Daily"))
    execute("INSERT INTO allergies(visit_id,allergy,reaction) VALUES(?,?,?)",(visit_id,"Reported allergy","Reported reaction"))
    execute("INSERT INTO documents(visit_id,title,filename,mime_type,extracted_text,category,category_confirmed) VALUES(?,?,?,?,?,?,1)",(visit_id,"A very long uploaded record filename that must wrap cleanly.pdf","long.pdf","application/pdf","Appointment date is January 1.\n\nReferral information appears here.","Referral"))
    execute("INSERT INTO questions(visit_id,question,priority) VALUES(?,?,1)",(visit_id,"A question the user wants to ask the provider?",))
    try:
        app=AppTest.from_file(str(Path(__file__).parents[1]/"app.py"),default_timeout=30).run()
        assert not app.exception
        for page in ["Overview","Visit Readiness","Symptoms","Medications","Records","Records Assistant","Questions","Visit Brief"]:
            app.radio[0].set_value(page).run()
            assert not app.exception, f"{page}: {app.exception}"
            assert not app.error, f"{page}: {app.error}"
    finally:
        delete_item("visits",visit_id)
