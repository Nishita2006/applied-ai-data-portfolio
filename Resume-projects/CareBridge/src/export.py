from __future__ import annotations

from io import BytesIO

import pandas as pd
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.figure import Figure


def build_visit_pdf(appointment: pd.Series, symptoms: pd.DataFrame, medications: pd.DataFrame, questions: pd.DataFrame) -> bytes:
    """Create a compact, printable patient-prepared visit brief."""
    buffer = BytesIO()
    with PdfPages(buffer) as pdf:
        figure = Figure(figsize=(8.27, 11.69), facecolor="white")
        axis = figure.subplots()
        axis.axis("off")
        y = .96

        def line(text: str, *, size: int = 10, weight: str = "normal", gap: float = .032) -> None:
            nonlocal y
            axis.text(.07, y, text, fontsize=size, weight=weight, color="#18313b", va="top", wrap=True)
            y -= gap

        line("CareBridge", size=20, weight="bold", gap=.04)
        line("Patient-prepared visit brief", size=13, weight="bold", gap=.045)
        line("FICTIONAL SAMPLE DATA · NOT INDEPENDENTLY VERIFIED", size=8, weight="bold", gap=.05)
        line("Appointment", size=12, weight="bold")
        line(f"{appointment.title} with {appointment.provider}")
        line("September 18, 2026 at 10:30 AM · In person")
        line(f"Main reason: {appointment.reason}", gap=.055)
        line("Symptoms", size=12, weight="bold")
        for row in symptoms.itertuples():
            line(f"• {row.symptom} — started {row.onset_date}; severity {row.severity}/10; {row.pattern}")
        y -= .02
        line("Current medications", size=12, weight="bold")
        for row in medications.itertuples():
            line(f"• {row.name}, {row.strength}, {row.frequency}")
        y -= .02
        line("Priority questions", size=12, weight="bold")
        for row in questions.loc[questions.priority == 1].itertuples():
            line(f"• {row.question}")
        y -= .025
        line("CareBridge supports appointment preparation only. It does not diagnose, recommend treatment, or replace professional medical care.", size=8)
        pdf.savefig(figure, bbox_inches="tight")
    return buffer.getvalue()
