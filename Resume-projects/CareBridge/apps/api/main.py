from __future__ import annotations

import json
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, Response
from pydantic import BaseModel, Field

from services.core import extract_tasks, guard_assistant, readiness_score, structure_symptom, validate_upload

ROOT = Path(__file__).resolve().parents[2]
DATA_PATH = ROOT / "demo_data" / "seed_data" / "demo.json"
WEB = ROOT / "apps" / "web"

app = FastAPI(title="CareBridge API", version="1.0.0", description="Non-diagnostic appointment preparation demo")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


def demo_data() -> dict:
    return json.loads(DATA_PATH.read_text(encoding="utf-8"))


class AssistantRequest(BaseModel):
    question: str = Field(min_length=2, max_length=500)


class SymptomRequest(BaseModel):
    text: str = Field(min_length=2, max_length=2000)


class InstructionRequest(BaseModel):
    instructions: str = Field(min_length=2, max_length=4000)


@app.get("/api/health")
def health():
    return {"status": "ok", "safety_mode": "non-diagnostic"}


@app.get("/api/demo")
def get_demo():
    data = demo_data()
    data["preparationScore"] = readiness_score(data["checklist"])
    return data


@app.post("/api/assistant")
def assistant(request: AssistantRequest):
    guard = guard_assistant(request.question)
    if not guard["allowed"]:
        return guard
    data = demo_data()
    q = request.question.lower()
    if "missing" in q or "documents" in q:
        missing = [item["title"] for item in data["checklist"] if item["status"] != "complete"]
        return {"allowed": True, "answer": "Still open: " + "; ".join(missing) + ".", "citations": ["Appointment checklist · current version"], "confidence": "high"}
    if "follow-up" in q or "follow up" in q:
        return {"allowed": True, "answer": "The primary-care summary says to attend the cardiology follow-up on September 18, 2026.", "citations": ["Primary care visit summary · Page 2 · Plan"], "confidence": "high"}
    if "question" in q:
        return {"allowed": True, "answer": "You prepared six questions; three are marked priority.", "citations": ["Patient question list · updated August 22, 2026"], "confidence": "high"}
    return {"allowed": True, "answer": "I can help locate administrative details, organize your timeline, or summarize a selected record. I do not provide diagnoses or treatment advice.", "citations": [], "confidence": "not_applicable"}


@app.post("/api/symptoms/structure")
def organize_symptom(request: SymptomRequest):
    return structure_symptom(request.text)


@app.post("/api/follow-ups/extract")
def tasks(request: InstructionRequest):
    return {"tasks": extract_tasks(request.instructions), "requires_verification": True}


@app.post("/api/documents")
async def upload_document(file: UploadFile = File(...)):
    content = await file.read()
    valid, reason = validate_upload(file.filename or "", len(content))
    if not valid:
        raise HTTPException(status_code=400, detail=reason)
    return {"title": file.filename, "size": len(content), "status": "validated_demo", "notice": "Demo mode validates metadata but does not persist uploads."}


@app.get("/api/summary.pdf")
def summary_pdf():
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas
    except ImportError as exc:
        raise HTTPException(503, "PDF dependency unavailable") from exc
    from io import BytesIO
    data = demo_data()
    stream = BytesIO()
    pdf = canvas.Canvas(stream, pagesize=letter)
    y = 750
    for line in ["CareBridge — Patient-Prepared Visit Summary", "SYNTHETIC DEMO DATA", "", f"Patient: {data['patient']['name']}", f"Visit: {data['appointment']['title']} — September 18, 2026", f"Provider: {data['appointment']['provider']}", "", "Main concern:", data['appointment']['reason'], "", "Not independently verified by a healthcare professional."]:
        pdf.drawString(54, y, line)
        y -= 22
    pdf.save()
    return Response(stream.getvalue(), media_type="application/pdf", headers={"Content-Disposition": "attachment; filename=carebridge-visit-summary.pdf"})


@app.get("/{path:path}")
def web(path: str = ""):
    target = WEB / (path or "index.html")
    if target.is_file() and WEB in target.resolve().parents:
        return FileResponse(target)
    return FileResponse(WEB / "index.html")

