from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional


# ---------- User schemas ----------

class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


# ---------- Application schemas ----------

class ApplicationCreate(BaseModel):
    company_name: str
    job_title: str
    status: Optional[str] = "applied"
    notes: Optional[str] = None


class ApplicationUpdate(BaseModel):
    company_name: Optional[str] = None
    job_title: Optional[str] = None
    status: Optional[str] = None
    notes: Optional[str] = None


class ApplicationOut(BaseModel):
    id: int
    company_name: str
    job_title: str
    status: str
    notes: Optional[str]
    applied_date: datetime
    owner_id: int

    class Config:
        from_attributes = True