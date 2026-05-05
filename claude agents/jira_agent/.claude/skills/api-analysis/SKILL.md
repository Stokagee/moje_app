# API Analysis — SKILL.md

Load this skill when analyzing a ticket, when you need to map an endpoint
to Swagger/OpenAPI specification, find request/response structure,
or understand authentication flow.

## When to Load This Skill

- Phase 1 workflow (Ticket Analysis)
- `/explore [endpoint]` command
- When you need to verify endpoint against specification
- When you need to find request/response schema

## API Specification Sources

```
# OpenAPI 3.0 specification:
API_SPEC_DIR: C:\Users\stoka\Documents\moje_app
API_SPEC_FILE: openapi_spec.json
API_SPEC_FORMAT: openapi-3.0

# Online (interactive):
SWAGGER_URL: http://localhost:20300/docs
REDOC_URL: http://localhost:20300/redoc
OPENAPI_JSON: http://localhost:20300/openapi.json

# Services in API:
/orders/*       - Orders (CRUD + lifecycle)
/couriers/*     - Couriers (CRUD + GPS)
/dispatch/*     - Auto/manual dispatch
/auth/*         - Authentication (test-token, csrf, me, logout)
/form/*         - Legacy form data
/logs/*         - Logs (read-only)
```

## How to Find Endpoint in Specification

### Step 1 — Search for Endpoint

```bash
# Search by path
rg "/orders" $API_SPEC_DIR/ --type yaml --type json

# Search by operationId
rg "operationId.*createOrder" $API_SPEC_DIR/ --type yaml --type json

# Search by description
rg -i "create.*order\|order.*create" $API_SPEC_DIR/ --type yaml --type json

# Search specific HTTP method + path
rg "post.*orders\|/orders.*post" $API_SPEC_DIR/ --type yaml --type json -A 5

# List all endpoints (paths)
rg "^\s+/(api|v[0-9])" $API_SPEC_DIR/ --type yaml --type json
```

### Step 2 — Analyze Endpoint

When you find an endpoint, determine:

1. **HTTP method and path**: `POST /api/v1/orders`
2. **Description**: What the endpoint does
3. **Parameters**:
   - Path params: `/orders/{id}`
   - Query params: `?page=1&limit=20`
   - Headers: `Authorization`, `Content-Type`, custom headers
4. **Request body**: Schema, required fields, types, validation
5. **Response**: Status codes, response body schema
6. **Authentication**: What auth mechanism the endpoint requires
7. **Rate limiting**: If specified

### Step 3 — Extract Schema

```bash
# Find schema/model definition
rg "OrderRequest\|OrderResponse\|Order:" $API_SPEC_DIR/ -A 20

# Look for $ref references to schema
rg "\$ref.*Order" $API_SPEC_DIR/

# Find required fields
rg "required:" $API_SPEC_DIR/ -A 10
```

## Reading OpenAPI 3.x Specification

### OpenAPI File Structure

```yaml
openapi: "3.0.0"
info:
  title: My API
  version: "1.0"
servers:
  - url: https://api.example.com/v1
paths:
  /orders:
    get:
      summary: List orders
      operationId: listOrders
      parameters: [...]
      responses:
        '200':
          description: Success
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/OrderList'
    post:
      summary: Create order
      operationId: createOrder
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/CreateOrderRequest'
      responses:
        '201':
          description: Created
        '422':
          description: Validation error
components:
  schemas:
    Order:
      type: object
      required: [id, name, status]
      properties:
        id:
          type: integer
        name:
          type: string
          maxLength: 200
        status:
          type: string
          enum: [pending, active, completed, cancelled]
  securitySchemes:
    bearerAuth:
      type: http
      scheme: bearer
```

### What to Focus On

| Section | What to Look For |
|---------|------------------|
| `paths` | All endpoints, methods, parameters |
| `parameters` | Path, query, header parameters; `required: true` |
| `requestBody` | Schema, content type, required field |
| `responses` | Status codes, response schemas, error responses |
| `components/schemas` | Data models, types, validation, enum values |
| `security` | Global and per-endpoint auth requirements |
| `servers` | Base URL for different environments |

## Reading Swagger 2.0 Specification

### Key Differences from OpenAPI 3.x

| Swagger 2.0 | OpenAPI 3.x |
|-------------|-------------|
| `swagger: "2.0"` | `openapi: "3.0.x"` |
| `host` + `basePath` | `servers[].url` |
| `definitions` | `components/schemas` |
| `parameters` (body) | `requestBody` |
| `produces/consumes` | `content` in request/response |

## Mapping Ticket to Endpoint

When you receive a Jira ticket, follow this process:

### 1. Identify Endpoint from Ticket

Look for in ticket:
- URL / endpoint path
- HTTP method
- Service / module name
- API operation name
- Error message (may contain path)
- Screenshot (may contain URL)

### 2. Verify Against Specification

```bash
# Search for endpoint
rg "/endpoint-from-ticket" $API_SPEC_DIR/

# If endpoint is NOT in specification → STOP AND ASK
# Never invent endpoints!
```

### 3. Map Dependencies

- Does endpoint require authentication? → Need login request as precondition
- Does endpoint require existing data? → Need setup (create entity)
- Does it depend on another service? → Verify availability

## Authentication Analysis

```
# Project uses OAuth2 PKCE (JWT Bearer tokens)
# For testing, /auth/test-token endpoint is available (dev only!)

# Test Token (development only):
POST {{base_url}}/auth/test-token
Content-Type: application/json

{
  "username": "test_courier",
  "role": "courier",      # user | courier | admin
  "user_id": 5,
  "scopes": "orders:read orders:write"
}

Response:
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}

# Token usage:
Authorization: Bearer {{access_token}}

# CSRF (optional, only when FORCE_HTTPS=true):
GET {{base_url}}/auth/csrf-token
Response: { "csrf_token": "..." }
Header: X-CSRF-Token: {{csrf_token}}

# PKCE Flow (production):
1. GET {{auth_url}}/authorize?client_id=mobile-app&redirect_uri=myapp://callback&response_type=code&code_challenge=<challenge>&code_challenge_method=S256&scope=orders:read
2. POST {{auth_url}}/token (code + code_verifier)
3. Authorization: Bearer {{access_token}}

# Token validity:
- Access token: 30 minutes (ACCESS_TOKEN_EXPIRE_MINUTES)
- Auth code: 10 minutes (AUTH_CODE_EXPIRE_SECONDS)

# Roles and scopes:
| Role | Default scopes |
|------|----------------|
| user/customer | orders:read |
| courier | orders:read orders:write |
| admin | orders:read orders:write orders:admin |
```

## Response Code Analysis

### Standard HTTP Status Codes

| Code | Meaning | What to Test |
|------|---------|--------------|
| 200 | OK | Happy path, correct data |
| 201 | Created | Newly created entity, ID in response |
| 204 | No Content | Successful deletion, empty body |
| 400 | Bad Request | Malformed request, missing required field |
| 401 | Unauthorized | Missing or invalid token |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Non-existent resource |
| 409 | Conflict | Duplicate entry, state doesn't allow operation |
| 422 | Unprocessable Entity | Validation errors |
| 429 | Too Many Requests | Rate limiting |
| 500 | Internal Server Error | Backend bug |
| 502 | Bad Gateway | Upstream service problem |
| 503 | Service Unavailable | Service unavailable |

### What to Look for in Error Responses

```bash
# Search for error response schema
rg "error\|Error\|ErrorResponse" $API_SPEC_DIR/ --type yaml --type json

# Typical error response structure:
# {
#   "error": "string",
#   "message": "string",
#   "details": [...],
#   "code": "string"
# }
```

## Test Type Identification

Based on ticket, determine what test is needed:

| Ticket Type | Test Type | What to Test |
|-------------|-----------|--------------|
| Bug fix | Fix verification | Reproduce bug → verify fix |
| New feature | Feature test | Happy path + edge cases |
| Regression | Regression test | Existing functionality not broken |
| Security | Security test | Auth, injection, permissions |
| Performance | Performance smoke | Response time, load |

## Common Patterns in API

### Pagination
```
GET /api/v1/orders?page=1&limit=20
Response: { data: [...], total: 100, page: 1, limit: 20 }
```

### Filtering
```
GET /api/v1/orders?status=active&created_after=2025-01-01
```

### Sorting
```
GET /api/v1/orders?sort=created_at&order=desc
```

### Nested Resources
```
GET /api/v1/orders/{order_id}/items
POST /api/v1/orders/{order_id}/items
```

## Checklist — What to Determine Before Testing

- [ ] Endpoint exists in specification
- [ ] HTTP method is correct
- [ ] Know required parameters (path, query, body)
- [ ] Know required auth mechanism
- [ ] Know expected response codes
- [ ] Know response body schema
- [ ] Know preconditions (existing data, system state)
- [ ] Know which environment to test on
- [ ] Have access to test data

## If Endpoint is Missing from Specification

**STOP.** Don't write test without verified specification.

Ask:
1. "Endpoint `POST /api/v1/xyz` is not in Swagger specification. Can you confirm
   the correct path and method?"
2. "I see `POST /api/v2/xyz` in specification, but ticket references v1.
   Which version is correct?"
3. "Specification doesn't have description for error response 422. What is the expected
   error response structure?"
