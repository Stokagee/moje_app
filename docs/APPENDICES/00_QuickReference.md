# Quick Reference Guide

## Robot Framework

### Basic Syntax
```robotframework
*** Settings ***        # Libraries, metadata
*** Variables ***       # Variables
*** Test Cases ***      # Test definitions
*** Keywords ***        # Custom keywords
```

### Comments
```robotframework
# Single line comment
Log    Comment after keyword
```

### Variables
```robotframework
${scalar}=    Set Variable    value
@{list}=      Create List    item1    item2
&{dict}=      Create Dictionary    key=value
```

---

## Browser Library (UI Testing)

### Session Management
```robotframework
New Browser    chromium    headless=${True}
New Context    viewport={'width': 1920, 'height': 1080}
New Page    http://localhost:8081
Close Context
Close Browser
```

### Element Interaction
```robotframework
Fill Text    [data-testid="input"]    text
Click    [data-testid="button"]
Select Options By    [data-testid="select"]    label    Option
Upload File    [data-testid="upload"]    /path/to/file
```

### Waiting
```robotframework
Wait For Elements State    ${selector}    visible    timeout=10s
Wait For Elements State    ${selector}    hidden
Wait For Network Idle    timeout=30s
```

### Assertions
```robotframework
Get Text    ${selector}    ==    Expected Text
Get Url    *=    localhost:8081
Get Title    ==    Page Title
```

### Selectors
```robotframework
[data-testid="name"]          # Recommended
#id                            # ID
.class                         # Class
[name="field"]                  # Attribute
"Submit button"                 # Text
//button[@type="submit"]       # XPath
[data-testid^="list-"]          # Starts with
[data-testid$="-name"]          # Ends with
```

---

## Requests Library (API Testing)

### Session Management
```robotframework
Create Session    alias    http://localhost:8000/api/v1
Delete All Sessions
```

### HTTP Methods
```robotframework
${response}=    GET On Session    alias    /endpoint
${response}=    POST On Session    alias    /endpoint    json=${data}
${response}=    PUT On Session    alias    /endpoint    json=${data}
${response}=    PATCH On Session    alias    /endpoint    json=${data}
${response}=    DELETE On Session    alias    /endpoint
```

### Response Handling
```robotframework
${status}=      Set Variable    ${response.status_code}
${body}=        Set Variable    ${response.text}
${json}=        Evaluate    json.loads('${body}')    modules=json
${headers}=     Set Variable    ${response.headers}
```

### Assertions
```robotframework
Should Be Equal As Strings    ${status}    200
Should Be Equal    ${json}[field]    expected_value
Should Contain    ${json}[detail]    error message
```

---

## Database Library

### Connection Setup
```robotframework
# Basic connection
Connect To Database    psycopg2    ${DB_NAME}    ${USER}    ${PASS}    ${HOST}

# With port specified
Connect To Database    psycopg2    ${DB_NAME}    ${USER}    ${PASS}    ${HOST}    ${PORT}

# SUITE scope (recommended for multiple tests)
Suite Setup     Connect To Database    psycopg2    ${DB_NAME}    ${USER}    ${PASS}    ${HOST}
Suite Teardown  Disconnect From Database

# Always disconnect
Disconnect From Database
```

### Query Keywords
```robotframework
# Execute SELECT query
${result}=    Query    SELECT * FROM form_data WHERE id = ${form_id}

# Count rows
${count}=     Row Count    SELECT COUNT(*) FROM form_data

# Execute SQL without return (INSERT, UPDATE, DELETE)
Execute Sql String    INSERT INTO form_data (email) VALUES ('test@example.com')
Execute Sql Script    /path/to/script.sql

# Check if table exists
Table Must Exist    form_data
Table Must Exist In Database    form_data    moje_app
```

### Transaction Keywords
```robotframework
# Transaction control
Begin Transaction
Commit Transaction
Rollback Transaction

# Check transaction state
Transaction Is Committed
Transaction Is Rolled Back
```

### Data Verification
```robotframework
# Row count assertions
${count}=    Row Count    SELECT COUNT(*) FROM form_data WHERE email = '${email}'
Should Be Equal As Integers    ${count}    1

# Result access
${row}=    Get From List    ${result}    0
${email}=  Set Variable    ${row}[email]

# Verify field value
Should Be Equal    ${row}[first_name]    John
Should Be Equal    ${row}[email]    test@example.com

# Check if result exists
${row_count}=    Get Length    ${result}
Should Be True    ${row_count} > 0
```

### TRY/FINALLY Syntax (Robot Framework 5.0+)
```robotframework
*** Test Cases ***
Test With Guaranteed Cleanup
    Connect To Database    psycopg2    ${DB_NAME}    ${USER}    ${PASS}    ${HOST}

    TRY
        # Test code here
        ${result}=    Query    SELECT * FROM form_data
        Should Not Be Empty    ${result}

    EXCEPT    OperationalError
        # Handle database errors
        Log    Database error occurred: ${ERROR}

    ELSE
        # Runs if no exception
        Log    Query executed successfully

    FINALLY
        # ALWAYS executes - cleanup here
        Disconnect From Database
        Log    Cleanup complete
    END
```

### Database Best Practices Quick Reference

| Pattern | Good Practice | Example |
|---------|---------------|---------|
| **Connection** | Use SUITE scope | `Suite Setup     Connect To Database` |
| **Cleanup** | Use FINALLY block | `FINALLY    Disconnect From Database    END` |
| **Columns** | Select only needed | `SELECT id, email FROM form_data` |
| **Counting** | Use COUNT(*) | `Row Count    SELECT COUNT(*) FROM form_data` |
| **Timeouts** | Set statement timeout | `SET statement_timeout = 30000` |
| **Constants** | Use named variables | `${QUERY_TIMEOUT_S}=    30` |
| **Config** | Separate credentials | Use variables file |
| **Retry** | Connection retry logic | Loop with `max_attempts` |

### Database Anti-Patterns Quick Reference

| Anti-Pattern | ❌ BAD | ✅ GOOD |
|--------------|--------|---------|
| **Hardcoded credentials** | `Connect To Database    psycopg2    db    user    pass123` | `Connect To Database    psycopg2    ${DB_NAME}    ${DB_USER}    ${DB_PASS}    ${DB_HOST}` |
| **Magic numbers** | `Sleep    70` | `${QUERY_TIMEOUT_S}=    70` |
| **No cleanup** | Test ends without disconnect | `FINALLY    Disconnect From Database    END` |
| **SELECT \*** | `SELECT * FROM form_data` | `SELECT id, email FROM form_data` |
| **Count in code** | `${result}=    Query    SELECT * ...` `${count}=    Get Length    ${result}` | `${count}=    Row Count    SELECT COUNT(*) FROM form_data` |
| **Test dependencies** | Tests rely on data from previous tests | Each test creates own data |
| **Query in loop** | `FOR    ${id}    IN    @{ids}` `Query    ... WHERE id = ${id}` `END` | `Query    ... WHERE id IN (${id_list})` |

### Common SQL Patterns

#### SELECT Queries
```sql
-- All columns
SELECT * FROM form_data

-- Specific columns
SELECT id, first_name, email FROM form_data

-- With condition
SELECT * FROM form_data WHERE email = 'test@example.com'

-- Multiple conditions
SELECT * FROM form_data WHERE first_name = 'Jan' AND status = 'active'

-- Pattern matching
SELECT * FROM form_data WHERE email LIKE '%@example.com'

-- Ordering
SELECT * FROM form_data ORDER BY created_at DESC

-- Limit results
SELECT * FROM form_data LIMIT 10
```

#### JOIN Queries
```sql
-- INNER JOIN
SELECT f.*, a.filename
FROM form_data f
INNER JOIN attachments a ON f.id = a.form_data_id

-- LEFT JOIN (includes unmatched rows)
SELECT f.id, f.email, COUNT(a.id) as attachment_count
FROM form_data f
LEFT JOIN attachments a ON f.id = a.form_data_id
GROUP BY f.id, f.email
```

#### Aggregate Queries
```sql
-- Total count
SELECT COUNT(*) FROM form_data

-- Count with condition
SELECT COUNT(*) FROM form_data WHERE gender = 'male'

-- Group by
SELECT gender, COUNT(*) as count
FROM form_data
GROUP BY gender
ORDER BY count DESC

-- Multiple aggregates
SELECT
    COUNT(*) as total,
    COUNT(*) FILTER (WHERE status = 'active') as active,
    COUNT(*) FILTER (WHERE status = 'inactive') as inactive
FROM form_data
```

#### DELETE Operations
```sql
-- Delete specific record
DELETE FROM form_data WHERE id = ${form_id}

-- Delete by pattern
DELETE FROM form_data WHERE email LIKE '%@test.example.com'

-- Delete all (be careful!)
DELETE FROM form_data

-- Delete with subquery
DELETE FROM attachments
WHERE form_data_id IN (SELECT id FROM form_data WHERE email = 'test@example.com')
```

### Error Handling Patterns

```robotframework
# Connection retry
Connect With Retry
    [Arguments]    ${max_attempts}=3    ${retry_delay_s}=2
    FOR    ${attempt}    IN RANGE    ${max_attempts}
        TRY
            Connect To Database    psycopg2    ${DB_NAME}    ${DB_USER}    ${DB_PASS}    ${DB_HOST}
            ${result}=    Query    SELECT 1
            RETURN
        EXCEPT    OperationalError
            IF    ${attempt} < ${max_attempts} - 1
                Sleep    ${retry_delay_s}s
            END
        END
    END
    Fail    Could not connect after ${max_attempts} attempts

# Query with timeout
Query With Timeout
    [Arguments]    ${query}    ${timeout_s}=30
    Execute Sql String    SET statement_timeout = ${timeout_s * 1000}
    TRY
        ${result}=    Query    ${query}
        [Return]    ${result}
    EXCEPT    OperationalError
        Fail    Query timed out after ${timeout_s}s
    FINALLY
        Execute Sql String    SET statement_timeout = 0
    END
```

### Performance Tips

```robotframework
# ✅ GOOD: Select specific columns
${result}=    Query    SELECT id, email FROM form_data WHERE id = ${form_id}

# ❌ BAD: Select all columns
${result}=    Query    SELECT * FROM form_data WHERE id = ${form_id}

# ✅ GOOD: Use LIMIT
${result}=    Query    SELECT id FROM form_data LIMIT 100

# ✅ GOOD: Use COUNT for existence
${count}=    Row Count    SELECT COUNT(*) FROM form_data WHERE email = '${email}'

# ❌ BAD: Get all rows just to count
${result}=    Query    SELECT * FROM form_data WHERE email = '${email}'
${count}=    Get Length    ${result}

# ✅ GOOD: Single query with IN
${id_list}=    Evaluate    ','.join(map(str, ${form_ids}))    modules=string
${result}=    Query    SELECT * FROM form_data WHERE id IN (${id_list})

# ❌ BAD: Query in loop
FOR    ${form_id}    IN    @{form_ids}
    ${result}=    Query    SELECT * FROM form_data WHERE id = ${form_id}
END
```

### Connection Scope Comparison

| Scope | Setup | Use When | Example |
|-------|-------|----------|---------|
| **SUITE** | `Suite Setup/Teardown` | Multiple tests, shared connection | Most test suites |
| **TEST** | `Test Setup/Teardown` | Isolated state needed | Transactions, parallel tests |

### Cleanup Strategies

```robotframework
# Teardown cleanup
*** Settings ***
Test Teardown    Clean Up Test Data

*** Keywords ***
Clean Up Test Data
    Execute Sql String    DELETE FROM form_data WHERE email LIKE '%@test.example.com'

# FINALLY cleanup (guaranteed)
*** Test Cases ***
Test With Cleanup
    Connect To Database
    TRY
        # Test code
    FINALLY
        Disconnect From Database
    END

# Suite cleanup
*** Settings ***
Suite Teardown    Clean Up Suite Data

*** Keywords ***
Clean Up Suite Data
    FOR    ${form_id}    IN    @{CREATED_IDS}
        Execute Sql String    DELETE FROM form_data WHERE id = ${form_id}
    END
```

---

## Common Patterns

### Test Setup/Teardown
```robotframework
*** Settings ***
Suite Setup     Log    Suite setup
Suite Teardown  Log    Suite teardown
Test Setup      Log    Test setup
Test Teardown   Log    Test teardown
```

### Tags
```robotframework
Force Tags      smoke    regression
Default Tags    sanity

*** Test Cases ***
My Test
    [Tags]    critical    form
    No Operation
```

### Run Tests
```bash
# Run all tests
robot tests/

# Run specific test
robot tests/my_test.robot

# Run by tag
robot --include smoke tests/

# Exclude tag
robot --exclude slow tests/

# Parallel execution
pabot --processes 4 tests/
```

---

## Status Codes

| Code | Meaning | Usage |
|------|---------|-------|
| 200 | OK | GET/PUT/PATCH success |
| 201 | Created | POST success |
| 204 | No Content | DELETE success |
| 400 | Bad Request | Invalid data |
| 404 | Not Found | Resource doesn't exist |
| 500 | Server Error | Server bug |

---

## Selectors Reference

| Type | Example | Use Case |
|------|---------|----------|
| data-testid | `[data-testid="name"]` | Recommended |
| ID | `#submit` | Stable IDs |
| Class | `.button` | May change |
| Attribute | `[type="submit"]` | Specific attributes |
| Text | `"Submit"` | Not recommended |
| XPath | `//button[@type="submit"]` | Complex cases |

---

## Application Quick Reference

### API Endpoints
```
GET    /api/v1/form/              # List all forms
POST   /api/v1/form/              # Create form
GET    /api/v1/form/{id}          # Get form by ID
DELETE /api/v1/form/{id}          # Delete form
```

### UI Selectors
```
[data-testid="firstName-input"]
[data-testid="lastName-input"]
[data-testid="email-input"]
[data-testid="phone-input"]
[data-testid="genderPicker"]
[data-testid="submitButton"]
```

### Database Tables
```
form_data (id, first_name, last_name, phone, gender, email)
attachments (id, form_data_id, filename, content, mime_type)
instructions (id, form_data_id, text)
```

---

## FakerLibrary Methods

```robotframework
${first}=   FakerLibrary.First Name
${last}=    FakerLibrary.Last Name
${email}=   FakerLibrary.Email
${phone}=   FakerLibrary.Phone Number
${address}= FakerLibrary.Address
${company}= FakerLibrary.Company
```

---

## Common Commands

### Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Start backend
cd be && uvicorn app.main:app --reload

# Start frontend
cd fe/mojeApp && npm run web

# Start database
docker compose up -d db
```

### Testing
```bash
# Run Robot Framework tests
robot tests/

# Run with output
robot --outputdir results/ tests/

# Run specific tags
robot --include smoke tests/

# Debug mode
robot --loglevel DEBUG tests/
```

---

## File Locations

### Frontend
- Pages: `/fe/mojeApp/src/component/pages/`
- Components: `/fe/mojeApp/src/component/common/`
- Test IDs defined in components

### Backend
- API: `/be/app/api/endpoints/`
- Models: `/be/app/models/`
- Config: `/be/app/core/config.py`

### Tests
- UI: `/RF/UI/`
- API: `/RF/API/`
- DB: `/RF/db/`

---

## Troubleshooting

### Browser Issues
- **Playwright not installed**: `playwright install chromium`
- **Port occupied**: Change browser port
- **Timeout**: Increase wait time

### API Issues
- **Connection refused**: Start backend server
- **404 errors**: Check endpoint path
- **400 errors**: Verify request data

### Database Issues
- **Connection failed**: Check DB credentials
- **Table not found**: Verify table name
- **Query errors**: Test SQL in DB client

---

## Tips

1. **Always use data-testid selectors** for stability
2. **Clean up test data** after each test
3. **Use FakerLibrary** for test data
4. **Take screenshots** on failures
5. **Use tags** for test organization
6. **Run tests in parallel** with pabot
7. **Verify API responses** in database
8. **Use explicit waits** instead of Sleep
9. **Log meaningful messages** for debugging
10. **Use TRY-EXCEPT** for error handling

---

## Resources

- [RF User Guide](https://robotframework.org/robotframework/latest/RobotFrameworkUserGuide.html)
- [Browser Library](https://marketsquare.github.io/robotframework-browser/Browser.html)
- [RequestsLibrary](https://github.com/arketii/robotframework-requests)
- [DatabaseLibrary](https://github.com/frank-rouvy/RobotFramework-Database-Library)
- [Playwright Docs](https://playwright.dev/docs/intro)
