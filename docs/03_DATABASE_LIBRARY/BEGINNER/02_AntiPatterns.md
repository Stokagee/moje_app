# Database Library Anti-Patterns

## Learning Objectives
- [ ] Recognize common database testing anti-patterns
- [ ] Understand why each pattern is problematic
- [ ] Learn the correct alternatives
- [ ] Apply best practices to avoid these mistakes

---

## Overview

This guide shows common **anti-patterns** (what NOT to do) when writing database tests with Robot Framework. Each anti-pattern includes the problem, why it's bad, and the correct approach.

---

## Anti-Pattern 1: Hardcoded Test Data

### ❌ BAD: Hardcoded Values in Tests

```robotframework
*** Test Cases ***
Hardcoded Credentials Example
    [Documentation]    BAD: Credentials hardcoded in test

    Connect To Database    psycopg2    moje_app    postgres    postgres    localhost

    Create User    john.doe@example.com    mySuperSecretPassword123
```

**Problems:**
- Not flexible - can't change for different environments
- Exposes sensitive information in version control
- Difficult to maintain - same values repeated everywhere
- Security risk - passwords visible in code

---

### ✅ GOOD: Using Configuration Variables

```robotframework
*** Settings ***
Variables    ../../resources/variables.resource

*** Test Cases ***
Using Config Variables Example
    [Documentation]    GOOD: Values from external config

    Connect To Database    psycopg2    ${DB_NAME}    ${DB_USER}    ${DB_PASSWORD}    ${DB_HOST}

    Create User    ${TEST_USER}    ${TEST_PASSWORD}
```

**Benefits:**
- Single source of truth for configuration
- Easy to change for different environments
- Sensitive data not in version control
- Tests are flexible and reusable

---

## Anti-Pattern 2: Magic Numbers

### ❌ BAD: Unnamed Numbers in Code

```robotframework
*** Test Cases ***
Magic Numbers Example
    [Documentation]    BAD: What do these numbers mean?

    Assess Security Threat    Phishing    70
    Assess Security Threat    Malware    85
    Assess Security Threat    Ransomware    90

    Sleep    30
    Sleep    5000
```

**Problems:**
- Unclear what numbers represent
- Hard to maintain when values change
- No context for why these values
- Difficult to reuse in other tests

---

### ✅ GOOD: Named Constants

```robotframework
*** Variables ***
# Risk scores - meaningful names
${PHISHING_RISK_SCORE}      70
${MALWARE_RISK_SCORE}       85
${RANSOMWARE_RISK_SCORE}    90

# Timeouts - clear purpose
${DB_CONNECTION_TIMEOUT_S}  30
${POLL_INTERVAL_MS}         5000

*** Test Cases ***
Named Constants Example
    [Documentation]    GOOD: Self-documenting values

    Assess Security Threat    Phishing    ${PHISHING_RISK_SCORE}
    Assess Security Threat    Malware    ${MALWARE_RISK_SCORE}
    Assess Security Threat    Ransomware    ${RANSOMWARE_RISK_SCORE}

    Sleep    ${DB_CONNECTION_TIMEOUT_S}s
```

**Benefits:**
- Code is self-documenting
- Easy to change in one place
- Clear what values represent
- Can reuse constants across tests

---

## Anti-Pattern 3: No Cleanup

### ❌ BAD: Test Data Not Cleaned Up

```robotframework
*** Test Cases ***
No Cleanup Example
    [Documentation]    BAD: Data pollution

    ${form_id}=    Create Test Form    test@example.com

    # Verify in database
    ${result}=    Query    SELECT * FROM form_data WHERE id = ${form_id}
    Should Be Equal    ${result}[0][email]    test@example.com

    # Test ends - DATA REMAINS IN DATABASE FOREVER
```

**Problems:**
- Test data accumulates in database
- Future tests may fail due to old data
- "It works on my machine" syndrome
- Difficult to debug with polluted data
- Tests can't run in parallel

---

### ✅ GOOD: Proper Cleanup with FINALLY

```robotframework
*** Test Cases ***
With Cleanup Example
    [Documentation]    GOOD: Data always cleaned up

    ${test_email}=    Set Variable    cleanup-test-${timestamp}@example.com
    ${form_id}=    Create Test Form    ${test_email}

    Connect To Database    psycopg2    ${DB_NAME}    ${DB_USER}    ${DB_PASSWORD}    ${DB_HOST}

    TRY
        ${result}=    Query    SELECT * FROM form_data WHERE id = ${form_id}
        Should Be Equal    ${result}[0][email]    ${test_email}

    FINALLY
        # ALWAYS executes - even if test fails
        Execute Sql String    DELETE FROM form_data WHERE email = '${test_email}'
        Disconnect From Database
        Log    Test data cleaned up
    END
```

**Benefits:**
- Clean database after each test
- Tests are idempotent (can run multiple times)
- Tests can run in parallel
- Reliable debugging environment

---

## Anti-Pattern 4: Complex Logic in Tests

### ❌ BAD: Business Logic in Test Cases

```robotframework
*** Test Cases ***
Complex Logic Example
    [Documentation]    BAD: Hard to read and maintain

    ${result}=    Query    SELECT * FROM form_data
    ${count}=    Get Length    ${result}

    IF    ${count} > 100
        FOR    ${i}    IN RANGE    ${count}
            ${row}=    Get From List    ${result}    ${i}
            ${email}=    Set Variable    ${row}[email]
            ${domain}=    Evaluate    $email.split('@')[1]    modules=re
            IF    '${domain}' == 'test.com'
                ${is_test}=    Set Variable    ${TRUE}
            ELSE
                ${is_test}=    Set Variable    ${FALSE}
            END
            # ... more nested logic
        END
    ELSE
        Log    Not enough records
    END
```

**Problems:**
- Test is hard to read
- Business logic mixed with test logic
- Difficult to debug
- Not reusable
- Test does too many things

---

### ✅ GOOD: Logic Moved to Keywords

```robotframework
*** Test Cases ***
Clean Test Example
    [Documentation]    GOOD: Clear and focused

    ${test_count}=    Count Test Domain Records

    Should Be True    ${test_count} > 0
    Log    Found ${test_count} test domain records

*** Keywords ***
Count Test Domain Records
    [Documentation]    Count records with test.com domain
    ${result}=    Query    SELECT email FROM form_data WHERE email LIKE '%@test.com'
    ${count}=    Get Length    ${result}
    [Return]    ${count}
```

**Benefits:**
- Test is clear and focused
- Logic is reusable
- Easier to test logic separately
- Better error messages

---

## Anti-Pattern 5: Test Dependencies

### ❌ BAD: Tests Depending on Each Other

```robotframework
*** Test Cases ***
Create Test Data
    [Documentation]    BAD: Creates data used by next test

    ${user_id}=    Create User    test@example.com
    Set Suite Variable    ${USER_ID}    ${user_id}

Verify User Data
    [Documentation]    BAD: Depends on Create Test Data running first

    # Requires ${USER_ID} from previous test
    ${result}=    Query    SELECT * FROM users WHERE id = ${USER_ID}
    Should Be Equal    ${result}[0][email]    test@example.com
```

**Problems:**
- Tests can't run in any order
- Can't run single test in isolation
- Parallel execution impossible
- Difficult to debug failures
- Fragile test suite

---

### ✅ GOOD: Independent Tests

```robotframework
*** Test Cases ***
Create And Verify User
    [Documentation]    GOOD: Self-contained test

    # Setup: Create unique data
    ${test_email}=    Set Variable    independent-${timestamp}@test.com
    ${user_id}=    Create User    ${test_email}

    # Verify: Check what we created
    ${result}=    Query    SELECT * FROM users WHERE id = ${user_id}
    Should Be Equal    ${result}[0][email]    ${test_email}

    # Teardown: Clean up
    Execute Sql String    DELETE FROM users WHERE id = ${user_id}
```

**Benefits:**
- Tests can run in any order
- Can run single test in isolation
- Parallel execution possible
- Easier to debug
- More reliable test suite

---

## Anti-Pattern 6: No Connection Error Handling

### ❌ BAD: Connection Errors Not Handled

```robotframework
*** Test Cases ***
No Error Handling Example
    [Documentation]    BAD: Fails confusingly on connection issues

    # If database is down, test fails with unclear error
    Connect To Database    psycopg2    ${DB_NAME}    ${DB_USER}    ${DB_PASSWORD}    ${DB_HOST}

    ${result}=    Query    SELECT * FROM form_data
    # ... test continues

    Disconnect From Database
```

**Problems:**
- Unclear error messages
- Connection might remain open on failure
- Doesn't distinguish between connection errors and test failures
- Difficult to diagnose issues

---

### ✅ GOOD: Proper Error Handling

```robotframework
*** Test Cases ***
With Error Handling Example
    [Documentation]    GOOD: Clear error handling

    TRY
        Connect To Database    psycopg2    ${DB_NAME}    ${DB_USER}    ${DB_PASSWORD}    ${DB_HOST}

        ${result}=    Query    SELECT * FROM form_data
        Should Not Be Empty    ${result}

    EXCEPT    OperationalError
        Log    ❌ Database connection failed
        Log    Check if database is running: ${DB_HOST}:${DB_PORT}
        Fail    Database not accessible

    EXCEPT
        Log    ❌ Unexpected error: ${ERROR}
        Fail    Unexpected database error

    ELSE
        Log    ✅ Database operations successful

    FINALLY
        Disconnect From Database
    END
```

**Benefits:**
- Clear error messages
- Proper cleanup guaranteed
- Distinguishes error types
- Easier debugging

---

## Anti-Pattern 7: Inefficient Queries

### ❌ BAD: Selecting All Data

```robotframework
*** Test Cases ***
Inefficient Query Example
    [Documentation]    BAD: Selects unnecessary data

    ${result}=    Query    SELECT * FROM form_data

    # Only checking if any records exist
    ${count}=    Get Length    ${result}
    Should Be True    ${count} > 0
```

**Problems:**
- Wastes bandwidth and memory
- Slower query execution
- Returns sensitive data not needed
- Doesn't scale with large tables

---

### ✅ GOOD: Optimized Queries

```robotframework
*** Test Cases ***
Efficient Query Example
    [Documentation]    GOOD: Selects only what's needed

    # Option 1: Use Row Count
    ${count}=    Row Count    SELECT COUNT(*) FROM form_data
    Should Be True    ${count} > 0

    # Option 2: Select specific columns with LIMIT
    ${result}=    Query    SELECT id FROM form_data LIMIT 1
    Should Not Be Empty    ${result}
```

**Benefits:**
- Faster query execution
- Less memory usage
- Better scalability
- More focused tests

---

## Anti-Pattern 8: Sleep Instead of Waits

### ❌ BAD: Using Fixed Delays

```robotframework
*** Test Cases ***
Sleep Example
    [Documentation]    BAD: Unreliable and slow

    Create Form    test@example.com

    # Hope database is ready...
    Sleep    5s

    ${result}=    Query    SELECT * FROM form_data WHERE email = 'test@example.com'
    Should Not Be Empty    ${result}
```

**Problems:**
- Unreliable (too short or too long)
- Slow tests (wastes time)
- Brittle timing
- Frustrating to run

---

### ✅ GOOD: Active Waiting

```robotframework
*** Test Cases ***
Active Wait Example
    [Documentation]    GOOD: Polls until condition met

    Create Form    test@example.com

    # Wait actively for data to appear
    Wait Until Keyword Succeeds    10s    1s
    ...    Record Should Exist In Database    test@example.com

    ${result}=    Query    SELECT * FROM form_data WHERE email = 'test@example.com'
    Should Not Be Empty    ${result}

*** Keywords ***
Record Should Exist In Database
    [Arguments]    ${email}

    ${count}=    Row Count    SELECT COUNT(*) FROM form_data WHERE email = '${email}'
    Should Be True    ${count} > 0
```

**Benefits:**
- Reliable (not dependent on timing)
- Fast (doesn't wait longer than needed)
- Clear failure conditions
- Better developer experience

---

## Anti-Pattern 9: Direct SQL in Tests

### ❌ BAD: SQL Scattered in Tests

```robotframework
*** Test Cases ***
SQL In Tests Example
    [Documentation]    BAD: SQL mixed with test logic

    Execute Sql String    INSERT INTO form_data (first_name, last_name, email) VALUES ('Test', 'User', 'test@example.com')

    Execute Sql String    SELECT * FROM form_data WHERE email = 'test@example.com'

    Execute Sql String    DELETE FROM form_data WHERE email = 'test@example.com'
```

**Problems:**
- SQL errors not caught until runtime
- Hard to maintain (SQL everywhere)
- Difficult to reuse queries
- No type safety
- Easy to make typos

---

### ✅ GOOD: Keywords with Query

```robotframework
*** Test Cases ***
Using Keywords Example
    [Documentation]    GOOD: Reusable keywords

    ${form_id}=    Create Test Form    Test    User    test@example.com

    ${result}=    Get Form By Email    test@example.com
    Should Be Equal    ${result}[first_name]    Test

    Delete Form By Id    ${form_id}

*** Keywords ***
Create Test Form
    [Arguments]    ${first_name}    ${last_name}    ${email}
    ${result}=    Query
    ...    INSERT INTO form_data (first_name, last_name, email)
    ...    VALUES ('${first_name}', '${last_name}', '${email}')
    ...    RETURNING id
    ${form_id}=    Set Variable    ${result}[0][0]
    [Return]    ${form_id}

Get Form By Email
    [Arguments]    ${email}
    ${result}=    Query    SELECT * FROM form_data WHERE email = '${email}'
    ${row}=    Get From List    ${result}    0
    [Return]    ${row}
```

**Benefits:**
- Reusable database operations
- Easier to test logic separately
- Single place to fix SQL bugs
- Better abstraction
- Type safety through parameters

---

## Anti-Pattern 10: Shared State Between Tests

### ❌ BAD: Tests Modify Shared Data

```robotframework
*** Variables ***
# Shared state - BAD
${SHARED_USER_ID}    ${EMPTY}

*** Test Cases ***
Test A Creates Data
    [Documentation]    BAD: Modifies shared state

    ${user_id}=    Create User    shared@example.com
    Set Suite Variable    ${SHARED_USER_ID}    ${user_id}

Test B Uses Data
    [Documentation]    BAD: Depends on Test A

    # Requires SHARED_USER_ID to be set
    Delete User    ${SHARED_USER_ID}
```

**Problems:**
- Tests can't run independently
- Order-dependent failures
- Can't parallelize
- Difficult to debug
- Flaky tests

---

### ✅ GOOD: Each Test Is Isolated

```robotframework
*** Test Cases ***
Test A Is Independent
    [Documentation]    GOOD: Creates and cleans its own data

    ${user_id}=    Create User    test-a-${timestamp}@example.com
    # ... do test
    Delete User    ${user_id}

Test B Is Independent
    [Documentation]    GOOD: Creates and cleans its own data

    ${user_id}=    Create User    test-b-${timestamp}@example.com
    # ... do test
    Delete User    ${user_id}
```

**Benefits:**
- Tests are independent
- Can run in any order
- Can parallelize
- Easy to debug
- Reliable tests

---

## Quick Reference: Anti-Patterns Summary

| Anti-Pattern | Problem | Solution |
|--------------|---------|----------|
| Hardcoded data | Not flexible, insecure | Use config variables |
| Magic numbers | Unclear meaning | Use named constants |
| No cleanup | Data pollution | Use FINALLY/Teardown |
| Complex logic | Hard to read/maintain | Move to keywords |
| Test dependencies | Can't run independently | Make tests isolated |
| No error handling | Unclear failures | Use TRY/EXCEPT |
| Inefficient queries | Slow, wasteful | Optimize SQL |
| Sleep waits | Unreliable, slow | Use active waiting |
| SQL in tests | Hard to maintain | Use keywords |
| Shared state | Flaky tests | Isolate test data |

---

## Best Practices Checklist

Before committing database tests, verify:

- [ ] No hardcoded credentials or sensitive data
- [ ] All numbers are named constants
- [ ] All test data is cleaned up (FINALLY or Teardown)
- [ ] Complex logic is in keywords, not test cases
- [ ] Tests can run in any order (no dependencies)
- [ ] Error handling uses TRY/EXCEPT appropriately
- [ ] Queries select only needed columns
- [ ] No fixed Sleep delays - use active waiting
- [ ] SQL is in reusable keywords
- [ ] Each test creates its own unique data

---

## Exercise: Refactor Anti-Patterns

**Task:** Refactor the following test to follow best practices.

**Starting Code (Anti-Patterns):**
```robotframework
*** Test Cases ***
Bad Test
    Connect To Database    psycopg2    moje_app    postgres    postgres    localhost

    Execute Sql String    INSERT INTO form_data (first_name, last_name, phone, gender, email) VALUES ('Test', 'User', '+420123456789', 'male', 'test@example.com')

    Sleep    3

    ${result}=    Query    SELECT * FROM form_data
    ${count}=    Get Length    ${result}
    Should Be True    ${count} > 0
```

**Hints:**
1. Use TRY/FINALLY for cleanup
2. Use named constants
3. Use variables from config
4. Remove Sleep
5. Use Row Count instead of selecting all
6. Add cleanup

---

## Solution

See [`01_BestPractices.md`](01_BestPractices.md) for correct patterns.

The refactored test should:
- Use config variables for connection
- Use TRY/FINALLY for guaranteed cleanup
- Use Row Count for verification
- Include proper cleanup
- Have clear documentation

---

## References

- [Robot Framework Anti-Patterns](https://github.com/vshneidmiller/robot-framework-best-practices)
- [How to Write Good Test Cases](https://github.com/robotframework/HowToWriteGoodTestCases)
- [Database Library Best Practices](01_BestPractices.md)
