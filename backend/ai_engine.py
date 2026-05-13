import fitz
import random

def extract_text_from_pdf(pdf_path):

    doc = fitz.open(pdf_path)

    text = ""

    for page in doc:
        text += page.get_text()

    return text


def generate_ai_metadata(text):

    text_lower = text.lower()

    severity = "Low"
    incident_type = "General"
    department = "Operations"

    # Severity Detection
    if "death" in text_lower or "explosion" in text_lower:
        severity = "Critical"

    elif "chemical" in text_lower or "injury" in text_lower:
        severity = "High"

    elif "minor" in text_lower:
        severity = "Medium"

    # Incident Type
    if "chemical" in text_lower:
        incident_type = "Chemical Leakage"

    elif "fire" in text_lower:
        incident_type = "Fire Accident"

    elif "machine" in text_lower:
        incident_type = "Machine Failure"

    elif "injury" in text_lower:
        incident_type = "Worker Injury"

    # Department
    if "packing" in text_lower:
        department = "Packaging"

    elif "maintenance" in text_lower:
        department = "Maintenance"

    elif "production" in text_lower:
        department = "Production"

    # AI Summary
    summary = text[:300]

    return {
        "severity": severity,
        "incident_type": incident_type,
        "department": department,
        "risk_score": random.randint(70, 98),
        "summary": summary
    }