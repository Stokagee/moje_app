"""
API Endpointy pro Auth Demo.

Organizováno do 4 sekcí:
1. Registrace (sdílená)
2. Session-based autentizace
3. JWT Token autentizace
4. OAuth2 s HTML stránkou
"""
from fastapi import APIRouter, Depends, HTTPException, Response, Request, Form
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from schemas import UserCreate, UserOut, Token, Message
from fake_users import create_user, verify_user, get_all_users
from auth import (
    # Session
    create_session_token,
    get_current_user_session,
    # JWT
    create_jwt_token,
    get_current_user_jwt,
    # OAuth2 HTML
    get_current_user_oauth2,
)
from config import SESSION_COOKIE_NAME


# Router instance
router = APIRouter()

# Jinja2 templates
templates = Jinja2Templates(directory="templates")


# ============================================================
# REGISTRACE (sdílená pro všechny typy auth)
# ============================================================

@router.post("/register", response_model=UserOut, tags=["Registrace"])
def register(user_data: UserCreate):
    """
    Registrace nového uživatele.

    Vytvoří uživatele v in-memory databázi.
    Heslo je automaticky zahashováno pomocí bcrypt.

    **Testovací účty (už existují):**
    - admin / admin123
    - user / user123
    """
    try:
        user = create_user(user_data.username, user_data.password, user_data.email)
        return UserOut(username=user["username"], email=user["email"])
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/users", response_model=list[UserOut], tags=["Registrace"])
def list_users():
    """Seznam všech registrovaných uživatelů."""
    return get_all_users()


# ============================================================
# 1. SESSION-BASED AUTENTIZACE
# ============================================================

@router.post("/session/login", response_model=Message, tags=["1. Session Auth"])
def session_login(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
):
    """
    Přihlášení pomocí session cookie.

    **Jak to funguje:**
    1. Server ověří username + password
    2. Vytvoří podepsanou session cookie
    3. Cookie se automaticky posílá s každým dalším requestem

    **Testovací účty:**
    - admin / admin123
    - user / user123
    """
    user = verify_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Neplatné přihlašovací údaje",
        )

    # Vytvoř session token a nastav cookie
    session_token = create_session_token(user["username"])
    response.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=session_token,
        httponly=True,  # JavaScript nemůže číst cookie (bezpečnost)
        samesite="lax",  # CSRF ochrana
    )

    return Message(message=f"Přihlášen jako {user['username']}")


@router.post("/session/logout", response_model=Message, tags=["1. Session Auth"])
def session_logout(response: Response):
    """
    Odhlášení - smaže session cookie.
    """
    response.delete_cookie(SESSION_COOKIE_NAME)
    return Message(message="Odhlášen")


@router.get("/session/me", response_model=UserOut, tags=["1. Session Auth"])
def session_me(user: dict = Depends(get_current_user_session)):
    """
    Vrátí aktuálně přihlášeného uživatele (session auth).

    Vyžaduje platnou session cookie.
    """
    return user


# ============================================================
# 2. JWT TOKEN AUTENTIZACE
# ============================================================

@router.post("/jwt/login", response_model=Token, tags=["2. JWT Auth"])
def jwt_login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Přihlášení pomocí JWT tokenu.

    **Jak to funguje:**
    1. Server ověří username + password
    2. Vrátí JWT token
    3. Klient posílá token v hlavičce: `Authorization: Bearer <token>`

    **Testovací účty:**
    - admin / admin123
    - user / user123

    **Swagger UI:**
    Klikni na "Authorize" tlačítko vpravo nahoře a zadej credentials.
    """
    user = verify_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Neplatné přihlašovací údaje",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_jwt_token(user["username"])
    return Token(access_token=access_token, token_type="bearer")


@router.get("/jwt/me", response_model=UserOut, tags=["2. JWT Auth"])
def jwt_me(user: dict = Depends(get_current_user_jwt)):
    """
    Vrátí aktuálně přihlášeného uživatele (JWT auth).

    Vyžaduje platný Bearer token v hlavičce Authorization.
    """
    return user


# ============================================================
# 3. OAUTH2 S VLASTNÍ HTML STRÁNKOU
# ============================================================

@router.get("/oauth2/login", response_class=HTMLResponse, tags=["3. OAuth2 HTML"])
def oauth2_login_page(request: Request, error: str = None):
    """
    Zobrazí HTML login stránku.

    Toto je vlastní login formulář (ne Swagger UI).
    Po úspěšném přihlášení vrátí JWT token.
    """
    return templates.TemplateResponse(
        "login.html",
        {"request": request, "error": error},
    )


@router.post("/oauth2/token", response_model=Token, tags=["3. OAuth2 HTML"])
def oauth2_token(
    username: str = Form(...),
    password: str = Form(...),
):
    """
    Zpracuje login z HTML formuláře.

    **Poznámka:** Toto je endpoint pro HTML formulář,
    přijímá data jako form-data (ne JSON).
    """
    user = verify_user(username, password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Neplatné přihlašovací údaje",
        )

    access_token = create_jwt_token(user["username"])
    return Token(access_token=access_token, token_type="bearer")


@router.get("/oauth2/me", response_model=UserOut, tags=["3. OAuth2 HTML"])
def oauth2_me(user: dict = Depends(get_current_user_oauth2)):
    """
    Vrátí aktuálně přihlášeného uživatele (OAuth2 HTML auth).

    Vyžaduje platný Bearer token.
    """
    return user
