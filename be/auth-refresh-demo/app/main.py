# Main FastAPI application for Refresh Token Demo

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import init_db
from app.routes import auth
from shared.logging.logger import setup_logging, get_logger
from shared.logging.middleware import LoggingMiddleware

# Setup logging
setup_logging()
logger = get_logger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Refresh Token Flow Demo",
    version="1.0.0",
    description="""# OAuth2 Refresh Token Flow Demo

Implementace **Refresh Token** flow pro udržení uživatelské session.

## Co je Refresh Token Flow?

Řeší problém expirace access tokenů:
- **Access token**: Platnost 30 minut, používá se pro API requesty
- **Refresh token**: Platnost 30 dní, používá se jen pro získání nového access tokenu
- Při expiraci access tokenu lze získat nový bez opětovného přihlášení

## Flow Diagram

```
┌─────────┐                 ┌──────────┐
│  Klient │                 │  Server  │
└────┬────┘                 └─────┬────┘
     │ 1. POST /login              │
     │    (username, password)      │
     │─────────────────────────────>│
     │                              │
     │ 2. access_token (30min)      │
     │    refresh_token (30d)       │
     │<─────────────────────────────│
     │                              │
     │ 3. API request s tokenem     │
     │─────────────────────────────>│
     │ ...po 30 minutách...         │
     │                              │
     │ 4. 401 Unauthorized          │
     │<─────────────────────────────│
     │                              │
     │ 5. POST /refresh             │
     │    (refresh_token)           │
     │─────────────────────────────>│
     │                              │
     │ 6. Nový access_token         │
     │<─────────────────────────────│
```

## Token Rotation

Při každém refresh se zneplatní starý refresh token a vytvoří se nový.
To zabraňuje opakovanému použití stejného tokenu.

## Demo Credentials

- Username: `testuser`
- Password: `testpass123`
""",
    openapi_tags=[
        {
            "name": "authentication",
            "description": "Autentizační endpointy - registrace, login, refresh, logout"
        },
        {
            "name": "users",
            "description": "Správa uživatelských dat"
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

# Include routers
app.include_router(auth.router, prefix=settings.API_V1_STR)


@app.on_event("startup")
def startup_event():
    """Initialize database on startup"""
    logger.info("Starting Refresh Token Demo API", extra={"event_type": "api_startup"})
    init_db()
    logger.info("Database initialized", extra={"event_type": "db_initialized"})


@app.get("/", tags=["root"])
def root():
    """Root endpoint s informacemi o API"""
    return {
        "message": "Refresh Token Demo API",
        "docs": "/docs",
        "endpoints": {
            "register": "/api/v1/auth/register",
            "login": "/api/v1/auth/login",
            "refresh": "/api/v1/auth/refresh",
            "logout": "/api/v1/auth/logout",
            "me": "/api/v1/auth/me"
        },
        "demo_credentials": {
            "username": "testuser",
            "password": "testpass123"
        }
    }


@app.get("/health", tags=["health"])
def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5102)
