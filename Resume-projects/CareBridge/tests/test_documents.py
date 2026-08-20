from io import BytesIO
import pytest
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.figure import Figure
from src.documents import DocumentError, extract_text
def test_txt_extracts(): assert extract_text(b"Referral appointment date", "record.txt")[0].startswith("Referral")
def test_empty_file_rejected():
    with pytest.raises(DocumentError): extract_text(b"","empty.txt")
def test_unsupported_file_rejected():
    with pytest.raises(DocumentError): extract_text(b"data","record.docx")
def test_text_pdf_extracts():
    buf=BytesIO()
    with PdfPages(buf) as pdf:
        fig=Figure(); fig.subplots().text(.1,.5,"Appointment September 18"); pdf.savefig(fig)
    assert "Appointment" in extract_text(buf.getvalue(),"record.pdf")[0]
