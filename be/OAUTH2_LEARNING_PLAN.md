# OAuth2 Advanced Concepts Learning Plan

**Repository:** `/be/`

Tento learning plan obsahuje kompletní implementace pokročilých OAuth2 konceptů s pytest testy a vylepšenou Swagger dokumentací.

---

## 📚 Přehled Demo Projektů

### 1. Refresh Token Demo (`auth-refresh-demo/`)
**Co umí:** Udržení uživatele přihlášeného bez nutnosti opakovaného loginu

**Klíčové koncepty:**
- Access token (krátkodobý, 5-30 min)
- Refresh token (dlouhodobý, 30 dní)
- Token rotation (starý se zneplatní)
- Refresh token lze revokovat (např. logout)

**Endpointy:**
- `POST /api/v1/auth/register` - Registrace uživatele
- `POST /api/v1/auth/login` - Login (vrací access + refresh token)
- `POST /api/v1/auth/refresh` - Obnovení access tokenu
- `POST /api/v1/auth/logout` - Revokace refresh tokenů
- `GET /api/v1/auth/me` - Získání uživatelských dat

**Port:** `10001`

**Pytest Testy:** `be/auth-refresh-demo/tests/test_*.py`
**RF Test:** `RF/auth-refresh-tests/refresh_token_flow.robot` (odkaz)

---

### 2. Client Credentials Demo (`auth-client-credentials-demo/`)
**Co umí:** Machine-to-Machine (M2M) autentizace bez uživatelského kontextu

**Klíčové koncepty:**
- Service account autentizace
- Client ID + Client Secret
- Scope-based access control
- Token bez user subjektu

**Endpointy:**
- `POST /oauth2/token` - Získání M2M tokenu
- `POST /oauth2/introspect` - Informace o tokenu
- `GET /api/v1/secure/data` - Chráněný endpoint (read scope)
- `POST /api/v1/secure/data` - Write endpoint (write scope)
- `GET /api/v1/whoami` - Info o klientovi

**Port:** `10002`

**Pytest Testy:** `be/auth-client-credentials-demo/tests/test_*.py`
**RF Test:** `RF/auth-client-credentials-tests/client_credentials_flow.robot` (odkaz)

**Demo Credentials:**
- `client_id=demo-service`
- `client_secret=demo-secret123`

---

### 3. Authorization Code Demo (`auth-authorization-code-demo/`)
**Co umí:** Standardní OAuth2 flow jako Google, GitHub, Facebook

**Klíčové koncepty:**
- Consent stránka (uživatel schvaluje přístup)
- Authorization code (jednorázový, 10 min platnost)
- Code exchange za access token
- State parametr (CSRF ochrana)
- Redis pro uložení authorization codes

**Endpointy:**
- `GET /oauth2/authorize` - Inicializace flow (consent stránka)
- `POST /oauth2/approve` - Schválení a získání code
- `POST /oauth2/token` - Výměna code za access token
- `GET /oauth2/userinfo` - User info s tokenem

**Port:** `10003`

**Pytest Testy:** `be/auth-authorization-code-demo/tests/test_*.py`
**RF Test:** `RF/auth-authorization-code-tests/authorization_code_flow.robot` (odkaz)

**Demo Credentials:**
- User: `username=demo`, `password=demo123`
- Client: `client_id=demo-client`, `client_secret=demo-client-secret`
- Redirect URI: `http://localhost:3000/callback`

---

### 4. PKCE Extension (`auth-pkce-demo/`)
**Co umí:** Rozšíření Authorization Code flow pro SPA a mobile apps

**Klíčové koncepty:**
- Code verifier + Code challenge
- SHA256 hashování
- Bez client_secret (nelze bezpečně uložit v SPA/mobile)
- S256 metoda (výchozí)

**Soubory:**
- `pkce_utils.py` - Utility pro generování PKCE pair
- `pkce_extension.py` - Rozšíření Authorization Code endpointů

---

## 🚀 Rychlý Start

### Refresh Token Demo

```bash
cd be/auth-refresh-demo
pip install -r requirements.txt
python -m app.main

# Pytest testy:
pytest tests/ -v

# RF test (odkaz):
cd RF/auth-refresh-tests
robot refresh_token_flow.robot
```

### Client Credentials Demo

```bash
cd be/auth-client-credentials-demo
pip install -r requirements.txt
python -m app.main

# Pytest testy:
pytest tests/ -v

# RF test (odkaz):
cd RF/auth-client-credentials-tests
robot client_credentials_flow.robot
```

### Authorization Code Demo

**Vyžaduje Redis!**

```bash
# Spustit Redis
docker run -d -p 6379:6379 redis

cd be/auth-authorization-code-demo
pip install -r requirements.txt
python -m app.main

# Pytest testy:
pytest tests/ -v

# RF test (odkaz):
cd RF/auth-authorization-code-tests
robot authorization_code_flow.robot
```

---

## 📊 Porovnání OAuth2 Flows

| Flow | Kdy použít | Client Secret | User Context | Scénář |
|------|-----------|---------------|--------------|--------|
| **Password Grant** | Interní aplikace | Ano | Ano | First-party mobile/desktop |
| **Refresh Token** | Produkční apps | Ano | Ano | Udržení session |
| **Client Credentials** | M2M | Ano | Ne | Microservices |
| **Authorization Code** | Third-party login | Ano | Ano | "Login with Google" |
| **PKCE** | SPA/Mobile | Ne | Ano | Moderní web/mobile |

---

## 🎓 Co se naučíte

Po absolvování tohoto learning planu budete umět:

1. **Refresh Token Flow**
   - Implementovat token rotation
   - Revokovat refresh tokeny
   - Správně nastavit expirace

2. **Client Credentials Grant**
   - Vytvořit service account
   - Implementovat scope-based access control
   - Otestovat M2M komunikaci

3. **Authorization Code Flow**
   - Implementovat consent stránku
   - Pracovat s authorization codes
   - Validovat redirect URIs
   - Používat Redis pro dočasná data

4. **PKCE Extension**
   - Generovat code_verifier/challenge
   - Rozšířit Authorization Code flow
   - Otestovat na SPA nebo mobile

---

## 🧪 Testování

Všechny dema jsou otestována pomocí Robot Framework.

### Spuštění všech testů

```bash
# Refresh Token
cd RF/auth-refresh-tests
robot refresh_token_flow.robot

# Client Credentials
cd RF/auth-client-credentials-tests
robot client_credentials_flow.robot

# Authorization Code
cd RF/auth-authorization-code-tests
robot authorization_code_flow.robot
```

### Test Coverage

**Refresh Token Tests:**
- Kompletní flow (login → refresh → logout)
- Neplatný refresh token
- Epirrovaný refresh token
- Neautorizovaný request
- Neplatný access token

**Client Credentials Tests:**
- Kompletní M2M flow
- Neplatné credentials
- Neplatný grant type
- Scope validace
- Token introspekce
- Chráněný endpoint bez tokenu

**Authorization Code Tests:**
- Kompletní flow (authorize → approve → token)
- Neplatný client_id
- Neplatná redirect URI
- Špatné heslo na consent stránce
- Neplatný code
- Špatný client secret

---

## 🌐 Swagger UI Interaktivní Dokumentace

Každá demo aplikace má automaticky generovanou Swagger UI dokumentaci na:

| Demo | Swagger UI URL |
|------|---------------|
| Refresh Token | http://localhost:10001/docs |
| Client Credentials | http://localhost:10002/docs |
| Authorization Code | http://localhost:10003/docs |

### Jak používat Swagger UI

1. Otevřete URL v prohlížeči
2. Klikněte na endpoint pro detailní dokumentaci
3. Klikněte "Try it out"
4. Vyplňte parametry (credentials jsou uvedeny v dokumentaci)
5. Klikněte "Execute"
6. Prohlédněte Response

### Výhody Swagger UI

- **Interaktivní testování API** přímo v prohlížeči
- **Kompletní dokumentace** všech request/response formátů
- **Příklady** pro každý endpoint
- **Zobrazení chybových scénářů** s příklady

### Demo Credentials ve Swagger

Všechny dema mají přístupné demo credentials přímo ve Swagger dokumentaci:

**Refresh Token Demo:**
- Username: `testuser`
- Password: `testpass123`

**Client Credentials Demo:**
- Client ID: `demo-service`
- Client Secret: `demo-secret123`

**Authorization Code Demo:**
- User: `username=demo`, `password=demo123`
- Client: `client_id=demo-client`, `client_secret=demo-client-secret`

---

## 📁 Struktura Projektu

```
be/
├── auth-refresh-demo/              # Refresh Token Demo
│   ├── app/
│   │   ├── core/                   # Config, security, database
│   │   ├── models/                 # SQLAlchemy models
│   │   ├── routes/                 # API endpoints
│   │   ├── schemas/                # Pydantic schemas
│   │   └── main.py                 # FastAPI app
│   ├── tests/                      # Pytest testy
│   │   ├── conftest.py             # Fixtures
│   │   ├── test_auth_flow.py       # Flow testy
│   │   └── test_validation.py      # Validační testy
│   └── requirements.txt
│
├── auth-client-credentials-demo/   # Client Credentials Demo
│   ├── app/
│   │   └── ... (stejná struktura)
│   ├── tests/                      # Pytest testy
│   │   ├── conftest.py
│   │   └── test_m2m_flow.py
│   └── requirements.txt
│
├── auth-authorization-code-demo/   # Authorization Code Demo
│   ├── app/
│   │   └── ...
│   ├── templates/                  # HTML consent stránka
│   ├── tests/                      # Pytest testy
│   │   ├── conftest.py
│   │   └── test_auth_code_flow.py
│   └── requirements.txt
│
└── auth-pkce-demo/                 # PKCE Extension
    ├── pkce_utils.py               # PKCE utilities
    └── pkce_extension.py           # Extension endpoints

RF/
├── auth-refresh-tests/
│   └── refresh_token_flow.robot
├── auth-client-credentials-tests/
│   └── client_credentials_flow.robot
└── auth-authorization-code-tests/
    └── authorization_code_flow.robot
```

---

## 🔧 Konfigurace

### Porty

| Demo | Port |
|------|------|
| Refresh Token | 10001 |
| Client Credentials | 10002 |
| Authorization Code | 10003 |

### Databáze

Všechny dema používají SQLite (pro jednoduchost):
- `auth_refresh.db`
- `auth_client_credentials.db`
- `auth_auth_code.db`

### Redis (Authorization Code Demo)

```bash
# Lokální Redis
docker run -d -p 6379:6379 redis

# nebo
brew install redis  # macOS
sudo apt install redis-server  # Ubuntu
```

---

## 📖 Zdroje pro další studium

- [OAuth 2.0 Specification (RFC 6749)](https://datatracker.ietf.org/doc/html/rfc6749)
- [OAuth 2.0 for Browser-Based Apps (RFC draft)](https://datatracker.ietf.org/doc/html/draft-ietf-oauth-browser-based-apps
- [OAuth 2.0 Security Best Current Practice](https://datatracker.ietf.org/doc/html/draft-ietf-oauth-security-topics
- [FastAPI Security documentation](https://fastapi.tiangolo.com/tutorial/security/)
- [Postman OAuth 2.0 documentation](https://learning.postman.com/docs/sending-requests/authorization/)

---

## 🎯 Cvičení

### Refresh Token
1. Implementujte refresh token storage v PostgreSQL
2. Přidejte rotaci refresh tokenů
3. Otestujte RF testem

### Client Credentials
1. Implementujte OAuth2Client model
2. Přidejte /token endpoint s grant_type validací
3. Vytvořte testovací service account
4. Otestujte M2M scénář

### Authorization Code
1. Implementujte authorize endpoint s consent stránkou
2. Přidejte Redis pro uložení authorization codes
3. Implementujte code exchange
4. Otestujte kompletní flow

### PKCE
1. Přidejte PKCE do Authorization Code demo
2. Implementujte code_verifier/challenge
3. Otestujte na SPA nebo mobile

---

## ⚠️ Bezpečnostní Poznámky

### Refresh Token
- Ukládejte refresh tokeny bezpečně (HttpOnly cookies)
- Implementujte rotaci (starý zneplatnit)
- Revokujte při logoutu

### Client Credentials
- Client secret musí být hashovaný (bcrypt)
- Ověřujte scopes na každém requestu
- Používejte krátkou expiraci (1 hodina)

### Authorization Code
- Validujte redirect URI (povolené seznam)
- Používejte state parametr (CSRF ochrana)
- Authorization code musí být jednorázový

### PKCE
- Vždy používejte S256 metodu
- Code verifier musí být náhodný (secrets.token_urlsafe)
- Délka verifieru: 43-128 znaků

---

## 📝 Poznámky

- Všechny dema používají SQLite pro jednoduchost
- V produkci použijte PostgreSQL
- Secret keys by měly být v environment variables
- Redis je vyžadován pro Authorization Code Demo
- RF testy lze spustit nezávisle na každém demu
- Pytest testy jsou primární testovací nástroj
- Swagger UI (/docs) poskytuje interaktivní dokumentaci každého demo

---

**Autor:** Claude Code
**Datum:** 2026-01-19
**Verze:** 1.0.0
