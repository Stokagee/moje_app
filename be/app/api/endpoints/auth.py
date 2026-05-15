"""Authentication endpoints.

This module provides:
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
    """Response with CSRF token."""
    csrf_token: str
    message: str = "Include this token in X-CSRF-Token header for POST/PUT/DELETE requests"


class UserInfoResponse(BaseModel):
    """Response with user information."""
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
    summary="Get CSRF token",
    description="""
Returns a CSRF token for protection against Cross-Site Request Forgery.

## How it works:
1. Frontend calls this endpoint before a state-changing operation
2. Server returns the token and sets it in a cookie
3. Frontend must send the token in the `X-CSRF-Token` header

## Usage example:
```javascript
// 1. Get CSRF token
const response = await fetch('/api/v1/auth/csrf-token');
const { csrf_token } = await response.json();

// 2. Use in POST request
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

## Note:
- Token is valid for 1 hour
- Token is bound to a cookie (SameSite=strict)
"""
)
async def get_csrf_token(response: Response):
    """Returns a CSRF token for state-changing operations."""
    token = generate_csrf_token(response)
    return CsrfTokenResponse(csrf_token=token)


@router.get(
    "/me",
    response_model=UserInfoResponse,
    summary="Get current user info",
    description="""
Returns information about the currently authenticated user from the JWT token.

Requires a Bearer token in the Authorization header.
"""
)
async def get_user_info(
    user: CurrentUser = Depends(get_current_user)
):
    """Returns info about the authenticated user."""
    return UserInfoResponse(
        username=user.username,
        user_id=user.user_id,
        role=user.role,
        scopes=user.scopes
    )


@router.post(
    "/logout",
    summary="Log out user",
    description="""
Logs the user out by invalidating the token.

Note: In the current JWT implementation without a token blacklist,
this is a "soft logout" — the client should delete the token locally.
"""
)
async def logout(
    request: Request,
    response: Response,
    user: CurrentUser = Depends(get_current_user)
):
    """Logs the user out."""
    # CSRF validace pro logout
    await validate_csrf_or_raise(request)

    # V produkci bychom přidali token do blacklist (Redis)
    # Pro teď jen smažeme cookie
    response.delete_cookie(key="csrf_token")

    return {"message": "Logged out successfully"}


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Refresh access token",
    description="""
Refreshes the access token using a refresh token.

TODO: Implement refresh token flow with Redis storage.
"""
)
async def refresh_token(
    credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme)
):
    """Refreshes the access token."""
    # TODO: Implementovat refresh token flow
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Refresh token flow not implemented yet. Use auth-refresh-demo service."
    )


# ============================================
# Test Token Endpoint - FOR TESTING ONLY!
# ============================================

class TestTokenRequest(BaseModel):
    """Request for creating a test token."""
    username: str = "test_user"
    role: str = "user"  # user, courier, admin
    user_id: int = 1
    scopes: str = "orders:read"


@router.post(
    "/test-token",
    response_model=TokenResponse,
    summary="[TEST ONLY] Create a test token",
    description="""
**FOR TESTING PURPOSES ONLY!**

Creates a JWT token with the given role without requiring the PKCE flow.
This endpoint should be disabled in production!

## Available roles:
- `user` / `customer` - Basic user
- `courier` - Courier (can pickup/deliver)
- `admin` - Administrator (full access)

## Example:
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
    """Creates a test JWT token (development/testing only)."""
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
