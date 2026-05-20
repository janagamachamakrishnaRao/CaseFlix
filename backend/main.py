from ai_engine import extract_text, generate_ai_metadata
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from database import SessionLocal, engine
from models import Incident
from database import Base
from sqlalchemy import or_
import shutil
import os
from converter import convert_to_pdf
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
        "http://localhost:5173",
        "http://127.0.0.1:5173",
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
async def upload_file(
    file: UploadFile = File(...),
    department: str = Form(...),
    location: str = Form(...)
):

    original_path = os.path.join(
        UPLOAD_FOLDER,
        file.filename
    )

    with open(original_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # UNIVERSAL CONVERSION
    pdf_file = convert_to_pdf(original_path)

    filename = os.path.basename(pdf_file)

    # EXTRACT TEXT
    text = extract_text(pdf_file)

    metadata = generate_ai_metadata(text)
    db = SessionLocal()
    
    new_incident = Incident(
    filename=filename,
    
    incident_type=metadata["incident_type"],
    department=department,
    location=location,
    
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
                
                "incident_type": item.incident_type,
                "department": item.department,
                "location": item.location,
               
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
                
                "location": item.location,
                
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
            Incident.location.ilike(f"%{query}%"),
            
            Incident.summary.ilike(f"%{query}%")

        )

    ).all()

    final_results = []

    for item in results:

        final_results.append({

            "filename": item.filename,

            "metadata": {

                "incident_type": item.incident_type,
                "department": item.department,
                "location": item.location,
                "summary": item.summary

            }

        })

    db.close()

    return {"results": final_results}
@app.delete("/delete/{filename}")
def delete_case(filename: str):

    db = SessionLocal()

    incident = db.query(Incident).filter(
        Incident.filename == filename
    ).first()

    if not incident:
        db.close()
        raise HTTPException(
            status_code=404,
            detail="Case not found"
        )

    # DELETE FILE
    file_path = os.path.join(
        UPLOAD_FOLDER,
        filename
    )

    if os.path.exists(file_path):
        os.remove(file_path)

    # DELETE DATABASE RECORD
    db.delete(incident)
    db.commit()
    db.close()

    return {
        "message": "Case deleted successfully"
    }

class RenameRequest(BaseModel):
    new_filename: str


@app.put("/rename/{filename}")
def rename_case(
    filename: str,
    request: RenameRequest
):

    db = SessionLocal()

    incident = db.query(Incident).filter(
        Incident.filename == filename
    ).first()

    if not incident:
        db.close()
        raise HTTPException(
            status_code=404,
            detail="Case not found"
        )

    old_path = os.path.join(
        UPLOAD_FOLDER,
        filename
    )

    new_path = os.path.join(
        UPLOAD_FOLDER,
        request.new_filename
    )

    # RENAME FILE
    if os.path.exists(old_path):
        os.rename(old_path, new_path)

    # UPDATE DATABASE
    incident.filename = request.new_filename

    db.commit()
    db.close()

    return {
        "message": "Case renamed successfully"
    }

