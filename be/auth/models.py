"""
SQLAlchemy modely pro Auth Demo.
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func

from database import Base


class User(Base):
    """
    Model uživatele pro autentizaci.

    Tabulka: auth_users (oddělená od ostatních tabulek v DB)
    """
    __tablename__ = "auth_users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())

    def __repr__(self):
        return f"<User(username='{self.username}', email='{self.email}')>"
