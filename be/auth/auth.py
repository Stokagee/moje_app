"""
Autentizační logika - 3 typy autentizace v jednom souboru.

1. SESSION-BASED - klasický login s cookie
2. JWT TOKEN - stateless Bearer token
3. OAUTH2 HTML - vlastní login stránka

Pro výukové účely - demonstrace rozdílů mezi přístupy.
"""
from datetime import datetime, timedelta, timezone
from typing import Optional

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, APIKeyCookie
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from sqlalchemy.orm import Session

from config import (
    SECRET_KEY,
    ALGORITHM,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    SESSION_COOKIE_NAME,
    SESSION_MAX_AGE,
)
from database import get_db
from crud import get_user


# ============================================================
# 1. SESSION-BASED AUTENTIZACE
# ============================================================
"""
Jak to funguje:
1. Uživatel pošle username + password
2. Server ověří credentials
3. Server vytvoří podepsanou session cookie
4. Cookie se posílá s každým requestem (automaticky prohlížečem)
5. Server ověří podpis cookie a vrátí uživatele

VÝHODY:
- Jednoduchý koncept
- Prohlížeč automaticky spravuje cookies
- Server může invalidovat session

NEVÝHODY:
- Stavová (stateful) autentizace
- Problematické pro horizontální škálování
- CSRF útoky (potřeba CSRF tokeny)
"""

# Serializer pro podepsané cookies (itsdangerous)
session_serializer = URLSafeTimedSerializer(SECRET_KEY)

# FastAPI security scheme pro cookies
cookie_scheme = APIKeyCookie(name=SESSION_COOKIE_NAME, auto_error=False)


def create_session_token(username: str) -> str:
    """
    Vytvoří podepsaný session token.

    Args:
        username: Uživatelské jméno

    Returns:
        Podepsaný token string
    """
    return session_serializer.dumps({"username": username})


def verify_session_token(token: str) -> Optional[str]:
    """
    Ověří a dekóduje session token.

    Args:
        token: Podepsaný token

    Returns:
        Username nebo None pokud token neplatný/expirovaný
    """
    try:
        data = session_serializer.loads(token, max_age=SESSION_MAX_AGE)
        return data.get("username")
    except (BadSignature, SignatureExpired):
        return None


async def get_current_user_session(
    session_token: str = Depends(cookie_scheme),
    db: Session = Depends(get_db),
) -> dict:
    """
    FastAPI dependency pro session-based autentizaci.

    Použití v endpointu:
        @app.get("/session/me")
        def me(user: dict = Depends(get_current_user_session)):
            return user
    """
    if not session_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nepřihlášen - chybí session cookie",
        )

    username = verify_session_token(session_token)
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Neplatná nebo expirovaná session",
        )

    user = get_user(db, username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Uživatel neexistuje",
        )

    return {"username": user.username, "email": user.email}


# ============================================================
# 2. JWT TOKEN AUTENTIZACE
# ============================================================
"""
Jak to funguje:
1. Uživatel pošle username + password
2. Server ověří credentials
3. Server vytvoří JWT token obsahující user info + expiraci
4. Klient uloží token a posílá ho v Authorization header
5. Server ověří podpis tokenu a extrahuje user info

VÝHODY:
- Bezstavová (stateless) autentizace
- Snadné horizontální škálování
- Token obsahuje metadata (claims)
- Žádné CSRF problémy

NEVÝHODY:
- Token nelze invalidovat před expirací
- Větší velikost než session cookie
- Klient musí spravovat token
"""

# FastAPI OAuth2 scheme - automaticky hledá "Authorization: Bearer <token>"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/jwt/login")


def create_jwt_token(username: str, expires_delta: Optional[timedelta] = None) -> str:
    """
    Vytvoří JWT token.

    Args:
        username: Uživatelské jméno (bude v 'sub' claim)
        expires_delta: Volitelná expirace (default: ACCESS_TOKEN_EXPIRE_MINUTES)

    Returns:
        Zakódovaný JWT token string
    """
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    # JWT payload (claims)
    payload = {
        "sub": username,           # subject - identifikátor uživatele
        "exp": expire,             # expiration time
        "iat": datetime.now(timezone.utc),  # issued at
    }

    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def verify_jwt_token(token: str) -> Optional[str]:
    """
    Ověří a dekóduje JWT token.

    Args:
        token: JWT token string

    Returns:
        Username nebo None pokud token neplatný
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        return username
    except jwt.PyJWTError:
        return None


async def get_current_user_jwt(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> dict:
    """
    FastAPI dependency pro JWT autentizaci.

    Použití v endpointu:
        @app.get("/jwt/me")
        def me(user: dict = Depends(get_current_user_jwt)):
            return user
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Neplatný token",
        headers={"WWW-Authenticate": "Bearer"},
    )

    username = verify_jwt_token(token)
    if not username:
        raise credentials_exception

    user = get_user(db, username)
    if not user:
        raise credentials_exception

    return {"username": user.username, "email": user.email}


# ============================================================
# 3. OAUTH2 S VLASTNÍ HTML STRÁNKOU
# ============================================================
"""
Jak to funguje:
1. Uživatel navštíví /oauth2/login - zobrazí se HTML formulář
2. Uživatel vyplní credentials a odešle formulář
3. Server ověří credentials a vrátí JWT token
4. Klient může použít token pro další requesty

Toto je kombinace:
- Vlastní HTML login stránka (ne Swagger UI)
- JWT token pro autentizaci API

VÝHODY:
- Plná kontrola nad UI
- Vlastní branding/design
- Kombinuje výhody JWT

NEVÝHODY:
- Více práce na implementaci
- Nutnost spravovat HTML šablony
"""

# OAuth2 scheme pro HTML flow (jiný tokenUrl)
oauth2_html_scheme = OAuth2PasswordBearer(tokenUrl="/oauth2/token", auto_error=False)


async def get_current_user_oauth2(
    token: str = Depends(oauth2_html_scheme),
    db: Session = Depends(get_db),
) -> dict:
    """
    FastAPI dependency pro OAuth2 HTML autentizaci.

    Funguje stejně jako JWT, ale token URL je /oauth2/token.
    """
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nepřihlášen",
            headers={"WWW-Authenticate": "Bearer"},
        )

    username = verify_jwt_token(token)
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Neplatný token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = get_user(db, username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Uživatel neexistuje",
        )

    return {"username": user.username, "email": user.email}
