# OAuth2 PKCE Flow Routes

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../shared"))

"""
PKCE (Proof Key for Code Exchange) Flow for Public Clients.

This is designed for:
- Single Page Applications (SPA)
- Mobile apps (iOS, Android)
- Any client that cannot securely store client_secret

Flow:
1. Client generates code_verifier and code_challenge (SHA256)
2. Client redirects to /oauth2/authorize with code_challenge
3. User approves consent
4. Server redirects back with authorization code
5. Client exchanges code for token using code_verifier (not client_secret!)
6. Server verifies code_verifier matches code_challenge
7. Server returns access token
"""

from fastapi import APIRouter, Depends, HTTPException, Request, Form
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import (
    verify_password,
    create_access_token,
    decode_token,
    generate_state
)
from app.core.config import settings
from app.core.redis_client import (
    save_authorization_code,
    get_authorization_code,
    delete_authorization_code
)
from app.models.pkce_client import User, OAuth2Client
from app.schemas.oauth2_pkce import (
    TokenResponse,
    UserInfoResponse,
    PKCEDemoResponse
)
from app.utils.pkce_helpers import verify_code_verifier
from app.utils.pkce_utils import generate_code_verifier, create_code_challenge
from shared.logging.logger import get_logger
from shared.logging.formatters import log_auth_event, log_token_issued
import secrets

router = APIRouter(prefix="/oauth2", tags=["oauth2-pkce"])
templates = Jinja2Templates(directory="templates")
logger = get_logger(__name__)


# ============================================
# Authorize Endpoint - s code_challenge
# ============================================

@router.get("/authorize")
def authorize(
    request: Request,
    client_id: str,
    redirect_uri: str,
    code_challenge: str,  # PKCE parameter
    code_challenge_method: str = "S256",
    response_type: str = "code",
    scope: str = "read",
    state: str = None,
    db: Session = Depends(get_db)
):
    """
    Authorization Endpoint s PKCE podporou.

    PKCE Parameters:
    - code_challenge: SHA256(code_verifier) - odesílá klient v authorize requestu
    - code_challenge_method: Vždy "S256" (SHA256)

    Proces:
    1. Klient generuje code_verifier (náhodný řetězec 43-128 znaků)
    2. Klient vypočítá code_challenge = SHA256(code_verifier)
    3. Klient pošle code_challenge v tomto requestu
    4. Server uloží code_challenge s authorization code
    5. Při token exchange klient pošle code_verifier
    6. Server ověří SHA256(verifier) == uložená challenge
    """

    # Validate response_type
    if response_type != "code":
        logger.warning("PKCE authorization failed: invalid response_type", extra=log_auth_event(
            event_type="authorize_failed",
            success=False,
            auth_flow="pkce",
            client_id=client_id,
            reason="invalid_response_type"
        ))
        raise HTTPException(400, f"Unsupported response_type: {response_type}")

    # Find client
    client = db.query(OAuth2Client).filter(
        OAuth2Client.client_id == client_id
    ).first()

    if not client or not client.is_active:
        logger.warning("PKCE authorization failed: invalid client", extra=log_auth_event(
            event_type="authorize_failed",
            success=False,
            auth_flow="pkce",
            client_id=client_id,
            reason="invalid_client"
        ))
        raise HTTPException(400, "Invalid client_id")

    # Validate redirect_uri
    if redirect_uri not in client.redirect_uri_list:
        logger.warning("PKCE authorization failed: invalid redirect_uri", extra=log_auth_event(
            event_type="authorize_failed",
            success=False,
            auth_flow="pkce",
            client_id=client_id,
            reason="invalid_redirect_uri"
        ))
        raise HTTPException(400, f"Invalid redirect_uri")

    # Validate code_challenge_method - ONLY S256 allowed
    if code_challenge_method != "S256":
        logger.warning("PKCE authorization failed: invalid challenge method", extra=log_auth_event(
            event_type="authorize_failed",
            success=False,
            auth_flow="pkce",
            client_id=client_id,
            reason="invalid_challenge_method",
            challenge_method=code_challenge_method
        ))
        raise HTTPException(
            400,
            "Unsupported code_challenge_method. Only 'S256' is supported for security."
        )

    # Validate code_challenge is present
    if not code_challenge:
        logger.warning("PKCE authorization failed: missing code_challenge", extra=log_auth_event(
            event_type="authorize_failed",
            success=False,
            auth_flow="pkce",
            client_id=client_id,
            reason="missing_code_challenge"
        ))
        raise HTTPException(400, "code_challenge is required for PKCE flow")

    # Validate scopes
    requested_scopes = scope.split() if scope else []
    for scope_item in requested_scopes:
        if scope_item not in client.scope_list:
            logger.warning("PKCE authorization failed: unauthorized scope", extra=log_auth_event(
                event_type="authorize_failed",
                success=False,
                auth_flow="pkce",
                client_id=client_id,
                reason="unauthorized_scope",
                requested_scope=scope_item
            ))
            raise HTTPException(400, f"Invalid scope: {scope_item}")

    logger.info("PKCE authorization request initiated with code_challenge", extra=log_auth_event(
        event_type="authorize_initiated",
        success=True,
        auth_flow="pkce",
        client_id=client_id,
        redirect_uri=redirect_uri,
        scopes=" ".join(requested_scopes),
        has_state=bool(state),
        has_code_challenge=True,
        challenge_method=code_challenge_method
    ))

    # Show consent page with PKCE indicator
    return templates.TemplateResponse("consent_pkce.html", {
        "request": request,
        "client_name": client.name,
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "state": state,
        "scopes": requested_scopes,
        "code_challenge": code_challenge,
        "pkce_enabled": True,
        "is_public_client": client.is_public
    })


# ============================================
# Approve Endpoint - uloží code_challenge
# ============================================

@router.post("/approve")
def approve_consent(
    request: Request,
    client_id: str = Form(...),
    redirect_uri: str = Form(...),
    state: str = Form(None),
    scopes: str = Form(...),
    code_challenge: str = Form(...),  # PKCE: uložit challenge
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    """
    Consent Approval s PKCE - uloží code_challenge do Redis.

    Po schválení:
    1. Vytvoří authorization code
    2. Uloží code_challenge s code do Redis
    3. Redirectne zpět na client redirect_uri
    """

    # Authenticate user
    user = db.query(User).filter(User.username == username).first()

    if not user or not verify_password(password, user.hashed_password):
        return templates.TemplateResponse("consent_pkce.html", {
            "request": request,
            "client_name": "Unknown",
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "state": state,
            "scopes": scopes.split(),
            "code_challenge": code_challenge,
            "pkce_enabled": True,
            "error": "Invalid username or password"
        })

    # Validate client
    client = db.query(OAuth2Client).filter(
        OAuth2Client.client_id == client_id
    ).first()

    if not client:
        raise HTTPException(400, "Invalid client_id")

    # Validate redirect_uri
    if redirect_uri not in client.redirect_uri_list:
        raise HTTPException(400, "Invalid redirect_uri")

    # Create authorization code
    auth_code = secrets.token_urlsafe(32)

    # Save authorization code s code_challenge
    code_data = {
        "user_id": user.id,
        "username": user.username,
        "client_id": client.client_id,
        "scopes": scopes.split(),
        "code_challenge": code_challenge  # PKCE: uložit challenge pro pozdější ověření
    }

    save_authorization_code(auth_code, code_data)

    # Redirect back with code
    redirect_url = f"{redirect_uri}?code={auth_code}"
    if state:
        redirect_url += f"&state={state}"

    return RedirectResponse(redirect_url, status_code=302)


# ============================================
# Token Endpoint - ověří code_verifier
# ============================================

@router.post("/token", response_model=TokenResponse)
def exchange_code(
    grant_type: str = Form(...),
    code: str = Form(...),
    client_id: str = Form(...),
    code_verifier: str = Form(...),  # PKCE: verifier místo client_secret!
    redirect_uri: str = Form(...),
    db: Session = Depends(get_db)
):
    """
    Token Endpoint s PKCE ověřením.

    KEY DIFFERENCE from Authorization Code flow:
    - No client_secret required
    - Uses code_verifier instead
    - Verifier is validated against stored code_challenge

    PKCE Verification:
    1. Načte authorization code z Redis (obsahuje code_challenge)
    2. Vypočítá expected_challenge = SHA256(code_verifier)
    3. Porovná expected_challenge s uloženou code_challenge
    4. Pokud match → vydá access token
    """

    # Validate grant_type
    if grant_type != "authorization_code":
        logger.warning("PKCE token exchange failed: invalid grant_type", extra=log_auth_event(
            event_type="token_exchange_failed",
            success=False,
            auth_flow="pkce",
            client_id=client_id,
            reason="invalid_grant_type"
        ))
        raise HTTPException(400, f"Unsupported grant_type: {grant_type}")

    # Get authorization code from Redis
    code_data = get_authorization_code(code)

    if not code_data:
        logger.warning("PKCE token exchange failed: invalid code", extra=log_auth_event(
            event_type="token_exchange_failed",
            success=False,
            auth_flow="pkce",
            client_id=client_id,
            reason="invalid_code"
        ))
        raise HTTPException(400, "Invalid or expired authorization code")

    # Validate client_id
    if code_data["client_id"] != client_id:
        logger.warning("PKCE token exchange failed: client mismatch", extra=log_auth_event(
            event_type="token_exchange_failed",
            success=False,
            auth_flow="pkce",
            client_id=client_id,
            reason="client_mismatch"
        ))
        raise HTTPException(400, "Client ID mismatch")

    # Validate client
    client = db.query(OAuth2Client).filter(
        OAuth2Client.client_id == client_id
    ).first()

    if not client:
        logger.warning("PKCE token exchange failed: client not found", extra=log_auth_event(
            event_type="token_exchange_failed",
            success=False,
            auth_flow="pkce",
            client_id=client_id,
            reason="client_not_found"
        ))
        raise HTTPException(400, "Invalid client_id")

    # Validate redirect_uri
    if redirect_uri not in client.redirect_uri_list:
        logger.warning("PKCE token exchange failed: invalid redirect_uri", extra=log_auth_event(
            event_type="token_exchange_failed",
            success=False,
            auth_flow="pkce",
            client_id=client_id,
            reason="invalid_redirect_uri"
        ))
        raise HTTPException(400, "Invalid redirect_uri")

    # PKCE: Ověřit code_verifier
    if "code_challenge" not in code_data:
        logger.warning("PKCE token exchange failed: missing code_challenge", extra=log_auth_event(
            event_type="token_exchange_failed",
            success=False,
            auth_flow="pkce",
            client_id=client_id,
            reason="missing_code_challenge"
        ))
        raise HTTPException(400, "Missing code_challenge in authorization code")

    if not verify_code_verifier(code_verifier, code_data["code_challenge"]):
        logger.warning("PKCE token exchange failed: invalid code_verifier", extra=log_auth_event(
            event_type="token_exchange_failed",
            success=False,
            auth_flow="pkce",
            client_id=client_id,
            reason="invalid_code_verifier"
        ))
        raise HTTPException(400, "Invalid code_verifier")

    # Delete the authorization code (single use)
    delete_authorization_code(code)

    # Create access token
    access_token = create_access_token(
        sub=code_data["username"],
        extra_data={
            "user_id": code_data["user_id"],
            "client_id": code_data["client_id"],
            "scopes": " ".join(code_data["scopes"]),
            "pkce": True  # Indikace, že token byl získán přes PKCE
        }
    )

    logger.info("PKCE access token issued after code_verifier validation", extra=log_token_issued(
        token_type="access",
        auth_flow="pkce",
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


# ============================================
# Userinfo Endpoint - získat user info z tokenu
# ============================================

@router.get("/userinfo", response_model=UserInfoResponse)
def get_userinfo(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Get user information from access token.

    Authorization: Bearer <access_token>
    """
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(401, "Missing or invalid Authorization header")

    token = auth_header.split(" ")[1]
    payload = decode_token(token)

    if not payload:
        raise HTTPException(401, "Invalid or expired token")

    username = payload.get("sub")
    if not username:
        raise HTTPException(401, "Invalid token payload")

    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(404, "User not found")

    return UserInfoResponse(
        sub=str(user.id),
        username=user.username,
        email=user.email,
        full_name=user.full_name
    )


# ============================================
# PKCE Demo Endpoint - pro klienty
# ============================================

@router.get("/pkce/demo", response_model=PKCEDemoResponse)
def pkce_demo():
    """
    Demo endpoint ukazující PKCE flow.

    Vrací vygenerovaný PKCE pair a příklady requestů.
    Klienti by měli generovat verifier/challenge na své straně!
    """
    verifier = generate_code_verifier()
    challenge = create_code_challenge(verifier)

    return PKCEDemoResponse(
        code_verifier=verifier,
        code_challenge=challenge,
        code_challenge_method="S256",
        example_authorize_url=(
            f"/oauth2/authorize?"
            f"client_id=pkce-spa-client&"
            f"redirect_uri=http://localhost:3000/callback&"
            f"response_type=code&"
            f"code_challenge={challenge}&"
            f"code_challenge_method=S256"
        ),
        example_token_request={
            "grant_type": "authorization_code",
            "code": "<code_from_redirect>",
            "client_id": "pkce-spa-client",
            "code_verifier": verifier,
            "redirect_uri": "http://localhost:3000/callback"
        }
    )
