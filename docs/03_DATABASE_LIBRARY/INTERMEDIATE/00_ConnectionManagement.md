# Connection Management (INTERMEDIATE)

## Learning Objectives
- [ ] Understand SUITE vs TEST scope for connections
- [ ] Implement connection retry logic
- [ ] Handle connection failures gracefully
- [ ] Use connection pooling patterns
- [ ] Configure query timeouts
- [ ] Verify connection health

---

## Overview

Connection management is critical for reliable database testing. Poor connection management leads to:
- Slow test execution (connecting for every test)
- Connection leaks (unclosed connections)
- Flaky tests (connection failures)
- Resource exhaustion

---

## 1. Connection Scope Strategies

### SUITE Scope Connection (Recommended)

**Best for:** Most test suites with multiple database tests

```robotframework
*** Settings ***
Library     DatabaseLibrary

Suite Setup     Connect To Test Database
Suite Teardown  Disconnect From Database

*** Test Cases ***
Test One
    # Uses shared connection
    ${result}=    Query    SELECT * FROM form_data

Test Two
    # Reuses same connection
    ${count}=    Row Count    SELECT COUNT(*) FROM form_data

*** Keywords ***
Connect To Test Database
    Connect To Database    psycopg2    ${DB_NAME}    ${DB_USER}    ${DB_PASS}    ${DB_HOST}
    Log    ✅ Connected to ${DB_NAME} (SUITE scope)

    # Verify connection
    ${result}=    Query    SELECT 1
    Log    Connection verified
```

**Benefits:**
- Single connection for entire suite (faster)
- Less overhead on database
- Simplified setup/teardown

**When to use:**
- Multiple tests in same suite
- Tests are independent (don't modify shared state)
- Database supports concurrent queries

---

### TEST Scope Connection

**Best for:** Tests that modify database state significantly

```robotframework
*** Settings ***
Library     DatabaseLibrary

Test Setup      Connect To Database
Test Teardown   Disconnect From Database

*** Test Cases ***
Test With Fresh Connection
    # Gets new connection
    ${result}=    Query    SELECT * FROM form_data
```

**Benefits:**
- Each test has isolated connection
- Can use transactions safely
- Clearer state for each test

**When to use:**
- Tests use transactions
- Tests modify database structure
- Parallel test execution needed

---

## 2. Connection Retry Logic

### Pattern: Retry on Connection Failure

```robotframework
*** Keywords ***
Connect With Retry
    [Documentation]    Connect with retry logic for reliability
    [Arguments]    ${max_attempts}=3    ${retry_delay_s}=2

    FOR    ${attempt}    IN RANGE    ${max_attempts}
        TRY
            Connect To Database    psycopg2    ${DB_NAME}    ${DB_USER}    ${DB_PASS}    ${DB_HOST}
            Log    ✅ Connected on attempt ${attempt + 1}

            # Verify connection with test query
            ${result}=    Query    SELECT 1
            Log    Connection verified
            RETURN    # Success - exit keyword

        EXCEPT    OperationalError
            Log    ⚠️  Connection attempt ${attempt + 1} failed: ${ERROR}

            IF    ${attempt} < ${max_attempts} - 1
                Log    Retrying in ${retry_delay_s}s...
                Sleep    ${retry_delay_s}s
            END

        EXCEPT
            Log    ❌ Unexpected error: ${ERROR}
            IF    ${attempt} < ${max_attempts} - 1
                Sleep    ${retry_delay_s}s
            END
        END
    END

    Fail    ❌ Could not connect after ${max_attempts} attempts
```

**Usage:**
```robotframework
*** Test Cases ***
Test With Resilient Connection
    Connect With Retry    max_attempts=5    retry_delay_s=1

    # Test code here
    ${result}=    Query    SELECT COUNT(*) FROM form_data
```

---

## 3. Connection Health Verification

### Pattern: Ping Database

```robotframework
*** Keywords ***
Database Is Healthy
    [Documentation]    Verify database is accessible
    [Arguments]    ${timeout_s}=5

    ${start}=    Get Time    epoch

    TRY
        ${result}=    Query    SELECT 1 AS health_check
        Log    ✅ Database is healthy

        ${end}=    Get Time    epoch
        ${elapsed}=    Evaluate    ${end} - ${start}
        Log    Query response time: ${elapsed}ms

        [Return]    ${TRUE}

    EXCEPT
        Log    ❌ Database health check failed: ${ERROR}
        [Return]    ${FALSE}
    END
```

**Usage:**
```robotframework
*** Test Cases ***
Test With Health Check
    Connect To Database    psycopg2    ${DB_NAME}    ${DB_USER}    ${DB_PASS}    ${DB_HOST}

    ${healthy}=    Database Is Healthy
    Should Be True    ${healthy}
```

---

## 4. Connection String Configuration

### Pattern: Using Connection Strings

```robotframework
*** Keywords ***
Connect With Connection String
    [Documentation]    Connect using formatted connection string
    [Arguments]    ${db_config}    ${timeout_s}=30

    ${conn_str}=    Catenate    SEPARATOR=
    ...    host=${db_config}[host]
    ...    port=${db_config}[port]
    ...    dbname=${db_config}[database]
    ...    user=${db_config}[user]
    ...    password=${db_config}[password]
    ...    connect_timeout=${timeout_s}

    Connect To Database Using Connection String    psycopg2    ${conn_str}
    Log    Connected via connection string
```

**Config Dictionary:**
```robotframework
*** Variables ***
&{DB_CONFIG}
host=        localhost
port=        5432
database=    moje_app
user=        postgres
password=    postgres
```

---

## 5. Query Timeout Configuration

### Pattern: Statement Timeout

```robotframework
*** Keywords ***
Query With Timeout
    [Documentation]    Execute query with timeout
    [Arguments]    ${query}    ${timeout_s}=30

    # Set statement timeout (PostgreSQL)
    Execute Sql String    SET statement_timeout = ${timeout_s * 1000}

    TRY
        ${result}=    Query    ${query}
        [Return]    ${result}

    EXCEPT    OperationalError
        Log    ❌ Query timeout or error: ${ERROR}
        Fail    Query failed or timed out after ${timeout_s}s

    FINALLY
        # Reset timeout
        Execute Sql String    SET statement_timeout = 0
    END
```

**Usage:**
```robotframework
*** Test Cases ***
Test Slow Query With Timeout
    ${result}=    Query With Timeout
    ...    SELECT * FROM large_table WHERE complex_condition
    ...    timeout_s=60
```

---

## 6. Connection Pool Pattern

### Pattern: Reusing Connection

```robotframework
*** Settings ***
Library     DatabaseLibrary

Suite Setup     Initialize Database Connection
Suite Teardown  Close Database Connection

*** Variables ***
# Connection state
${DB_CONNECTED}=    ${FALSE}

*** Keywords ***
Initialize Database Connection
    [Documentation]    Initialize connection (lazy loading)

    # Don't connect yet - connect when first query runs
    Set Suite Variable    ${DB_CONNECTED}    ${FALSE}
    Log    Database connection initialized (lazy)

Get Database Connection
    [Documentation]    Get or create connection (lazy pattern)
    IF    not ${DB_CONNECTED}
        Log    Connecting to database...
        Connect To Database    psycopg2    ${DB_NAME}    ${DB_USER}    ${DB_PASS}    ${DB_HOST}
        Set Suite Variable    ${DB_CONNECTED}    ${TRUE}
        Log    ✅ Database connected
    END

Close Database Connection
    [Documentation]    Close connection if open
    IF    ${DB_CONNECTED}
        Disconnect From Database
        Set Suite Variable    ${DB_CONNECTED}    ${FALSE}
        Log    Database disconnected
    END
```

**Usage:**
```robotframework
*** Test Cases ***
Lazy Connection Test
    # Connection established on first use
    Get Database Connection

    ${result}=    Query    SELECT COUNT(*) FROM form_data
```

---

## 7. Multi-Database Connections

### Pattern: Managing Multiple Databases

```robotframework
*** Settings ***
Library     DatabaseLibrary    WITH NAME    MainDB
Library     DatabaseLibrary    WITH NAME    TestDB

Suite Setup     Setup Both Databases
Suite Teardown  Close Both Databases

*** Keywords ***
Setup Both Databases
    Connect To Database    psycopg2    ${MAIN_DB}    ${DB_USER}    ${DB_PASS}    ${DB_HOST}    alias=MainDB
    Connect To Database    psycopg2    ${TEST_DB}    ${DB_USER}    ${DB_PASS}    ${DB_HOST}    alias=TestDB
    Log    ✅ Connected to both databases

Close Both Databases
    Disconnect From Database    alias=MainDB
    Disconnect From Database    alias=TestDB
    Log    Databases disconnected

Query Main Database
    [Arguments]    ${query}
    ${result}=    Query    ${query}    alias=MainDB
    [Return]    ${result}

Query Test Database
    [Arguments]    ${query}
    ${result}=    Query    ${query}    alias=TestDB
    [Return]    ${result}
```

---

## 8. Connection Error Handling

### Pattern: Graceful Degradation

```robotframework
*** Keywords ***
Connect Or Skip Suite
    [Documentation]    Connect to database, skip tests if unavailable
    [Arguments]    ${critical}=${TRUE}

    TRY
        Connect To Database    psycopg2    ${DB_NAME}    ${DB_USER}    ${DB_PASS}    ${DB_HOST}
        Log    ✅ Database connected

    EXCEPT    OperationalError
        IF    ${critical}
            Fail    Database is required but unavailable: ${ERROR}
        ELSE
            Warn    Database unavailable - skipping tests: ${ERROR}
            Skip Test    Database not available
        END

    EXCEPT
        Fail    Unexpected connection error: ${ERROR}
    END
```

---

## 9. Connection State Tracking

### Pattern: Track Connection Lifecycle

```robotframework
*** Settings ***
Library     DatabaseLibrary

Suite Setup     Initialize Connection Tracking
Suite Teardown  Cleanup Connection Tracking

*** Variables ***
# Connection state
${CONNECTION_STATE}=    disconnected
${CONNECTION_ID}=       ${EMPTY}

*** Keywords ***
Initialize Connection Tracking
    [Documentation]    Initialize connection tracking
    Set Suite Variable    ${CONNECTION_STATE}    disconnected
    Set Suite Variable    ${CONNECTION_ID}    ${EMPTY}

Establish Tracked Connection
    [Documentation]    Connect and track state
    [Arguments]    ${connection_id}    ${timeout_s}=30

    Log    Connecting to database (${connection_id})...

    TRY
        Connect To Database    psycopg2    ${DB_NAME}    ${DB_USER}    ${DB_PASS}    ${DB_HOST}
        Set Suite Variable    ${CONNECTION_STATE}    connected
        Set Suite Variable    ${CONNECTION_ID}    ${connection_id}

        ${result}=    Query    SELECT inet_server_addr() AS server_addr
        Log    ✅ Connected to ${result}[0][server_addr]} (ID: ${connection_id})

    EXCEPT
        Set Suite Variable    ${CONNECTION_STATE}    failed
        Fail    Connection ${connection_id} failed: ${ERROR}
    END

Cleanup Connection Tracking
    [Documentation]    Cleanup based on connection state

    Log    Connection state: ${CONNECTION_STATE}

    IF    '${CONNECTION_STATE}' == 'connected'
        Disconnect From Database
        Set Suite Variable    ${CONNECTION_STATE}    disconnected
        Log    Connection closed
    ELSE
        Log    No active connection to close
    END
```

---

## 10. Environment-Aware Connection

### Pattern: Different Connections per Environment

```robotframework
*** Variables ***
# Environment-specific configuration
${ENVIRONMENT}=    Get Environment Variable    TEST_ENV    default=development

*** Keywords ***
Get Database Config For Environment
    [Documentation]    Return database config for current environment
    [Arguments]    ${environment}

    IF    '${environment}' == 'production'
        &{config}=    Create Dictionary
        ...    host=${PROD_DB_HOST}
        ...    database=${PROD_DB_NAME}
        ...    user=${PROD_DB_USER}
        ...    password=${PROD_DB_PASSWORD}
        ...    port=5432

    ELSE IF    '${environment}' == 'staging'
        &{config}=    Create Dictionary
        ...    host=${STAGING_DB_HOST}
        ...    database=${STAGING_DB_NAME}
        ...    user=${STAGING_DB_USER}
        ...    password=${STAGING_DB_PASSWORD}
        ...    port=5432

    ELSE
        &{config}=    Create Dictionary
        ...    host=localhost
        ...    database=moje_app_test
        ...    user=postgres
        ...    password=postgres
        ...    port=5432
    END

    [Return]    ${config}
```

**Usage:**
```robotframework
*** Test Cases ***
Environment Aware Test
    ${env}=    Get Environment Variable    TEST_ENV    default=development

    &{config}=    Get Database Config For Environment    ${env}
    Connect To Database    psycopg2    ${config}[database]    ${config}[user]    ${config}[password]    ${config}[host]

    Log    Testing against ${env} environment
```

---

## Best Practices Summary

| Pattern | When to Use | Key Benefit |
|---------|-------------|-------------|
| SUITE scope | Multiple tests in suite | Faster execution |
| TEST scope | Isolated state needed | Clearer test boundaries |
| Retry logic | Unstable connections | More reliable tests |
| Health checks | Critical database tests | Early failure detection |
| Query timeout | Long-running queries | Prevent hanging |
| Lazy connection | Not all tests need DB | Resource efficiency |
| Connection tracking | Complex test suites | Better debugging |
| Environment-aware | Multiple environments | Flexible deployment |

---

## Common Pitfalls

### ❌ Don't: Connect Without Verification

```robotframework
# BAD - Assumes connection worked
Connect To Database    psycopg2    ${DB}    ${user}    ${pass}    ${host}
# Continues without checking...
```

### ✅ Do: Verify Connection

```robotframework
# GOOD - Verifies connection
Connect To Database    psycopg2    ${DB}    ${user}    ${pass}    ${host}
${result}=    Query    SELECT 1
Should Not Be Empty    ${result}
```

---

### ❌ Don't: Ignore Connection State

```robotframework
# BAD - No tracking
Disconnect From Database
Disconnect From Database  # What if already disconnected?
```

### ✅ Do: Track Connection State

```robotframework
# GOOD - State-aware
IF    ${DB_CONNECTED}
    Disconnect From Database
    Set Suite Variable    ${DB_CONNECTED}    ${FALSE}
END
```

---

## References

- [Database Library Documentation](https://github.com/frank-rouvy/RobotFramework-Database-Library)
- [PostgreSQL Connection Settings](https://www.postgresql.org/docs/libpq-connect.html)
- [Best Practices Guide](../BEGINNER/01_BestPractices.md)
