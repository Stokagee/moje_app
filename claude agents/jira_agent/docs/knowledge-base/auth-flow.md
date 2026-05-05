# Auth Flow

> Authentication flow step by step — how to get token, how to use it.

## Authentication Type

**OAuth2 PKCE** (Proof Key for Code Exchange) - for mobile and public clients.

Backend uses JWT Bearer tokens issued by `auth-pkce-demo` service (port 5105).

## Flow Diagram

```
1. Client → GET /auth/csrf-token
2. Server → 200 OK { csrf_token } + cookie
3. Client → POST /auth/test-token (TEST ONLY) or PKCE flow
4. Server → 200 OK { access_token, token_type, expires_in }
5. Client → GET /api/v1/orders (Authorization: Bearer <token>)
6. Server → 200 OK { data }
```

## Getting Token

### Option 1: Test Token (testing only)

```bash
POST {{base_url}}/auth/test-token
Content-Type: application/json

{
  "username": "test_courier",
  "role": "courier",
  "user_id": 5,
  "scopes": "orders:read orders:write"
}
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

### Option 2: PKCE Flow (production)

1. **Generate code_verifier and code_challenge**
   ```javascript
   // code_verifier: random 43-128 characters
   // code_challenge: SHA256(verifier) base64url encoded
   ```

2. **Get authorization code**
   ```
   GET {{auth_url}}/authorize?
     client_id=mobile-app&
     redirect_uri=myapp://callback&
     response_type=code&
     code_challenge=<challenge>&
     code_challenge_method=S256&
     scope=orders:read orders:write
   ```

3. **Exchange code for token**
   ```bash
   POST {{auth_url}}/token
   Content-Type: application/x-www-form-urlencoded

   grant_type=authorization_code&
   code=<auth_code>&
   code_verifier=<verifier>&
   client_id=mobile-app&
   redirect_uri=myapp://callback
   ```

## Using Token

```bash
GET {{base_url}}/orders/
Authorization: Bearer {{access_token}}
```

## Token Expiration

| Token Type | Validity | Configuration |
|------------|----------|---------------|
| Access token | 30 minutes | `ACCESS_TOKEN_EXPIRE_MINUTES` |
| Auth code | 10 minutes | `AUTH_CODE_EXPIRE_SECONDS` |

### Refresh Token

Currently not implemented in main backend. Use `auth-refresh-demo` service (port 5102).

## CSRF

For POST/PUT/DELETE operations (when `FORCE_HTTPS=true`):

```bash
# 1. Get CSRF token
GET {{base_url}}/auth/csrf-token
# Response: { "csrf_token": "..." }

# 2. Use in request
POST {{base_url}}/orders/
X-CSRF-Token: {{csrf_token}}
Authorization: Bearer {{access_token}}
```

## Test Credentials

### Via /auth/test-token endpoint

| Role | username | user_id | scopes |
|------|----------|---------|--------|
| Admin | test_admin | 1 | orders:read orders:write orders:admin |
| Courier | test_courier | 5 | orders:read orders:write |
| Customer | test_customer | 10 | orders:read |

### Bruno Environment

```javascript
// In Bruno pre-request script:
bru.setEnvVar('admin_token', res.body.access_token);
bru.setEnvVar('courier_token', res.body.access_token);
```

## JWT Token Payload

```json
{
  "sub": "test_courier",
  "user_id": 5,
  "role": "courier",
  "scopes": "orders:read orders:write",
  "exp": 1704067200,
  "iat": 1704065400
}
```

## Roles and Permissions

| Role | Scopes | Endpoints |
|------|--------|-----------|
| user/customer | orders:read | GET /orders, GET /orders/{id}, POST /orders/{id}/cancel |
| courier | orders:read, orders:write | + POST /orders/{id}/pickup, POST /orders/{id}/deliver |
| admin | orders:read, orders:write, orders:admin | + PATCH /orders/{id}/status, DELETE /orders/{id} |

## Errors

| Status | Detail | Solution |
|--------|--------|----------|
| 401 | Invalid or expired token | Get new token |
| 401 | Invalid token payload | Token doesn't have 'sub' field |
| 403 | Courier role required | Use token with courier/admin role |
| 403 | Admin role required | Use token with admin role |
| 403 | Missing required scope: X | Token doesn't have needed scope |

## Notes

- Test token endpoint is **for development only** - disable in production!
- PKCE demo runs on port 5105 (`auth_url` in Bruno environment)
- CSRF protection is disabled by default (`FORCE_HTTPS=false`)
