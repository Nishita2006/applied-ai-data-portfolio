from io import BytesIO
from pypdf import PdfReader
MAX_FILE_BYTES=10*1024*1024
class DocumentError(ValueError): pass
def extract_text(data: bytes,filename: str)->tuple[str,str]:
    if not data: raise DocumentError("The selected file is empty.")
    if len(data)>MAX_FILE_BYTES: raise DocumentError("The file is larger than the 10 MB limit.")
    suffix=filename.lower().rsplit(".",1)[-1]
    if suffix=="txt": text=data.decode("utf-8",errors="replace").strip(); mime="text/plain"
    elif suffix=="pdf":
        try:
            reader=PdfReader(BytesIO(data))
            if reader.is_encrypted: raise DocumentError("Encrypted PDFs are not supported. Please upload an unlocked copy.")
            text="\n\n".join((p.extract_text() or "").strip() for p in reader.pages).strip(); mime="application/pdf"
        except DocumentError: raise
        except Exception as exc: raise DocumentError("CareBridge could not read this PDF.") from exc
        if not text: raise DocumentError("No selectable text was found. This may be a scanned PDF; OCR is not currently available.")
    else: raise DocumentError("Unsupported file type. Upload a TXT or PDF file.")
    if not text: raise DocumentError("No readable text was found in this file.")
    return text,mime
