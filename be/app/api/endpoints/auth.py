"""Autentizační endpointy.

Tento modul poskytuje:
- OAuth2 PKCE token endpoint
- CSRF token endpoint
- User info endpoint
- Logout endpoint
"""
from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Optional

from app.core.auth import (
    get_current_user,
    CurrentUser,
    create_access_token,
    decode_token
)
from app.core.csrf import generate_csrf_token, validate_csrf_or_raise
from app.core.config import settings


router = APIRouter(prefix="/auth", tags=["authentication"])

oauth2_scheme = HTTPBearer()


class CsrfTokenResponse(BaseModel):
    """Response s CSRF tokenem."""
    csrf_token: str
    message: str = "Include this token in X-CSRF-Token header for POST/PUT/DELETE requests"


class UserInfoResponse(BaseModel):
    """Response s informacemi o uživateli."""
    username: str
    user_id: Optional[int]
    role: str
    scopes: list[str]


class TokenResponse(BaseModel):
    """OAuth2 token response."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int


@router.get(
    "/csrf-token",
    response_model=CsrfTokenResponse,
    summary="Získat CSRF token",
    description="""
Vrátí CSRF token pro ochranu proti Cross-Site Request Forgery.

## Jak to funguje:
1. Frontend zavolá tento endpoint před state-changing operací
2. Server vrátí token a nastaví ho do cookie
3. Frontend musí poslat token v hlavičce `X-CSRF-Token`

## Příklad použití:
```javascript
// 1. Získat CSRF token
const response = await fetch('/api/v1/auth/csrf-token');
const { csrf_token } = await response.json();

// 2. Použít v POST requestu
await fetch('/api/v1/orders/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'X-CSRF-Token': csrf_token,
        'Authorization': 'Bearer <access_token>'
    },
    body: JSON.stringify(orderData)
});
```

## Poznámka:
- Token je validní 1 hodinu
- Token je vázán na cookie (SameSite=strict)
"""
)
async def get_csrf_token(response: Response):
    """Vrátí CSRF token pro state-changing operace."""
    token = generate_csrf_token(response)
    return CsrfTokenResponse(csrf_token=token)


@router.get(
    "/me",
    response_model=UserInfoResponse,
    summary="Získat info o přihlášeném uživateli",
    description="""
Vrátí informace o aktuálně přihlášeném uživateli z JWT tokenu.

Vyžaduje Bearer token v hlavičce Authorization.
"""
)
async def get_user_info(
    user: CurrentUser = Depends(get_current_user)
):
    """Vrátí info o přihlášeném uživateli."""
    return UserInfoResponse(
        username=user.username,
        user_id=user.user_id,
        role=user.role,
        scopes=user.scopes
    )


@router.post(
    "/logout",
    summary="Odhlásit uživatele",
    description="""
Odhlásí uživatele invalidací tokenu.

Poznámka: V aktuální implementaci s JWT bez token blacklistu
je toto pouze "soft logout" - klient by měl smazat token lokálně.
"""
)
async def logout(
    request: Request,
    response: Response,
    user: CurrentUser = Depends(get_current_user)
):
    """Odhlásí uživatele."""
    # CSRF validace pro logout
    await validate_csrf_or_raise(request)

    # V produkci bychom přidali token do blacklist (Redis)
    # Pro teď jen smažeme cookie
    response.delete_cookie(key="csrf_token")

    return {"message": "Logged out successfully"}


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Obnovit access token",
    description="""
Obnoví access token pomocí refresh tokenu.

TODO: Implementovat refresh token flow s Redis storage.
"""
)
async def refresh_token(
    credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme)
):
    """Obnoví access token."""
    # TODO: Implementovat refresh token flow
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Refresh token flow not implemented yet. Use auth-refresh-demo service."
    )


# ============================================
# Test Token Endpoint - POUZE PRO TESTOVÁNÍ!
# ============================================

class TestTokenRequest(BaseModel):
    """Request pro vytvoření testovacího tokenu."""
    username: str = "test_user"
    role: str = "user"  # user, courier, admin
    user_id: int = 1
    scopes: str = "orders:read"


@router.post(
    "/test-token",
    response_model=TokenResponse,
    summary="[TEST ONLY] Vytvořit testovací token",
    description="""
**POUZE PRO TESTOVACÍ ÚČELY!**

Vytvoří JWT token s danou rolí bez nutnosti PKCE flow.
V produkci by tento endpoint měl být zakázán!

## Dostupné role:
- `user` / `customer` - Základní uživatel
- `courier` - Kurýr (může pickup/deliver)
- `admin` - Administrátor (plný přístup)

## Příklad:
```json
{
    "username": "test_courier",
    "role": "courier",
    "user_id": 5,
    "scopes": "orders:read orders:write"
}
```
"""
)
async def create_test_token(request: TestTokenRequest):
    """Vytvoří testovací JWT token (pouze pro development/testing)."""
    from app.core.auth import create_access_token

    # Normalizace role
    role = request.role.lower()
    if role == "customer":
        role = "user"

    # Výchozí scopes podle role
    default_scopes = {
        "user": "orders:read",
        "courier": "orders:read orders:write",
        "admin": "orders:read orders:write orders:admin"
    }

    scopes = request.scopes if request.scopes else default_scopes.get(role, "orders:read")

    token_data = {
        "sub": request.username,
        "user_id": request.user_id,
        "role": role,
        "scopes": scopes
    }

    access_token = create_access_token(token_data)

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )
