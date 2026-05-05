# Business Rules

> Business rules for validation — what is and isn't allowed.

## Order

### Validation

| Field | Type | Required | Validation | Default |
|-------|------|----------|------------|---------|
| customer_name | string | Yes | min 1 character | - |
| customer_phone | string | Yes | phone format | - |
| pickup_address | string | Yes | min 1 character | - |
| pickup_lat | float | Yes | -90 to 90 | - |
| pickup_lng | float | Yes | -180 to 180 | - |
| delivery_address | string | Yes | min 1 character | - |
| delivery_lat | float | Yes | -90 to 90 | - |
| delivery_lng | float | Yes | -180 to 180 | - |
| is_vip | boolean | No | true/false | false |
| required_tags | array | No | list of strings | [] |

### State Transitions

```
CREATED ──► SEARCHING ──► ASSIGNED ──► PICKED ──► DELIVERED
    │           │            │            │
    └───────────┴────────────┴────────────┴──► CANCELLED
```

| Transition | Trigger | Conditions | Side Effect |
|------------|---------|------------|-------------|
| CREATED → SEARCHING | auto dispatch fail | - | - |
| CREATED/SEARCHING → ASSIGNED | dispatch success | courier available | courier → busy |
| ASSIGNED → PICKED | pickup endpoint | only assigned courier | - |
| PICKED → DELIVERED | deliver endpoint | only assigned courier | courier → available |
| * → CANCELLED | cancel endpoint | not DELIVERED/CANCELLED | courier → available (if assigned) |

### Terminal States

- `DELIVERED` - cannot be changed further
- `CANCELLED` - cannot be changed further

### Ownership Rules

| Operation | Who Can |
|------------|---------|
| pickup | courier with `order.courier_id == user_id` or admin |
| deliver | courier with `order.courier_id == user_id` or admin |
| cancel | any authenticated user |
| delete | admin only |

## Courier

### Validation

| Field | Type | Required | Validation | Default |
|-------|------|----------|------------|---------|
| name | string | Yes | min 1 character | - |
| phone | string | Yes | phone format | - |
| email | string | Yes | valid email, unique | - |
| lat | float | No | -90 to 90 | null |
| lng | float | No | -180 to 180 | null |
| status | enum | No | available, busy, offline | offline |
| tags | array | No | list of strings | [] |

### State Transitions

```
offline ──► available ──► busy ──► available
    ▲           │           │
    └───────────┴───────────┘
```

| Transition | Trigger | Conditions |
|------------|---------|------------|
| offline → available | update status | - |
| available → busy | dispatch | assignment to order |
| busy → available | deliver / cancel | completion/cancellation of order |

## Dispatch

### Algorithm

1. **Candidate Filter**
   - `status = available`
   - has valid GPS location (lat, lng not null)

2. **Tag Matching**
   - if `order.required_tags` exists, courier must have **all** these tags

3. **VIP Priority**
   - if `order.is_vip = true`, prefer couriers with `vip` tag
   - if no VIP courier, use regular

4. **Phased Search (radius)**
   - Phase 1: 750 km from pickup
   - Phase 2: 1500 km from pickup (fallback)

5. **Selection**
   - closest to pickup location (Haversine)

### Dispatch Limitations

| Condition | Result |
|-----------|--------|
| order doesn't exist | success: false, "not found" |
| order status ≠ CREATED/SEARCHING | success: false, "cannot be dispatched" |
| no available courier | success: false, order → SEARCHING |
| courier doesn't have required tags | success: false |

## Idempotence

| Operation | Idempotent | Note |
|------------|------------|------|
| POST /orders/ | NO | creates new order |
| POST /orders/{id}/pickup | NO | changes state |
| POST /orders/{id}/deliver | NO | changes state |
| POST /orders/{id}/cancel | YES* | can only cancel once |
| DELETE /orders/{id} | YES | delete or 404 |
| POST /dispatch/auto/{id} | NO* | may assign different courier |
| POST /dispatch/manual | NO | manual assignment |

\* As long as order is in same state

## Limits

| Type | Value | Where |
|------|-------|-------|
| Pagination max | 1000 items | skip/limit params |
| Pagination default | 100 items | - |
| Dispatch radius | 750 / 1500 km | dispatch_service.py |
| Token expiration | 30 min | ACCESS_TOKEN_EXPIRE_MINUTES |
| Auth code expiration | 10 min | AUTH_CODE_EXPIRE_SECONDS |

## Specific Rules

### GPS Coordinates

- pickup/delivery lat/lng are **required** for order creation
- For dispatch, distance is calculated from pickup location
- Distance calculated using Haversine formula (spherical earth)

### Tags

- Courier tags: `["bike", "car", "vip", "fragile_ok", "fast"]`
- Order required_tags: must be subset of courier tags
- VIP orders prefer VIP couriers (but not required)

### Dispatch Log

Every dispatch is logged to `dispatch_logs` table:
- `auto_assigned` - automatic dispatch successful
- `manual_assigned` - manual dispatch by operator
- `auto_failed` - automatic dispatch failed

## Notes

- Status changes via PATCH /orders/{id}/status for admin only
- For regular operations use specific endpoints (pickup, deliver, cancel)
- Courier is automatically released after deliver or cancel
- Test token endpoint (`/auth/test-token`) only in development!
