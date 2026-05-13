from sqlalchemy import Column, Integer, String, Text
from database import Base

class Incident(Base):

    __tablename__ = "incidents"

    id = Column(Integer, primary_key=True, index=True)

    filename = Column(String)

    severity = Column(String)

    incident_type = Column(String)

    department = Column(String)

    risk_score = Column(Integer)

    summary = Column(Text)

class User(Base):

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    username = Column(String, unique=True)

    password = Column(String)

    role = Column(String, default="employee")