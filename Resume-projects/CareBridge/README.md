# CareBridge — Patient Visit Preparation Assistant

CareBridge helps a user organize an upcoming healthcare visit from a clean, private-by-design workspace: appointment details, readiness tasks, symptoms in the user's own words, medications, allergies, records, provider questions, and a reviewed visit brief.

**Live application:** https://carebridge-ai.streamlit.app/

CareBridge supports preparation and communication. It does not diagnose, triage, recommend treatment, or advise medication changes. The public deployment is a portfolio project and is not certified for protected health information.

## Workflow

Create a visit → complete readiness tasks → record symptoms → add medications and allergies → upload TXT/PDF records → confirm document categories → ask source-grounded record questions → prepare provider questions → review and confirm the visit brief → export PDF or JSON.

All end-user content comes from the user. A new database starts empty.

## Architecture and stack

- Streamlit UI in `app.py`
- Supabase Auth, PostgreSQL, private Storage, and Row Level Security for deployed persistence
- Repository boundary in `src/store.py`; SQLite is available only when explicit local-development mode is enabled
- TXT/PDF extraction in `src/documents.py`
- Cached TF-IDF/logistic-regression document routing in `src/ml.py`
- Local TF-IDF retrieval with citations in `src/rag.py`
- Optional evidence-only Groq composition using the official Groq SDK
- Matplotlib PDF generation in `src/export.py`
- Pytest and Streamlit AppTest coverage in `tests/`

## Local setup

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pip install -r requirements-dev.txt
streamlit run app.py
```

Run tests with:

```powershell
pytest
```

For isolated SQLite development without authentication, set `CAREBRIDGE_LOCAL_MODE=true`. Never enable local mode on a public deployment.

## Supabase setup

1. Create a Supabase project.
2. Run `sql/supabase_schema.sql` once in the Supabase SQL Editor.
3. In Supabase Authentication, keep email/password enabled and configure the Site URL and redirect URLs for the deployed Streamlit address.
4. Add the following Streamlit secrets:

```toml
SUPABASE_URL = "https://your-project.supabase.co"
SUPABASE_ANON_KEY = "your publishable or anon key"
```

Never use a Supabase service-role key in this application. Without Supabase configuration, the public marketing page remains visible but account and workspace creation are disabled.

## Optional environment configuration

Set the API key as an environment variable or Streamlit secret to enable the optional grounded response composer. The model setting is optional:

```toml
GROQ_API_KEY = "..."
GROQ_MODEL = "llama-3.1-8b-instant"
```

CareBridge sends only the question and locally retrieved excerpts, not the full database or all records. If configuration or the Groq call fails, it falls back to local retrieval. When `GROQ_MODEL` is omitted, CareBridge uses `llama-3.1-8b-instant`.

## Deployment

Deploy `app.py` on Streamlit Community Cloud after applying `sql/supabase_schema.sql` and adding Supabase secrets. The deployed application uses Supabase rather than Streamlit local disk. Uploaded files are stored in the private `carebridge-records` bucket using `user_id/visit_id/document_id/filename` paths.

## Responsible AI design

- Retrieval answers use only saved record excerpts and display source, passage, and relevance.
- Insufficient evidence produces an explicit non-answer.
- Document confidence describes routing only, never medical certainty.
- User symptom wording is stored without clinical rewriting.
- Emergency-type language receives a concise direction to immediate professional help; CareBridge does not triage.
- Export is unavailable until the user explicitly confirms the brief.

## Current limitations

- Supabase must be configured and the supplied RLS migration applied before account and workspace functionality is available.
- A hard browser refresh may require sign-in again because Streamlit does not provide this app with a secure browser-cookie session adapter; persisted account data remains available after signing in.
- Real multi-user/RLS verification must be completed against the configured Supabase project before public launch.
- PDF extraction supports selectable text; scanned PDFs need OCR before upload.
- The small document classifier covers broad administrative record categories and requires user confirmation.
- Optional Groq behavior requires a valid API key and network access and automatically falls back to local retrieval.
- Clinical, security, accessibility, and regulatory validation would be required before healthcare production use.
