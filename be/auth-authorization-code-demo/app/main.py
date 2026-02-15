# Main FastAPI application for Authorization Code Demo

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.core.database import init_db
from app.core.security import get_password_hash
from app.routes import oauth2
from app.models.auth_code import User, OAuth2Client
from app.core.database import SessionLocal
from shared.logging.logger import setup_logging, get_logger
from shared.logging.middleware import LoggingMiddleware

# Setup logging
setup_logging()
logger = get_logger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Authorization Code Flow Demo",
    version="1.0.0",
    description="""# OAuth2 Authorization Code Flow Demo

Implementace OAuth2 **Authorization Code** flow - standard používaný Google, GitHub, Facebook.

## Co je Authorization Code Flow?

Třetí-strana autentizace, kde:
- Aplikace nikdy nevidí uživatelské heslo
- Uživatel schválí přístup na consent stránce
- Token se získá přes authorization code (redirect)

## Flow Diagram

```
┌──────────┐      ┌─────────┐      ┌──────────┐
│  User    │      │ Client  │      │ OAuth2   │
│ Browser  │      │  App    │      │ Server   │
└────┬─────┘      └────┬────┘      └────┬─────┘
     │                 │                 │
     │ 1. Klik "Login with X"        │
     │────────────────>│                 │
     │                 │ 2. Redirect → /oauth2/authorize
     │                 │    ?client_id=...
     │                 │    &redirect_uri=...
     │                 │    &response_type=code
     │                 │────────────────>│
     │                 │                 │
     │ 3. Zobraz consent stránka      │
     │<─────────────────────────────────│
     │                 │                 │
     │ 4. User zadá credentials       │
     │    a schválí                     │
     │─────────────────────────────────>│
     │                 │                 │
     │ 5. Redirect zpět s code=abc    │
     │<─────────────────────────────────│
     │                 │                 │
     │ 6. Client vymění code za token  │
     │                 │ 7. POST /oauth2/token
     │                 │    code=abc
     │                 │    grant_type=authorization_code
     │                 │────────────────>│
     │                 │ 8. access_token
     │                 │<────────────────│
```

## Komponenty flowu

1. **Authorize**: Klient pošle request na `/oauth2/authorize`
2. **Consent**: Uživatel vidí consent stránku a schválí
3. **Code**: Server redirectuje zpět s `code` parametrem
4. **Exchange**: Klient vymění code za access token na `/oauth2/token`

## Požadavky

- **Redis**: Musí běžet na localhost:6379
- **Authorization code**: Platnost 10 minut, jednorázové použití
- **State**: CSRF protection (doporučeno)

## Demo Credentials

- **User**: username=`demo`, password=`demo123`
- **Client**: client_id=`demo-client`, client_secret=`demo-client-secret`
- **Redirect URI**: `http://localhost:3000/callback`
""",
    openapi_tags=[
        {
            "name": "oauth2",
            "description": "OAuth2 Authorization Code flow endpointy"
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
    allow_origins=["*"],
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
app.include_router(oauth2.router)


@app.on_event("startup")
def startup_event():
    """Initialize database on startup and create demo data"""
    logger.info("Starting Authorization Code Demo API", extra={"event_type": "api_startup"})
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

        # Create demo client
        demo_client = db.query(OAuth2Client).filter(
            OAuth2Client.client_id == "demo-client"
        ).first()

        if not demo_client:
            demo_client = OAuth2Client(
                client_id="demo-client",
                client_secret="demo-client-secret",
                name="Demo Client Application",
                redirect_uris="\n".join(settings.ALLOWED_REDIRECT_URIS),
                scopes="read write"
            )
            db.add(demo_client)
            db.commit()
            logger.info("Demo client created", extra={
                "event_type": "demo_data_initialized",
                "client_id": "demo-client"
            })

    finally:
        db.close()

    logger.info("Database initialized", extra={"event_type": "db_initialized"})


@app.get("/", tags=["root"])
def root():
    """Root endpoint s informacemi o API"""
    return {
        "message": "Authorization Code Demo API",
        "docs": "/docs",
        "flow_steps": {
            "1": "GET /oauth2/authorize - Show consent page",
            "2": "POST /oauth2/approve - User approves and gets code",
            "3": "POST /oauth2/token - Exchange code for access token",
            "4": "GET /oauth2/userinfo - Get user info with token"
        },
        "demo_credentials": {
            "user": {
                "username": "demo",
                "password": "demo123"
            },
            "client": {
                "client_id": "demo-client",
                "client_secret": "demo-client-secret",
                "redirect_uri": "http://localhost:3000/callback"
            }
        }
    }


@app.get("/health", tags=["health"])
def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5104)
