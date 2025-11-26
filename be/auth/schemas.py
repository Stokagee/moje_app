"""
Pydantic schémata pro Auth Demo.
"""
from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    """Schéma pro registraci nového uživatele."""
    username: str
    email: EmailStr
    password: str


class UserOut(BaseModel):
    """Schéma pro výstup uživatele (bez hesla)."""
    username: str
    email: str


class Token(BaseModel):
    """Schéma pro JWT token response."""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Data extrahovaná z JWT tokenu."""
    username: str | None = None


class Message(BaseModel):
    """Obecná zpráva."""
    message: str
