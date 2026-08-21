from pypdf import PdfReader
from io import BytesIO
from src.export import build_visit_pdf
VISIT={"appointment_date":"2026-09-18","appointment_time":"10:30","provider":"Clinic","specialty":"Primary care","reason":"A very long concern "*20,"location":"","notes":""}
def test_valid_pdf_with_missing_optional_values_and_long_text():
    result=build_visit_pdf(VISIT,[],[],[],[],[]); assert result.startswith(b"%PDF"); assert len(PdfReader(BytesIO(result)).pages)>=1
def test_pdf_handles_all_sections():
    result=build_visit_pdf(VISIT,[{"name":"Headache","onset":"recently","severity":4,"description":"Own words"}],[{"name":"Medicine","dose":"","frequency":""}],[{"allergy":"Latex","reaction":"rash"}],[{"title":"Referral","category":"Referral"}],[{"question":"What next?"}]); assert len(result)>5000

def test_long_visit_pdf_paginates_without_placeholder_none():
    long_text="Patient-entered detail "*40
    result=build_visit_pdf({**VISIT,"reason":long_text},[{"name":long_text,"onset":"recently","severity":4,"description":long_text} for _ in range(8)],[],[],[],[{"question":long_text} for _ in range(8)])
    reader=PdfReader(BytesIO(result)); text="\n".join(page.extract_text() or "" for page in reader.pages)
    assert len(reader.pages)>=2
    assert "None" not in text
