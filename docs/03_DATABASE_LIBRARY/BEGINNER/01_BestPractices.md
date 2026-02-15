# Database Library Best Practices

## Learning Objectives
- [ ] Understand connection management best practices
- [ ] Learn proper cleanup patterns with TRY/FINALLY
- [ ] Implement data verification strategies
- [ ] Use configuration separation for security
- [ ] Apply error handling patterns

---

## Overview

This guide covers industry best practices for database testing with Robot Framework Database Library. These patterns ensure your tests are reliable, maintainable, and secure.

---

## 1. Connection Management

### Pattern: SUITE Scope Connection

**Why:** Reuse connection across tests for better performance.

```robotframework
*** Settings ***
Library     DatabaseLibrary

Suite Setup     Connect To Test Database
Suite Teardown  Disconnect From Database

*** Keywords ***
Connect To Test Database
    [Documentation]    Connect to database with proper configuration
    Connect To Database    psycopg2    ${DB_NAME}    ${DB_USER}    ${DB_PASS}    ${DB_HOST}
    Log    Connected to database: ${DB_NAME}@${DB_HOST}

    # Verify connection works
    ${result}=    Query    SELECT 1
    Log    Connection verified successfully
```

**Benefits:**
- Single connection for entire test suite
- Faster test execution
- Simplified teardown
- Connection verification on startup

---

### Pattern: Connection with Timeout

**Why:** Prevent tests from hanging on connection issues.

```robotframework
*** Keywords ***
Connect To Database With Timeout
    [Documentation]    Connect with timeout to prevent hanging
    [Arguments]    ${timeout_s}=30

    ${connection_string}=    Set Variable
    ...    host=${DB_HOST} port=${DB_PORT} dbname=${DB_NAME} user=${DB_USER} password=${DB_PASSWORD} connect_timeout=${timeout_s}

    Connect To Database Using Connection String    psycopg2    ${connection_string}
    Log    Connected with ${timeout_s}s timeout
```

---

## 2. Cleanup Strategies

### Pattern: TRY/FINALLY for Guaranteed Cleanup

**Why:** FINALLY block executes regardless of test success or failure.

```robotframework
*** Test Cases ***
Verify Form Data In Database
    [Documentation]    Verify API created data in database
    [Tags]    database    verification

    Connect To Database    psycopg2    ${DB_NAME}    ${DB_USER}    ${DB_PASS}    ${DB_HOST}

    TRY
        # Create form via API
        ${form_id}=    Create Test Form Via API

        # Verify in database
        ${result}=    Query    SELECT * FROM form_data WHERE id = ${form_id}
        Should Be Equal    ${result}[0][email]    test@example.com

        Log    ✅ Data verified successfully

    EXCEPT
        Log    ❌ Test failed: ${ERROR}
        Fail    Database verification failed

    FINALLY
        # ALWAYS executed - even on failure
        Disconnect From Database
        Log    Database disconnected (cleanup complete)
    END
```

**Key Points:**
- `TRY`: Test code that might fail
- `EXCEPT`: Optional error handling
- `FINALLY`: Cleanup that ALWAYS runs
- `END`: Closes the block

---

### Pattern: Teardown Cleanup

**Why:** Automatic cleanup after each test.

```robotframework
*** Settings ***
Test Teardown    Clean Up Test Data

*** Test Cases ***
Create And Verify Form
    [Documentation]    Test with automatic cleanup
    ${form_id}=    Create Test Form Via API    ${TEST_EMAIL}
    Verify Form In Database    ${form_id}    ${TEST_EMAIL}

*** Keywords ***
Clean Up Test Data
    [Documentation]    Clean up data created during test
    Connect To Database    psycopg2    ${DB_NAME}    ${DB_USER}    ${DB_PASS}    ${DB_HOST}

    TRY
        # Delete test data by email pattern
        Execute Sql String    DELETE FROM form_data WHERE email LIKE '%@test.example.com'
        Log    Test data cleaned up
    FINALLY
        Disconnect From Database
    END
```

---

## 3. Data Verification Patterns

### Pattern: Verify Single Record

```robotframework
*** Keywords ***
Verify Form In Database
    [Documentation]    Verify form data exists in database
    [Arguments]    ${form_id}    ${expected_email}

    ${result}=    Query    SELECT * FROM form_data WHERE id = ${form_id}

    # Check record exists
    ${count}=    Get Length    ${result}
    Should Be Equal As Integers    ${count}    1    msg=Form ${form_id} not found

    # Verify specific field
    ${row}=    Get From List    ${result}    0
    Should Be Equal    ${row}[email]    ${expected_email}    msg=Email mismatch

    Log    ✅ Form ${form_id} verified: email=${expected_email}
```

---

### Pattern: Verify Multiple Fields

```robotframework
*** Keywords ***
Verify Form Fields In Database
    [Documentation]    Verify multiple fields match expected values
    [Arguments]    ${form_id}    &{expected_data}

    ${result}=    Query    SELECT * FROM form_data WHERE id = ${form_id}
    ${row}=    Get From List    ${result}    0

    # Verify each field
    FOR    ${key}    IN    @{expected_data.keys}
        ${actual}=    Get From Dictionary    ${row}    ${key}
        ${expected}=    Get From Dictionary    ${expected_data}    ${key}
        Should Be Equal    ${actual}    ${expected}    msg=Field ${key}: expected ${expected}, got ${actual}
        Log    ✅ Field ${key} verified: ${actual}
    END
```

**Usage:**
```robotframework
*** Test Cases ***
Verify All Form Fields
    &{data}=    Create Dictionary
    ...    first_name=Jan
    ...    last_name=Novák
    ...    email=jan.novak@example.com

    Verify Form Fields In Database    ${form_id}    ${data}
```

---

### Pattern: Verify Record Count

```robotframework
*** Keywords ***
Verify Record Count
    [Documentation]    Verify exact number of records
    [Arguments]    ${table}    ${expected_count}    ${where_clause}=${EMPTY}

    ${where}=    Set Variable If    '${where_clause}' != ${EMPTY}    WHERE ${where_clause}    ${EMPTY}
    ${query}=    Set Variable    SELECT COUNT(*) FROM ${table} ${where}

    ${count}=    Row Count    ${query}
    Should Be Equal As Integers    ${count}    ${expected_count}

    Log    ✅ Record count verified: ${count} records in ${table}
```

---

## 4. Configuration Separation

### Pattern: External Configuration

**Why:** Keep sensitive data separate from test code.

**config/config.py:**
```python
# Database configuration
DB_HOST = "localhost"
DB_PORT = 5432
DB_NAME = "moje_app"
DB_USER = "postgres"
DB_PASSWORD = "postgres"

# Test data configuration
TEST_EMAIL_DOMAIN = "test.example.com"
BASE_TEST_EMAIL = "rf-test"
```

**variables.resource:**
```robotframework
*** Variables ***
# Import global configuration
Variables    ../../config/config.py

# Test-specific variables (can use config values as defaults)
${TEST_EMAIL}    ${BASE_TEST_EMAIL}@${TEST_EMAIL_DOMAIN}
```

**Usage in tests:**
```robotframework
*** Variables ***
Variables    ../../resources/variables.resource

*** Test Cases ***
Test With Config
    # Use config values
    Connect To Database    psycopg2    ${DB_NAME}    ${DB_USER}    ${DB_PASSWORD}    ${DB_HOST}
```

**Benefits:**
- Single source of truth for configuration
- Easy to change for different environments
- Sensitive data not in version control
- Tests can use different configs (dev, staging, prod)

---

## 5. Variable Usage Patterns

### Pattern: Named Constants

**Why:** Improve readability and maintainability.

```robotframework
*** Variables ***
# BAD: Magic numbers (what do these mean?)
${TIMEOUT_1}     30
${TIMEOUT_2}     70
${TIMEOUT_3}     5000

# GOOD: Named constants
${DB_CONNECTION_TIMEOUT_S}      30
${QUERY_TIMEOUT_S}              70
${NETWORK_IDLE_TIMEOUT_MS}      5000

# Test configuration
${MAX_RETRY_COUNT}              3
${RETRY_DELAY_MS}               1000
${TEST_EMAIL}                   robot-test@example.com
```

**Usage:**
```robotframework
Connect To Database    psycopg2    ${DB_NAME}    ${DB_USER}    ${DB_PASS}    ${DB_HOST}
Wait For Network Idle    timeout=${NETWORK_IDLE_TIMEOUT_MS}ms
```

---

### Pattern: Environment-Specific Variables

```robotframework
*** Variables ***
# Environment detection
${ENVIRONMENT}=    Get Environment Variable    ENVIRONMENT    default=${EMPTY}

# Database configuration based on environment
${DB_HOST}=       Set Variable If    '${ENVIRONMENT}' == 'production'    ${PROD_DB_HOST}
...                                      ${DEV_DB_HOST}

${DB_NAME}=       Set Variable If    '${ENVIRONMENT}' == 'production'    ${PROD_DB_NAME}
...                                      ${DEV_DB_NAME}
```

---

## 6. Error Handling Patterns

### Pattern: TRY/EXCEPT/ELSE/FINALLY

```robotframework
*** Test Cases ***
Database Operation With Error Handling
    Connect To Database    psycopg2    ${DB_NAME}    ${DB_USER}    ${DB_PASS}    ${DB_HOST}

    TRY
        ${result}=    Query    SELECT * FROM form_data WHERE id = 999999
        Should Not Be Empty    ${result}

    EXCEPT    No row found
        Log    ℹ️  No record found (expected behavior)
        # This is OK for this test

    EXCEPT
        Log    ❌ Unexpected error: ${ERROR}
        Fail    Unexpected database error

    ELSE
        Log    ✅ Query executed successfully

    FINALLY
        Disconnect From Database
    END
```

---

### Pattern: Connection Retry

```robotframework
*** Keywords ***
Connect With Retry
    [Documentation]    Retry connection on failure
    [Arguments]    ${max_attempts}=3    ${retry_delay_s}=2

    FOR    ${attempt}    IN RANGE    ${max_attempts}
        TRY
            Connect To Database    psycopg2    ${DB_NAME}    ${DB_USER}    ${DB_PASS}    ${DB_HOST}
            Log    ✅ Connected on attempt ${attempt + 1}
            RETURN    # Success - exit keyword

        EXCEPT
            Log    ⚠️  Connection attempt ${attempt + 1} failed
            IF    ${attempt} < ${max_attempts} - 1
                Sleep    ${retry_delay_s}s
            END
        END
    END

    Fail    Could not connect to database after ${max_attempts} attempts
```

---

## 7. Logging Patterns

### Pattern: Structured Logging

```robotframework
*** Keywords ***
Log Query Result
    [Documentation]    Log query result in structured format
    [Arguments]    ${result}    ${log_rows}=5

    ${row_count}=    Get Length    ${result}
    Log    📊 Query returned ${row_count} rows

    # Log first N rows for debugging
    ${rows_to_log}=    Set Variable If    ${row_count} < ${log_rows}    ${row_count}    ${log_rows}

    FOR    ${i}    IN RANGE    ${rows_to_log}
        ${row}=    Get From List    ${result}    ${i}
        Log    Row ${i}: ${row}
    END

    IF    ${row_count} > ${log_rows}
        Log    ... and ${row_count - ${log_rows}} more rows
    END
```

---

### Pattern: Test Data Logging

```robotframework
*** Keywords ***
Log Test Data Creation
    [Documentation]    Log test data for debugging
    [Arguments]    ${form_id}    &{form_data}

    Log    📝 Created test form:
    Log    ├─ ID: ${form_id}
    Log    ├─ Name: ${form_data}[first_name] ${form_data}[last_name]
    Log    ├─ Email: ${form_data}[email]
    Log    ├─ Phone: ${form_data}[phone]
    Log    └─ Gender: ${form_data}[gender]
```

---

## 8. Performance Patterns

### Pattern: Column Selection

**Why:** Only select needed columns for better performance.

```robotframework
# BAD: Select all columns
${result}=    Query    SELECT * FROM form_data WHERE id = ${form_id}

# GOOD: Select only needed columns
${result}=    Query    SELECT id, email, created_at FROM form_data WHERE id = ${form_id}
```

---

### Pattern: Limit Results

```robotframework
# BAD: Could return thousands of rows
${result}=    Query    SELECT * FROM form_data

# GOOD: Limit results
${result}=    Query    SELECT * FROM form_data LIMIT 100

# Or use Row Count for verification
${count}=    Row Count    SELECT COUNT(*) FROM form_data
```

---

## 9. Test Isolation

### Pattern: Unique Test Data

**Why:** Prevent test collisions and ensure independent tests.

```robotframework
*** Keywords ***
Generate Unique Test Data
    [Documentation]    Generate unique test data using timestamp
    [Arguments]    ${prefix}=test

    ${timestamp}=    Get Time    epoch
    ${unique_id}=    Set Variable    ${prefix}-${timestamp}

    &{data}=    Create Dictionary
    ...    first_name=Test
    ...    last_name=User
    ...    email=${unique_id}@example.com
    ...    phone=+420123456789
    ...    gender=male

    [Return]    ${unique_id}    ${data}
```

**Usage:**
```robotframework
*** Test Cases ***
Test With Unique Data
    ${unique_id}    &{data}=    Generate Unique Test Data
    ${form_id}=    Create Form    ${data}
    # This test won't collide with other tests
```

---

## 10. Anti-Pattern Warnings

### ❌ Anti-Pattern: Hardcoded Credentials

```robotframework
# BAD - Exposes credentials in test code
Connect To Database    psycopg2    moje_app    postgres    postgres    localhost
```

**✅ Correct Approach:**
```robotframework
# GOOD - Use variables from config
Connect To Database    psycopg2    ${DB_NAME}    ${DB_USER}    ${DB_PASSWORD}    ${DB_HOST}
```

---

### ❌ Anti-Pattern: No Cleanup

```robotframework
# BAD - Data pollution
*** Test Cases ***
Create Form
    Create Test Form
    # No cleanup - test data remains in database
```

**✅ Correct Approach:**
```robotframework
# GOOD - Always clean up
*** Test Cases ***
Create Form
    ${test_email}=    Set Variable    unique-${timestamp}@test.com
    Create Test Form    ${test_email}
    [Teardown]    Clean Up Test Data    ${test_email}
```

---

### ❌ Anti-Pattern: Sleep Instead of Wait

```robotframework
# BAD - Unreliable and slow
Sleep    5s
```

**✅ Correct Approach:**
```robotframework
# GOOD - Use explicit verification
Wait Until Keyword Succeeds    10s    1s    Database Is Ready
```

---

## Best Practices Checklist

Before committing database tests, verify:

- [ ] Connection uses variables from config (not hardcoded)
- [ ] All cleanup is in FINALLY block or Teardown
- [ ] Tests use unique identifiers to prevent collisions
- [ ] Queries select only needed columns
- [ ] Error handling uses TRY/EXCEPT appropriately
- [ ] Sensitive data is in separate config files
- [ ] Tests can run in any order (no dependencies)
- [ ] Logging is clear and helpful for debugging
- [ ] Timeouts are configured appropriately
- [ ] Test data is cleaned up after test completion

---

## References

- [DatabaseLibrary Documentation](https://github.com/frank-rouvy/RobotFramework-Database-Library)
- [Robot Framework User Guide - Error Handling](https://robotframework.org/robotframework/latest/RobotFrameworkUserGuide.html#automatic-error-handling-try-except)
- [PostgreSQL Best Practices](https://wiki.postgresql.org/wiki/Don%27t_Do_This)
- Project: `/be/app/models/` for database schema
