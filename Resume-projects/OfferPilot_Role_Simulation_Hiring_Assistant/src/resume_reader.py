from pypdf import PdfReader


def extract_text_from_pdf(uploaded_file):
    reader = PdfReader(uploaded_file)
    resume_text = ""

    # Read each page and collect text
    for page in reader.pages:
        page_text = page.extract_text()

        if page_text:
            resume_text += page_text + "\n"

    return resume_text.strip()