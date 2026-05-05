# Security Learning Lab - OAuth2 + RBAC + CSRF + mTLS

> **Cíl:** Naučit se prakticky používat security vrstvy na Orders API
> 
> **Co potřebuješ:**
> - Bruno API klient (https://www.usebruno.com)
> - Přístup k běžícímu backendu (`http://localhost:20300`)
> - Terminal pro generování tokenů

---

## 📚 Teoretický úvod (čti pozorně!)

### Co postupně naučíš:
1. **OAuth2 PKCE** - Jak se autentizovat bez hesla (pouze token)
2. **RBAC** - Jak role ovlivňují co můžeš dělat
3. **CSRF** - Proč potřebuješ dva tokeny místo jednoho
4. **mTLS** - Jak certifikáty nahrazují hesla

### Architektura:
```
┌─────────────┐                    ┌─────────────┐
│    Bruno    │───1. Login────────▶│  Auth Demo  │
│  (klient)   │◀──2. Token─────────│   :5105     │
│             │                    └─────────────┘
│             │                    
│             │───3. API Call─────▶┌─────────────┐
│             │   + Bearer Token   │   Backend   │
│             │   + CSRF Token     │   :20300    │
│             │◀──4. Response──────│             │
└─────────────┘                    └─────────────┘
```

---

## 🎯 ÚKOL 1: Pochopit JWT Token

### Co je JWT token?
JWT (JSON Web Token) je jako "občanka" v digitální podobě:
- Kdo jsi (sub = subject)
- Jaká máš práva (scopes)
- Kdy vyprší (exp)

### Struktura tokenu:
```
xxxxx.yyyyy.zzzzz
│     │     └── Signature (podepsáno SECRET_KEY)
│     └── Payload (data o tobě)
└── Header (typ tokenu)
```

### 📝 Tvůj první úkol:
1. Otevři terminál
2. Spusť tento Python kód:

```python
# Dekódování JWT tokenu (bez validace)
import base64
import json

token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJjb3VyaWVyMSIsInJvbGUiOiJjb3VyaWVyIiwic2NvcGVzIjoib3JkZXJzOnJlYWQgb3JkZXJzOndyaXRlIiwiZXhwIjoxNzAwMDAwMDAwfQ.SIGNATURE"

# Rozdělit na části
parts = token.split('.')
payload = parts[1]

# Doplnit padding a dekódovat
payload += '=' * (4 - len(payload) % 4)
decoded = base64.urlsafe_b64decode(payload)
print(json.dumps(json.loads(decoded), indent=2))
```

**❓ Otázka pro tebe:** Co vidíš v payloadu? Jaká je role?

---

## 🎯 ÚKOL 2: Získat token z Auth Serveru

### Teorie: OAuth2 Authorization Code + PKCE Flow

```
1. Klient vygeneruje:
   - code_verifier (náhodný řetězec 43-128 znaků)
   - code_challenge = SHA256(code_verifier)

2. Klient přesměruje na:
   /oauth2/authorize?code_challenge=xxx&client_id=yyy

3. Uživatel se přihlásí a schválí

4. Server vrátí: authorization_code

5. Klient vymění code za token:
   POST /oauth2/token
   {
     "code": "xxx",
     "code_verifier": "původní verifier",
     "client_id": "yyy"
   }

6. Server ověří: SHA256(verifier) == challenge

7. Server vrátí: access_token
```

### 📝 Tvůj úkol v Brunu:

```http
### Krok 1: Zjistit PKCE parametry (demo endpoint)
GET http://localhost:5105/oauth2/pkce/demo
```

**❓ Co dostaneš?** Výpis `code_verifier` a `code_challenge`.

```http
### Krok 2: Otevřít authorize v prohlížeči
# Zkopíruj URL z předchozího response a otevři v prohlížeči
# NEBO použij tento template:
GET http://localhost:5105/oauth2/authorize
    ?client_id=pkce-spa-client
    &redirect_uri=http://localhost:3000/callback
    &response_type=code
    &code_challenge={{code_challenge_z_kroku_1}}
    &code_challenge_method=S256
    &scope=orders:read orders:write
```

**📝 Poznámka:** V prohlížeči:
1. Přihlas se (username/password z PKCE demo)
2. Schval consent
3. Zkopíruj `code` z redirect URL

```http
### Krok 3: Vyměnit code za token
POST http://localhost:5105/oauth2/token
Content-Type: application/x-www-form-urlencoded

grant_type=authorization_code
&code={{code_z_prohlížeče}}
&client_id=pkce-spa-client
&code_verifier={{code_verifier_z_kroku_1}}
&redirect_uri=http://localhost:3000/callback
```

**✅ Úspěch:** Dostaneš `access_token`!

**❓ Otázka:** Jak dlouho token platí? Najdi `expires_in`.

---

## 🎯 ÚKOL 3: Použít token na chráněný endpoint

### Teorie: Bearer Authentication

Bearer = "ten, kdo nese token"
- Token se posílá v hlavičce: `Authorization: Bearer <token>`
- Server ověří podpis a expiraci
- Pokud je OK, request projde

### 📝 Tvůj úkol:

```http
### Volání BEZ tokenu - mělo by selhat
GET http://localhost:20300/api/v1/orders/

# Očekávaný výsledek: 401 Unauthorized
# Detail: "Not authenticated"
```

**❓ Proč to selhalo?** Chybí `Authorization` hlavička.

```http
### Volání S tokenem
GET http://localhost:20300/api/v1/orders/
Authorization: Bearer {{access_token_z_úkolu_2}}

# Očekávaný výsledek: 200 OK + seznam objednávek
```

**✅ Úspěch:** Vidíš objednávky!

**❓ Otázka:** Kolik objednávek vidíš? Jaká je struktura response?

---

## 🎯 ÚKOL 4: Vyzkoušet si RBAC (Role-Based Access Control)

### Teorie: Role a oprávnění

| Role | Co může dělat |
|------|---------------|
| `customer` | Číst vlastní objednávky |
| `courier` | Vyzvednout/doručit přiřazené objednávky |
| `admin` | Všechno, včetně delete |

### 📝 Tvůj úkol:

Nejprve potřebuješ tokeny s různými rolemi. Zde jsou testovací tokeny
(předpokládáme, že máš přístup k auth serveru):

```http
### Vytvořit token s CUSTOMER rolí
# V auth-pkce-demo se přihlas jako customer uživatel
# Nebo vygeneruj token manuálně (viz níže)

POST http://localhost:5105/oauth2/token
Content-Type: application/x-www-form-urlencoded

grant_type=authorization_code
&code={{customer_code}}
&client_id=pkce-spa-client
&code_verifier={{code_verifier}}
&redirect_uri=http://localhost:3000/callback
```

```http
### Zkusit pickup jako CUSTOMER - mělo by selhat
POST http://localhost:20300/api/v1/orders/1/pickup
Authorization: Bearer {{customer_token}}

# Očekávaný výsledek: 403 Forbidden
# Detail: "Courier role required for this operation"
```

**❓ Proč 403 a ne 401?**
- 401 = nejsi přihlášen (chybí token)
- 403 = jsi přihlášen, ale nemáš oprávnění

```http
### Zkusit delete jako COURIER - mělo by selhat
DELETE http://localhost:20300/api/v1/orders/1
Authorization: Bearer {{courier_token}}

# Očekávaný výsledek: 403 Forbidden
# Detail: "Admin role required for this operation"
```

**✅ Pochopil jsi:** Role určuje co můžeš dělat!

---

## 🎯 ÚKOL 5: CSRF Protection

### Teorie: Proč potřebujeme CSRF?

**Problém:**
1. Jsi přihlášený na `mybank.com`
2. Otevřeš `evil.com` v jiné záložce
3. `evil.com` pošle POST na `mybank.com/transfer`
4. Browser automaticky pošle tvoje cookies
5. Banka vykoná převod!

**Řešení:**
1. Server vygeneruje CSRF token
2. Token je v cookie (HTTP-only) + v response
3. Klient musí poslat token v hlavičce `X-CSRF-Token`
4. Server ověří, že cookie == header
5. `evil.com` nemůže přečíst cookie (SameSite)

### 📝 Tvůj úkol:

```http
### Krok 1: Získat CSRF token
GET http://localhost:20300/api/v1/auth/csrf-token
Authorization: Bearer {{access_token}}

# Response obsahuje:
# {
#   "csrf_token": "abc123...",
#   "message": "Include this token in X-CSRF-Token header..."
# }
```

**📝 Ulož si token:** `{{csrf_token}}`

```http
### Krok 2: Vytvořit objednávku BEZ CSRF (v produkci by selhalo)
# POZOR: V development módu (FORCE_HTTPS=false) to projde!

POST http://localhost:20300/api/v1/orders/
Authorization: Bearer {{access_token}}
Content-Type: application/json

{
  "customer_name": "Test Customer",
  "customer_phone": "+420606123456",
  "pickup_address": "Test 1",
  "pickup_lat": 50.0,
  "pickup_lng": 14.0,
  "delivery_address": "Test 2",
  "delivery_lat": 50.1,
  "delivery_lng": 14.1
}

# V development: 201 Created
# V produkci (bez X-CSRF-Token): 403 Forbidden
```

```http
### Krok 3: Vytvořit objednávku S CSRF (správně)
POST http://localhost:20300/api/v1/orders/
Authorization: Bearer {{access_token}}
Content-Type: application/json
X-CSRF-Token: {{csrf_token}}

{
  "customer_name": "Test Customer",
  "customer_phone": "+420606123456",
  "pickup_address": "Test 1",
  "pickup_lat": 50.0,
  "pickup_lng": 14.0,
  "delivery_address": "Test 2",
  "delivery_lat": 50.1,
  "delivery_lng": 14.1
}

# Vždy: 201 Created
```

**✅ Pochopil jsi:** CSRF chrání před útoky z jiných webů!

---

## 🎯 ÚKOL 6: mTLS (Mutual TLS)

### Teorie: Proč mTLS?

**Běžné HTTPS:**
- Server předloží certifikát
- Klient ověří, že server je důvěryhodný

**mTLS:**
- Server předloží certifikát
- **Klient také předloží certifikát**
- Server ověří, že klient je důvěryhodný

**Výhody:**
- Není potřeba heslo
- Certifikát nelze ukrást (bez private key)
- Hardware tokeny (YubiKey)

### 📝 Příprava certifikátů:

```bash
# V terminálu spusť:
cd certs

# Linux/Mac:
./generate-certs.sh

# Windows PowerShell:
.\generate-certs.ps1
```

Toto vytvoří:
- `ca.crt` - Certificate Authority (důvěryhodná)
- `server.crt` - Server certifikát
- `client.crt` - Tvůj klientský certifikát
- `client.key` - Tvůj private key (NEUKAZOVAT!)

### 📝 Spustit produkční prostředí:

```bash
# Spustit s nginx (mTLS)
docker compose --profile production up -d

# Nginx běží na:
# - :443 (HTTPS + mTLS)
# - :80 (redirect na HTTPS)
```

### 📝 Tvůj úkol v Bruno:

```http
### Krok 1: Bez certifikátu - selže
GET https://localhost/api/v1/orders/
Authorization: Bearer {{access_token}}

# Očekávaný výsledek: SSL Error
# "SSL handshake failed"
```

**❓ Proč?** Nginx vyžaduje klientský certifikát.

### V Bruno nastavit klientský certifikát:

1. Otevři Collection Settings
2. Jdi do "Client Certificates"
3. Přidej:
   - **Host:** localhost
   - **CRT file:** `certs/client.crt`
   - **KEY file:** `certs/client.key`
   - **Passphrase:** (prázdné)

```http
### Krok 2: S certifikátem - projde
GET https://localhost/api/v1/orders/
Authorization: Bearer {{access_token}}

# Očekávaný výsledek: 200 OK
```

**✅ Pochopil jsi:** mTLS přidává další vrstvu zabezpečení!

---

## 🎯 BONUSOVÝ ÚKOL: Kompletní flow

### Scénář: Vytvořit a doručit objednávku

```http
### 1. Získat CSRF token
GET http://localhost:20300/api/v1/auth/csrf-token
Authorization: Bearer {{courier_token}}
```

```http
### 2. Získat info o sobě
GET http://localhost:20300/api/v1/auth/me
Authorization: Bearer {{courier_token}}

# Ověř, že máš správnou roli!
```

```http
### 3. Vytvořit objednávku (jako admin/dispatcher)
POST http://localhost:20300/api/v1/orders/
Authorization: Bearer {{admin_token}}
Content-Type: application/json
X-CSRF-Token: {{csrf_token}}

{
  "customer_name": "Jan Novák",
  "customer_phone": "+420606123456",
  "pickup_address": "Restaurace U Zlatého lva, Praha 1",
  "pickup_lat": 50.0875,
  "pickup_lng": 14.4210,
  "delivery_address": "Vinohradská 50, Praha 2",
  "delivery_lat": 50.0755,
  "delivery_lng": 14.4378
}

# Ulož si order_id z response!
```

```http
### 4. Přiřadit kurýra (jako dispatcher)
POST http://localhost:20300/api/v1/dispatch/auto/{{order_id}}
Authorization: Bearer {{dispatcher_token}}
X-CSRF-Token: {{csrf_token}}

# Nebo manuálně:
POST http://localhost:20300/api/v1/orders/{{order_id}}/assign
Authorization: Bearer {{dispatcher_token}}
X-CSRF-Token: {{csrf_token}}

{
  "courier_id": {{courier_id}}
}
```

```http
### 5. Vyzvednout objednávku (jako courier)
POST http://localhost:20300/api/v1/orders/{{order_id}}/pickup
Authorization: Bearer {{courier_token}}
X-CSRF-Token: {{csrf_token}}

# Ověř: status == "PICKED"
```

```http
### 6. Doručit objednávku (jako courier)
POST http://localhost:20300/api/v1/orders/{{order_id}}/deliver
Authorization: Bearer {{courier_token}}
X-CSRF-Token: {{csrf_token}}

# Ověř: status == "DELIVERED"
# Ověř: courier je opět "available"
```

```http
### 7. Smazat objednávku (jako admin)
DELETE http://localhost:20300/api/v1/orders/{{order_id}}
Authorization: Bearer {{admin_token}}
X-CSRF-Token: {{csrf_token}}

# Očekávaný výsledek: 204 No Content
```

---

## 📝 Shrnutí co ses naučil

### OAuth2 PKCE:
- ✅ Jak získat token bez uložení hesla
- ✅ Proč code_verifier/code_challenge
- ✅ Jak používat Bearer token

### RBAC:
- ✅ Role určují oprávnění
- ✅ 401 vs 403 rozdíl
- ✅ Jak chránit endpointy podle rolí

### CSRF:
- ✅ Proč potřebuješ dva tokeny
- ✅ Jak útočník zneužije cookies
- ✅ Jak CSRF brání

### mTLS:
- ✅ Jak certifikáty nahrazují hesla
- ✅ Proč server ověřuje klienta
- ✅ Jak nastavit Bruno s certifikáty

---

## 🚀 Další kroky pro samostudium

1. **Zkusit refresh token flow** (`be/auth-refresh-demo`)
2. **Zkusit M2M client credentials** (`be/auth-client-credentials-demo`)
3. **Přečíst OWASP Top 10** (https://owasp.org/Top10/)
4. **Zkusit Burp Suite** pro testování API

---

## 📚 Zdroje

- [OAuth2 PKCE RFC](https://datatracker.ietf.org/doc/html/rfc7636)
- [JWT.io](https://jwt.io) - JWT debugger
- [OWASP CSRF Prevention](https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html)
- [mTLS Explained](https://www.cloudflare.com/learning/access-management/what-is-mutual-tls/)

---

> **Tip:** Ulož si tento soubor do `bruno/collections/security-learning` a pracuj v něm interaktivně!
