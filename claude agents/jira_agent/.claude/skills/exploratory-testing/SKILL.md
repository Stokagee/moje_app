# Exploratory Testing — SKILL.md

Load this skill for exploratory testing of an endpoint, when you need to
systematically explore API behavior beyond specification.

## When to Load This Skill

- `/explore [endpoint]` command
- When tester says "explore", "test", "verify behavior"
- New endpoint without existing tests
- After finding a bug — explore surrounding behavior

## What is Exploratory Testing

Structured exploration of API without predetermined test plan.
Goal: Find unexpected behavior, edge cases, security issues
and inconsistencies in API.

**It's not** random clicking. It's guided exploration with heuristics.

## Workflow

### 1. Understand Endpoint

Before testing, find out:
- What the endpoint does (from ticket, specification, knowledge base)
- What inputs and outputs it has
- What authentication it uses
- What business rules it has

### 2. Choose Techniques

Select 2–3 techniques from below based on context.

### 3. Test and Record

For each finding:
- What you tested (request)
- What you expected
- What happened
- Whether it's a bug or expected behavior

### 4. Report

Use format from bug-reporting SKILL.md for failures.
For overall summary:

```
🔍 EXPLORATORY: [endpoint]
Environment: [staging/local]
Techniques: [which you used]
Findings: [count] (X bugs, Y observations)
[list of findings]
```

## Techniques

### 1. Boundary Value Analysis

Test boundary values of input fields:

| Field Type | Test |
|------------|------|
| String | Empty `""`, 1 character, max length, max+1, very long (10000+ chars) |
| Number | 0, 1, -1, MAX_INT, MIN_INT, float where int expected, NaN |
| Array | Empty `[]`, 1 element, max elements, max+1 |
| Date | Past, today, future, invalid format, epoch 0 |
| Enum | Valid values, invalid value, empty value, case sensitivity |
| ID | Existing, non-existent, 0, negative, UUID vs int, max ID |

Example:
```
# String boundary — empty name
body:json { {"name": "", "amount": 100} }
# → Expect 422 with validation error

# String boundary — extremely long
body:json { {"name": "A repeated 10000 times...", "amount": 100} }
# → Expect 422 or success with truncation

# Number boundary — negative
body:json { {"name": "Test", "amount": -1} }
# → Expect 422

# Number boundary — zero
body:json { {"name": "Test", "amount": 0} }
# → Depends on business rules

# Number boundary — MAX
body:json { {"name": "Test", "amount": 99999999999} }
# → Expect 422 or overflow handling
```

### 2. Negative Testing

Test how API responds to invalid inputs:

```
# Missing required field
body:json { {"amount": 100} }
# → Expect 422 with info about missing field

# Wrong data type
body:json { {"name": 12345, "amount": "not-a-number"} }
# → Expect 422

# Invalid JSON
body:text { this is not json }
# → Expect 400

# Non-existent endpoint
GET /api/v1/nonexistent
# → Expect 404

# Wrong HTTP method
DELETE /api/v1/orders (on endpoint that only supports GET/POST)
# → Expect 405 Method Not Allowed

# Duplicate creation
POST /api/v1/orders (with same data 2x)
# → Depends on business rules — 409 Conflict or new record?
```

### 3. Authentication & Authorization Testing

```
# Without token
GET /api/v1/orders (without Authorization header)
# → Expect 401

# Invalid token
Authorization: Bearer invalid-token-12345
# → Expect 401

# Expired token
Authorization: Bearer <expired-token>
# → Expect 401

# Token of different user (access to others' data)
GET /api/v1/orders/{someone-elses-order-id}
# → Expect 403 or 404 (not 200 with someone else's data!)

# Low role on admin endpoint
POST /api/v1/admin/users (with user token)
# → Expect 403

# SQL injection in auth
body:json { {"username": "admin' OR '1'='1", "password": "x"} }
# → Expect 401 (not successful login!)
```

### 4. Injection Testing (Basic)

> **Note:** This is NOT a full penetration test. These are basic checks
> of whether API sanitizes inputs.

```
# SQL injection
body:json { {"name": "'; DROP TABLE orders; --"} }
# → Must not return DB error or affect data

# XSS
body:json { {"name": "<script>alert('xss')</script>"} }
# → Must not return unescaped HTML

# Path traversal
GET /api/v1/files/../../../etc/passwd
# → Expect 400 or 404

# Command injection
body:json { {"name": "; rm -rf /"} }
# → Must not execute command

# NoSQL injection (for MongoDB backends)
body:json { {"username": {"$gt": ""}, "password": {"$gt": ""}} }
# → Expect 400 or 401
```

### 5. Special Characters Testing

```
# Unicode / diacritics
body:json { {"name": "Řehoř Žluťoučký"} }
# → Must work correctly

# Emoji
body:json { {"name": "Test 🎉🚀"} }
# → Must either work or return understandable error

# Null bytes
body:json { {"name": "test\u0000null"} }
# → Must not cause crash

# Whitespace variations
body:json { {"name": "  leading spaces  "} }
body:json { {"name": "\ttab\nand\nnewlines"} }
# → Check trimming behavior
```

### 6. Response Consistency

```
# Same request → same response?
# Send identical request 3x and compare responses

# Pagination consistency
GET /api/v1/orders?page=1&limit=10
GET /api/v1/orders?page=2&limit=10
# → No duplicates between pages
# → Total count is consistent

# Sorting consistency
GET /api/v1/orders?sort=created_at&order=asc
GET /api/v1/orders?sort=created_at&order=desc
# → Opposite order

# Filter consistency
GET /api/v1/orders?status=active
# → All returned records have status=active
```

### 7. Performance Smoke

```
# Response time for single request
# → Under 1s for simple CRUD
# → Under 3s for complex operations

# Large payload
body:json { {"items": [... 1000 items ...]} }
# → Can it handle? Timeout? Memory error?

# Large response
GET /api/v1/orders?limit=10000
# → Can it handle? Is max limit enforced?
```

### 8. Idempotence Testing

```
# PUT should be idempotent (repeated call = same result)
PUT /api/v1/orders/123 (with same data 2x)
# → Both responses should be 200 with same result

# DELETE — second call
DELETE /api/v1/orders/123
DELETE /api/v1/orders/123
# → Second call should be 404 (or 204 if idempotent)

# POST — NOT idempotent
POST /api/v1/orders (with same data 2x)
# → Should create 2 records (or 409 Conflict)
```

## Heuristics — What to Think About

### CRUD Coverage
For each resource (orders, users, ...):
- **C**reate: Does creation work?
- **R**ead: Does reading work? Single + list?
- **U**pdate: Does update work? Partial (PATCH) and full (PUT)?
- **D**elete: Does deletion work? What happens to related records?

### Error Response Quality
- Does API return **understandable** error messages?
- Does error response contain **error code** for frontend?
- Does API NOT return **stack trace** or internal details in production?
- Are error responses **consistent** across endpoints?

### Data Integrity
- Is data the **same** after save and load? (Create → Read → compare)
- Does API preserve **encoding** (UTF-8)?
- Does **cascade** work correctly? (Delete parent → what about children?)

## Recording Findings

For each finding record:

```
### Finding [number]
- **Technique:** [Boundary / Negative / Auth / Injection / ...]
- **Request:** [METHOD /path + body]
- **Expected:** [what you expected]
- **Actual:** [what happened]
- **Severity:** [Critical / High / Medium / Low / Observation]
- **Type:** [Bug / Observation / Question]
```

**Observation** = interesting behavior, but not necessarily a bug (e.g., "API trims
whitespace" — might be intentional). Record for context.

**Question** = you're not sure if it's a bug. Need info
from developer or PM.

## What NOT to Test

- **Production environment** — never
- **Destructive operations on shared data** — unless isolated test data
- **Full penetration test** — that's security team's job
- **Load testing** — requires different tools (k6, JMeter, Artillery)
- **Endpoints not in specification** — ask first
