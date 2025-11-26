# Auth Demo - 3 typy autentizace ve FastAPI

Vyukova ukazka demonstrujici rozdily mezi tremi pristupy k autentizaci.

## Spusteni

```bash
cd be/auth
pip install -r requirements.txt
uvicorn main:app --reload --port 8001
```

## Dostupne URL

| URL | Popis |
|-----|-------|
| http://localhost:8001/docs | Swagger UI dokumentace |
| http://localhost:8001/redoc | ReDoc dokumentace |
| http://localhost:8001/oauth2/login | Vlastni HTML login stranka |

## Vychozi admin ucet

Ucet se vytvori automaticky pri startu aplikace. Nastaveni v `.env`:

```env
DEFAULT_ADMIN_USERNAME=admin
DEFAULT_ADMIN_PASSWORD=admin123
DEFAULT_ADMIN_EMAIL=admin@example.com
```

## Registrace novych uzivatelu

```bash
curl -X POST "http://localhost:8001/register" \
  -H "Content-Type: application/json" \
  -d '{"username":"novyuser","password":"heslo123","email":"user@example.com"}'
```

---

## 3 typy autentizace

### 1. Session-based (`/session/*`)

**Jak to funguje:**
1. Uzivatel posle username + password na `/session/login`
2. Server overi credentials a vytvori podepsanou session cookie
3. Cookie se automaticky posila s kazdym dalsim requestem
4. Server overi podpis a vrati uzivatelska data

**Endpointy:**
- `POST /session/login` - Prihlaseni (nastavi cookie)
- `POST /session/logout` - Odhlaseni (smaze cookie)
- `GET /session/me` - Info o prihlasenem uzivateli

**Priklad (curl):**
```bash
# Login - ulozi cookie do souboru
curl -c cookies.txt -X POST "http://localhost:8001/session/login" \
  -d "username=admin&password=admin123"

# Pouziti cookie
curl -b cookies.txt "http://localhost:8001/session/me"

# Logout
curl -b cookies.txt -X POST "http://localhost:8001/session/logout"
```

**Vyhody:**
- Jednoduchy koncept
- Prohlizec automaticky spravuje cookies
- Server muze invalidovat session

**Nevyhody:**
- Stavova (stateful) autentizace
- Problematicke pro horizontalni skalovani
- CSRF utoky

---

### 2. JWT Token (`/jwt/*`)

**Jak to funguje:**
1. Uzivatel posle username + password na `/jwt/login`
2. Server overi credentials a vrati JWT token
3. Klient uklada token a posila ho v hlavicce: `Authorization: Bearer <token>`
4. Server overi podpis tokenu a extrahuje user info

**Endpointy:**
- `POST /jwt/login` - Prihlaseni (vrati token)
- `GET /jwt/me` - Info o prihlasenem uzivateli

**Priklad (curl):**
```bash
# Login - ziskej token
TOKEN=$(curl -s -X POST "http://localhost:8001/jwt/login" \
  -d "username=admin&password=admin123" | jq -r '.access_token')

# Pouziti tokenu
curl -H "Authorization: Bearer $TOKEN" "http://localhost:8001/jwt/me"
```

**Vyhody:**
- Bezstavova (stateless) autentizace
- Snadne horizontalni skalovani
- Token obsahuje metadata
- Zadne CSRF problemy

**Nevyhody:**
- Token nelze invalidovat pred expiraci
- Vetsi velikost nez session cookie
- Klient musi spravovat token

---

### 3. OAuth2 s HTML (`/oauth2/*`)

**Jak to funguje:**
1. Uzivatel navstivi `/oauth2/login` - zobrazi se HTML formular
2. Uzivatel vyplni credentials a odesle formular
3. Server overi credentials a vrati JWT token
4. Klient muze pouzit token pro dalsi requesty

**Endpointy:**
- `GET /oauth2/login` - HTML login stranka
- `POST /oauth2/token` - Zpracovani loginu (vrati token)
- `GET /oauth2/me` - Info o prihlasenem uzivateli

**Priklad (curl):**
```bash
# Ziskej token
TOKEN=$(curl -s -X POST "http://localhost:8001/oauth2/token" \
  -d "username=admin&password=admin123" | jq -r '.access_token')

# Pouziti tokenu
curl -H "Authorization: Bearer $TOKEN" "http://localhost:8001/oauth2/me"
```

**Vyhody:**
- Plna kontrola nad UI
- Vlastni branding/design
- Kombinuje vyhody JWT

**Nevyhody:**
- Vice prace na implementaci
- Nutnost spravovat HTML sablony

---

## Srovnavaci tabulka

| Vlastnost | Session | JWT | OAuth2 HTML |
|-----------|---------|-----|-------------|
| Stav | Stateful | Stateless | Stateless |
| Ulozeni | Cookie (server) | Token (klient) | Token (klient) |
| Invalidace | Okamzita | Az po expiraci | Az po expiraci |
| Skalovani | Slozitejsi | Snadne | Snadne |
| CSRF ochrana | Potreba | Neni treba | Neni treba |
| Pouziti | Web apps | API, SPA, Mobile | API + vlastni UI |

---

## Konfigurace (.env)

Vsechna nastaveni jsou centralizovana v `.env` souboru:

```env
# Databaze (PostgreSQL z docker-compose)
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/moje_app

# JWT/Session
SECRET_KEY=super-secret-key-change-in-production-123!
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
SESSION_COOKIE_NAME=session_id
SESSION_MAX_AGE=3600

# OAuth2 (pro budouci rozsireni)
OAUTH2_CLIENT_ID=my-app-client
OAUTH2_CLIENT_SECRET=my-app-secret

# Vychozi admin ucet
DEFAULT_ADMIN_USERNAME=admin
DEFAULT_ADMIN_PASSWORD=admin123
DEFAULT_ADMIN_EMAIL=admin@example.com
```

---

## Struktura projektu

```
auth/
├── main.py           # FastAPI aplikace + DB init
├── config.py         # Konfigurace z .env
├── database.py       # SQLAlchemy pripojeni
├── models.py         # User model
├── crud.py           # Databazove operace
├── schemas.py        # Pydantic schemata
├── auth.py           # Autentizacni logika (3 typy)
├── routes.py         # API endpointy
├── requirements.txt  # Zavislosti
├── .env              # Lokalni konfigurace
├── .env.example      # Sablona konfigurace
├── templates/
│   └── login.html    # OAuth2 login stranka
└── README.md         # Tato dokumentace
```

---

## Databazova tabulka

Uzivatele jsou ulozeni v PostgreSQL tabulce `auth_users`:

| Sloupec | Typ | Popis |
|---------|-----|-------|
| id | INTEGER | Primarni klic |
| username | VARCHAR(50) | Unikatni uzivatelske jmeno |
| email | VARCHAR(100) | Unikatni email |
| hashed_password | VARCHAR(255) | Bcrypt hash hesla |
| is_active | BOOLEAN | Aktivni ucet |
| created_at | DATETIME | Datum vytvoreni |

---

## Pozadavky

- Python 3.10+
- PostgreSQL (bezi v docker-compose)
- Zavislosti v `requirements.txt`

---

## Bezpecnostni poznamky

Toto je **vyukova ukazka** - v produkci je potreba:

1. **SECRET_KEY** - pouzit silny nahodny klic
2. **HTTPS** - vzdy pouzivat sifrovane spojeni
3. **CORS** - omezit `allow_origins` na konkretni domeny
4. **Rate limiting** - ochrana proti brute-force utokum
5. **Refresh tokeny** - pro dlouhodobe sessions
