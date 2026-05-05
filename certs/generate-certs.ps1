# Generování mTLS certifikátů pro Food Delivery API (PowerShell verze)
#
# Tento skript vytvoří:
# 1. Certificate Authority (CA) - důvěryhodná autorita
# 2. Server certifikát - pro backend API
# 3. Klientský certifikát - pro frontend/Postman
#
# POZOR: Spusťte pouze jednou! Opětovné spuštění přepíše existující certifikáty.

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$CertsDir = $ScriptDir

Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "       Generování mTLS certifikátů" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host ""

# Kontrola OpenSSL
$openssl = Get-Command openssl -ErrorAction SilentlyContinue
if (-not $openssl) {
    Write-Host "❌ OpenSSL není nainstalován." -ForegroundColor Red
    Write-Host ""
    Write-Host "Instalace na Windows:" -ForegroundColor Yellow
    Write-Host "  1. Stáhněte z: https://slproweb.com/products/Win32OpenSSL.html" -ForegroundColor Yellow
    Write-Host "  2. Nebo použijte Chocolatey: choco install openssl" -ForegroundColor Yellow
    Write-Host "  3. Nebo použijte Git Bash a spusťte generate-certs.sh" -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ OpenSSL nalezen: $(openssl version)" -ForegroundColor Green
Write-Host ""

# ============================================================================
# 1. Certificate Authority (CA)
# ============================================================================
Write-Host "📌 Krok 1/6: Generování CA private key..." -ForegroundColor Yellow

if (Test-Path "$CertsDir\ca.key") {
    $reply = Read-Host "⚠️  ca.key již existuje. Přepsat? (y/N)"
    if ($reply -ne "y" -and $reply -ne "Y") {
        Write-Host "❌ Zrušeno." -ForegroundColor Red
        exit 1
    }
}

openssl genrsa -out "$CertsDir\ca.key" 4096
Write-Host "✅ CA private key vytvořen: ca.key" -ForegroundColor Green
Write-Host ""

Write-Host "📌 Krok 2/6: Generování CA certifikátu..." -ForegroundColor Yellow
openssl req -x509 -new -nodes `
    -key "$CertsDir\ca.key" `
    -sha256 `
    -days 365 `
    -out "$CertsDir\ca.crt" `
    -subj "/C=CZ/ST=Praha/L=Praha/O=MojeApp-Training/CN=MojeApp-CA"
Write-Host "✅ CA certifikát vytvořen: ca.crt" -ForegroundColor Green
Write-Host ""

# ============================================================================
# 2. Server certifikát
# ============================================================================
Write-Host "📌 Krok 3/6: Generování server private key..." -ForegroundColor Yellow
openssl genrsa -out "$CertsDir\server.key" 2048
Write-Host "✅ Server private key vytvořen: server.key" -ForegroundColor Green
Write-Host ""

Write-Host "📌 Krok 4/6: Generování server certifikátu..." -ForegroundColor Yellow

# Vytvořit config pro SAN (Subject Alternative Names)
$sanConfig = @"
subjectAltName=DNS:localhost,DNS:backend,IP:127.0.0.1
"@
Set-Content -Path "$CertsDir\server.cnf" -Value $sanConfig

openssl req -new `
    -key "$CertsDir\server.key" `
    -out "$CertsDir\server.csr" `
    -subj "/C=CZ/ST=Praha/L=Praha/O=MojeApp/CN=localhost"

openssl x509 -req `
    -in "$CertsDir\server.csr" `
    -CA "$CertsDir\ca.crt" `
    -CAkey "$CertsDir\ca.key" `
    -CAcreateserial `
    -out "$CertsDir\server.crt" `
    -days 365 `
    -sha256 `
    -extfile "$CertsDir\server.cnf"

Remove-Item "$CertsDir\server.csr"
Remove-Item "$CertsDir\server.cnf"
Write-Host "✅ Server certifikát vytvořen: server.crt" -ForegroundColor Green
Write-Host ""

# ============================================================================
# 3. Klientský certifikát
# ============================================================================
Write-Host "📌 Krok 5/6: Generování klientského private key..." -ForegroundColor Yellow
openssl genrsa -out "$CertsDir\client.key" 2048
Write-Host "✅ Klientský private key vytvořen: client.key" -ForegroundColor Green
Write-Host ""

Write-Host "📌 Krok 6/6: Generování klientského certifikátu..." -ForegroundColor Yellow
openssl req -new `
    -key "$CertsDir\client.key" `
    -out "$CertsDir\client.csr" `
    -subj "/C=CZ/ST=Praha/L=Praha/O=MojeApp/CN=frontend-client"

openssl x509 -req `
    -in "$CertsDir\client.csr" `
    -CA "$CertsDir\ca.crt" `
    -CAkey "$CertsDir\ca.key" `
    -CAcreateserial `
    -out "$CertsDir\client.crt" `
    -days 365 `
    -sha256

Remove-Item "$CertsDir\client.csr"
Write-Host "✅ Klientský certifikát vytvořen: client.crt" -ForegroundColor Green
Write-Host ""

# ============================================================================
# 4. PFX pro Windows/Postman
# ============================================================================
Write-Host "📌 Bonus: Vytváření PFX pro Postman/Windows..." -ForegroundColor Yellow
openssl pkcs12 -export `
    -out "$CertsDir\client.pfx" `
    -inkey "$CertsDir\client.key" `
    -in "$CertsDir\client.crt" `
    -certfile "$CertsDir\ca.crt" `
    -passout pass:
Write-Host "✅ PFX vytvořen: client.pfx (heslo: prázdné)" -ForegroundColor Green
Write-Host ""

# ============================================================================
# 5. Výpis informací
# ============================================================================
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "           Souhrn vygenerovaných certifikátů" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "📁 Výstupní adresář: $CertsDir" -ForegroundColor White
Write-Host ""

Write-Host "Soubory:" -ForegroundColor White
Get-ChildItem "$CertsDir" -Filter "*.key" | ForEach-Object { Write-Host "  $($_.Name)" }
Get-ChildItem "$CertsDir" -Filter "*.crt" | ForEach-Object { Write-Host "  $($_.Name)" }
Get-ChildItem "$CertsDir" -Filter "*.pfx" | ForEach-Object { Write-Host "  $($_.Name)" }
Write-Host ""

Write-Host "🔒 CA certifikát:" -ForegroundColor White
openssl x509 -in "$CertsDir\ca.crt" -noout -subject -issuer -dates
Write-Host ""

Write-Host "🖥️  Server certifikát:" -ForegroundColor White
openssl x509 -in "$CertsDir\server.crt" -noout -subject -issuer -dates
Write-Host ""

Write-Host "👤 Klientský certifikát:" -ForegroundColor White
openssl x509 -in "$CertsDir\client.crt" -noout -subject -issuer -dates
Write-Host ""

# ============================================================================
# 6. Gitignore připomenutí
# ============================================================================
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "                 ⚠️  DŮLEŽITÉ ⚠️" -ForegroundColor Yellow
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "🔴  Přidejte do .gitignore:" -ForegroundColor Red
Write-Host ""
Write-Host "    certs/*.key" -ForegroundColor Yellow
Write-Host "    certs/*.crt" -ForegroundColor Yellow
Write-Host "    certs/*.pfx" -ForegroundColor Yellow
Write-Host "    certs/*.srl" -ForegroundColor Yellow
Write-Host ""

Write-Host "✅ Hotovo! Certifikáty jsou připraveny." -ForegroundColor Green
