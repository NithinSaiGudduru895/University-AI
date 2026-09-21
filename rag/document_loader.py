import os
from pypdf import PdfReader
from docx import Document

def extract_document(path):
    ext = path.rsplit(".", 1)[-1].lower()

    if ext == "pdf":
        reader = PdfReader(path)
        pages = []
        all_text = []
        for number, page in enumerate(reader.pages, 1):
            text = page.extract_text() or ""
            pages.append({"page": number, "text": text})
            all_text.append(text)
        return "\n".join(all_text), pages

    if ext == "docx":
        doc = Document(path)
        text = "\n".join(p.text for p in doc.paragraphs)
        return text, [{"page": None, "text": text}]

    if ext == "txt":
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            text = f.read()
        return text, [{"page": None, "text": text}]

    raise ValueError("Unsupported document type")
