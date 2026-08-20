from __future__ import annotations
from datetime import date
from io import BytesIO
from textwrap import wrap
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.figure import Figure

def build_visit_pdf(visit: dict, symptoms: list[dict], medications: list[dict], allergies: list[dict], documents: list[dict], questions: list[dict]) -> bytes:
    buffer=BytesIO()
    sections=[("Appointment",[f"{visit['appointment_date']} at {visit['appointment_time']}",f"{visit['provider']} — {visit['specialty']}",f"Purpose: {visit['reason']}"] + ([f"Location: {visit['location']}"] if visit.get('location') else [])),
      ("Main concern",[visit['reason']]),
      ("Symptoms",[f"{x['name']} | onset: {x.get('onset') or 'not provided'} | patient-reported severity: {x.get('severity') if x.get('severity') is not None else 'not provided'} | {x.get('description') or ''}" for x in symptoms]),
      ("Medications",[f"{x['name']} | {x.get('dose') or 'dose not provided'} | {x.get('frequency') or 'frequency not provided'}" for x in medications]),
      ("Allergies",[f"{x['allergy']} | reported reaction: {x.get('reaction') or 'not provided'}" for x in allergies]),
      ("Relevant records",[f"{x['title']} | {x.get('category') or 'category unconfirmed'}" for x in documents]),
      ("Questions for provider",[x['question'] for x in questions])]
    pages=[]; lines=[("CareBridge visit brief",18,True),(f"Generated {date.today().isoformat()} · Patient-prepared and reviewed",9,False)]
    for title,items in sections:
        lines.append((title,12,True))
        lines += [("• "+part,9,False) for item in (items or ["None entered"]) for part in wrap(str(item),100)]
    while lines: pages.append(lines[:38]); lines=lines[38:]
    with PdfPages(buffer) as pdf:
        for page in pages:
            fig=Figure(figsize=(8.27,11.69),facecolor="white"); ax=fig.subplots(); ax.axis("off"); y=.95
            for text,size,bold in page: ax.text(.07,y,text,fontsize=size,weight="bold" if bold else "normal",va="top",color="#173a4c"); y-=.035 if size<12 else .048
            ax.text(.07,.035,"Preparation and communication support only — not medical advice.",fontsize=8,color="#61747b")
            pdf.savefig(fig,bbox_inches="tight")
    return buffer.getvalue()
