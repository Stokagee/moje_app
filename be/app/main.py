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
# Food Delivery API - System for managing a food delivery service

This API provides a complete solution for managing **couriers**, **orders**, and **dispatch**
for a food delivery service.

## Key features

### Couriers (`/couriers`)
- Create, update, and delete couriers
- Real-time GPS location management
- Courier statuses: **available** (free), **busy** (delivering), **offline** (unavailable)
- Tag system for specializations (e.g. `bike`, `car`, `vip`, `fragile_ok`, `fast`)

### Orders (`/orders`)
- Complete order lifecycle
- Statuses: **CREATED** → **SEARCHING** → **ASSIGNED** → **PICKED** → **DELIVERED**
- VIP order support with priority processing
- Courier tag requirements (e.g. orders requiring `fragile_ok`)

### Dispatch (`/dispatch`)
- **Auto dispatch**: Algorithm selects the nearest suitable courier
- **Manual dispatch**: Operator can assign a specific courier
- Phased algorithm: 750 km → 1500 km radius
- VIP orders prefer couriers with the `vip` tag
- Full assignment history log

## Order state diagram

```
CREATED ──────────────────────────────────────┐
    │                                          │
    ▼                                          │
SEARCHING (looking for courier)                │
    │                                          │
    ▼                                          ▼
ASSIGNED (courier accepted) ───────────────► CANCELLED
    │                                          ▲
    ▼                                          │
PICKED (picked up) ────────────────────────────┤
    │                                          │
    ▼                                          │
DELIVERED                                      │
```

## Courier state diagram

```
offline ◄───────────────────────────────────────┐
    │                                            │
    ▼                                            │
available (waiting for order) ◄─────────────────┤
    │                                            │
    ▼ (dispatch)                                 │ (deliver/cancel)
busy (delivering) ───────────────────────────────┘
```

## Auto-dispatch algorithm

1. Finds all **available** couriers with a valid GPS location
2. Filters out couriers who do not have the required tags
3. For VIP orders, prefers couriers with the `vip` tag
4. **Phase 1**: Looks for couriers within 750 km of the pickup point
5. **Phase 2**: If none found, expands to 1500 km
6. Selects the nearest courier by GPS distance
7. Assigns the courier and changes their status to `busy`

## Usage examples

### Complete delivery workflow
1. `POST /couriers` - Create a courier
2. `PATCH /couriers/{id}/status` - Set to `available`
3. `PATCH /couriers/{id}/location` - Update GPS
4. `POST /orders` - Create an order
5. `POST /dispatch/auto/{order_id}` - Assign a courier
6. `POST /orders/{id}/pickup` - Courier picked up
7. `POST /orders/{id}/deliver` - Courier delivered

---
**Contact**: support@fooddelivery.cz | **Version**: 2.0.0
""",
    openapi_tags=[
        {
            "name": "couriers",
            "description": "Courier management - create, edit, location and status updates. A courier is a person who delivers orders to customers.",
        },
        {
            "name": "orders",
            "description": "Order management - creation, lifecycle and delivery. An order represents a delivery request from a pickup location to a customer.",
        },
        {
            "name": "dispatch",
            "description": "Dispatch - assigning couriers to orders. Automatic and manual assignment with history logging.",
        },
        {
            "name": "Forms",
            "description": "Form CRUD operations - create, read, delete records. Includes easter egg mini game.",
        },
        {
            "name": "Attachments",
            "description": "File attachment upload and management for forms. Supports PDF and TXT, max 1 MB.",
        },
        {
            "name": "Instructions",
            "description": "Text instructions for forms - create, update, read.",
        },
        {
            "name": "Mini game",
            "description": "Easter egg feature - evaluates secret names (neo, trinity, morpheus, jan, pavla, matrix).",
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
