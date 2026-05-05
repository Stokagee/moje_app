from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
# Shared logging module with Loki integration
from shared.logging.logger import setup_logging, get_logger, intercept_standard_logging
from shared.logging.middleware import LoggingMiddleware
from app.api.endpoints.form_data import router as form_data_router
from app.api.endpoints.couriers import router as couriers_router
from app.api.endpoints.orders import router as orders_router
from app.api.endpoints.dispatch import router as dispatch_router
from app.api.endpoints.auth import router as auth_router  # NOVÝ
from app.api.endpoints.logs import router as logs_router
from app.database import engine, Base
from app.core.csrf import csrf_protect  # NOVÝ - CSRF protection
from app.core.config import settings  # NOVÝ - pro FORCE_HTTPS a jiné
# DŮLEŽITÉ: naimportovat modely před create_all, aby se tabulky vytvořily
from app.models import form_data as _model_form_data  # noqa: F401
from app.models import attachment as _model_attachment  # noqa: F401
from app.models import instruction as _model_instruction  # noqa: F401
from app.models import courier as _model_courier  # noqa: F401
from app.models import order as _model_order  # noqa: F401
from app.models import dispatch_log as _model_dispatch_log  # noqa: F401

# Vytvoření tabulek (pro vývoj, v produkci použít migrace)
Base.metadata.create_all(bind=engine)

# Nastavení logování
setup_logging()
logger = get_logger(__name__)
intercept_standard_logging()


# ============================================================================
# Exception Handlers - log error details before returning response
# ============================================================================

async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """
    Log HTTPException details before returning response.
    Captures error_detail for all endpoints automatically (400, 404, etc.).
    """
    logger.bind(
        event_type="http_exception",
        status_code=exc.status_code,
        error_detail=str(exc.detail),
        endpoint=request.url.path,
        method=request.method,
    ).error(f"HTTP {exc.status_code}: {exc.detail}")

    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """
    Log Pydantic validation errors (422) with full detail.
    Shows what fields failed validation and why.
    """
    errors = exc.errors()

    logger.bind(
        event_type="validation_error",
        status_code=422,
        error_detail=str(errors),
        endpoint=request.url.path,
        method=request.method,
    ).error(f"Validation error: {errors}")

    return JSONResponse(
        status_code=422,
        content={"detail": errors},
    )


# ============================================================================
# FastAPI Application
# ============================================================================

app = FastAPI(
    title="Food Delivery API",
    version="2.0.0",
    description="""
# Food Delivery API - Systém pro správu rozvozové služby

Toto API poskytuje kompletní řešení pro správu **kurýrů**, **objednávek** a **dispečinku**
rozvozové služby jídla.

## Hlavní funkce

### Kurýři (`/couriers`)
- Vytváření, úprava a mazání kurýrů
- Správa GPS polohy v reálném čase
- Stavy kurýrů: **available** (volný), **busy** (zaneprázdněný), **offline** (nedostupný)
- Systém tagů pro specializace (např. `bike`, `car`, `vip`, `fragile_ok`, `fast`)

### Objednávky (`/orders`)
- Kompletní životní cyklus objednávky
- Stavy: **CREATED** → **SEARCHING** → **ASSIGNED** → **PICKED** → **DELIVERED**
- Podpora VIP objednávek s prioritním zpracováním
- Požadavky na tagy kurýra (např. objednávka vyžadující `fragile_ok`)

### Dispečink (`/dispatch`)
- **Automatický dispatch**: Algoritmus vybírá nejbližšího vhodného kurýra
- **Manuální dispatch**: Operátor může přiřadit konkrétního kurýra
- Fázový algoritmus: 2km → 5km radius
- VIP objednávky preferují kurýry s tagem `vip`
- Historie všech přiřazení v logu

## Stavový diagram objednávky

```
CREATED ──────────────────────────────────────┐
    │                                          │
    ▼                                          │
SEARCHING (hledá se kurýr)                     │
    │                                          │
    ▼                                          ▼
ASSIGNED (kurýr přijal) ──────────────────► CANCELLED
    │                                          ▲
    ▼                                          │
PICKED (vyzvednuto) ───────────────────────────┤
    │                                          │
    ▼                                          │
DELIVERED (doručeno)                           │
```

## Stavový diagram kurýra

```
offline ◄───────────────────────────────────────┐
    │                                            │
    ▼                                            │
available (čeká na objednávku) ◄────────────────┤
    │                                            │
    ▼ (dispatch)                                 │ (deliver/cancel)
busy (doručuje) ─────────────────────────────────┘
```

## Algoritmus automatického dispatchnutí

1. Najde všechny **available** kurýry s platnou GPS polohou
2. Odfiltruje kurýry, kteří nemají požadované tagy
3. Pro VIP objednávky preferuje kurýry s tagem `vip`
4. **Fáze 1**: Hledá kurýry do 2 km od místa vyzvednutí
5. **Fáze 2**: Pokud nikdo není, rozšíří na 5 km
6. Vybere nejbližšího kurýra podle GPS vzdálenosti
7. Přiřadí kurýra a změní jeho stav na `busy`

## Příklady použití

### Kompletní workflow doručení
1. `POST /couriers` - Vytvoř kurýra
2. `PATCH /couriers/{id}/status` - Nastav `available`
3. `PATCH /couriers/{id}/location` - Aktualizuj GPS
4. `POST /orders` - Vytvoř objednávku
5. `POST /dispatch/auto/{order_id}` - Přiřaď kurýra
6. `POST /orders/{id}/pickup` - Kurýr vyzvednul
7. `POST /orders/{id}/deliver` - Kurýr doručil

---
**Kontakt**: support@fooddelivery.cz | **Verze**: 2.0.0
""",
    openapi_tags=[
        {
            "name": "couriers",
            "description": "Správa kurýrů - vytváření, editace, lokace a stavy. Kurýr je osoba, která doručuje objednávky zákazníkům.",
        },
        {
            "name": "orders",
            "description": "Správa objednávek - vytváření, lifecycle a doručení. Objednávka představuje požadavek na doručení od místa vyzvednutí k zákazníkovi.",
        },
        {
            "name": "dispatch",
            "description": "Dispečink - přiřazování kurýrů k objednávkám. Automatické i manuální přiřazení s logováním historie.",
        },
        {
            "name": "Formuláře",
            "description": "CRUD operace nad formuláři - vytváření, čtení, mazání záznamů. Obsahuje easter egg mini hru.",
        },
        {
            "name": "Přílohy",
            "description": "Nahrávání a správa souborových příloh k formulářům. Podporuje PDF a TXT, max 1 MB.",
        },
        {
            "name": "Instrukce",
            "description": "Textové instrukce k formulářům - vytvoření, aktualizace, čtení.",
        },
        {
            "name": "Mini hra",
            "description": "Easter egg funkce - vyhodnocení tajných jmen (neo, trinity, morpheus, jan, pavla, matrix).",
        },
    ],
    contact={
        "name": "Food Delivery Support",
        "email": "support@fooddelivery.cz",
    },
    license_info={
        "name": "MIT",
    },
)

# Exception handlers - log errors before returning response
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)

# CORS - allow requests from mobile apps and development clients
# In production, replace allow_origins with explicit trusted origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:20301", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# CSRF Middleware - ochrana proti Cross-Site Request Forgery
# ============================================================================
#
# CSRF (Cross-Site Request Forgery) je útok, kdy škodlivý web může nechat
# váš prohlížeč poslat požadavek na server, kde jste přihlášeni.
#
# Jak to funguje:
# 1. Frontend získá CSRF token z /api/v1/auth/csrf-token
# 2. Server vrátí token a nastaví ho do cookie
# 3. Frontend musí poslat token v hlavičce X-CSRF-Token
# 4. Middleware ověří, že header matchuje cookie
#
# CSRF je povoleno pouze v produkci (FORCE_HTTPS=true).
# V development módu není CSRF vyžadováno pro snadnější testování.
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request as StarletteRequest
from starlette.responses import JSONResponse as StarletteJSONResponse


class CSRFMiddleware(BaseHTTPMiddleware):
    """
    CSRF protection middleware pro unsafe HTTP metody.

    Aplikuje se na: POST, PUT, DELETE, PATCH
    Neaplikuje se na: GET, HEAD, OPTIONS, TRACE

    V development módu (FORCE_HTTPS=false) je middleware neaktivní.
    """

    UNSAFE_METHODS = {"POST", "PUT", "DELETE", "PATCH"}

    async def dispatch(self, request: StarletteRequest, call_next):
        # V development módu přeskočit CSRF
        if not settings.FORCE_HTTPS:
            return await call_next(request)

        # Aplikovat pouze na unsafe metody
        if request.method not in self.UNSAFE_METHODS:
            return await call_next(request)

        # Přeskočit CSRF pro auth endpointů (login, csrf-token)
        if request.url.path in ["/api/v1/auth/csrf-token", "/api/v1/auth/login"]:
            return await call_next(request)

        # Validovat CSRF token
        try:
            await csrf_protect.validate_csrf_token(request)
        except Exception as e:
            logger.warning(
                f"CSRF validation failed for {request.method} {request.url.path}: {e}",
                extra={
                    "event_type": "csrf_validation_failed",
                    "method": request.method,
                    "path": request.url.path,
                    "error": str(e)
                }
            )
            return StarletteJSONResponse(
                status_code=403,
                content={
                    "detail": "CSRF token missing or invalid. Get token from /api/v1/auth/csrf-token",
                    "error_code": "csrf_failed"
                }
            )

        return await call_next(request)


# Přidat CSRF middleware (před logging middleware, aby logoval i CSRF chyby)
app.add_middleware(CSRFMiddleware)


# Logging middleware - tracks all HTTP requests with duration_ms, endpoint, status_code
app.add_middleware(LoggingMiddleware)

# Přidání routerů
app.include_router(form_data_router, prefix="/api/v1")
app.include_router(couriers_router, prefix="/api/v1", tags=["couriers"])
app.include_router(orders_router, prefix="/api/v1", tags=["orders"])
app.include_router(dispatch_router, prefix="/api/v1", tags=["dispatch"])
app.include_router(logs_router, prefix="/api/v1", tags=["Logs"])
app.include_router(auth_router, prefix="/api/v1", tags=["authentication"])  # NOVÝ - auth endpoints

@app.get("/")
def root():
    return {"message": "Moje App API is running!", "docs": "/docs"}