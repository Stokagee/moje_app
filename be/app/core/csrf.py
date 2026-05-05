"""CSRF (Cross-Site Request Forgery) Protection.

Tento modul poskytuje CSRF ochranu pro state-changing operace.

Jak CSRF funguje:
1. Frontend si vyžádá CSRF token z /api/v1/auth/csrf-token
2. Server vrátí token a nastaví ho do cookie
3. Frontend musí poslat token v hlavičce X-CSRF-Token
4. Server ověří, že header matchuje cookie

Použití:
    # V endpointu
    from app.core.csrf import get_csrf_protect

    @router.get("/csrf-token")
    async def get_csrf_token(response: Response):
        csrf = get_csrf_protect()
        token = csrf.generate_csrf_token()
        csrf.set_csrf_cookie(token, response)
        return {"csrf_token": token}
"""

from fastapi import Request, HTTPException, status, Response
from fastapi_csrf_protect import CsrfProtect
from fastapi_csrf_protect.exceptions import CsrfProtectError
from pydantic import BaseModel
from typing import Optional

from app.core.config import settings


class CsrfSettings(BaseModel):
    """CSRF konfigurace pro fastapi-csrf-protect."""
    secret_key: str = settings.CSRF_SECRET_KEY
    cookie_key: str = "csrf_token"
    header_name: str = "X-CSRF-Token"
    header_type: Optional[str] = None
    cookie_path: str = "/"
    cookie_domain: Optional[str] = None
    cookie_secure: bool = settings.FORCE_HTTPS
    cookie_samesite: str = "strict"
    cookie_httponly: bool = False
    token_lifetime: int = 3600


# Načtení konfigurace
@CsrfProtect.load_config
def get_csrf_settings():
    return CsrfSettings()


# Globální instance
csrf_protect = CsrfProtect()


async def validate_csrf_or_raise(request: Request):
    """
    Validuje CSRF token a vyhodí výjimku pokud je nevalidní.

    Použití:
        @router.post("/orders")
        async def create_order(request: Request):
            await validate_csrf_or_raise(request)
            # ... business logic
    """
    try:
        await csrf_protect.validate_csrf_token(request)
    except CsrfProtectError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"CSRF validation failed: {e.reason}"
        )


def generate_csrf_token(response: Response) -> str:
    """
    Generuje CSRF token a nastavuje cookie.

    Použití:
        @router.get("/csrf-token")
        async def get_csrf_token(response: Response):
            token = generate_csrf_token(response)
            return {"csrf_token": token}
    """
    token, _ = csrf_protect.generate_csrf_tokens()
    csrf_protect.set_csrf_cookie(token, response)
    return token


# Dependency pro automatickou CSRF validaci
async def csrf_protect_dep(
    request: Request,
    response: Response
):
    """
    FastAPI dependency pro CSRF validaci.

    Použití:
        @router.post("/protected", dependencies=[Depends(csrf_protect_dep)])
        async def protected():
            pass
    """
    await validate_csrf_or_raise(request)
    return True
