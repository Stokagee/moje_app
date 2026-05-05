# mTLS Certifikáty

Tento adresář obsahuje certifikáty pro mTLS (mutual TLS) autentizaci.

## Co je mTLS?

mTLS (mutual TLS) je bezpečnostní mechanismus, kde:
1. **Server** předloží svůj certifikát klientovi (jako u běžného HTTPS)
2. **Klient** také předloží svůj certifikát serveru (navíc oproti běžnému HTTPS)
3. Obě strany ověří certifikát druhé strany

To zajišťuje, že:
- Klient ověřuje, že mluví se správným serverem
- Server ověřuje, že klient je oprávněný

## Struktura

```
certs/
├── ca.key              # CA private key (DRŽET V TAJNOSTI!)
├── ca.crt              # CA certificate (veřejný)
├── server.key          # Server private key
├── server.crt          # Server certificate
├── client.key          # Client private key
└── client.crt          # Client certificate
```

## Generování certifikátů

### Linux/Mac (bash)
```bash
chmod +x generate-certs.sh
./generate-certs.sh
```

### Windows (PowerShell)
```powershell
.\generate-certs.ps1
```

### Manuálně (OpenSSL)

1. **Vytvořit CA (Certificate Authority)**
```bash
openssl genrsa -out certs/ca.key 4096
openssl req -x509 -new -nodes -key certs/ca.key -sha256 -days 365 -out certs/ca.crt -subj "/C=CZ/ST=Praha/L=Praha/O=MojeApp/CN=MojeApp-CA"
```

2. **Vytvořit server certifikát**
```bash
openssl genrsa -out certs/server.key 2048
openssl req -new -key certs/server.key -out certs/server.csr -subj "/C=CZ/ST=Praha/L=Praha/O=MojeApp/CN=localhost"
openssl x509 -req -in certs/server.csr -CA certs/ca.crt -CAkey certs/ca.key -CAcreateserial -out certs/server.crt -days 365 -sha256
```

3. **Vytvořit klientský certifikát**
```bash
openssl genrsa -out certs/client.key 2048
openssl req -new -key certs/client.key -out certs/client.csr -subj "/C=CZ/ST=Praha/L=Praha/O=MojeApp/CN=frontend-client"
openssl x509 -req -in certs/client.csr -CA certs/ca.crt -CAkey certs/ca.key -CAcreateserial -out certs/client.crt -days 365 -sha256
```

4. **Vytvořit PFX pro Windows/Postman** (volitelné)
```bash
openssl pkcs12 -export -out certs/client.pfx -inkey certs/client.key -in certs/client.crt -certfile certs/ca.crt
```

## Použití

### s curl
```bash
# Bez klientského certifikátu - SELŽE
curl https://localhost/api/v1/orders/

# S klientským certifikátem - USPĚJE (ale vrátí 401 pro chybějící Bearer token)
curl --cert certs/client.crt --key certs/client.key https://localhost/api/v1/orders/
```

### s Postman
1. Settings → Certificates → Client certificates
2. Add certificate:
   - Host: localhost
   - CRT file: `certs/client.crt`
   - KEY file: `certs/client.key`
   - PFX file: (volitelné) `certs/client.pfx`

### s Python requests
```python
import requests

response = requests.get(
    "https://localhost/api/v1/orders/",
    cert=("certs/client.crt", "certs/client.key"),
    verify="certs/ca.crt"
)
```

## Bezpečnost

⚠️ **DŮLEŽITÉ:**
- `ca.key` a `*.key` soubory nikdy necommitovat do gitu!
- V produkci používejte profesionální CA (LetsEncrypt, DigiCert, atd.)
- Klientské certifikáty generovat individuálně pro každého klienta

## Produkční nasazení

V produkci:
1. Použijte veřejnou CA pro server certifikát (LetsEncrypt)
2. Použijte vlastní CA pouze pro klientské certifikáty
3. Implementujte CRL (Certificate Revocation List) nebo OCSP pro revokaci
4. Pravidelně rotujte certifikáty
