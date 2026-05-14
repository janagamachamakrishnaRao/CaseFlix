from ai_engine import extract_text_from_pdf, generate_ai_metadata
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from database import SessionLocal, engine
from models import Incident
from database import Base
from sqlalchemy import or_
import shutil
import os
import subprocess
from fastapi import HTTPException
from pydantic import BaseModel
from auth import (
    hash_password,
    verify_password,
    create_access_token
)
from models import User

Base.metadata.create_all(bind=engine)


app = FastAPI()

class UserAuth(BaseModel):
    username: str
    password: str

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Allow frontend connection
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://case-flix.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_FOLDER = "uploads"

# Create uploads folder if not exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.get("/")
def home():
    return {"message": "CaseFlix Backend Running"}

@app.post("/register")
def register(user: UserAuth):

    db = SessionLocal()

    existing_user = db.query(User).filter(
        User.username == user.username
    ).first()

    if existing_user:
        db.close()
        raise HTTPException(
            status_code=400,
            detail="Username already exists"
        )

    hashed = hash_password(user.password)

    new_user = User(
        username=user.username,
        password=hashed
    )

    db.add(new_user)
    db.commit()
    db.close()

    return {
        "message": "User registered successfully"
    }

@app.post("/login")
def login(user: UserAuth):

    db = SessionLocal()

    existing_user = db.query(User).filter(
        User.username == user.username
    ).first()

    if not existing_user:
        db.close()
        raise HTTPException(
            status_code=401,
            detail="Invalid username"
        )

    valid = verify_password(
        user.password,
        existing_user.password
    )

    if not valid:
        db.close()
        raise HTTPException(
            status_code=401,
            detail="Invalid password"
        )

    token = create_access_token(
        data={
            "sub": existing_user.username,
            "role": existing_user.role
        }
    )

    db.close()

    return {
        "access_token": token,
        "role": existing_user.role,
        "username": existing_user.username
    }

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):

    file_path = os.path.join(UPLOAD_FOLDER, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # DOCX Conversion
    if file.filename.endswith(".docx"):

        subprocess.run([
            "libreoffice",
            "--headless",
            "--convert-to",
            "pdf",
            file_path,
            "--outdir",
            UPLOAD_FOLDER
        ])

        pdf_filename = file.filename.replace(".docx", ".pdf")

        file_path = os.path.join(UPLOAD_FOLDER, pdf_filename)

        filename = pdf_filename

    else:

        filename = file.filename



    text = extract_text_from_pdf(file_path)

    metadata = generate_ai_metadata(text)
    db = SessionLocal()

    new_incident = Incident(
        filename=filename,
        severity=metadata["severity"],
        incident_type=metadata["incident_type"],
        department=metadata["department"],
        risk_score=metadata["risk_score"],
        summary=metadata["summary"]
    )

    db.add(new_incident)
    db.commit()
    db.close()


    return {
        "filename": filename,
        "message": "File processed successfully",
        "metadata": metadata
    }

@app.get("/files")
def get_files():

    db = SessionLocal()

    incidents = db.query(Incident).all()

    results = []

    for item in incidents:

        results.append({
            "filename": item.filename,
            "metadata": {
                "severity": item.severity,
                "incident_type": item.incident_type,
                "department": item.department,
                "risk_score": item.risk_score,
                "summary": item.summary
            }
        })

    db.close()

    return {"files": results}

@app.get("/related/{filename}")
def get_related_cases(filename: str):

    db = SessionLocal()

    current_case = db.query(Incident).filter(
        Incident.filename == filename
    ).first()

    if not current_case:
        db.close()
        return {"related": []}

    related_cases = db.query(Incident).filter(
        Incident.incident_type == current_case.incident_type,
        Incident.filename != filename
    ).limit(4).all()

    results = []

    for item in related_cases:

        results.append({
            "filename": item.filename,
            "metadata": {
                "incident_type": item.incident_type,
                "department": item.department,
                "severity": item.severity,
                "risk_score": item.risk_score,
                "summary": item.summary
            }
        })

    db.close()

    return {"related": results}

@app.get("/search/{query}")
def search_cases(query: str):

    db = SessionLocal()

    results = db.query(Incident).filter(

        or_(

            Incident.filename.ilike(f"%{query}%"),
            Incident.incident_type.ilike(f"%{query}%"),
            Incident.department.ilike(f"%{query}%"),
            Incident.summary.ilike(f"%{query}%")

        )

    ).all()

    final_results = []

    for item in results:

        final_results.append({

            "filename": item.filename,

            "metadata": {

                "severity": item.severity,
                "incident_type": item.incident_type,
                "department": item.department,
                "risk_score": item.risk_score,
                "summary": item.summary

            }

        })

    db.close()

    return {"results": final_results}

