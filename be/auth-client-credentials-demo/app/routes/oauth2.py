# OAuth2 routes for Client Credentials Demo

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../shared"))

from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Form
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import (
    verify_client_secret,
    get_client_secret_hash,
    create_m2m_token,
    decode_token,
    verify_scope
)
from app.core.config import settings
from app.models.oauth2_client import OAuth2Client
from app.schemas.token import M2MTokenResponse, TokenIntrospectResponse
from app.schemas.client import ClientCreate, ClientResponse
from shared.logging.logger import get_logger
from shared.logging.formatters import log_auth_event, log_token_issued

router = APIRouter(prefix="/oauth2", tags=["oauth2"])
security = HTTPBearer()
logger = get_logger(__name__)


def get_m2m_client(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> OAuth2Client:
    """
    Get authenticated M2M client from JWT token.

    This is used to protect endpoints that require M2M authentication.
    """

    token = credentials.credentials
    payload = decode_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if payload.get("type") != "m2m":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type (expected M2M token)"
        )

    client_id = payload.get("sub") or payload.get("client_id")
    if client_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )

    client = db.query(OAuth2Client).filter(OAuth2Client.client_id == client_id).first()
    if client is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Client not found"
        )

    if not client.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Client account is disabled"
        )

    return client


def require_scopes(required_scopes: list[str]):
    """
    Dependency factory that checks if the authenticated client has required scopes.

    Usage:
        @router.get("/api/data")
        def get_data(client: OAuth2Client = Depends(require_scopes(["read"]))):
            ...
    """
    def dependency(
        credentials: HTTPAuthorizationCredentials = Depends(security),
        db: Session = Depends(get_db)
    ) -> OAuth2Client:
        client = get_m2m_client(credentials, db)

        # Get scopes from token
        payload = decode_token(credentials.credentials)
        token_scopes = payload.get("scopes", "")

        # Verify required scopes
        if not verify_scope(required_scopes, token_scopes):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient scope. Required: {', '.join(required_scopes)}"
            )

        return client

    return dependency


@router.post(
    "/token",
    response_model=M2MTokenResponse,
    summary="Získat M2M token (Client Credentials)",
    description="""Získá access token pro machine-to-machine komunikaci.

## Request Form Data (application/x-www-form-urlencoded)

| Pole | Hodnota | Popis |
|------|---------|-------|
| grant_type | `client_credentials` | Typ OAuth2 grant (povinné) |
| client_id | `<váš-client-id>` | ID aplikace |
| client_secret | `<váš-client-secret>` | Secret aplikace |
| scope | `read write` | Požadované scopes (volitelné) |

## Token

- **Platnost**: 1 hodina
- **Bez refresh tokenu**: M2M tokeny nemají refresh token
- **Bez uživatelského kontextu**: Token nemá informace o uživateli

## Chyby

- **400**: Nepodporovaný grant_type
- **401**: Neplatné client_id nebo client_secret
- **403**: Client deaktivován
- **400**: Client nemá požadované scopes

## Příklad curl

```bash
curl -X POST "http://localhost:11002/oauth2/token" \\
  -d "grant_type=client_credentials" \\
  -d "client_id=demo-service" \\
  -d "client_secret=demo-secret123" \\
  -d "scope=read write"
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
                        "expires_in": 3600,
                        "scope": "read write"
                    }
                }
            }
        },
        401: {
            "description": "Neplatné credentials",
            "content": {
                "application/json": {
                    "example": {"detail": "Invalid client_id or client_secret"}
                }
            }
        }
    }
)
def client_credentials_token(
    grant_type: str = Form(default="client_credentials"),
    client_id: str = Form(...),
    client_secret: str = Form(...),
    scope: str = Form(default="read"),
    db: Session = Depends(get_db)
):
    """
    OAuth2 Client Credentials Token Endpoint.

    This endpoint implements the Client Credentials grant flow.
    It allows machine-to-machine (M2M) authentication where a service
    can obtain a token on its own behalf (not on behalf of a user).

    The token:
    - Does NOT have a user subject
    - Uses client_id as the subject
    - Has scopes that define what the client can do
    - Expires after a short period (default 1 hour)
    """

    # Validate grant_type
    if grant_type != "client_credentials":
        logger.warning("M2M token request failed: invalid grant_type", extra=log_auth_event(
            event_type="token_request_failed",
            success=False,
            auth_flow="client_credentials",
            client_id=client_id,
            reason="invalid_grant_type"
        ))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported grant_type. Use 'client_credentials'"
        )

    # Find client
    client = db.query(OAuth2Client).filter(
        OAuth2Client.client_id == client_id
    ).first()

    if not client:
        logger.warning("M2M token request failed: client not found", extra=log_auth_event(
            event_type="token_request_failed",
            success=False,
            auth_flow="client_credentials",
            client_id=client_id,
            reason="client_not_found"
        ))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid client_id or client_secret"
        )

    # Verify client secret
    if not verify_client_secret(client_secret, client.client_secret_hash):
        logger.warning("M2M token request failed: invalid secret", extra=log_auth_event(
            event_type="token_request_failed",
            success=False,
            auth_flow="client_credentials",
            client_id=client_id,
            reason="invalid_secret"
        ))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid client_id or client_secret"
        )

    if not client.is_active:
        logger.warning("M2M token request failed: client disabled", extra=log_auth_event(
            event_type="token_request_failed",
            success=False,
            auth_flow="client_credentials",
            client_id=client_id,
            reason="client_disabled"
        ))
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Client account is disabled"
        )

    # Parse requested scopes
    requested_scopes = scope.split() if scope else []

    # Validate scopes - client can only request scopes it has been granted
    for req_scope in requested_scopes:
        if not client.has_scope(req_scope):
            logger.warning("M2M token request failed: unauthorized scope", extra=log_auth_event(
                event_type="token_request_failed",
                success=False,
                auth_flow="client_credentials",
                client_id=client_id,
                reason="unauthorized_scope",
                requested_scope=req_scope
            ))
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Client does not have scope: {req_scope}"
            )

    # If no scopes requested, use client's default scopes
    if not requested_scopes:
        requested_scopes = client.scope_list

    # Create M2M token
    access_token = create_m2m_token(
        client_id=client.client_id,
        scopes=requested_scopes,
        expires_delta=timedelta(hours=settings.M2M_TOKEN_EXPIRE_HOURS)
    )

    logger.info("M2M token issued successfully", extra=log_token_issued(
        token_type="access",
        auth_flow="client_credentials",
        expires_in=settings.M2M_TOKEN_EXPIRE_HOURS * 3600,
        client_id=client.client_id,
        scopes=" ".join(requested_scopes)
    ))

    return M2MTokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.M2M_TOKEN_EXPIRE_HOURS * 3600,
        scope=" ".join(requested_scopes)
    )


@router.post(
    "/introspect",
    response_model=TokenIntrospectResponse,
    summary="Introspectovat M2M token",
    description="""Vrátí informace o tokenu pro ověření jeho platnosti.

## Požadavek

Poslat token v request body jako JSON:
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

Nebo v Authorization header.

## Response

- **active**: `true` pokud je token platný, `false` jinak
- **client_id**: Client ID z tokenu
- **scopes**: Scopes udělené tokenu
- **type**: Typ tokenu (např. "m2m")
""",
    responses={
        200: {
            "description": "Výsledek introspekce",
            "content": {
                "application/json": {
                    "examples": {
                        "active": {
                            "summary": "Platný token",
                            "value": {
                                "active": True,
                                "client_id": "demo-service",
                                "scopes": "read write",
                                "type": "m2m"
                            }
                        },
                        "inactive": {
                            "summary": "Neplatný token",
                            "value": {"active": False}
                        }
                    }
                }
            }
        }
    }
)
def introspect_token(
    form_data: dict = None,
    credentials: HTTPAuthorizationCredentials = Depends(lambda: None),
    db: Session = Depends(get_db)
):
    """
    Token Introspection Endpoint.

    Returns information about a token to determine if it's active
    and what permissions it has.
    """

    # Get token from Authorization header or form body
    token = None
    if credentials:
        token = credentials.credentials
    elif form_data and "token" in form_data:
        token = form_data["token"]

    if not token:
        logger.warning("Token introspection failed: no token provided", extra=log_auth_event(
            event_type="introspect_failed",
            success=False,
            auth_flow="client_credentials",
            reason="no_token"
        ))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token required"
        )

    # Decode and verify token
    payload = decode_token(token)

    if payload is None:
        logger.warning("Token introspection: invalid token", extra=log_auth_event(
            event_type="introspect_result",
            success=True,
            auth_flow="client_credentials",
            active=False,
            reason="invalid_token"
        ))
        return TokenIntrospectResponse(active=False)

    # Check token type
    if payload.get("type") != "m2m":
        logger.warning("Token introspection: wrong token type", extra=log_auth_event(
            event_type="introspect_result",
            success=True,
            auth_flow="client_credentials",
            active=False,
            reason="wrong_token_type"
        ))
        return TokenIntrospectResponse(active=False)

    # Verify client still exists and is active
    client_id = payload.get("sub") or payload.get("client_id")
    client = db.query(OAuth2Client).filter(
        OAuth2Client.client_id == client_id
    ).first()

    if not client or not client.is_active:
        logger.warning("Token introspection: client inactive", extra=log_auth_event(
            event_type="introspect_result",
            success=True,
            auth_flow="client_credentials",
            active=False,
            client_id=client_id,
            reason="client_inactive"
        ))
        return TokenIntrospectResponse(active=False)

    logger.info("Token introspection: active token", extra=log_auth_event(
        event_type="introspect_result",
        success=True,
        auth_flow="client_credentials",
        active=True,
        client_id=client.client_id,
        scopes=payload.get("scopes", "")
    ))

    return TokenIntrospectResponse(
        active=True,
        client_id=client.client_id,
        scopes=payload.get("scopes", ""),
        type=payload.get("type", "")
    )


@router.post(
    "/clients",
    response_model=ClientResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Vytvořit OAuth2 client",
    description="""Vytvoří nový OAuth2 client (demo/testing endpoint).

## Poznámka
Toto je demo endpoint pro testování. V produkci by správa clientů
měla být admin operace vyžadující speciální oprávnění.
""",
    responses={
        201: {
            "description": "Client úspěšně vytvořen",
            "content": {
                "application/json": {
                    "example": {
                        "id": 1,
                        "client_id": "my-service",
                        "name": "My Service",
                        "description": "My service application",
                        "scopes": "read write",
                        "is_active": True
                    }
                }
            }
        },
        400: {
            "description": "Client ID již existuje",
            "content": {
                "application/json": {
                    "example": {"detail": "client_id already exists"}
                }
            }
        }
    }
)
def create_client(
    request: ClientCreate,
    db: Session = Depends(get_db)
):
    """Create a new OAuth2 client (for demo/testing purposes)"""

    # Check if client_id already exists
    existing = db.query(OAuth2Client).filter(
        OAuth2Client.client_id == request.client_id
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="client_id already exists"
        )

    # Create client
    client = OAuth2Client(
        client_id=request.client_id,
        client_secret_hash=get_client_secret_hash(request.client_secret),
        name=request.name,
        description=request.description,
        scopes=request.scopes
    )

    db.add(client)
    db.commit()
    db.refresh(client)

    return client


@router.get(
    "/clients",
    response_model=list[ClientResponse],
    summary="Vypsat OAuth2 clients",
    description="""Vypsat všechny OAuth2 clients (admin endpoint).

## Autentizace
Vyžaduje `admin_key` query parameter (demo: `demo-admin-key`).

## Poznámka
Toto je demo endpoint pro testování. V produkci by mělo být
náležitě zabezpečeno.
""",
    responses={
        200: {
            "description": "Seznam clientů",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "id": 1,
                            "client_id": "demo-service",
                            "name": "Demo Service",
                            "description": "Demo service account",
                            "scopes": "read write",
                            "is_active": True
                        }
                    ]
                }
            }
        },
        401: {
            "description": "Chybějící nebo neplatný admin_key",
            "content": {
                "application/json": {
                    "example": {"detail": "Admin key required"}
                }
            }
        }
    }
)
def list_clients(
    admin_key: str = None,
    db: Session = Depends(get_db)
):
    """List all OAuth2 clients (admin endpoint for demo)"""

    # Simple admin check (in production, use proper authentication)
    if admin_key != "demo-admin-key":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Admin key required"
        )

    clients = db.query(OAuth2Client).all()
    return clients
