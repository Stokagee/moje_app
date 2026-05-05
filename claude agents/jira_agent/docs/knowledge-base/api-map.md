# API Map

> Overview of endpoints, methods, services.

## Base URL

| Environment | URL |
|-------------|-----|
| Local (Docker) | http://localhost:20300/api/v1 |
| Local (native) | http://localhost:8000/api/v1 |

## API Version

- v1: `/api/v1/...` (current)

## Services / Modules

### Auth (`/auth`)

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | /auth/csrf-token | Get CSRF token | None |
| GET | /auth/me | Info about logged-in user | Bearer |
| POST | /auth/logout | Logout user | Bearer + CSRF |
| POST | /auth/refresh | Refresh access token | Bearer (refresh) |
| POST | /auth/test-token | **[TEST ONLY]** Create test token | None |

### Orders (`/orders`)

| Method | Endpoint | Description | Auth | Role |
|--------|----------|-------------|------|------|
| GET | /orders/ | List orders | Bearer | user |
| GET | /orders/pending | Orders waiting for courier | Bearer | user |
| GET | /orders/by-status/{status} | Orders by status | Bearer | user |
| GET | /orders/{id} | Order detail | Bearer | user |
| POST | /orders/ | Create order | Bearer | user |
| POST | /orders/{id}/pickup | Mark as picked up | Bearer | courier |
| POST | /orders/{id}/deliver | Mark as delivered | Bearer | courier |
| POST | /orders/{id}/cancel | Cancel order | Bearer | user |
| PATCH | /orders/{id}/status | Change status (admin) | Bearer | admin |
| DELETE | /orders/{id} | Delete order | Bearer | admin |

### Dispatch (`/dispatch`)

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | /dispatch/auto/{order_id} | Automatic dispatch | None |
| POST | /dispatch/manual | Manual dispatch | None |
| GET | /dispatch/available-couriers/{order_id} | List available couriers | None |
| GET | /dispatch/logs/order/{order_id} | Dispatch history for order | None |
| GET | /dispatch/logs/courier/{courier_id} | Dispatch history for courier | None |

### Couriers (`/couriers`)

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | /couriers/ | List couriers | None |
| GET | /couriers/{id} | Courier detail | None |
| POST | /couriers/ | Create courier | None |
| PATCH | /couriers/{id}/status | Change courier status | None |
| PATCH | /couriers/{id}/location | Update GPS location | None |

### Form Data (`/form`)

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | /form/ | List forms | None |
| GET | /form/{id} | Form detail | None |
| POST | /form/ | Create form | None |
| DELETE | /form/{id} | Delete form | None |
| POST | /form/evaluate-name | Evaluate name (easter egg) | None |

### Logs (`/logs`)

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | /logs/ | List logs | None |

## Order Status Values

| Status | Description |
|--------|-------------|
| `CREATED` | Newly created, waiting for dispatch |
| `SEARCHING` | Looking for courier |
| `ASSIGNED` | Courier assigned |
| `PICKED` | Picked up by courier |
| `DELIVERED` | Delivered (terminal) |
| `CANCELLED` | Cancelled (terminal) |

## Courier Status Values

| Status | Description |
|--------|-------------|
| `available` | Available for assignment |
| `busy` | On an order |
| `offline` | Offline |

## Roles

| Role | Permissions |
|------|-------------|
| `user` / `customer` | Read own orders |
| `courier` | Pick up/deliver assigned orders |
| `admin` | Full access, delete, status update |

## Bruno Collections

```
bruno/collections/
├── orders-flow/           # Main flow tests
│   ├── 00a-get-admin-token.bru
│   ├── 00b-get-courier-token.bru
│   ├── 00c-get-customer-token.bru
│   ├── 10-create-order.bru
│   ├── 20-flow-create.bru
│   ├── 21-flow-dispatch.bru
│   ├── 22-flow-pickup.bru
│   ├── 23-flow-deliver.bru
│   └── ...
├── security-learning/     # Security tests
│   ├── Get CSRF Token.bru
│   ├── Get PKCE Token.bru
│   └── ...
└── test-simple/           # Simple tests
```

## Notes

- All POST/PUT/DELETE operations should include CSRF token (when `FORCE_HTTPS=true`)
- Test token endpoint (`/auth/test-token`) is for development/testing only
- Dispatch endpoints have no auth (internal service)
