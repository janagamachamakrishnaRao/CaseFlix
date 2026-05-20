import fitz
import random
from docx import Document


def extract_text(file_path):

    # PDF SUPPORT
    if file_path.endswith(".pdf"):

        doc = fitz.open(file_path)

        text = ""

        for page in doc:
            text += page.get_text()

        return text

    # DOCX SUPPORT
    elif file_path.endswith(".docx"):

        doc = Document(file_path)

        text = ""

        for para in doc.paragraphs:
            text += para.text + "\n"

        return text

    return ""


def generate_ai_metadata(text):

    text_lower = text.lower()

    incident_type = "General"

    # Incident Type
    if "chemical" in text_lower:
        incident_type = "Chemical Leakage"

    elif "fire" in text_lower:
        incident_type = "Fire Accident"

    elif "machine" in text_lower:
        incident_type = "Machine Failure"

    elif "injury" in text_lower:
        incident_type = "Worker Injury"

    # AI Summary
    summary = text[:300]

    return {
        "incident_type": incident_type,
        "summary": summary
    }