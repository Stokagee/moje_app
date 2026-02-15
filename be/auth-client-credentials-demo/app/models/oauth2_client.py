# OAuth2 Client model for Client Credentials Demo

from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from app.core.database import Base


class OAuth2Client(Base):
    """
    OAuth2 Client Application model.

    Represents a service or application that can authenticate
    using Client Credentials grant (M2M authentication).
    """
    __tablename__ = "oauth2_clients"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(String(100), unique=True, index=True, nullable=False)
    client_secret_hash = Column(String(255), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    scopes = Column(String(500), nullable=False, default="read")  # Space-separated scopes
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @property
    def scope_list(self) -> list[str]:
        """Get scopes as a list"""
        return self.scopes.split() if self.scopes else []

    def has_scope(self, scope: str) -> bool:
        """Check if client has a specific scope"""
        return scope in self.scope_list
