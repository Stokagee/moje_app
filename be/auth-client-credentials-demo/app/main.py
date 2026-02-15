# Main FastAPI application for Client Credentials Demo

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import init_db
from app.routes import oauth2, api
from shared.logging.logger import setup_logging, get_logger
from shared.logging.middleware import LoggingMiddleware

# Setup logging
setup_logging()
logger = get_logger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Client Credentials Grant Demo (M2M)",
    version="1.0.0",
    description="""# OAuth2 Client Credentials Demo

Implementace OAuth2 **Client Credentials** flow pro Machine-to-Machine (M2M) komunikaci.

## Co je Client Credentials?

OAuth2 flow, kde si aplikace získá token sama pro sebe (**NE** na behalf of uživatele).

## Rozdíl od Password Grant

| Password Grant | Client Credentials |
|----------------|-------------------|
| Username/password uživatele | Client ID/Client Secret aplikace |
| Token pro uživatele | Token pro aplikaci |
| Má uživatelská data | Bez uživatelského kontextu |

## Kdy se používá

- Service A volá Service B (microservices)
- Background job volá API
- Daemon synchronize data
- CI/CD pipeline volá deployment API

## Scopes (Oprávnění)

| Scope | Popis | Endpoint příklad |
|-------|-------|-----------------|
| `read` | Čtení dat | GET /api/v1/secure/data |
| `write` | Zápis dat | POST /api/v1/secure/data |
| `delete` | Mazání dat | DELETE /api/v1/secure/data/{id} |
| `admin` | Admin operace | GET /api/v1/secure/admin |

## Demo Credentials

- **client_id**: `demo-service`
- **client_secret**: `demo-secret123`
- **Scopes**: `read write`
""",
    openapi_tags=[
        {
            "name": "oauth2",
            "description": "OAuth2 endpointy - získání tokenu, introspekce"
        },
        {
            "name": "api",
            "description": "Chráněné API endpointy s scope validací"
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
app.include_router(oauth2.router)
app.include_router(api.router)


@app.on_event("startup")
def startup_event():
    """Initialize database on startup and create demo client"""
    logger.info("Starting Client Credentials Demo API", extra={"event_type": "api_startup"})
    init_db()

    # Create demo client for testing
    from app.core.database import SessionLocal
    from app.core.security import get_client_secret_hash
    from app.models.oauth2_client import OAuth2Client

    db = SessionLocal()
    try:
        # Check if demo client exists
        demo_client = db.query(OAuth2Client).filter(
            OAuth2Client.client_id == "demo-service"
        ).first()

        if not demo_client:
            demo_client = OAuth2Client(
                client_id="demo-service",
                client_secret_hash=get_client_secret_hash("demo-secret123"),
                name="Demo Service",
                description="Demo service account for testing Client Credentials flow",
                scopes="read write"
            )
            db.add(demo_client)
            db.commit()
            logger.info("Demo client created", extra={
                "event_type": "demo_data_initialized",
                "client_id": "demo-service"
            })
    finally:
        db.close()

    logger.info("Database initialized", extra={"event_type": "db_initialized"})


@app.get("/", tags=["root"])
def root():
    """Root endpoint s informacemi o API"""
    return {
        "message": "Client Credentials Demo API (M2M Authentication)",
        "docs": "/docs",
        "endpoints": {
            "oauth2": {
                "token": "/oauth2/token",
                "introspect": "/oauth2/introspect"
            },
            "api": {
                "public": "/api/v1/data",
                "secure_read": "/api/v1/secure/data",
                "whoami": "/api/v1/whoami"
            }
        },
        "demo_client": {
            "client_id": "demo-service",
            "client_secret": "demo-secret123"
        }
    }


@app.get("/health", tags=["health"])
def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5103)
