# Main FastAPI application for PKCE Demo

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.core.database import init_db
from app.core.security import get_password_hash
from app.routes import oauth2_pkce
from app.models.pkce_client import User, OAuth2Client
from app.core.database import SessionLocal
from shared.logging.logger import setup_logging, get_logger
from shared.logging.middleware import LoggingMiddleware

# Setup logging
setup_logging()
logger = get_logger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="OAuth2 PKCE Flow Demo",
    version="1.0.0",
    description="""# OAuth2 PKCE (Proof Key for Code Exchange) Flow Demo

Implementace OAuth2 **Authorization Code flow s PKCE** - standard pro **veřejné klienty** (SPA, mobilní apps).

## Co je PKCE?

PKCE (Proof Key for Code Exchange) rozšiřuje Authorization Code flow pro aplikace, které nemohou bezpečně uložit `client_secret`:

- **Single Page Applications** (React, Vue, Angular)
- **Mobile apps** (iOS, Android)
- **Desktop aplikace**

## Problém který řeší

V klasickém Authorization Code flow:
- Klient musí mít tajný `client_secret`
- Ale v SPA/mobile app nelze bezpečně uložit secret
- Secret je viditelný v browseru nebo dekompilovatelný v app

Řešení PKCE:
- Místo secret se používá dynamický `code_verifier`
- Verifier je generován při každém requestu
- Server ověřuje, že klient zná původní verifier

## PKCE Flow Diagram

```
┌──────────┐      ┌─────────┐      ┌──────────┐
┌──────────┐      │  SPA /  │      │ OAuth2   │
│  User    │      │ Mobile  │      │ Server   │
│ Browser  │      │  App    │      │          │
└────┬─────┘      └────┬────┘      └────┬─────┘
     │                 │                 │
     │ 1. Login with X                  │
     │────────────────>│                 │
     │                 │                 │
     │ 2. Generate PKCE pair:           │
     │    verifier = random()           │
     │    challenge = SHA256(verifier)  │
     │<─────────────────│                 │
     │                 │                 │
     │ 3. Redirect → /oauth2/authorize  │
     │    ?code_challenge=...           │
     │                 │────────────────>│
     │                 │                 │
     │ 4. Show consent page              │
     │<─────────────────────────────────│
     │                 │                 │
     │ 5. User approves                  │
     │─────────────────────────────────>│
     │                 │                 │
     │ 6. Redirect s code=abc            │
     │<─────────────────────────────────│
     │                 │                 │
     │ 7. POST /oauth2/token            │
     │    code=abc                       │
     │    code_verifier=ORIGINAL         │
     │                 │────────────────>│
     │                 │ 8. Verify:      │
     │                 │    SHA256(verifier) == stored_challenge?
     │                 │ 9. access_token  │
     │                 │<────────────────│
```

## Klíčové rozdíly oproti Authorization Code flow

| Aspect | Authorization Code | PKCE |
|--------|-------------------|------|
| Client type | Confidential (server) | Public (SPA/mobile) |
| Client secret | Required | ❌ Not used |
| Code verifier | ❌ Not used | ✅ Required |
| Code challenge | ❌ Not used | ✅ Required |
| Security | Client secret proves identity | Verifier proves identity |

## Endpointy

1. **GET /oauth2/authorize** - Autorizační endpoint s `code_challenge`
   - Parametry: `client_id`, `redirect_uri`, `code_challenge`, `code_challenge_method=S256`

2. **POST /oauth2/approve** - Consent approval
   - Uloží `code_challenge` s authorization code

3. **POST /oauth2/token** - Token exchange s `code_verifier`
   - Parametry: `code`, `client_id`, `code_verifier`, `redirect_uri`
   - **Bez client_secret!**

4. **GET /oauth2/userinfo** - Získat user info z tokenu

5. **GET /oauth2/pkce/demo** - Demo endpoint pro PKCE pair generování

## Demo Credentials

- **User**: username=`demo`, password=`demo123`
- **Client**: client_id=`pkce-spa-client`, client_secret=`None` (veřejný klient!)
- **Redirect URI**: `http://localhost:3000/callback`

## Požadavky

- **Redis**: Musí běžet pro uložení authorization codes
- **Authorization code**: Platnost 10 minut, jednorázové použití
- **PKCE**: Vždy vyžadovat `S256` metodu (odmítnout `plain`)
""",
    openapi_tags=[
        {
            "name": "oauth2-pkce",
            "description": "OAuth2 PKCE flow endpointy pro veřejné klienty"
        },
        {
            "name": "root",
            "description": "Základní endpointy"
        },
        {
            "name": "health",
            "description": "Health check endpointy"
        }
    ]
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add logging middleware
app.add_middleware(LoggingMiddleware)


# Exception handler for better error messages
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": str(exc)}
    )


# Include routers
app.include_router(oauth2_pkce.router)


@app.on_event("startup")
def startup_event():
    """Initialize database on startup and create demo data"""
    logger.info("Starting PKCE Demo API", extra={"event_type": "api_startup"})
    init_db()

    db = SessionLocal()
    try:
        # Create demo user
        demo_user = db.query(User).filter(User.username == "demo").first()
        if not demo_user:
            demo_user = User(
                username="demo",
                email="demo@example.com",
                hashed_password=get_password_hash("demo123"),
                full_name="Demo User"
            )
            db.add(demo_user)
            db.commit()
            logger.info("Demo user created", extra={"event_type": "demo_data_initialized", "username": "demo"})

        # Create public client (PKCE) - NO client_secret!
        demo_client = db.query(OAuth2Client).filter(
            OAuth2Client.client_id == "pkce-spa-client"
        ).first()

        if not demo_client:
            demo_client = OAuth2Client(
                client_id="pkce-spa-client",
                client_secret=None,  # PKCE clients don't have secrets!
                name="PKCE SPA Client",
                redirect_uris="\n".join(settings.ALLOWED_REDIRECT_URIS),
                scopes="read write",
                is_public=1  # Public client (PKCE)
            )
            db.add(demo_client)
            db.commit()
            logger.info("Demo public client created", extra={
                "event_type": "demo_data_initialized",
                "client_id": "pkce-spa-client",
                "is_public_client": True
            })

    finally:
        db.close()

    logger.info("Database initialized", extra={"event_type": "db_initialized"})


@app.get("/", tags=["root"])
def root():
    """Root endpoint s informacemi o API"""
    return {
        "message": "OAuth2 PKCE Flow Demo API",
        "docs": "/docs",
        "pkce_info": {
            "what_is_pkce": "Proof Key for Code Exchange - secure auth for public clients (SPA, mobile)",
            "key_difference": "No client_secret required! Uses code_verifier instead.",
            "flow_steps": {
                "1": "Generate PKCE pair: verifier + challenge = SHA256(verifier)",
                "2": "GET /oauth2/authorize?code_challenge=... - Show consent page",
                "3": "POST /oauth2/approve - User approves (stores code_challenge)",
                "4": "GET redirect?code=... - Receive authorization code",
                "5": "POST /oauth2/token?code_verifier=... - Exchange code for token",
                "6": "GET /oauth2/userinfo - Get user info with token"
            },
            "demo_credentials": {
                "user": {
                    "username": "demo",
                    "password": "demo123"
                },
                "client": {
                    "client_id": "pkce-spa-client",
                    "client_secret": None,
                    "redirect_uri": "http://localhost:3000/callback",
                    "type": "public (PKCE)"
                }
            }
        },
        "endpoints": {
            "authorize": "GET /oauth2/authorize?code_challenge=...",
            "approve": "POST /oauth2/approve",
            "token": "POST /oauth2/token (with code_verifier, NOT client_secret)",
            "userinfo": "GET /oauth2/userinfo",
            "demo": "GET /oauth2/pkce/demo"
        }
    }


@app.get("/health", tags=["health"])
def health_check():
    """Health check endpoint"""
    from app.core.redis_client import check_redis_connection
    redis_ok = check_redis_connection()
    return {
        "status": "healthy" if redis_ok else "degraded",
        "redis": "connected" if redis_ok else "disconnected"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5105)
