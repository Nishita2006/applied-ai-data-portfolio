from pypdf import PdfReader


def extract_text_from_pdf(uploaded_file):
    reader = PdfReader(uploaded_file)
    resume_text = ""
    links = []

    # Read each page and collect text
    for page in reader.pages:
        page_text = page.extract_text()

        if page_text:
            resume_text += page_text + "\n"

        # Many resumes display "LinkedIn" or "GitHub" while storing the real URL
        # only in a PDF link annotation. Include those URIs in the extracted text.
        annotations = page.get("/Annots") or []
        for annotation_ref in annotations:
            try:
                annotation = annotation_ref.get_object()
                action = annotation.get("/A") or {}
                uri = action.get("/URI")
                if uri and str(uri) not in links:
                    links.append(str(uri))
            except Exception:
                continue

    if links:
        resume_text += "\nProfile links:\n" + "\n".join(links)

    return resume_text.strip()
