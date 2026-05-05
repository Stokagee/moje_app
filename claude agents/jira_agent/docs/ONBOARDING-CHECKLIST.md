# Onboarding Checklist

> Checklist for onboarding a new tester to the Delivery App project.

## Prerequisites

- [x] Repository access (local: `C:\Users\stoka\Documents\moje_app`)
- [ ] Jira project access (TODO: fill in project key)
- [ ] Docker Desktop installed
- [ ] Bruno CLI installed (`npm install -g @usebruno/cli`)
- [ ] Bruno Desktop installed (optional, for GUI)

## Setup

### 1. Project

```bash
# Start environment
cd C:\Users\stoka\Documents\moje_app
docker compose up --build

# Verify running services:
# - Backend:     http://localhost:20300/docs (Swagger)
# - Frontend:    http://localhost:20301
# - Adminer:     http://localhost:20380
# - Grafana:     http://localhost:20350 (admin/admin)
```

- [ ] Run `docker compose up --build`
- [ ] Verify backend at http://localhost:20300/docs
- [ ] Verify Swagger UI (interactive API documentation)

### 2. Bruno

```bash
# Path to collections
cd C:\Users\stoka\Documents\moje_app\bruno\collections\orders-flow

# Run tests
bru run . --env Local
```

- [ ] Open Bruno collection in `bruno/collections/orders-flow/`
- [ ] Set environment to "Local"
- [ ] Run `00a-get-admin-token.bru` → verify `admin_token` is saved
- [ ] Run `10-create-order.bru` → verify order creation

### 3. API Specification

- [ ] Open Swagger UI: http://localhost:20300/docs
- [ ] Find OpenAPI spec: `openapi_spec.json` in project root
- [ ] Map main endpoints:
  - `/orders/*` - orders
  - `/couriers/*` - couriers
  - `/dispatch/*` - dispatch
  - `/auth/*` - authentication

### 4. Knowledge Base

- [ ] Read `docs/knowledge-base/architecture.md` - how the app works
- [ ] Read `docs/knowledge-base/auth-flow.md` - how to get token
- [ ] Read `docs/knowledge-base/api-map.md` - endpoint overview
- [ ] Read `docs/knowledge-base/business-rules.md` - validation and states
- [ ] Read `docs/knowledge-base/known-issues.md` - known issues
- [ ] Read `docs/knowledge-base/env-overview.md` - environments and URLs

### 5. Authentication (Testing)

```
# Get test token (development only!)
POST http://localhost:20300/api/v1/auth/test-token
{
  "username": "test_admin",
  "role": "admin",
  "user_id": 1,
  "scopes": "orders:read orders:write orders:admin"
}

# Use in Bruno:
Authorization: Bearer {{admin_token}}
```

- [ ] Get admin token via `/auth/test-token`
- [ ] Get courier token (role: "courier")
- [ ] Get customer token (role: "user")
- [ ] Test protected endpoint with token

### 6. Claude Agent

- [ ] Read `CLAUDE.md` in agent folder
- [ ] Try `/test-ticket` command on test ticket
- [ ] Try `/explore` command on `/orders` endpoint
- [ ] Try `/regression-check` command on orders-flow collection

## First Tasks

1. [ ] Run entire orders-flow (00a → 60) and verify PASS
2. [ ] Reproduce known issue from `known-issues.md`
3. [ ] Create new Bruno test for edge case
4. [ ] Propose knowledge base update based on what you learned

## Services and Ports

| Service | Port | URL |
|---------|------|-----|
| Backend API | 20300 | http://localhost:20300 |
| Frontend | 20301 | http://localhost:20301 |
| Adminer | 20380 | http://localhost:20380 |
| Grafana | 20350 | http://localhost:20350 |
| Loki | 20351 | http://localhost:20351 |
| Auth PKCE | 5105 | http://localhost:5105 |

## Database

| Field | Value |
|-------|-------|
| Host | localhost:20343 |
| User | postgres |
| Password | postgres |
| Database | moje_app |

## Completion

- [ ] Fill in missing information in knowledge base
- [ ] Update this checklist if something is missing
- [ ] Report any setup issues
