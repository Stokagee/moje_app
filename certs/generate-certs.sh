#!/bin/bash
# Generování mTLS certifikátů pro Food Delivery API
#
# Tento skript vytvoří:
# 1. Certificate Authority (CA) - důvěryhodná autorita
# 2. Server certifikát - pro backend API
# 3. Klientský certifikát - pro frontend/Postman
#
# POZOR: Spusťte pouze jednou! Opětovné spuštění přepíše existující certifikáty.

set -e  # Ukončit při chybě

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CERTS_DIR="$SCRIPT_DIR"

echo "=================================================="
echo "       Generování mTLS certifikátů"
echo "=================================================="
echo ""

# Kontrola OpenSSL
if ! command -v openssl &> /dev/null; then
    echo "❌ OpenSSL není nainstalován. Nainstalujte openssl."
    exit 1
fi

echo "✅ OpenSSL nalezen: $(openssl version)"
echo ""

# ============================================================================
# 1. Certificate Authority (CA)
# ============================================================================
echo "📌 Krok 1/6: Generování CA private key..."

if [ -f "$CERTS_DIR/ca.key" ]; then
    read -p "⚠️  ca.key již existuje. Přepsat? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ Zrušeno."
        exit 1
    fi
fi

openssl genrsa -out "$CERTS_DIR/ca.key" 4096
echo "✅ CA private key vytvořen: ca.key"
echo ""

echo "📌 Krok 2/6: Generování CA certifikátu..."
openssl req -x509 -new -nodes \
    -key "$CERTS_DIR/ca.key" \
    -sha256 \
    -days 365 \
    -out "$CERTS_DIR/ca.crt" \
    -subj "/C=CZ/ST=Praha/L=Praha/O=MojeApp-Training/CN=MojeApp-CA"
echo "✅ CA certifikát vytvořen: ca.crt"
echo ""

# ============================================================================
# 2. Server certifikát
# ============================================================================
echo "📌 Krok 3/6: Generování server private key..."
openssl genrsa -out "$CERTS_DIR/server.key" 2048
echo "✅ Server private key vytvořen: server.key"
echo ""

echo "📌 Krok 4/6: Generování server certifikátu..."
openssl req -new \
    -key "$CERTS_DIR/server.key" \
    -out "$CERTS_DIR/server.csr" \
    -subj "/C=CZ/ST=Praha/L=Praha/O=MojeApp/CN=localhost"

openssl x509 -req \
    -in "$CERTS_DIR/server.csr" \
    -CA "$CERTS_DIR/ca.crt" \
    -CAkey "$CERTS_DIR/ca.key" \
    -CAcreateserial \
    -out "$CERTS_DIR/server.crt" \
    -days 365 \
    -sha256 \
    -extfile <(echo "subjectAltName=DNS:localhost,DNS:backend,IP:127.0.0.1")

rm "$CERTS_DIR/server.csr"
echo "✅ Server certifikát vytvořen: server.crt"
echo ""

# ============================================================================
# 3. Klientský certifikát
# ============================================================================
echo "📌 Krok 5/6: Generování klientského private key..."
openssl genrsa -out "$CERTS_DIR/client.key" 2048
echo "✅ Klientský private key vytvořen: client.key"
echo ""

echo "📌 Krok 6/6: Generování klientského certifikátu..."
openssl req -new \
    -key "$CERTS_DIR/client.key" \
    -out "$CERTS_DIR/client.csr" \
    -subj "/C=CZ/ST=Praha/L=Praha/O=MojeApp/CN=frontend-client"

openssl x509 -req \
    -in "$CERTS_DIR/client.csr" \
    -CA "$CERTS_DIR/ca.crt" \
    -CAkey "$CERTS_DIR/ca.key" \
    -CAcreateserial \
    -out "$CERTS_DIR/client.crt" \
    -days 365 \
    -sha256

rm "$CERTS_DIR/client.csr"
echo "✅ Klientský certifikát vytvořen: client.crt"
echo ""

# ============================================================================
# 4. PFX pro Windows/Postman (volitelné)
# ============================================================================
echo "📌 Bonus: Vytváření PFX pro Postman/Windows..."
openssl pkcs12 -export \
    -out "$CERTS_DIR/client.pfx" \
    -inkey "$CERTS_DIR/client.key" \
    -in "$CERTS_DIR/client.crt" \
    -certfile "$CERTS_DIR/ca.crt" \
    -passout pass:
echo "✅ PFX vytvořen: client.pfx (heslo: prázdné)"
echo ""

# ============================================================================
# 5. Výpis informací
# ============================================================================
echo "=================================================="
echo "           Souhrn vygenerovaných certifikátů"
echo "=================================================="
echo ""
echo "📁 Výstupní adresář: $CERTS_DIR"
echo ""
echo "Soubory:"
ls -la "$CERTS_DIR"/*.{key,crt,pfx} 2>/dev/null || ls -la "$CERTS_DIR"
echo ""
echo "🔒 CA certifikát (veřejný):"
openssl x509 -in "$CERTS_DIR/ca.crt" -noout -subject -issuer -dates
echo ""
echo "🖥️  Server certifikát:"
openssl x509 -in "$CERTS_DIR/server.crt" -noout -subject -issuer -dates
echo ""
echo "👤 Klientský certifikát:"
openssl x509 -in "$CERTS_DIR/client.crt" -noout -subject -issuer -dates
echo ""

# ============================================================================
# 6. Gitignore připomenutí
# ============================================================================
echo "=================================================="
echo "                 ⚠️  DŮLEŽITÉ ⚠️"
echo "=================================================="
echo ""
echo "🔴  Přidejte do .gitignore:"
echo ""
echo "    certs/*.key"
echo "    certs/*.crt"
echo "    certs/*.pfx"
echo "    certs/*.srl"
echo ""
echo "✅ Hotovo! Certifikáty jsou připraveny."
