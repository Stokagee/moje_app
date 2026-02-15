# Models for Authorization Code Demo

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text
from app.core.database import Base


class User(Base):
    """User model for authentication"""
    __tablename__ = "auth_users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))


class OAuth2Client(Base):
    """OAuth2 Client Application model"""
    __tablename__ = "oauth2_clients"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(String(100), unique=True, index=True, nullable=False)
    client_secret = Column(String(255), nullable=False)
    name = Column(String(100), nullable=False)
    redirect_uris = Column(Text, nullable=False)  # Newline-separated URIs
    scopes = Column(String(500), default="read")  # Space-separated scopes
    is_active = Column(Integer, default=1)

    @property
    def redirect_uri_list(self) -> list[str]:
        """Get redirect URIs as a list"""
        return self.redirect_uris.split('\n') if self.redirect_uris else []

    @property
    def scope_list(self) -> list[str]:
        """Get scopes as a list"""
        return self.scopes.split() if self.scopes else []
