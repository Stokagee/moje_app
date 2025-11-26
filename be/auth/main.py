"""
Auth Demo - Výuková ukázka 3 typů autentizace ve FastAPI.

Spuštění:
    cd be/auth
    pip install -r requirements.txt
    uvicorn main:app --reload --port 8001

Dostupné URL:
    - Swagger UI: http://localhost:8001/docs
    - ReDoc: http://localhost:8001/redoc
    - OAuth2 login: http://localhost:8001/oauth2/login

Výchozí admin účet (nastavitelný v .env):
    - admin / admin123
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from routes import router
from database import engine, SessionLocal
from models import Base
from crud import create_user, user_exists
from config import (
    DEFAULT_ADMIN_USERNAME,
    DEFAULT_ADMIN_PASSWORD,
    DEFAULT_ADMIN_EMAIL,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Startup/shutdown events pro FastAPI aplikaci.

    Při startu:
    1. Vytvoří databázové tabulky (pokud neexistují)
    2. Vytvoří výchozího admin uživatele (pokud neexistuje)
    """
    # Startup
    print("[START] Inicializace Auth Demo...")

    # Vytvoření tabulek
    Base.metadata.create_all(bind=engine)
    print("[OK] Databazove tabulky vytvoreny/overeny")

    # Vytvoření výchozího admin účtu
    db = SessionLocal()
    try:
        if not user_exists(db, DEFAULT_ADMIN_USERNAME):
            create_user(
                db,
                username=DEFAULT_ADMIN_USERNAME,
                password=DEFAULT_ADMIN_PASSWORD,
                email=DEFAULT_ADMIN_EMAIL,
            )
            print(f"[OK] Vytvoren vychozi admin ucet: {DEFAULT_ADMIN_USERNAME}")
        else:
            print(f"[INFO] Admin ucet '{DEFAULT_ADMIN_USERNAME}' jiz existuje")
    finally:
        db.close()

    print("[READY] Auth Demo pripraveno na http://localhost:8001/docs")

    yield

    # Shutdown
    print("[STOP] Auth Demo ukonceno")


# FastAPI instance
app = FastAPI(
    title="Auth Demo",
    description="""
<img src="/static/robot_framework.jpg" alt="Robot Framework Banner" style="width:100%; max-height:200px; object-fit:cover; border-radius:8px; margin-bottom:20px;">

## Vyukova ukazka 3 typu autentizace

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

### OAuth2 Login stranka

<a href="/oauth2/login" data-testid="oauth2-login-link" target="_blank"><strong>>>> Otevrit OAuth2 Login <<<</strong></a>

Po prihlaseni ziskate JWT token, ktery muzete pouzit v "Authorize" tlacitku vyse.

---

**Vychozi admin ucet:** `admin` / `admin123` (nastavitelny v .env)

**Registrace novych uzivatelu:** POST `/register`
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Pro výuku - v produkci omezit!
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files (pro banner obrazek)
app.mount("/static", StaticFiles(directory="static"), name="static")

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
        "default_admin": {
            "username": DEFAULT_ADMIN_USERNAME,
            "note": "Heslo a další nastavení v .env souboru",
        },
        "endpoints": {
            "register": "POST /register - registrace nového uživatele",
            "session_login": "POST /session/login - přihlášení pomocí cookie",
            "jwt_login": "POST /jwt/login - přihlášení pomocí JWT tokenu",
            "oauth2_login": "GET /oauth2/login - HTML login stránka",
        },
    }


@app.get("/health", tags=["Info"])
def health():
    """Health check endpoint."""
    return {"status": "ok"}
