# Architecture

> Overview of application architecture — modules, dependencies, communication.

## Overview

Full-stack delivery application with microservices-style architecture. Backend is monolithic FastAPI,
but with multiple auth demo services for learning purposes. Frontend is React Native/Expo.

## Services / Modules

| Service | Purpose | Tech Stack | Port | Communication |
|---------|---------|------------|------|---------------|
| backend | Main API - orders, couriers, dispatch | FastAPI + PostgreSQL | 20300 | REST |
| frontend | Mobile/web application | React Native + Expo | 20301 | REST → backend |
| db | Database | PostgreSQL 17 | 20343 | - |
| redis | Cache for auth codes | Redis 8 | 20400 | - |
| loki | Log aggregation | Grafana Loki 3.3 | 20351 | Push from backend |
| grafana | Monitoring dashboard | Grafana 11.4 | 20350 | Query Loki |
| adminer | DB admin UI | Adminer | 20380 | - |
| nginx | mTLS termination (prod) | Nginx | 443/80 | Reverse proxy |
| auth-demo | OAuth2 session demo | FastAPI + SQLite | 5101 | - |
| auth-refresh-demo | OAuth2 refresh token demo | FastAPI + SQLite | 5102 | - |
| auth-client-credentials-demo | OAuth2 M2M demo | FastAPI + SQLite | 5103 | - |
| auth-authorization-code-demo | OAuth2 auth code demo | FastAPI + SQLite + Redis | 5104 | - |
| auth-pkce-demo | OAuth2 PKCE demo (used) | FastAPI + SQLite + Redis | 5105 | - |

## Diagram

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Frontend   │────▶│   Backend   │────▶│  PostgreSQL │
│  :20301     │     │   :20300    │     │   :20343    │
└─────────────┘     └──────┬──────┘     └─────────────┘
                           │
                    ┌──────┴──────┐
                    │    Loki     │
                    │   :20351    │
                    └──────┬──────┘
                           │
                    ┌──────┴──────┐
                    │   Grafana   │
                    │   :20350    │
                    └─────────────┘

Production (mTLS):
┌─────────────┐  mTLS   ┌─────────────┐     ┌─────────────┐
│  Frontend   │────────▶│    Nginx    │────▶│   Backend   │
│  + client   │  :443   │ (mTLS term) │     │   :8000     │
│  cert       │         │             │     │             │
└─────────────┘         └─────────────┘     └─────────────┘
```

## Backend Structure

```
be/app/
├── main.py              # FastAPI app init
├── database.py          # SQLAlchemy engine
├── api/endpoints/       # API route handlers
│   ├── orders.py        # Orders CRUD + lifecycle
│   ├── couriers.py      # Couriers CRUD + GPS
│   ├── dispatch.py      # Auto/manual dispatch
│   ├── auth.py          # Auth endpoints
│   ├── form_data.py     # Legacy form CRUD
│   └── logs.py          # Logs endpoint
├── crud/                # Database operations
├── models/              # SQLAlchemy models
│   ├── order.py         # Order + OrderStatus enum
│   ├── courier.py       # Courier + CourierStatus enum
│   └── dispatch_log.py  # Dispatch audit log
├── schemas/             # Pydantic schemas
├── services/            # Business logic
│   └── dispatch_service.py  # Dispatch algorithm
├── core/                # Config + auth
│   ├── config.py        # Settings (env vars)
│   ├── auth.py          # JWT validation + dependencies
│   ├── csrf.py          # CSRF protection
│   ├── permissions.py   # RBAC dependencies
│   └── mtls.py          # mTLS middleware
└── shared/              # Shared logging module
```

## Database

### PostgreSQL (main)
- **Host:** localhost:20343 (Docker) / db:5432 (internal)
- **User:** postgres
- **Password:** postgres
- **Database:** moje_app

### Entities

| Entity | Table | Description |
|--------|-------|-------------|
| Order | orders | Order (customer, pickup, delivery, status) |
| Courier | couriers | Courier (name, GPS, status, tags) |
| DispatchLog | dispatch_logs | Dispatch operation audit log |
| FormData | form_data | Legacy form data |

### Relationships

- Order **N:1** Courier (optional assignment)
- Order **1:N** DispatchLog (assignment history)

## External Services

| Service | Purpose | URL |
|---------|---------|-----|
| Grafana | Monitoring dashboard | http://localhost:20350 |
| Loki | Log aggregation | http://localhost:20351 |
| Adminer | DB management | http://localhost:20380 |

## Auth Services (demo/learning)

Each auth demo service shows a different OAuth2 flow:

| Service | Flow | Use Case |
|---------|------|----------|
| auth-demo | Session-based | Basic session auth |
| auth-refresh-demo | Refresh Token | Long-lived sessions |
| auth-client-credentials-demo | Client Credentials | M2M communication |
| auth-authorization-code-demo | Authorization Code | Server-side apps |
| **auth-pkce-demo** | **PKCE** | **Mobile apps (used)** |

## Notes

- Backend runs on port 20300 (Docker mapping), internally 8000
- Auth demo services use SQLite, main backend PostgreSQL
- Logs from backend are sent to Loki (if `LOKI_URL` is set)
- mTLS is optional, activated with `--profile production`
- CSRF protection is activated by setting `FORCE_HTTPS=true`
