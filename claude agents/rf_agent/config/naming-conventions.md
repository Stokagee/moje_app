# Naming Conventions

Complete convention for naming variables, files and tests.

## Variables

### Basic Rule

Variable name must at first glance say:
- **What it contains** (entity)
- **Where it comes from** (source)
- **What it's for** (purpose)

### Recommended Format

```
${<role>_<domain>_<entity>_<purpose>}
```

### API Variables

| Pattern | Example | Description |
|---------|---------|-------------|
| `${api_<action>_<entity>_request_payload}` | `${api_create_user_request_payload}` | Request body |
| `${api_<action>_<entity>_response}` | `${api_create_user_response}` | Response object |
| `${api_<action>_<entity>_response_body}` | `${api_create_user_response_body}` | Response JSON |
| `${api_<action>_<entity>_response_status}` | `${api_create_user_response_status}` | Status code |

### DB Variables

| Pattern | Example | Description |
|---------|---------|-------------|
| `${db_<entity>_from_database}` | `${db_user_from_database}` | Query result |
| `${db_<entity>_<purpose>}` | `${db_created_user_record}` | Specific record |
| `${db_<entity>_expected_<property>}` | `${db_user_expected_row_count}` | Expected value |

### With Role (for multi-user tests)

```
${admin_api_create_user_response}
${customer_api_get_orders_response}
${courier_api_update_order_response}
```

### Constants

```
${BASE_URL}
${DEFAULT_TIMEOUT_SECONDS}
${API_TOKEN}
${DB_HOST}
```

### Local Variables (in keywords)

```
${user_id}
${created_order_id}
${expected_customer_name}
${context_name}
```

## FORBIDDEN Names

These names are strictly forbidden:

```
${data}       ❌  Too generic
${response}   ❌  Unclear context
${result}     ❌  Unclear context
${item}       ❌  Unclear context
${row}        ❌  Unclear context
${value}      ❌  Unclear context
${temp}       ❌  Unclear context
${test_data}  ❌  Too generic
```

## Test Case Names

### Format

```
<Feature> - <Scenario> - <Expected Outcome>
```

### Examples

```
✅ Users - Create Valid User - Returns 201 And User ID
✅ Users - Create Duplicate Email - Returns 409 Conflict
✅ Orders - Get By ID Non-Existent - Returns 404 Not Found
✅ Auth - Login Invalid Password - Returns 401 Unauthorized

❌ Test create user           (too generic)
❌ Create user test           (without expected outcome)
❌ User creation              (without scenario detail)
```

## Keyword Names

### Rules

1. **English** (code is in English)
2. **Action-oriented** (what it does, not what it is)
3. **Unambiguous** (no abbreviations)

### Examples

```
✅ Create User Via API
✅ Get User By ID
✅ Delete User By ID
✅ Verify User Exists In Database
✅ Prepare Test Environment

❌ CreateUser              (missing space, context)
❌ get_user               (lowercase)
❌ Do The Thing           (unclear)
❌ Helper                 (not action-oriented)
```

## File Names

### Test Files

```
<feature>_<action>.robot

Examples:
✅ users_crud.robot
✅ orders_create.robot
✅ auth_login.robot

❌ test1.robot            (without context)
❌ UsersTests.robot       (inconsistent case)
```

### Resource Files

```
<feature>_api.resource      (for API keywords)
<feature>_db.resource       (for DB keywords)
common_<domain>.resource    (for shared keywords)

Examples:
✅ users_api.resource
✅ orders_db.resource
✅ common_api.resource
```

## Tags

### Categories

```
api       - API tests
ui        - UI tests
db        - Database tests
e2e       - End-to-end tests
```

### Domains

```
users     - User management
orders    - Order processing
auth      - Authentication
payments  - Payment processing
```

### Types

```
positive  - Happy path
negative  - Error scenarios
smoke     - Critical tests
regression - Regression tests
```

### Examples

```robot
[Tags]    api    users    create    positive
[Tags]    api    auth    login    negative
[Tags]    e2e    checkout    smoke
```
