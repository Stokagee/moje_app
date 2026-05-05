# Wrappers Reference

List of existing wrappers in the moje_app project.

## API Wrappers (common_api.resource)

### Create API Session

Creates API session for tests.

```robot
Create API Session    api    ${BASE_URL}
```

| Argument | Type | Description |
|----------|------|-------------|
| session_alias | string | Alias for session (usually "api") |
| base_url | string | Base URL of API server |
| timeout | string | Timeout (default: 30s) |

---

### API request

Universal wrapper for HTTP requests.

```robot
${api_create_user_response}=    API request
...    method=POST
...    url=/api/v1/users
...    body=${api_create_user_request_payload}
...    expected_status=anything
...    context_name=Create user
```

| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| method | string | Yes | GET, POST, PUT, DELETE |
| url | string | Yes | Endpoint URL (relative) |
| body | dict | No | Request body (for POST/PUT) |
| headers | dict | No | Additional headers |
| expected_status | string/int | No | Expected status (default: anything) |
| context_name | string | Yes | Context for error messages |

**Returns:** Response object with `.json()` and `.status_code`

---

## DB Wrappers (common_db.resource)

### Connect To Test Database

Connects to test database.

```robot
Connect To Test Database
```

Uses environment variables or defaults:
- `${DB_HOST}`: localhost
- `${DB_PORT}`: 5432
- `${DB_NAME}`: test_db
- `${DB_USER}`: postgres
- `${DB_PASSWORD}`: postgres

---

### Disconnect From Test Database

Disconnects from database.

```robot
Disconnect From Test Database
```

---

### Delete All Test Data

Deletes all rows from tables.

```robot
Delete All Test Data    users    orders    products
```

| Argument | Type | Description |
|----------|------|-------------|
| @{table_names} | strings | Table names to clean |

---

### Verify Row Count In Database

Verifies row count in query result.

```robot
Verify Row Count In Database
...    query=SELECT * FROM users WHERE email='test@test.com'
...    expected_count=1
...    operator===
...    context_name=Verify user exists
```

| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| query | string | Yes | SQL SELECT query |
| expected_count | int | Yes | Expected row count |
| operator | string | No | Comparison operator (==, !=, <, >, <=, >=) |
| context_name | string | Yes | Context for error messages |

---

### Verify Value In Database

Verifies specific value in database.

```robot
Verify Value In Database
...    query=SELECT * FROM users WHERE id=1
...    column_name=email
...    expected_value=test@test.com
...    context_name=Verify user email
```

| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| query | string | Yes | SQL SELECT query (must return 1 row) |
| column_name | string | Yes | Column name |
| expected_value | any | Yes | Expected value |
| context_name | string | Yes | Context for error messages |

---

## Usage Rules

### ALWAYS

1. Use wrappers instead of direct library calls
2. Include `context_name` for meaningful error messages
3. Use `expected_status=anything` and validate status manually

### NEVER

1. Don't call `POST On Session`, `GET On Session` directly
2. Don't call `Query`, `Execute Sql String` directly in tests
3. Don't duplicate wrapper logic

## Adding New Wrapper

If you need a new wrapper:

1. Verify similar one doesn't exist: `grep -r "keyword_name" tests/`
2. Propose signature in `/rf:keyword`
3. Wait for approval
4. Implement in appropriate resource file
