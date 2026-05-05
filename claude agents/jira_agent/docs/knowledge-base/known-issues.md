# Known Issues

> Known problems, workarounds, and their status.

## Active Issues

| ID | Problem | Workaround | Status | Ticket |
|----|---------|------------|--------|--------|
| KI-001 | Test token endpoint is available in production | Disable endpoint in production via env var | Open | - |
| KI-002 | Dispatch endpoints have no authentication | Not required (internal service), but consider API key | Open | - |
| KI-003 | Refresh token not implemented in main backend | Use auth-refresh-demo (port 5102) or re-login | Open | - |

## Resolved Issues

| ID | Problem | Fix Version | Ticket |
|----|---------|-------------|--------|
| - | - | - | - |

## Flaky Tests

| Test | Problem | Cause |
|------|---------|-------|
| - | - | - |

## Environment-Specific Issues

### Local (Docker)

| Problem | Solution |
|---------|----------|
| Port already in use | Change port in `.env` (e.g., `BACKEND_PORT=20301`) |
| DB won't start | Wait for healthcheck, or `docker compose down -v && docker compose up --build` |
| Frontend crashing | `docker logs moje_app_frontend` for diagnostics |
| Backend can't see DB | Check healthcheck, wait for `db: condition: service_healthy` |

### Local (native)

| Problem | Solution |
|---------|----------|
| ModuleNotFoundError | `pip install -r requirements.txt` in `be/` directory |
| DB connection refused | Start PostgreSQL or use Docker (`docker compose up db`) |
| CORS errors | Backend has `allow_origins=["*"]` in development |

## Temporary Workarounds

### Auth Without PKCE (testing)

For quick testing, you can use `/auth/test-token` endpoint instead of full PKCE flow:

```bash
POST /auth/test-token
{
  "username": "test_courier",
  "role": "courier",
  "user_id": 5
}
```

**Warning:** This endpoint must be disabled in production!

### Dispatch Without GPS

Couriers without GPS location won't be assigned by automatic dispatch. For testing:

```bash
PATCH /couriers/{id}/location
{
  "lat": 50.0755,
  "lng": 14.4378
}
```

### Frontend Logs

Frontend sends logs to Loki, but logs may be lost during batching. For immediate sending:

```javascript
logger.flush();
```

## Security Notes

### Development vs Production

| Setting | Development | Production |
|---------|-------------|------------|
| CSRF protection | Disabled (`FORCE_HTTPS=false`) | Enabled |
| mTLS | Disabled | Optional (nginx profile) |
| Test token endpoint | Available | **Disable!** |
| CORS | `allow_origins=["*"]` | Restrict to frontend URL |

### Sensitive Data

Never save to repository:
- `SECRET_KEY` - JWT signing
- `CSRF_SECRET_KEY` - CSRF tokens
- `DATABASE_URL` with production credentials
- SSL certificates (`.pem`, `.p12`, `.key`)

## Architectural Limits

| Limit | Value | Reason |
|-------|-------|--------|
| Dispatch radius max | 1500 km | Hardcoded in dispatch_service.py |
| Pagination max | 1000 | DoS protection |
| Token validity | 30 min | Security |

## Notes

- When testing in Docker, always wait for DB healthcheck (`db: condition: service_healthy`)
- For mTLS you need to generate certificates (`certs/generate-certs.sh`)
- Redis is only used for auth demo services, not for main backend
