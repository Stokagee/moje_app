# Authentication schemas for Refresh Token Demo

from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    """Login request schema"""
    username: str = Field(..., description="Uživatelské jméno", examples=["testuser"])
    password: str = Field(..., description="Heslo uživatele", examples=["testpass123"])


class RegisterRequest(BaseModel):
    """Registration request schema"""
    username: str = Field(..., min_length=3, max_length=50, description="Uživatelské jméno (3-50 znaků)", examples=["newuser"])
    email: EmailStr = Field(..., description="Emailová adresa", examples=["user@example.com"])
    password: str = Field(..., min_length=6, description="Heslo (minimálně 6 znaků)", examples=["password123"])


class UserCreate(BaseModel):
    """Schema for creating a user (internal use)"""
    username: str
    email: str
    hashed_password: str
