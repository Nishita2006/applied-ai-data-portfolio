from pathlib import Path

from streamlit.testing.v1 import AppTest


PAGES = [
    "Overview",
    "Visit Readiness",
    "Symptoms & Timeline",
    "Document Intelligence",
    "Records Assistant",
    "Visit Brief",
]


def test_every_page_renders_without_secrets_or_runtime_errors():
    app_path = Path(__file__).resolve().parents[1] / "app.py"
    app = AppTest.from_file(str(app_path), default_timeout=30).run()
    assert not app.exception
    assert len(app.radio) == 1
    assert any("Welcome back, Maya" in item.value for item in app.markdown)
    assert not any("What this demonstrates" in item.value for item in app.markdown)
    assert not any("demo" in item.value.lower() for item in app.markdown)

    for page in PAGES:
        app.radio[0].set_value(page).run()
        assert not app.exception, f"{page}: {app.exception}"
        assert not app.error, f"{page}: {app.error}"
