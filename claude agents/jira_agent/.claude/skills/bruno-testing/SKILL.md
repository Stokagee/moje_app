# Bruno Testing — SKILL.md

Load this skill whenever you create, modify, or run Bruno tests.

## Overview

Bruno is an open-source API client that stores requests as plain-text `.bru`
files. The format is Git-friendly and human-readable.

> **Note:** Bruno v3 now also supports OpenCollection YAML format.
> This skill covers the `.bru` format, which is still fully supported.

## Collection Structure

```
C:\Users\stoka\Documents\moje_app\bruno\collections\
├── orders-flow/                    # Main order flow tests
│   ├── environments/
│   │   └── Local.bru               # base_url, tokens, order_id, courier_id
│   ├── collection.bru
│   ├── 00a-get-admin-token.bru     # Get admin token
│   ├── 00b-get-courier-token.bru   # Get courier token
│   ├── 00c-get-customer-token.bru  # Get customer token
│   ├── 00d-create-test-courier.bru # Create test courier
│   ├── 00e-set-courier-location.bru# Set GPS location
│   ├── 00f-set-courier-available.bru# Set status available
│   ├── 10-create-order.bru         # Create order
│   ├── 11-get-all-orders.bru       # List orders
│   ├── 12-get-order-by-id.bru      # Order detail
│   ├── 20-flow-create.bru          # Flow: create order
│   ├── 21-flow-dispatch.bru        # Flow: auto dispatch
│   ├── 22-flow-pickup.bru          # Flow: pickup
│   ├── 23-flow-deliver.bru         # Flow: deliver
│   ├── 30-create-no-auth.bru       # Negative: no auth
│   ├── 30-error-no-auth.bru        # Negative: 401 test
│   ├── 31-error-invalid-data.bru   # Negative: invalid data
│   ├── 40-dispatch-auto.bru        # Auto dispatch
│   ├── 50-cancel-order.bru         # Cancel order
│   └── 60-admin-delete.bru         # Admin delete
├── security-learning/              # Security tests
│   ├── environments/
│   │   └── Local.bru               # base_url, auth_url, csrf_token
│   ├── collection.bru
│   ├── Get CSRF Token.bru
│   ├── Get PKCE Token.bru
│   ├── Token Exchange.bru
│   ├── Token From BE.bru
│   ├── Get Order Without Token.bru
│   ├── Create New Order.bru
│   ├── Delete Order.bru
│   └── ...
└── test-simple/
    └── test.bru
```

## Naming Convention

Name new tests according to this pattern:
```
TICKET-ID_short-description.bru
```

Examples:
- `PROJ-1234_post-orders-500-special-chars.bru`
- `PROJ-5678_get-users-unauthorized.bru`
- `PROJ-9012_delete-order-nonexistent-id.bru`

If test is not tied to a ticket:
- `get-all-orders.bru`
- `create-user-validation-error.bru`

## .bru Syntax — Complete Reference

### Meta Block (Required)

```
meta {
  name: Get All Orders
  type: http
  seq: 1
}
```

- `name`: Human-readable request name
- `type`: `http` or `graphql`
- `seq`: Order in UI (number)

### HTTP Methods

```
get {
  url: {{base_url}}/api/v1/orders
  body: none
  auth: bearer
}
```

```
post {
  url: {{base_url}}/api/v1/orders
  body: json
  auth: bearer
}
```

```
put {
  url: {{base_url}}/api/v1/orders/:id
  body: json
  auth: bearer
}
```

```
delete {
  url: {{base_url}}/api/v1/orders/:id
  body: none
  auth: bearer
}
```

Supported methods: `get`, `post`, `put`, `delete`, `patch`, `options`,
`head`, `trace`, `connect`

### Query Parameters

```
params:query {
  page: 1
  limit: 20
  sort: created_at
  ~debug: true
}
```

- `~` prefix = disabled (commented parameter)

### Path Parameters

```
params:path {
  id: {{order_id}}
}
```

### Headers

```
headers {
  Content-Type: application/json
  Authorization: Bearer {{auth_token}}
  X-Request-ID: {{request_id}}
  ~X-Debug: true
}
```

### Body — JSON

```
body:json {
  {
    "name": "Test Order",
    "amount": 100,
    "currency": "CZK",
    "items": [
      {
        "product_id": "abc-123",
        "quantity": 2
      }
    ]
  }
}
```

### Body — Form URL Encoded

```
body:form-urlencoded {
  username: johndoe
  password: secret123
  grant_type: password
}
```

### Body — Multipart Form

```
body:multipart-form {
  file: @/path/to/file.pdf
  description: Test document
}
```

### Body — Text / XML

```
body:text {
  Plain text body here
}
```

```
body:xml {
  <request>
    <name>Test</name>
  </request>
}
```

## Authentication

### Bearer Token

```
auth:bearer {
  token: {{auth_token}}
}
```

### Basic Auth

```
auth:basic {
  username: {{username}}
  password: {{password}}
}
```

## Assertions (Declarative Tests)

Assertions are simple, declarative checks. Use them for
basic validation. For complex logic use `tests {}` block.

```
assert {
  res.status: eq 200
  res.body.data: isDefined
  res.body.items: isArray
  res.body.count: gt 0
  res.body.name: eq "Test Order"
  res.body.email: contains "@"
  res.body.id: isNumber
  res.body.active: eq true
  res.headers.content-type: contains "application/json"
}
```

### Assertion Operators

| Operator      | Description                   | Example                           |
|---------------|-------------------------------|-----------------------------------|
| `eq`          | Equals                        | `res.status: eq 200`              |
| `neq`         | Not equals                    | `res.status: neq 500`             |
| `gt`          | Greater than                  | `res.body.count: gt 0`            |
| `gte`         | Greater or equal              | `res.body.count: gte 1`           |
| `lt`          | Less than                     | `res.body.count: lt 100`          |
| `lte`         | Less or equal                 | `res.body.count: lte 50`          |
| `in`          | In list                       | `res.status: in [200, 201]`       |
| `contains`    | Contains substring            | `res.body.name: contains "test"`  |
| `matches`     | Regex match                   | `res.body.code: matches "^[A-Z]"` |
| `isNull`      | Is null                       | `res.body.deleted: isNull`        |
| `isDefined`   | Is defined                    | `res.body.id: isDefined`          |
| `isUndefined` | Is undefined                  | `res.body.error: isUndefined`     |
| `isArray`     | Is array                      | `res.body.items: isArray`         |
| `isNumber`    | Is number                     | `res.body.id: isNumber`           |
| `isString`    | Is string                     | `res.body.name: isString`         |
| `isBoolean`   | Is boolean                    | `res.body.active: isBoolean`      |
| `isJson`      | Is valid JSON                 | `res.body: isJson`                |
| `length`      | Array/string length           | `res.body.items: length 5`        |

## Tests Block (JavaScript, Chai)

For complex validation use `tests {}` block with Chai assertion library.

```
tests {
  test("should return 200", function() {
    expect(res.status).to.equal(200);
  });

  test("should return array of orders", function() {
    expect(res.body.data).to.be.an('array');
    expect(res.body.data.length).to.be.greaterThan(0);
  });

  test("each order should have required fields", function() {
    res.body.data.forEach(order => {
      expect(order).to.have.property('id');
      expect(order).to.have.property('status');
      expect(order).to.have.property('created_at');
    });
  });

  test("should respond under 1 second", function() {
    expect(res.getResponseTime()).to.be.lessThan(1000);
  });
}
```

### Available Objects in Tests

- `res.status` — HTTP status code
- `res.body` — Response body (automatically parsed JSON)
- `res.headers` — Response headers
- `res.getResponseTime()` — Response time in ms
- `res.getHeader("name")` — Specific header value
- `res.getBody()` — Response body
- `res.getStatus()` — Status code
- `req.getUrl()` — Request URL
- `req.getMethod()` — HTTP method
- `req.getHeaders()` — Request headers
- `req.getBody()` — Request body

### Available Objects for Variables

- `bru.setVar("name", value)` — Set runtime variable
- `bru.getVar("name")` — Get runtime variable
- `bru.setEnvVar("name", value)` — Set environment variable
- `bru.getEnvVar("name")` — Get environment variable
- `bru.getProcessEnv("name")` — Get process environment variable
- `bru.cwd()` — Path to current collection

## Scripting

### Pre-request Script

```
script:pre-request {
  const timestamp = Date.now();
  const uniqueEmail = `test-${timestamp}@example.com`;
  bru.setVar("testEmail", uniqueEmail);

  req.setHeader("X-Request-ID", require('crypto').randomUUID());
}
```

### Post-response Script

```
script:post-response {
  // Save token for subsequent requests
  if (res.status === 200) {
    bru.setVar("auth_token", res.body.token);
    bru.setVar("user_id", res.body.user.id);
  }
}
```

## Environment Variables

Environment file (`.bru` format):
```
vars {
  base_url: https://api.staging.example.com
  api_version: v1
}

vars:secret [
  auth_token,
  client_secret
]
```

Usage in requests: `{{base_url}}`, `{{auth_token}}`

### Standard Variables for Project

```
# orders-flow/environments/Local.bru
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

# security-learning/environments/Local.bru
vars {
  base_url: http://localhost:20300/api/v1
  auth_url: http://localhost:5105
  access_token:
  csrf_token:
  admin_token:
  courier_token:
  customer_token:
  order_id:
  courier_id:
  flow_order_id:
  flow_courier_id:
}
```

## Request Chaining

For tests that depend on each other (e.g., login → create → delete):

```
# 1. login.bru — gets token
script:post-response {
  bru.setVar("auth_token", res.body.token);
}

# 2. create-order.bru — creates order, saves ID
script:post-response {
  bru.setVar("order_id", res.body.id);
}

# 3. get-order.bru — verifies created order
get {
  url: {{base_url}}/api/v1/orders/{{order_id}}
}
assert {
  res.status: eq 200
  res.body.id: eq {{order_id}}
}

# 4. delete-order.bru — deletes order
delete {
  url: {{base_url}}/api/v1/orders/{{order_id}}
}
assert {
  res.status: eq 204
}
```

## Bruno CLI

### Running Tests

```bash
# Run entire collection
bru run $BRUNO_DIR --env staging

# Run specific test
bru run $BRUNO_DIR/orders/create-order.bru --env staging

# Run folder
bru run $BRUNO_DIR/orders/ --env staging

# With variables from command line
bru run $BRUNO_DIR --env staging --env-var apiKey=abc123

# Verbose output
bru run $BRUNO_DIR --env staging --verbose

# Fail on error (for CI/CD — exit code != 0 on failure)
bru run $BRUNO_DIR --env staging --failOnError

# With report
bru run $BRUNO_DIR --env staging --output results.json
```

### CLI Output

```
Running Folder Recursively
  Create Order (201 Created) - 194 ms
    ✓ assert: res.status: eq 201
    ✓ assert: res.body.id: isDefined
  Get Order (200 OK) - 87 ms
    ✓ assert: res.status: eq 200
  Delete Order (204 No Content) - 62 ms
    ✓ assert: res.status: eq 204

Requests:   3 passed, 3 total
Tests:      0 passed, 0 total
Assertions: 5 passed, 5 total
Ran all requests - 343 ms
```

## Templates — Typical Tests

### Fix Verification (Ticket)

```
meta {
  name: PROJ-1234 Verify fix for 500 on special chars
  type: http
  seq: 1
}

post {
  url: {{base_url}}/api/v1/orders
  body: json
  auth: bearer
}

auth:bearer {
  token: {{auth_token}}
}

body:json {
  {
    "name": "Test <script>alert('xss')</script>",
    "description": "Description with diacritics: ěščřžýáíé"
  }
}

assert {
  res.status: eq 201
  res.body.id: isDefined
  res.body.name: isDefined
}

tests {
  test("should handle special characters without 500", function() {
    expect(res.status).to.not.equal(500);
    expect(res.status).to.be.oneOf([200, 201]);
  });

  test("should sanitize input", function() {
    expect(res.body.name).to.not.contain('<script>');
  });
}
```

### Negative Test (Unauthorized Access)

```
meta {
  name: GET orders without auth returns 401
  type: http
  seq: 1
}

get {
  url: {{base_url}}/api/v1/orders
  body: none
  auth: none
}

assert {
  res.status: eq 401
  res.body.error: isDefined
}
```

### Validation Error Test

```
meta {
  name: POST order with invalid data returns 422
  type: http
  seq: 1
}

post {
  url: {{base_url}}/api/v1/orders
  body: json
  auth: bearer
}

auth:bearer {
  token: {{auth_token}}
}

body:json {
  {
    "name": "",
    "amount": -1,
    "email": "not-an-email"
  }
}

assert {
  res.status: eq 422
  res.body.errors: isArray
}

tests {
  test("should return validation errors", function() {
    expect(res.body.errors.length).to.be.greaterThan(0);
  });
}
```

## Best Practices

1. **Always add assertions** — never send request without them
2. **Test happy path and error path** — 200 and 400/401/404/422/500
3. **Use environment variables** — never hardcode URLs or tokens
4. **Name tests clearly** — name = what is being tested
5. **Keep tests atomic** — one test = one thing
6. **Version in Git** — `.bru` files are plain text
7. **Use `assert {}` for simple checks**, `tests {}` for
   complex validation
8. **Never modify existing tests without instruction** from tester
9. **Response time** — add assertion for response time on critical
   endpoints

## Where to Save New Tests

```
# Path to Bruno collections:
BRUNO_DIR=C:\Users\stoka\Documents\moje_app\bruno\collections

# Save to correct folder by test type:

# Order flow (main tests):
C:\Users\stoka\Documents\moje_app\bruno\collections\orders-flow\
- NAMING: XX-action-description.bru (XX = order)
- Example: 32-flow-cancel-order.bru, 40-dispatch-auto.bru

# Security tests:
C:\Users\stoka\Documents\moje_app\bruno\collections\security-learning\
- NAMING: Description-action.bru
- Example: Get CSRF Token.bru, Create New Order.bru

# For ticket tests add ticket ID at start:
- PROJ-1234_fix-special-chars.bru
- PROJ-5678_verify-auth-bypass.bru
```

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `bru: command not found` | `npm install -g @usebruno/cli` |
| Environment variable not working | Verify it's defined in environment file |
| Assertion `res.body.x` is undefined | Check response body — structure might be different |
| Test passes locally, fails on CI | Check environment and auth tokens |
| Timeout | Add `--timeout` flag or check connectivity |
