# Auth Demo - 3 typy autentizace ve FastAPI

Vyukova ukazka demonstrujici rozdily mezi tremi pristupy k autentizaci.

## Spusteni

```bash
cd be/auth
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

## Dostupne URL

| URL | Popis |
|-----|-------|
| http://localhost:8000/docs | Swagger UI dokumentace |
| http://localhost:8000/redoc | ReDoc dokumentace |
| http://localhost:8000/oauth2/login | Vlastni HTML login stranka |

## Testovaci ucty

| Username | Heslo |
|----------|-------|
| admin | admin123 |
| user | user123 |

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
curl -c cookies.txt -X POST "http://localhost:8000/session/login" \
  -d "username=admin&password=admin123"

# Pouziti cookie
curl -b cookies.txt "http://localhost:8000/session/me"

# Logout
curl -b cookies.txt -X POST "http://localhost:8000/session/logout"
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
TOKEN=$(curl -s -X POST "http://localhost:8000/jwt/login" \
  -d "username=admin&password=admin123" | jq -r '.access_token')

# Pouziti tokenu
curl -H "Authorization: Bearer $TOKEN" "http://localhost:8000/jwt/me"
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
TOKEN=$(curl -s -X POST "http://localhost:8000/oauth2/token" \
  -d "username=admin&password=admin123" | jq -r '.access_token')

# Pouziti tokenu
curl -H "Authorization: Bearer $TOKEN" "http://localhost:8000/oauth2/me"
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

## Struktura projektu

```
auth/
├── main.py           # FastAPI aplikace
├── config.py         # Konfigurace (SECRET_KEY, etc.)
├── fake_users.py     # In-memory uzivatele
├── schemas.py        # Pydantic schemata
├── auth.py           # Autentizacni logika (3 typy)
├── routes.py         # API endpointy
├── requirements.txt  # Zavislosti
├── templates/
│   └── login.html    # OAuth2 login stranka
└── README.md         # Tato dokumentace
```

---

## Bezpecnostni poznamky

Toto je **vyukova ukazka** - v produkci je potreba:

1. **SECRET_KEY** - pouzit silny nahodny klic, ne hardcoded
2. **HTTPS** - vzdy pouzivat sifrovane spojeni
3. **CORS** - omezit `allow_origins` na konkretni domeny
4. **Rate limiting** - ochrana proti brute-force utokum
5. **Refresh tokeny** - pro dlouhodobe sessions
6. **Databaze** - uzivatele ukladat do skutecne DB, ne in-memory
