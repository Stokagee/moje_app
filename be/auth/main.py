"""
Auth Demo - Výuková ukázka 3 typů autentizace ve FastAPI.

Spuštění:
    cd be/auth
    pip install -r requirements.txt
    uvicorn main:app --reload --port 8000

Dostupné URL:
    - Swagger UI: http://localhost:8000/docs
    - ReDoc: http://localhost:8000/redoc
    - OAuth2 login: http://localhost:8000/oauth2/login

Testovací účty:
    - admin / admin123
    - user / user123
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes import router

# FastAPI instance
app = FastAPI(
    title="Auth Demo",
    description="""
## Výuková ukázka 3 typů autentizace

Tato aplikace demonstruje rozdíly mezi třemi přístupy k autentizaci:

### 1. Session-based (`/session/*`)
- Klasický přístup s cookie
- Server uchovává stav (stateful)
- Vhodné pro tradiční webové aplikace

### 2. JWT Token (`/jwt/*`)
- Moderní stateless přístup
- Token v Authorization hlavičce
- Vhodné pro API a SPA aplikace

### 3. OAuth2 s HTML (`/oauth2/*`)
- Vlastní login stránka
- Kombinuje JWT s custom UI
- Vhodné pro vlastní branding

---

**Testovací účty:**
- `admin` / `admin123`
- `user` / `user123`

**Vlastní login stránka:** [/oauth2/login](/oauth2/login)
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Pro výuku - v produkci omezit!
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrace routeru
app.include_router(router)


@app.get("/", tags=["Info"])
def root():
    """
    Základní info o aplikaci.
    """
    return {
        "app": "Auth Demo",
        "version": "1.0.0",
        "docs": "/docs",
        "oauth2_login": "/oauth2/login",
        "test_accounts": [
            {"username": "admin", "password": "admin123"},
            {"username": "user", "password": "user123"},
        ],
    }


@app.get("/health", tags=["Info"])
def health():
    """Health check endpoint."""
    return {"status": "ok"}
