# 📋 Security Learning Checklist

> **Cíl:** Projít si interaktivně všechny security vrstvy Orders API

---

## 🎯 Příprava

### Nastavení prostředí

- [ ] **Spustit backend**
  ```bash
  cd /c/Users/stoka/Documents/moje_app
  docker compose up -d
  ```

- [ ] **Spustit auth-pkce-demo**
  ```bash
  docker compose up auth-pkce-demo -d
  ```

- [ ] **Ověřit, že služby běží**
  ```bash
  docker compose ps
  ```
  Mělo by ukázat: backend (20300), auth-pkce-demo (5105)

- [ ] **Otevřít Bruno**
  - Import kolekci: `bruno/collections/security-learning`
  - Otevřít `0-setup.bru` a nastavit proměnné

---

## 📚 Fáze 1: OAuth2 PKCE

### Teorie (čti pozorně)

- [ ] **Pochopit problém: Proč PKCE?**
  - OAuth2 Authorization Code Flow je zranitelný pro veřejné klienty
  - Útočník může ukrást authorization code
  - PKCE přidává kryptografický důkaz, že jsi původní žadatel

- [ ] **Vysvětlit flow někomu jinému**
  ```
  1. Klient vygeneruje code_verifier (tajný)
  2. Klient vypočítá code_challenge = SHA256(verifier)
  3. Klient pošle challenge na /authorize
  4. Server uloží challenge s authorization code
  5. Klient vymění code za token + pošle verifier
  6. Server ověří SHA256(verifier) == challenge
  ```

### Praxe (Bruno requesty)

- [ ] **1.1 - PKCE Demo**
  - Spustit request
  - Zkopírovat `code_verifier` do poznámek
  - Zkopírovat `code_challenge` do poznámek
  - **Otázka:** Jak dlouhý je verifier? Proč?

- [ ] **1.2 - Authorize (v prohlížeči)**
  - Zkopírovat URL do prohlížeče
  - Přihlásit se: `testuser` / `testpassword`
  - Schválit consent
  - Zkopírovat `code` z redirect URL
  - **Otázka:** Proč musíš schválit consent?

- [ ] **1.3 - Token Exchange**
  - Nastavit `code_z_prohlížeče`
  - Nastavit `code_verifier_z_1.1`
  - Spustit request
  - Uložit `access_token` do proměnných
  - **Otázka:** Jak dlouho token platí?

### ✅ Checkpoint

- [ ] **Vysvětlit vlastními slovy:**
  - Co je JWT token?
  - Co je PKCE?
  - Proč SHA256?

---

## 📚 Fáze 2: Role-Based Access Control

### Teorie

- [ ] **Pochopit RBAC**
  - Role = skupina oprávnění
  - Permissions = co můžeš dělat
  - Resources = s čím můžeš dělat

- [ ] **Zapamatovat role**
  | Role | Oprávnění |
  |------|-----------|
  | customer | Číst vlastní objednávky |
  | courier | Vyzvednout/doručit přiřazené |
  | admin | Všechno |

- [ ] **Rozdíl 401 vs 403**
  - 401 = Nevím kdo jsi (chybí token)
  - 403 = Vím kdo jsi, ale nemůžeš sem (špatná role)

### Praxe

- [ ] **2.1 - Orders BEZ tokenu**
  - Spustit request
  - Ověřit: 401 Unauthorized
  - **Otázka:** Proč 401 a ne 403?

- [ ] **2.2 - Orders S tokenem**
  - Nastavit `access_token`
  - Spustit request
  - Ověřit: 200 OK
  - **Otázka:** Kolik objednávek vidíš?

- [ ] **2.3 - Pickup jako CUSTOMER**
  - Potřebuješ token s rolí `customer`
  - Spustit request
  - Ověřit: 403 Forbidden
  - **Otázka:** Proč 403?

### ✅ Checkpoint

- [ ] **Nakreslit diagram:**
  ```
  Request → Auth Middleware → RBAC Check → Endpoint
            (401 if fail)    (403 if fail)
  ```

- [ ] **Vysvětlit vlastními slovy:**
  - Proč courier nemůže delete?
  - Proč customer nemůže pickup?

---

## 📚 Fáze 3: CSRF Protection

### Teorie

- [ ] **Pochopit CSRF útok**
  - Jsi přihlášený na bank.com
  - Otevřeš evil.com
  - evil.com pošle POST na bank.com/transfer
  - Browser pošle cookies automaticky
  - Banka vykoná převod!

- [ ] **Pochopit ochranu**
  - Server vygeneruje CSRF token
  - Token v cookie (evil.com nevidí)
  - Token v response (JS vidí)
  - JS musí poslat token v header
  - Server ověří: cookie == header

- [ ] **Proč SameSite cookie?**
  - Cookie se neposílá cross-site
  - evil.com nemůže poslat tvoji cookie

### Praxe

- [ ] **3.1 - Získat CSRF token**
  - Spustit request
  - Uložit `csrf_token`
  - **Otázka:** Kde je token uložen?

- [ ] **3.2 - Vytvořit objednávku**
  - Nastavit `csrf_token` v header
  - Spustit request
  - Ověřit: 201 Created
  - Uložit `order_id`

### ✅ Checkpoint

- [ ] **Vysvětlit vlastními slovy:**
  - Proč potřebujeme CSRF když máme token?
  - Jak evil.com nemůže přečíst cookie?
  - Proč X-CSRF-Token header?

---

## 📚 Fáze 4: mTLS (Bonus)

### Teorie

- [ ] **Pochopit TLS**
  - Server má certifikát
  - Klient ověří certifikát
  - Šifrovaná komunikace

- [ ] **Pochopit mTLS**
  - Klient TAKÉ má certifikát
  - Server ověří klientský certifikát
  - Dvoustranná autentizace

- [ ] **Výhody mTLS**
  - Není potřeba heslo
  - Certifikát nelze ukrást (bez private key)
  - Hardware tokeny (YubiKey)

### Praxe (volitelné)

- [ ] **Generovat certifikáty**
  ```bash
  cd certs
  ./generate-certs.sh  # Linux/Mac
  # nebo
  .\generate-certs.ps1  # Windows
  ```

- [ ] **Spustit s nginx**
  ```bash
  docker compose --profile production up -d
  ```

- [ ] **Nastavit Bruno certifikát**
  - Collection Settings → Client Certificates
  - Přidat client.crt + client.key

- [ ] **Test s certifikátem**
  - Spustit request na https://localhost/...
  - Bez certifikátu: SSL Error
  - S certifikátem: 200 OK

---

## 🎯 Kompletní Flow Test

- [ ] **4.1 - Kompletní objednávka flow**
  - Vytvořit objednávku (jako admin/dispatcher)
  - Přiřadit kurýra
  - Vyzvednout (jako courier)
  - Doručit (jako courier)
  - Smazat (jako admin)

---

## 📝 Závěrečné otázky

### OAuth2
- [ ] Co je difference mezi access token a refresh token?
- [ ] Proč PKCE pro SPA a mobilní aplikace?
- [ ] Jak dlouho by měl access token platit?

### RBAC
- [ ] Jak implementovat "user může editovat jen své vlastní data"?
- [ ] Jak přidat novou roli "dispatcher"?
- [ ] Jak logovat neautorizované přístupy?

### CSRF
- [ ] Proč CSRF nefunguje pro API-only aplikace?
- [ ] Jak CSRF spolupracuje s CORS?
- [ ] Proč SameSite=strict je nejbezpečnější?

### mTLS
- [ ] Jak rotovat certifikáty bez downtime?
- [ ] Co je CRL (Certificate Revocation List)?
- [ ] Jak integrovat mTLS s Kubernetes?

---

## 🚀 Další kroky

1. **Implementovat refresh token flow**
   - `be/auth-refresh-demo` je připraven
   - Vyzkoušet rotaci tokenů

2. **Implementovat M2M client credentials**
   - `be/auth-client-credentials-demo`
   - Pro service-to-service komunikaci

3. **Napsat vlastní testy**
   - Robot Framework
   - pytest

4. **Přečíst OWASP Top 10**
   - https://owasp.org/Top10/

---

## ✅ Kompletní úspěch!

Pokud jsi dokončil všechny položky:
- ✅ Chápeš OAuth2 PKCE
- ✅ Umíš implementovat RBAC
- ✅ Rozumíš CSRF ochraně
- ✅ Vyzkoušel jsi mTLS

**Gratuluji! Jsi připraven implementovat security v reálných projektech! 🎉**
