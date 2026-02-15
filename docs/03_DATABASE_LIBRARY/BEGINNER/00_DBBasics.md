# Database Testing Basics

## Learning Objectives
- [ ] Understand database testing concepts
- [ ] Connect to PostgreSQL database
- [ ] Execute simple queries
- [ ] Verify data in database

## Prerequisites
- Completed GETTING_STARTED
- PostgreSQL installed/running

---

## What is Database Testing?

**Database testing** verifies:
- Data is stored correctly
- Queries return expected results
- Data integrity is maintained
- Database operations work as expected

**Why test the database?**
- Verify API persistence
- Check data integrity
- Validate business rules at data level
- Find data corruption issues

---

## Database Library Setup

### Install Database Library

```bash
pip install robotframework-databaselibrary
```

### Install Database Driver

```bash
# For PostgreSQL
pip install psycopg2-binary

# For MySQL
pip install pymysql

# For Oracle
pip install cx_Oracle
```

---

## Connection Setup

### Basic Connection

```robotframework
*** Settings ***
Library     DatabaseLibrary

*** Variables ***
${DB_MODULE}           psycopg2
${DB_NAME}             moje_app
${DB_USER}             postgres
${DB_PASSWORD}         postgres
${DB_HOST}             localhost
${DB_PORT}             5432

*** Test Cases ***
Connect To Database
    # Connect to database
    Connect To Database
    ...    ${DB_MODULE}
    ...    db_name=${DB_NAME}
    ...    db_user=${DB_USER}
    ...    db_password=${DB_PASSWORD}
    ...    db_host=${DB_HOST}
    ...    db_port=${DB_PORT}

    # Verify connection
    ${result}=    Query    SELECT 1

    # Disconnect
    Disconnect From Database
```

### Connection with Config File

```robotframework
# In variables.resource
${DB_API}=    psycopg2
${DB_NAME}=  moje_app
${DB_USER}=  postgres
${DB_PASS}=  postgres
${DB_HOST}=  localhost

*** Keywords ***
Connect To Test Database
    Connect To Database    ${DB_API}    ${DB_NAME}    ${DB_USER}    ${DB_PASS}    ${DB_HOST}
    Log    Connected to database: ${DB_NAME}
```

---

## Simple Queries

### SELECT Query

```robotframework
*** Test Cases ***
Query Form Data
    Connect To Database    psycopg2    moje_app    postgres    postgres    localhost

    # Execute query
    ${result}=    Query    SELECT * FROM form_data

    # Log results
    Log    Query returned ${result} rows

    # Disconnect
    Disconnect From Database
```

### COUNT Query

```robotframework
*** Test Cases ***
Count Forms In Database
    Connect To Database    psycopg2    moje_app    postgres    postgres    localhost

    # Count records
    ${count}=    Row Count    SELECT COUNT(*) FROM form_data

    Log    Total forms in database: ${count}

    Disconnect From Database
```

### Query With Conditions

```robotframework
*** Test Cases ***
Query Specific Form
    Connect To Database    psycopg2    moje_app    postgres    postgres    localhost

    # Query specific record
    ${result}=    Query    SELECT * FROM form_data WHERE email = 'test@example.com'

    # Verify result
    ${row_count}=    Get Length    ${result}
    Should Be Equal As Integers    ${row_count}    1

    Disconnect From Database
```

---

## Data Verification

### Verify Data Exists

```robotframework
*** Keywords ***
Verify Form Exists In Database
    [Arguments]    ${email}

    ${result}=    Query    SELECT id FROM form_data WHERE email = '${email}'
    ${count}=    Get Length    ${result}

    Should Be True    ${count} > 0    msg=No form found with email ${email}
```

### Verify Data Values

```robotframework
*** Keywords ***
Verify FormData
    [Arguments]    ${email}    &{expected_data}

    ${result}=    Query
    ...    SELECT first_name, last_name, phone FROM form_data
    ...    WHERE email = '${email}'

    ${row}=    Get From List    ${result}    0

    # Verify each field
    FOR    ${key}    IN    @{expected_data.keys}
        ${actual}=    Get From Dictionary    ${row}    ${key}
        ${expected}=    Get From Dictionary    ${expected_data}    ${key}
        Should Be Equal    ${actual}    ${expected}    msg=Field ${key} mismatch
    END
```

### Verify Record Count

```robotframework
*** Keywords ***
Verify Record Count
    [Arguments]    ${table}    ${expected_count}    ${where}=${EMPTY}

    ${where_clause}=    Set Variable If    '${where}' == ${EMPTY}    ${EMPTY}    WHERE ${where}

    ${query}=    Set Variable    SELECT COUNT(*) FROM ${table} ${where_clause}
    ${count}=    Row Count    ${query}

    Should Be Equal As Integers    ${count}    ${expected_count}
```

---

## Application Examples

### Example 1: Verify Form Created

```robotframework
*** Test Cases ***
Verify Form Created In Database
    [Documentation]    Verify API call created record in DB

    # Setup: Create form via API
    Create Session    api    http://localhost:8000/api/v1

    &{data}=    Create Dictionary
    ...    first_name=DB
    ...    last_name=Test
    ...    phone=+420123456789
    ...    gender=male
    ...    email=db-test@example.com

    ${response}=    POST On Session    api    /form/    json=${data}
    ${json}=    Evaluate    json.loads('${response.text}')    modules=json
    ${form_id}=    Set Variable    ${json}[id]

    # Verify in database
    Connect To Database    psycopg2    moje_app    postgres    postgres    localhost

    # Query the record
    ${result}=    Query
    ...    SELECT first_name, last_name, email FROM form_data
    ...    WHERE id = ${form_id}

    # Verify data
    ${row}=    Get From List    ${result}    0
    Should Be Equal    ${row}[first_name]    DB
    Should Be Equal    ${row}[last_name]     Test
    Should Be Equal    ${row}[email]         db-test@example.com

    # Cleanup
    Disconnect From Database
    DELETE On Session    api    /form/${form_id}
```

### Example 2: Count Records

```robotframework
*** Test Cases ***
Count Forms By Name
    [Documentation]    Count forms with specific name

    Connect To Database    psycopg2    moje_app    postgres    postgres    localhost

    # Count forms with first_name = 'Jan'
    ${count}=    Row Count    SELECT COUNT(*) FROM form_data WHERE first_name = 'Jan'

    Log    Found ${count} forms with first_name 'Jan'

    # Verify count is non-negative
    Should Be True    ${count} >= 0

    Disconnect From Database
```

### Example 3: Verify Data After Delete

```robotframework
*** Test Cases ***
Verify Delete Removes From Database
    [Documentation]    Verify DELETE API removes DB record

    # Setup: Create form
    Create Session    api    http://localhost:8000/api/v1

    &{data}=    Create Dictionary
    ...    first_name=Delete
    ...    last_name=Me
    ...    phone=+420123456789
    ...    gender=male
    ...    email=delete-me@example.com

    ${create_resp}=    POST On Session    api    /form/    json=${data}
    ${json}=    Evaluate    json.loads('${create_resp.text}')    modules=json
    ${form_id}=    Set Variable    ${json}[id]

    # Verify exists before delete
    Connect To Database    psycopg2    moje_app    postgres    postgres    localhost

    ${before_count}=    Row Count    SELECT COUNT(*) FROM form_data WHERE id = ${form_id}
    Should Be Equal As Integers    ${before_count}    1

    # Delete via API
    DELETE On Session    api    /form/${form_id}

    # Verify removed from database
    ${after_count}=    Row Count    SELECT COUNT(*) FROM form_data WHERE id = ${form_id}
    Should Be Equal As Integers    ${after_count}    0

    Disconnect From Database
```

---

## Common SQL Queries

### SELECT Patterns

```robotframework
# All columns
SELECT * FROM form_data

# Specific columns
SELECT id, first_name, email FROM form_data

# With condition
SELECT * FROM form_data WHERE email = 'test@example.com'

# Multiple conditions
SELECT * FROM form_data WHERE first_name = 'Jan' AND last_name = 'Novák'

# Ordering
SELECT * FROM form_data ORDER BY created_at DESC

# Limit results
SELECT * FROM form_data LIMIT 10

# Pattern matching
SELECT * FROM form_data WHERE email LIKE '%@example.com'
```

### JOIN Queries

```robotframework
# Inner join orders with couriers
SELECT o.*, c.name as courier_name
FROM orders o
INNER JOIN couriers c ON o.courier_id = c.id
WHERE o.status = 'ASSIGNED'
```

### COUNT Queries

```robotframework
# Total count
SELECT COUNT(*) FROM form_data

# Count with condition
SELECT COUNT(*) FROM form_data WHERE gender = 'male'

# Count distinct values
SELECT COUNT(DISTINCT email) FROM form_data
```

---

## Common Pitfalls

| Pitfall | Why It Happens | Fix |
|---------|---------------|-----|
| Connection refused | Database not running | Start PostgreSQL/Docker |
| Authentication failed | Wrong credentials | Check DB_USER/DB_PASSWORD |
| Table not found | Wrong table name | Verify schema |
| SQL syntax error | Invalid SQL | Test query in DB client first |

---

## Best Practices

1. **Always disconnect after test:**
   ```robotframework
   [Teardown]    Disconnect From Database
   ```

2. **Use connection in Setup:**
   ```robotframework
   Suite Setup     Connect To Database    ...
   Suite Teardown  Disconnect From Database
   ```

3. **Clean up test data:**
   ```robotframework
   DELETE FROM form_data WHERE email LIKE '%@test.example.com'
   ```

4. **Verify connection before queries:**
   ```robotframework
   ${result}=    Query    SELECT 1
   ```

---

## Self-Check Questions

1. How do you connect to PostgreSQL database?
2. What's the keyword to execute SQL query?
3. How do you verify record count?
4. Why disconnect from database?

---

## Exercise: Database Verification

**Task:** Create a test that verifies API data persistence in database.

**Scenario:**
1. Create form via API
2. Verify data in database
3. Update via API
4. Verify update in database
5. Delete via API
6. Verify removal from database

**Acceptance Criteria:**
- [ ] All CRUD operations verified in DB
- [ ] Proper connection setup/teardown
- [ ] Data integrity verified

**Starter Code:**
```robotframework
*** Settings ***
Library     RequestsLibrary
Library     DatabaseLibrary

*** Variables ***
${BASE_URL}    http://localhost:8000/api/v1
${DB_NAME}    moje_app

*** Test Cases ***
Verify API Persistence In Database
    [Documentation]    TODO: Implement DB verification
    # TODO: Your code here

*** Keywords ***
# TODO: Add helper keywords
```

---

## Hints

### Hint 1
Flow: Connect → Create (API) → Verify (DB) → Delete (API) → Verify (DB) → Disconnect

### Hint 2
Use the form_id from API response for database queries.

### Hint 3
```robotframework
Verify API Persistence In Database
    # Setup database
    Connect To Database    psycopg2    ${DB_NAME}    postgres    postgres    localhost

    # Create via API
    # TODO: Create form and get ID

    # Verify in DB
    # TODO: Query by ID and verify fields

    # Cleanup
    Disconnect From Database
```

### Hint 4 (Full Solution)
```robotframework
*** Settings ***
Library     RequestsLibrary
Library     DatabaseLibrary

*** Variables ***
${BASE_URL}    http://localhost:8000/api/v1
${DB_NAME}    moje_app

*** Test Cases ***
Verify API Persistence In Database
    [Documentation]    Full database persistence verification
    [Tags]    beginner    exercise    database    api

    # Connect to database
    Connect To Database    psycopg2    ${DB_NAME}    postgres    postgres    localhost

    # Create form via API
    Create Session    api    ${BASE_URL}

    &{data}=    Create Dictionary
    ...    first_name=DBVerify
    ...    last_name=TestUser
    ...    phone=+420987654321
    ...    gender=male
    ...    email=dbverify@example.com

    ${response}=    POST On Session    api    /form/    json=${data}
    Should Be Equal As Strings    ${response.status_code}    201

    ${json}=    Evaluate    json.loads('${response.text}')    modules=json
    ${form_id}=    Set Variable    ${json}[id]

    Log    ✅ Created form via API with ID: ${form_id}

    # Verify in database
    ${result}=    Query
    ...    SELECT first_name, last_name, email FROM form_data
    ...    WHERE id = ${form_id}

    ${row}=    Get From List    ${result}    0

    Should Be Equal    ${row}[first_name]    DBVerify
    Should Be Equal    ${row}[last_name]     TestUser
    Should Be Equal    ${row}[email]         dbverify@example.com

    Log    ✅ Data verified in database

    # Verify count
    ${count}=    Row Count    SELECT COUNT(*) FROM form_data WHERE id = ${form_id}
    Should Be Equal As Integers    ${count}    1

    # Delete via API
    DELETE On Session    api    /form/${form_id}
    Should Be Equal As Strings    ${response.status_code}    200

    Log    ✅ Deleted form via API

    # Verify removal from database
    ${after_count}=    Row Count    SELECT COUNT(*) FROM form_data WHERE id = ${form_id}
    Should Be Equal As Integers    ${after_count}    0

    Log    ✅ Verified removal from database

    [Teardown]    Disconnect From Database

*** Keywords ***
# Additional helper keywords can be added here
```

---

---

## Next Steps

Congratulations on completing the BEGINNER level! 🎉

**Continue your learning:**

| Topic | Level | File |
|-------|-------|------|
| Best Practices | BEGINNER | [`01_BestPractices.md`](01_BestPractices.md) |
| Anti-Patterns | BEGINNER | [`02_AntiPatterns.md`](02_AntiPatterns.md) |
| Connection Management | INTERMEDIATE | [`../INTERMEDIATE/00_ConnectionManagement.md`](../INTERMEDIATE/00_ConnectionManagement.md) |
| Cleanup Strategies | INTERMEDIATE | [`../INTERMEDIATE/01_CleanupStrategies.md`](../INTERMEDIATE/01_CleanupStrategies.md) |
| Performance Patterns | ADVANCED | [`../ADVANCED/00_PerformancePatterns.md`](../ADVANCED/00_PerformancePatterns.md) |
| Complex Queries | ADVANCED | [`../ADVANCED/01_ComplexQueries.md`](../ADVANCED/01_ComplexQueries.md) |

---

## Best Practices Summary

✅ **DO:**
- Use TRY/FINALLY for guaranteed cleanup
- Use SUITE scope for connection reuse
- Select only needed columns (not `SELECT *`)
- Use named constants instead of magic numbers
- Store credentials in config files
- Clean up test data after tests
- Verify connection with test query
- Use COUNT() for counting (not `SELECT *`)

❌ **DON'T:**
- Hardcode credentials in tests
- Leave database connections open
- Select unnecessary data
- Use magic numbers without names
- Forget to clean up test data
- Create test dependencies
- Sleep instead of active waiting

---

## References

- [DatabaseLibrary Docs](https://github.com/frank-rouvy/RobotFramework-Database-Library)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [SQL Tutorial](https://www.w3schools.com/sql/)
- Project: `/RF/db/tests/verify_email.robot`
- DB models: `/be/app/models/`
