"""mTLS (Mutual TLS) Middleware pro FastAPI.

Tento modul poskytuje middleware pro ověření klientských certifikátů
přicházejících z Nginx reverse proxy.

Jak mTLS funguje:
1. Klient se připojí k Nginx přes HTTPS
2. Nginx vyžaduje klientský certifikát
3. Klient předloží certifikát
4. Nginx ověří certifikát a předá informace v hlavičkách
5. Tento middleware ověří hlavičky a blokuje neautorizované requesty

Použití:
    # V main.py
    from app.core.mtls import MTLSMiddleware

    app = FastAPI()
    app.add_middleware(MTLSMiddleware)
"""

from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from typing import Optional, Callable
import logging

from app.core.config import settings


logger = logging.getLogger(__name__)


class MTLSMiddleware(BaseHTTPMiddleware):
    """
    Middleware pro ověření mTLS klientského certifikátu.

    Tento middleware:
    1. Čte hlavičky od Nginx (X-Client-Verified, X-Client-CN)
    2. Ověřuje, že certifikát byl validní
    3. Volitelně kontroluje CN (Common Name) proti whitelistu

    Hlavičky od Nginx:
    - X-Client-Verified: "SUCCESS" nebo "FAILED:reason"
    - X-Client-CN: CN z klientského certifikátu
    - X-Client-Fingerprint: SHA256 fingerprint certifikátu

    Konfigurace:
    - FORCE_HTTPS: Pokud je true, middleware je aktivní
    - TRUSTED_PROXIES: IP adresy důvěryhodných proxy (Nginx)
    """

    async def dispatch(self, request: Request, call_next: Callable):
        # V development módu přeskočit mTLS
        if not settings.FORCE_HTTPS:
            logger.debug(
                f"mTLS skipped (FORCE_HTTPS=false) for {request.method} {request.url.path}"
            )
            return await call_next(request)

        # Přeskočit pro health check a docs
        if request.url.path in ["/health", "/docs", "/openapi.json", "/"]:
            return await call_next(request)

        # Přeskočit pro OPTIONS (CORS preflight)
        if request.method == "OPTIONS":
            return await call_next(request)

        # Číst hlavičky od Nginx
        client_verified = request.headers.get("X-Client-Verified", "")
        client_cn = request.headers.get("X-Client-CN", "")
        client_fingerprint = request.headers.get("X-Client-Fingerprint", "")

        # Ověřit, že request přišel přes mTLS
        if not client_verified:
            logger.warning(
                f"mTLS missing for {request.method} {request.url.path} - "
                "X-Client-Verified header not found. "
                "Request probably bypassed Nginx."
            )
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={
                    "detail": "mTLS required. Access denied.",
                    "error_code": "mtls_missing"
                }
            )

        if client_verified != "SUCCESS":
            logger.warning(
                f"mTLS verification failed for {request.method} {request.url.path}: "
                f"X-Client-Verified={client_verified}, CN={client_cn}"
            )
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={
                    "detail": f"Client certificate verification failed: {client_verified}",
                    "error_code": "mtls_failed"
                }
            )

        # Volitelně: kontrola CN proti whitelistu
        # if client_cn not in ALLOWED_CLIENTS:
        #     logger.warning(f"Unauthorized client CN: {client_cn}")
        #     return JSONResponse(
        #         status_code=403,
        #         content={"detail": "Client certificate not authorized"}
        #     )

        # Uložit certifikát info do request state pro pozdější použití
        request.state.mtls_verified = True
        request.state.mtls_cn = client_cn
        request.state.mtls_fingerprint = client_fingerprint

        logger.info(
            f"mTLS verified for {request.method} {request.url.path}: "
            f"CN={client_cn}, fingerprint={client_fingerprint[:16]}..."
        )

        return await call_next(request)


async def get_mtls_client(request: Request) -> dict:
    """
    Dependency pro získání mTLS klientských informací.

    Použití:
        @router.get("/protected")
        async def protected(client = Depends(get_mtls_client)):
            return {"client_cn": client["cn"]}

    Returns:
        dict s CN a fingerprint klientského certifikátu

    Raises:
        403 Forbidden: Pokud mTLS nebylo ověřeno
    """
    if not getattr(request.state, "mtls_verified", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="mTLS verification required"
        )

    return {
        "cn": request.state.mtls_cn,
        "fingerprint": request.state.mtls_fingerprint,
        "verified": True
    }


def require_client_cn(allowed_cns: list[str]):
    """
    Factory pro vytvoření dependency, která kontroluje CN klientského certifikátu.

    Použití:
        @router.get("/admin-only")
        async def admin_only(client = Depends(require_client_cn(["admin-client"]))):
            return {"message": "Admin access granted"}

    Args:
        allowed_cns: Seznam povolených CN (Common Names)

    Returns:
        FastAPI dependency funkce
    """
    async def cn_checker(request: Request) -> dict:
        client = await get_mtls_client(request)

        if client["cn"] not in allowed_cns:
            logger.warning(
                f"mTLS CN not authorized: {client['cn']} not in {allowed_cns}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Client certificate CN '{client['cn']}' not authorized"
            )

        return client

    return cn_checker
