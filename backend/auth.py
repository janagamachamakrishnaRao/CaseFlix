from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta

router = APIRouter()

SECRET_KEY = "caseflixsecret"
ALGORITHM = "HS256"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# TEMP USER DATABASE
fake_users_db = {}


class UserRegister(BaseModel):
    username: str
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


# HASH PASSWORD
def hash_password(password):
    return pwd_context.hash(password)


# VERIFY PASSWORD
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


# CREATE TOKEN
def create_access_token(data: dict):

    to_encode = data.copy()

    expire = datetime.utcnow() + timedelta(hours=24)

    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return encoded_jwt


# REGISTER
@router.post("/register")
def register(user: UserRegister):

    if user.username in fake_users_db:
        raise HTTPException(
            status_code=400,
            detail="User already exists"
        )

    hashed_password = hash_password(user.password)

    fake_users_db[user.username] = hashed_password

    return {
        "message": "User registered successfully"
    }


# LOGIN
@router.post("/login")
def login(user: UserLogin):

    if user.username not in fake_users_db:
        raise HTTPException(
            status_code=400,
            detail="Invalid username"
        )

    stored_password = fake_users_db[user.username]

    if not verify_password(user.password, stored_password):
        raise HTTPException(
            status_code=400,
            detail="Invalid password"
        )

    token = create_access_token({
        "sub": user.username
    })

    return {
        "access_token": token,
        "token_type": "bearer"
    }