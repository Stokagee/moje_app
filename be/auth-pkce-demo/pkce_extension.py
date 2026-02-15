# PKCE Extension for Authorization Code Demo

"""
Tento soubor ukazuje, jak rozšířit Authorization Code Demo o PKCE.

PKCE (Proof Key for Code Exchange) je rozšíření OAuth2 pro:
- Single Page Applications (SPA)
- Mobile apps (iOS, Android)
- Jakoukoli aplikaci, kde nemůže bezpečně uložit client_secret

Hlavní změny oproti standardnímu Authorization Code flow:
1. Klient generuje code_verifier a code_challenge
2. code_challenge se přidá do /authorize requestu
3. code_verifier se přidá do /token requestu
4. Server ověřuje, že challenge odpovídá verifieru
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
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
from app.models.auth_code import User, OAuth2Client
from app.schemas.oauth2 import TokenResponse
from pydantic import BaseModel
import secrets
import hashlib
import base64

router = APIRouter(prefix="/oauth2", tags=["oauth2-pkce"])
templates = Jinja2Templates(directory="templates")


# === PKCE Utilities ===

def verify_code_verifier(code_verifier: str, code_challenge: str) -> bool:
    """
    Ověří, zda code_verifier odpovídá code_challenge (S256 metoda).

    Args:
        code_verifier: Verifier z /token requestu
        code_challenge: Uložená challenge z /authorize requestu

    Returns:
        True pokud verifier odpovídá challenge
    """
    # Přepočítat challenge z verifieru
    verifier_hash = hashlib.sha256(code_verifier.encode()).digest()
    expected_challenge = base64.urlsafe_b64encode(verifier_hash).decode().rstrip('=')

    return expected_challenge == code_challenge


# === Modified Schemas for PKCE ===

class PKCETokenRequest(BaseModel):
    """Token request s code_verifier pro PKCE"""
    grant_type: str = "authorization_code"
    code: str
    client_id: str
    code_verifier: str  # PKCE: verifier místo client_secret
    redirect_uri: str


# === Modified Authorize Endpoint (s code_challenge) ===

@router.get("/authorize-pkce")
def authorize_pkce(
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

    Nové parametry:
    - code_challenge: Hash z code_verifieru
    - code_challenge_method: Metoda hashování (vždy "S256")
    """

    # Validate response_type
    if response_type != "code":
        raise HTTPException(400, f"Unsupported response_type: {response_type}")

    # Find client
    client = db.query(OAuth2Client).filter(
        OAuth2Client.client_id == client_id
    ).first()

    if not client or not client.is_active:
        raise HTTPException(400, "Invalid client_id")

    # Validate redirect_uri
    if redirect_uri not in client.redirect_uri_list:
        raise HTTPException(400, f"Invalid redirect_uri")

    # Validate code_challenge_method
    if code_challenge_method != "S256":
        raise HTTPException(400, "Unsupported code_challenge_method. Use 'S256'")

    # Validate scopes
    requested_scopes = scope.split() if scope else []
    for scope_item in requested_scopes:
        if scope_item not in client.scope_list:
            raise HTTPException(400, f"Invalid scope: {scope_item}")

    # Show consent page
    return templates.TemplateResponse("consent.html", {
        "request": request,
        "client_name": client.name,
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "state": state,
        "scopes": requested_scopes,
        "pkce_enabled": True  # Indikace pro šablonu
    })


# === Modified Approve Endpoint (uloží code_challenge) ===

class PKCEApproveForm(BaseModel):
    client_id: str
    redirect_uri: str
    state: str = None
    scopes: str
    code_challenge: str  # PKCE: uložit challenge
    username: str
    password: str


@router.post("/approve-pkce")
def approve_consent_pkce(
    request: Request,
    form_data: PKCEApproveForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Consent Approval s PKCE - uloží code_challenge.
    """

    # Authenticate user
    user = db.query(User).filter(User.username == form_data.username).first()

    if not user or not verify_password(form_data.password, user.hashed_password):
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
        raise HTTPException(400, "Invalid client_id")

    # Validate redirect_uri
    if form_data.redirect_uri not in client.redirect_uri_list:
        raise HTTPException(400, "Invalid redirect_uri")

    # Create authorization code
    auth_code = secrets.token_urlsafe(32)

    # Save authorization code s code_challenge
    code_data = {
        "user_id": user.id,
        "username": user.username,
        "client_id": client.client_id,
        "scopes": form_data.scopes.split(),
        "code_challenge": form_data.code_challenge  # PKCE: uložit challenge
    }

    save_authorization_code(auth_code, code_data)

    # Redirect back with code
    redirect_url = f"{form_data.redirect_uri}?code={auth_code}"
    if form_data.state:
        redirect_url += f"&state={form_data.state}"

    return RedirectResponse(redirect_url, status_code=302)


# === Modified Token Endpoint (ověří code_verifier) ===

@router.post("/token-pkce", response_model=TokenResponse)
def exchange_code_pkce(
    form_data: PKCETokenRequest,
    db: Session = Depends(get_db)
):
    """
    Token Endpoint s PKCE ověřením.

    Místo client_secret se ověřuje code_verifier.
    """

    # Validate grant_type
    if form_data.grant_type != "authorization_code":
        raise HTTPException(400, f"Unsupported grant_type")

    # Get authorization code from Redis
    code_data = get_authorization_code(form_data.code)

    if not code_data:
        raise HTTPException(400, "Invalid or expired authorization code")

    # Validate client_id
    if code_data["client_id"] != form_data.client_id:
        raise HTTPException(400, "Client ID mismatch")

    # Validate client
    client = db.query(OAuth2Client).filter(
        OAuth2Client.client_id == form_data.client_id
    ).first()

    if not client:
        raise HTTPException(400, "Invalid client_id")

    # Validate redirect_uri
    if form_data.redirect_uri not in client.redirect_uri_list:
        raise HTTPException(400, "Invalid redirect_uri")

    # PKCE: Ověřit code_verifier
    if "code_challenge" not in code_data:
        raise HTTPException(400, "Missing code_challenge in authorization code")

    if not verify_code_verifier(form_data.code_verifier, code_data["code_challenge"]):
        raise HTTPException(400, "Invalid code_verifier")

    # Delete the authorization code (single use)
    delete_authorization_code(form_data.code)

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

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        scope=" ".join(code_data["scopes"])
    )


# === PKCE Demo Endpoint (pro klienty) ===

@router.get("/pkce/demo")
def pkce_demo():
    """
    Demo endpoint ukazující PKCE flow.

    Vrací vygenerovaný PKCE pair a příklady requestů.
    """
    from pkce_utils import generate_pkce_pair

    verifier, challenge = generate_pkce_pair()

    return {
        "message": "PKCE Demo - Generate this on the client side",
        "code_verifier": verifier,
        "code_challenge": challenge,
        "code_challenge_method": "S256",
        "example_authorize_url": (
            f"/oauth2/authorize-pkce?"
            f"client_id=demo-client&"
            f"redirect_uri=http://localhost:3000/callback&"
            f"response_type=code&"
            f"code_challenge={challenge}&"
            f"code_challenge_method=S256"
        ),
        "example_token_request": {
            "grant_type": "authorization_code",
            "code": "<code_from_redirect>",
            "client_id": "demo-client",
            "code_verifier": verifier,
            "redirect_uri": "http://localhost:3000/callback"
        }
    }
