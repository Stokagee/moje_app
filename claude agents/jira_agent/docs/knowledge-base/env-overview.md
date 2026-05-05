# Environment Overview

> Overview of environments, URLs, credentials flow.

## Environment List

| Name | URL | Purpose | Data |
|------|-----|---------|------|
| Local (Docker) | http://localhost:20300 | Development | Test |
| Local (native) | http://localhost:8000 | Development without Docker | Test |

**Note:** Staging and Production environments are not currently configured.

## Access

### Local (Docker) - recommended

```bash
# Start everything
docker compose up --build

# Start in background
docker compose up -d

# Stop
docker compose down

# Reset database
docker compose down -v
```

### Local (native)

```bash
cd be
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

## Available Services (Docker)

| Service | URL | Login |
|---------|-----|-------|
| Backend API | http://localhost:20300 | - |
| API Docs (Swagger) | http://localhost:20300/docs | - |
| Frontend | http://localhost:20301 | - |
| Adminer (DB) | http://localhost:20380 | see below |
| Grafana | http://localhost:20350 | admin/admin |
| Loki | http://localhost:20351 | - |

### Adminer Login

| Field | Value |
|-------|-------|
| System | PostgreSQL |
| Server | db |
| User | postgres |
| Password | postgres |
| Database | moje_app |

### Auth Demo Services

| Service | Port | Purpose |
|---------|------|---------|
| auth-demo | 5101 | Session-based OAuth2 |
| auth-refresh-demo | 5102 | Refresh Token Flow |
| auth-client-credentials-demo | 5103 | M2M Client Credentials |
| auth-authorization-code-demo | 5104 | Authorization Code Flow |
| **auth-pkce-demo** | **5105** | **PKCE Flow (used)** |

## Credentials

### Database (PostgreSQL)

```bash
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=moje_app
DB_PORT=20343  # external port
```

### Backend (env vars)

| Variable | Default | Description |
|----------|---------|-------------|
| SECRET_KEY | super-secret-key-... | JWT signing |
| ALGORITHM | HS256 | JWT algorithm |
| ACCESS_TOKEN_EXPIRE_MINUTES | 30 | Token validity |
| CSRF_SECRET_KEY | csrf-secret-... | CSRF token signing |
| FORCE_HTTPS | false | Enables CSRF |
| LOG_LEVEL | INFO | Logging |

### Test Accounts (via /auth/test-token)

| Role | Username | User ID |
|------|----------|---------|
| Admin | test_admin | 1 |
| Courier | test_courier | 5 |
| Customer | test_customer | 10 |

**Note:** Passwords not needed - test token endpoint creates token directly.

## Bruno Environments

```
bruno/collections/
├── orders-flow/
│   └── environments/
│       └── Local.bru          # base_url, tokens, order_id, courier_id
└── security-learning/
    └── environments/
        └── Local.bru          # base_url, auth_url, tokens
```

### Local.bru (orders-flow)

```javascript
vars {
  base_url: http://localhost:20300/api/v1
  admin_token:
  courier_token:
  customer_token:
  order_id:
  courier_id:
  flow_order_id:
  test_courier_id:
}
```

### Local.bru (security-learning)

```javascript
vars {
  base_url: http://localhost:20300/api/v1
  auth_url: http://localhost:5105
  access_token:
  csrf_token:
  // ...
}
```

## Data Management

### Database Reset

```bash
# Delete all data
docker compose down -v

# Recreate
docker compose up --build
```

### Creating Test Data

1. **Courier:**
   ```bash
   POST /couriers/
   {
     "name": "Test Courier",
     "phone": "+420777123456",
     "email": "courier@test.com",
     "lat": 50.0755,
     "lng": 14.4378,
     "status": "available"
   }
   ```

2. **Order:**
   ```bash
   POST /orders/ (with Bearer token)
   {
     "customer_name": "Test Customer",
     "customer_phone": "+420606123456",
     ...
   }
   ```

3. **Via Bruno:**
   - `00a-get-admin-token.bru` → gets admin token
   - `10-create-order.bru` → creates order with random data

## Monitoring

### Grafana

- **URL:** http://localhost:20350
- **Login:** admin / admin
- **Dashboards:**
  - Main Backend API (logs from backend)
  - Frontend Logs (logs from frontend)

### Loki

- **URL:** http://localhost:20351/loki/api/v1/push
- **Query:** `{service="moje-app-backend"}` or `{service="moje-app-frontend"}`

### Logs from Backend

```bash
docker logs moje_app_backend
```

## Production Setup

### mTLS (optional)

```bash
# Generate certificates
cd certs && ./generate-certs.sh  # Linux/Mac
cd certs && .\generate-certs.ps1  # Windows

# Run with nginx and mTLS
docker compose --profile production up
```

### Environment Variables for Production

| Variable | Value |
|----------|-------|
| FORCE_HTTPS | true |
| TRUSTED_PROXIES | nginx |
| SECRET_KEY | (strong random key) |
| CSRF_SECRET_KEY | (strong random key) |

## Notes

- All services run in Docker network `moje_app_default`
- Frontend runs on port 20301 (Docker mapping), internally 3000
- Backend runs on port 20300 (Docker mapping), internally 8000
- For external DB access use port 20343
