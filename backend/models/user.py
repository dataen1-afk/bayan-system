"""
User-related Pydantic models.
"""
from pydantic import BaseModel, Field, EmailStr
from datetime import datetime, timezone
import uuid


class UserRegister(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: str = Field(default="client")


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    email: EmailStr
    role: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class TokenResponse(BaseModel):
    token: str
    user: User
