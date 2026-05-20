import fitz
from docx import Document
import pandas as pd


def extract_text(file_path):

    text = ""

    # PDF SUPPORT
    if file_path.endswith(".pdf"):

        doc = fitz.open(file_path)

        for page in doc:
            text += page.get_text()

    # DOCX SUPPORT
    elif file_path.endswith(".docx"):

        doc = Document(file_path)

        for para in doc.paragraphs:
            text += para.text + "\n"

    # EXCEL SUPPORT
    elif file_path.endswith(".xlsx"):

        df = pd.read_excel(file_path)

        text = df.to_string()

    # TXT SUPPORT
    elif file_path.endswith(".txt"):

        with open(file_path, "r", encoding="utf-8") as file:
            text = file.read()

    return text


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