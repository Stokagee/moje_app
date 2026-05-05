"""OAuth2 PKCE Authentication Dependencies.

Tento modul poskytuje FastAPI dependencies pro autentizaci pomocí JWT tokenů
z OAuth2 PKCE flow.

Použití:
    from app.core.auth import get_current_user, get_current_courier

    @router.post("/orders/{id}/pickup")
    async def pickup_order(
        order_id: int,
        courier = Depends(get_current_courier)
    ):
        # courier je ověřený kurýr z JWT tokenu
        pass
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime, timedelta

from app.core.config import settings


# OAuth2 Bearer scheme pro Swagger UI
oauth2_scheme = HTTPBearer(
    scheme_name="OAuth2 PKCE",
    description="Bearer token z OAuth2 PKCE flow"
)


class TokenPayload(BaseModel):
    """Struktura JWT tokenu z PKCE flow."""
    sub: str  # username
    user_id: Optional[int] = None
    client_id: Optional[str] = None
    scopes: Optional[str] = None
    role: Optional[str] = None
    exp: Optional[int] = None
    iat: Optional[int] = None


class CurrentUser(BaseModel):
    """Aktuální ověřený uživatel."""
    username: str
    user_id: Optional[int] = None
    scopes: List[str] = []
    role: str = "user"


# OAuth2 Bearer scheme pro Swagger UI
oauth2_scheme = HTTPBearer(
    scheme_name="OAuth2 PKCE",
    description="Bearer token z OAuth2 PKCE flow"
)


class TokenPayload(BaseModel):
    """Struktura JWT tokenu z PKCE flow."""
    sub: str  # username
    user_id: Optional[int] = None
    client_id: Optional[str] = None
    scopes: Optional[str] = None
    role: Optional[str] = None
    exp: Optional[int] = None
    iat: Optional[int] = None


class CurrentUser(BaseModel):
    """Aktuální ověřený uživatel."""
    username: str
    user_id: Optional[int] = None
    scopes: list[str] = []
    role: str = "user"


def decode_token(token: str) -> Optional[dict]:
    """
    Dekóduje a validuje JWT token.

    Args:
        token: JWT token string

    Returns:
        Decoded payload pokud je token validní, jinak None
    """
    try:
        # Použijeme stejný SECRET_KEY a ALGORITHM jako PKCE demo
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError:
        return None


def create_access_token(
    data: dict,
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Vytvoří nový JWT access token.

    Args:
        data: Data k zašifrování do tokenu (obvykle {"sub": username, ...})
        expires_delta: Volitelná doba platnosti

    Returns:
        JWT token string
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow()
    })

    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )

    return encoded_jwt


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme)
) -> CurrentUser:
    """
    FastAPI dependency pro získání aktuálního uživatele z JWT tokenu.

    Použití:
        @router.get("/protected")
        async def protected_route(user = Depends(get_current_user)):
            return {"username": user.username}

    Raises:
        401 Unauthorized: Pokud token chybí nebo je nevalidní

    Returns:
        CurrentUser s údaji o přihlášeném uživateli
    """
    token = credentials.credentials

    payload = decode_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"}
        )

    username = payload.get("sub")
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"}
        )

    # Parsovat scopes
    scopes_str = payload.get("scopes", "")
    scopes = scopes_str.split() if scopes_str else []

    return CurrentUser(
        username=username,
        user_id=payload.get("user_id"),
        scopes=scopes,
        role=payload.get("role", "user")
    )


async def get_current_courier(
    user: CurrentUser = Depends(get_current_user)
) -> CurrentUser:
    """
    FastAPI dependency pro získání kurýra s ověřením role.

    Použití:
        @router.post("/orders/{id}/pickup")
        async def pickup(courier = Depends(get_current_courier)):
            # courier má role="courier"
            pass

    Raises:
        401 Unauthorized: Pokud token chybí nebo je nevalidní
        403 Forbidden: Pokud uživatel nemá roli courier

    Returns:
        CurrentUser s ověřenou rolí courier
    """
    if user.role not in ["courier", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Courier role required for this operation"
        )

    return user


async def get_current_admin(
    user: CurrentUser = Depends(get_current_user)
) -> CurrentUser:
    """
    FastAPI dependency pro admin operace.

    Použití:
        @router.delete("/orders/{id}")
        async def delete_order(admin = Depends(get_current_admin)):
            pass

    Raises:
        401 Unauthorized: Pokud token chybí nebo je nevalidní
        403 Forbidden: Pokud uživatel nemá roli admin

    Returns:
        CurrentUser s ověřenou rolí admin
    """
    if user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin role required for this operation"
        )

    return user


def require_scopes(required_scopes: list[str]):
    """
    Factory pro vytvoření dependency, která kontroluje scopes.

    Použití:
        @router.get("/admin/orders")
        async def admin_orders(
            user = Depends(require_scopes(["orders:admin"]))
        ):
            pass

    Args:
        required_scopes: Seznam požadovaných scopes

    Returns:
        FastAPI dependency funkce
    """
    async def scope_checker(
        user: CurrentUser = Depends(get_current_user)
    ) -> CurrentUser:
        for scope in required_scopes:
            if scope not in user.scopes:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Missing required scope: {scope}"
                )
        return user

    return scope_checker
