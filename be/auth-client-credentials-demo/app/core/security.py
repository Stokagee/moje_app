# Security utilities for Client Credentials Demo

from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
import bcrypt
from app.core.config import settings


def verify_client_secret(plain_secret: str, hashed_secret: str) -> bool:
    """Verify a client secret against a hash"""
    return bcrypt.checkpw(plain_secret.encode('utf-8'), hashed_secret.encode('utf-8'))


def get_client_secret_hash(secret: str) -> str:
    """Hash a client secret"""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(secret.encode('utf-8'), salt).decode('utf-8')


def create_m2m_token(client_id: str, scopes: list[str], expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT token for machine-to-machine authentication.

    This token does NOT have a user subject (sub).
    Instead, it uses client_id as the subject.
    """

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=settings.M2M_TOKEN_EXPIRE_HOURS)

    payload = {
        "sub": client_id,  # Client ID is the subject for M2M
        "client_id": client_id,
        "scopes": " ".join(scopes),
        "type": "m2m",
        "exp": expire,
        "iat": datetime.utcnow()
    }

    encoded_jwt = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> Optional[dict]:
    """Decode and verify a JWT token"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None


def verify_scope(required_scopes: list[str], token_scopes: str) -> bool:
    """
    Verify if token has all required scopes.

    Args:
        required_scopes: List of scopes required for the operation
        token_scopes: Space-separated scopes from the token

    Returns:
        True if token has all required scopes
    """
    token_scope_list = token_scopes.split()
    return all(scope in token_scope_list for scope in required_scopes)
