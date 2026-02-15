# OAuth2 Authorization Code routes

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../shared"))

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    decode_token,
    generate_state
)
from app.core.config import settings
from app.core.redis_client import (
    save_authorization_code,
    get_authorization_code,
    delete_authorization_code,
    save_state,
    validate_state
)
from app.models.auth_code import User, OAuth2Client
from app.schemas.oauth2 import TokenRequest, TokenResponse
from pydantic import BaseModel
import secrets
from typing import Optional
from shared.logging.logger import get_logger
from shared.logging.formatters import log_auth_event, log_token_issued

router = APIRouter(prefix="/oauth2", tags=["oauth2"])
templates = Jinja2Templates(directory="templates")
logger = get_logger(__name__)


class AuthorizeParams(BaseModel):
    client_id: str
    redirect_uri: str
    response_type: str = "code"
    scope: str = "read"
    state: Optional[str] = None


class ApproveForm(BaseModel):
    client_id: str
    redirect_uri: str
    state: Optional[str] = None
    scopes: str
    username: str
    password: str


@router.get(
    "/authorize",
    summary="Inicializovat OAuth2 Authorization Code flow",
    description="""Začne Authorization Code flow zobrazením consent stránky.

## Query Parametry

| Parametr | Povinné | Popis |
|----------|---------|-------|
| client_id | Ano | ID klientské aplikace |
| redirect_uri | Ano | Kam redirectovat po schválení |
| response_type | Ano | Musí být `code` |
| scope | Ne | Požadované scopes (výchozí: `read`) |
| state | Ne | Náhodný řetězec pro CSRF ochranu |

## Co se stane

1. Server ověří client_id a redirect_uri
2. Zobrazí consent stránku s:
   - Jméno aplikace
   - Požadované scopes
   - Přihlašovací formulář
3. Po schválení redirectuje s `code` parametrem

## Redirect

Po schválení: `{redirect_uri}?code={auth_code}&state={state}`

Při chybě: `{redirect_uri}?error={error}&error_description={desc}&state={state}`

## Chyby

- **400**: Neplatný client_id
- **400**: Neplatná redirect_uri (není v povoleném seznamu)
- **400**: Nepodporovaný response_type (musí být `code`)

## Příklad URL

```
http://localhost:11003/oauth2/authorize?
  client_id=demo-client&
  redirect_uri=http://localhost:3000/callback&
  response_type=code&
  scope=read write&
  state=random-state-123
```
""",
    responses={
        200: {
            "description": "Consent stránka (HTML)",
            "content": {
                "text/html": {
                    "example": "<!DOCTYPE html>...consent form...</html>"
                }
            }
        },
        400: {
            "description": "Neplatný request",
            "content": {
                "application/json": {
                    "examples": {
                        "invalid_client": {
                            "summary": "Neplatný client_id",
                            "value": {"detail": "Invalid client_id"}
                        },
                        "invalid_redirect": {
                            "summary": "Neplatná redirect_uri",
                            "value": {"detail": "Invalid redirect_uri. Must be one of: [...]"}
                        },
                        "invalid_response_type": {
                            "summary": "Nepodporovaný response_type",
                            "value": {"detail": "Unsupported response_type: token. Use 'code'"}
                        }
                    }
                }
            }
        }
    }
)
def authorize(
    request: Request,
    client_id: str,
    redirect_uri: str,
    response_type: str = "code",
    scope: str = "read",
    state: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Authorization Endpoint - Step 1 of Authorization Code Flow

    This endpoint:
    1. Validates the client application
    2. Shows the user a consent page
    3. Generates an authorization code after user approval

    Parameters:
    - client_id: Identifies the client application
    - redirect_uri: Where to redirect after authorization
    - response_type: Must be "code" for Authorization Code flow
    - scope: What permissions the client is requesting
    - state: Random string for CSRF protection
    """

    # Validate response_type
    if response_type != "code":
        logger.warning("Authorization failed: invalid response_type", extra=log_auth_event(
            event_type="authorize_failed",
            success=False,
            auth_flow="authorization_code",
            client_id=client_id,
            reason="invalid_response_type"
        ))
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported response_type: {response_type}. Use 'code'"
        )

    # Find client
    client = db.query(OAuth2Client).filter(
        OAuth2Client.client_id == client_id
    ).first()

    if not client or not client.is_active:
        logger.warning("Authorization failed: invalid client", extra=log_auth_event(
            event_type="authorize_failed",
            success=False,
            auth_flow="authorization_code",
            client_id=client_id,
            reason="invalid_client"
        ))
        raise HTTPException(
            status_code=400,
            detail="Invalid client_id"
        )

    # Validate redirect_uri
    if redirect_uri not in client.redirect_uri_list:
        logger.warning("Authorization failed: invalid redirect_uri", extra=log_auth_event(
            event_type="authorize_failed",
            success=False,
            auth_flow="authorization_code",
            client_id=client_id,
            reason="invalid_redirect_uri"
        ))
        raise HTTPException(
            status_code=400,
            detail=f"Invalid redirect_uri. Must be one of: {client.redirect_uri_list}"
        )

    # Validate scopes
    requested_scopes = scope.split() if scope else []
    for scope_item in requested_scopes:
        if scope_item not in client.scope_list:
            logger.warning("Authorization failed: unauthorized scope", extra=log_auth_event(
                event_type="authorize_failed",
                success=False,
                auth_flow="authorization_code",
                client_id=client_id,
                reason="unauthorized_scope",
                requested_scope=scope_item
            ))
            raise HTTPException(
                status_code=400,
                detail=f"Client does not have scope: {scope_item}"
            )

    # Save state if provided
    if state:
        save_state(state, {"client_id": client_id})

    logger.info("Authorization request initiated", extra=log_auth_event(
        event_type="authorize_initiated",
        success=True,
        auth_flow="authorization_code",
        client_id=client_id,
        redirect_uri=redirect_uri,
        scopes=" ".join(requested_scopes),
        has_state=bool(state)
    ))

    # Show consent page
    return templates.TemplateResponse("consent.html", {
        "request": request,
        "client_name": client.name,
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "state": state,
        "scopes": requested_scopes
    })


@router.post(
    "/approve",
    summary="Schválit consent a získat authorization code",
    description="""Zpracuje odeslaný consent formulář.

## Form Data

| Pole | Popis |
|------|-------|
| client_id | ID klientské aplikace |
| redirect_uri | Redirect URI po schválení |
| state | State parameter z původního requestu |
| scopes | Požadované scopes (mezerou oddělené) |
| username | Uživatelské jméno |
| password | Heslo uživatele |

## Co se stane

1. Ověří uživatelské credentials
2. Vytvoří authorization code
3. Uloží code do Redis (platnost 10 minut)
4. Redirectuje zpět s code v URL

## Redirect

`{redirect_uri}?code={auth_code}&state={state}`
""",
    responses={
        302: {
            "description": "Redirect s authorization code",
            "headers": {
                "Location": {
                    "description": "Redirect URL s code parametrem",
                    "schema": {"type": "string"}
                }
            }
        },
        400: {
            "description": "Neplatný request",
            "content": {
                "text/html": {
                    "example": "<!DOCTYPE html>...error message...</html>"
                }
            }
        }
    }
)
def approve_consent(
    request: Request,
    form_data: ApproveForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Consent Approval Endpoint - Step 2 of Authorization Code Flow

    This endpoint:
    1. Authenticates the user
    2. Creates an authorization code
    3. Redirects back to the client with the code
    """

    # Authenticate user
    user = db.query(User).filter(User.username == form_data.username).first()

    if not user or not verify_password(form_data.password, user.hashed_password):
        logger.warning("Consent failed: invalid credentials", extra=log_auth_event(
            event_type="consent_failed",
            success=False,
            auth_flow="authorization_code",
            client_id=form_data.client_id,
            username=form_data.username,
            reason="invalid_credentials"
        ))
        # Return to consent page with error
        return templates.TemplateResponse("consent.html", {
            "request": request,
            "client_name": "Unknown",
            "client_id": form_data.client_id,
            "redirect_uri": form_data.redirect_uri,
            "state": form_data.state,
            "scopes": form_data.scopes.split(),
            "error": "Invalid username or password"
        })

    # Validate client
    client = db.query(OAuth2Client).filter(
        OAuth2Client.client_id == form_data.client_id
    ).first()

    if not client:
        logger.warning("Consent failed: invalid client", extra=log_auth_event(
            event_type="consent_failed",
            success=False,
            auth_flow="authorization_code",
            client_id=form_data.client_id,
            user_id=user.id,
            reason="invalid_client"
        ))
        raise HTTPException(400, "Invalid client_id")

    # Validate redirect_uri again
    if form_data.redirect_uri not in client.redirect_uri_list:
        logger.warning("Consent failed: invalid redirect_uri", extra=log_auth_event(
            event_type="consent_failed",
            success=False,
            auth_flow="authorization_code",
            client_id=form_data.client_id,
            user_id=user.id,
            reason="invalid_redirect_uri"
        ))
        raise HTTPException(400, "Invalid redirect_uri")

    # Validate state if provided
    if form_data.state:
        if not validate_state(form_data.state):
            logger.warning("Consent failed: invalid state", extra=log_auth_event(
                event_type="consent_failed",
                success=False,
                auth_flow="authorization_code",
                client_id=form_data.client_id,
                user_id=user.id,
                reason="invalid_state"
            ))
            raise HTTPException(400, "Invalid state parameter")

    # Create authorization code
    auth_code = secrets.token_urlsafe(32)

    # Save authorization code to Redis
    code_data = {
        "user_id": user.id,
        "username": user.username,
        "client_id": client.client_id,
        "scopes": form_data.scopes.split()
    }

    save_authorization_code(auth_code, code_data)

    logger.info("Consent approved, authorization code created", extra=log_auth_event(
        event_type="consent_approved",
        success=True,
        auth_flow="authorization_code",
        client_id=client.client_id,
        user_id=user.id,
        username=user.username,
        scopes=form_data.scopes,
        code_issued=auth_code[:8] + "..."
    ))

    # Redirect back with code
    redirect_url = f"{form_data.redirect_uri}?code={auth_code}"
    if form_data.state:
        redirect_url += f"&state={form_data.state}"

    return RedirectResponse(redirect_url, status_code=302)


@router.post(
    "/token",
    response_model=TokenResponse,
    summary="Vyměnit authorization code za access token",
    description="""Vymění authorization code za access token.

## Request Form Data

| Pole | Popis |
|------|-------|
| grant_type | Musí být `authorization_code` |
| code | Authorization code z redirectu |
| client_id | ID klientské aplikace |
| client_secret | Secret klientské aplikace |
| redirect_uri | Stejná redirect URI jako v authorize requestu |

## Co se stane

1. Ověří authorization code (z Redis)
2. Ověří client credentials
3. Smaže authorization code (jednorázové použití)
4. Vytvoří access token

## Chyby

- **400**: Neplatný nebo expirovaný code
- **400**: Neplatný grant_type
- **401**: Neplatný client_secret
- **400**: Neplatná redirect_uri

## Příklad

```bash
curl -X POST "http://localhost:11003/oauth2/token" \\
  -d "grant_type=authorization_code" \\
  -d "code=abc123..." \\
  -d "client_id=demo-client" \\
  -d "client_secret=demo-client-secret" \\
  -d "redirect_uri=http://localhost:3000/callback"
```
""",
    responses={
        200: {
            "description": "Token úspěšně získán",
            "content": {
                "application/json": {
                    "example": {
                        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                        "token_type": "bearer",
                        "expires_in": 1800,
                        "scope": "read write"
                    }
                }
            }
        },
        400: {
            "description": "Neplatný request",
            "content": {
                "application/json": {
                    "examples": {
                        "invalid_code": {
                            "summary": "Neplatný code",
                            "value": {"detail": "Invalid or expired authorization code"}
                        },
                        "invalid_grant": {
                            "summary": "Neplatný grant_type",
                            "value": {"detail": "Unsupported grant_type: password"}
                        },
                        "client_mismatch": {
                            "summary": "Client ID mismatch",
                            "value": {"detail": "Client ID mismatch"}
                        }
                    }
                }
            }
        },
        401: {
            "description": "Neplatný client_secret",
            "content": {
                "application/json": {
                    "example": {"detail": "Invalid client_secret"}
                }
            }
        }
    }
)
def exchange_code_for_token(
    form_data: TokenRequest,
    db: Session = Depends(get_db)
):
    """
    Token Endpoint - Step 3 of Authorization Code Flow

    This endpoint:
    1. Validates the authorization code
    2. Validates the client credentials
    3. Issues an access token
    4. Deletes the authorization code (single use)
    """

    # Validate grant_type
    if form_data.grant_type != "authorization_code":
        logger.warning("Token exchange failed: invalid grant_type", extra=log_auth_event(
            event_type="token_exchange_failed",
            success=False,
            auth_flow="authorization_code",
            client_id=form_data.client_id,
            reason="invalid_grant_type"
        ))
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported grant_type: {form_data.grant_type}"
        )

    # Get authorization code from Redis
    code_data = get_authorization_code(form_data.code)

    if not code_data:
        logger.warning("Token exchange failed: invalid code", extra=log_auth_event(
            event_type="token_exchange_failed",
            success=False,
            auth_flow="authorization_code",
            client_id=form_data.client_id,
            reason="invalid_code"
        ))
        raise HTTPException(
            status_code=400,
            detail="Invalid or expired authorization code"
        )

    # Validate client_id
    if code_data["client_id"] != form_data.client_id:
        logger.warning("Token exchange failed: client mismatch", extra=log_auth_event(
            event_type="token_exchange_failed",
            success=False,
            auth_flow="authorization_code",
            client_id=form_data.client_id,
            reason="client_mismatch"
        ))
        raise HTTPException(
            status_code=400,
            detail="Client ID mismatch"
        )

    # Validate client
    client = db.query(OAuth2Client).filter(
        OAuth2Client.client_id == form_data.client_id
    ).first()

    if not client:
        logger.warning("Token exchange failed: client not found", extra=log_auth_event(
            event_type="token_exchange_failed",
            success=False,
            auth_flow="authorization_code",
            client_id=form_data.client_id,
            reason="client_not_found"
        ))
        raise HTTPException(400, "Invalid client_id")

    # Validate client_secret
    if client.client_secret != form_data.client_secret:
        logger.warning("Token exchange failed: invalid secret", extra=log_auth_event(
            event_type="token_exchange_failed",
            success=False,
            auth_flow="authorization_code",
            client_id=form_data.client_id,
            reason="invalid_secret"
        ))
        raise HTTPException(
            status_code=401,
            detail="Invalid client_secret"
        )

    # Validate redirect_uri
    if form_data.redirect_uri not in client.redirect_uri_list:
        logger.warning("Token exchange failed: invalid redirect_uri", extra=log_auth_event(
            event_type="token_exchange_failed",
            success=False,
            auth_flow="authorization_code",
            client_id=form_data.client_id,
            reason="invalid_redirect_uri"
        ))
        raise HTTPException(400, "Invalid redirect_uri")

    # Delete the authorization code (single use)
    delete_authorization_code(form_data.code)

    # Create access token
    access_token = create_access_token(
        sub=code_data["username"],
        extra_data={
            "user_id": code_data["user_id"],
            "client_id": code_data["client_id"],
            "scopes": " ".join(code_data["scopes"])
        }
    )

    logger.info("Access token issued via authorization code", extra=log_token_issued(
        token_type="access",
        auth_flow="authorization_code",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user_id=code_data["user_id"],
        client_id=code_data["client_id"],
        scopes=" ".join(code_data["scopes"])
    ))

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        scope=" ".join(code_data["scopes"])
    )


@router.get(
    "/userinfo",
    summary="Získat uživatelské informace",
    description="""Vrátí informace o uživateli na základě access tokenu.

## Query Parametry

| Parametr | Popis |
|----------|-------|
| token | Access token |

## Response

- **sub**: User ID
- **username**: Uživatelské jméno
- **email**: Emailová adresa
- **name**: Celé jméno

## Chyby

- **401**: Neplatný token
- **404**: Uživatel nenalezen
""",
    responses={
        200: {
            "description": "Informace o uživateli",
            "content": {
                "application/json": {
                    "example": {
                        "sub": "1",
                        "username": "demo",
                        "email": "demo@example.com",
                        "name": "Demo User"
                    }
                }
            }
        },
        401: {
            "description": "Neplatný token",
            "content": {
                "application/json": {
                    "example": {"detail": "Invalid token"}
                }
            }
        },
        404: {
            "description": "Uživatel nenalezen",
            "content": {
                "application/json": {
                    "example": {"detail": "User not found"}
                }
            }
        }
    }
)
def userinfo(
    request: Request,
    token: str,
    db: Session = Depends(get_db)
):
    """Get user information from access token"""

    payload = decode_token(token)

    if not payload:
        raise HTTPException(401, "Invalid token")

    username = payload.get("sub")
    user = db.query(User).filter(User.username == username).first()

    if not user:
        raise HTTPException(404, "User not found")

    return {
        "sub": str(user.id),
        "username": user.username,
        "email": user.email,
        "name": user.full_name
    }
