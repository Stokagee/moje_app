# Cleanup Strategies (INTERMEDIATE)

## Learning Objectives
- [ ] Understand FINALLY block for guaranteed cleanup
- [ ] Implement Teardown-based cleanup
- [ ] Use Suite-level cleanup patterns
- [ ] Apply tag-based cleanup strategies
- [ ] Handle cleanup failures gracefully

---

## Overview

Proper cleanup is essential for reliable database testing. Without it:
- Test data accumulates
- Tests become flaky
- Debugging becomes difficult
- Parallel execution is impossible

---

## 1. FINALLY Block Pattern

### Best For: Guaranteed cleanup regardless of test outcome

```robotframework
*** Test Cases ***
Test With Guaranteed Cleanup
    [Documentation]    FINALLY block always executes

    ${test_email}=    Set Variable    cleanup-test-${timestamp}@example.com

    Connect To Database    psycopg2    ${DB_NAME}    ${DB_USER}    ${DB_PASS}    ${DB_HOST}

    TRY
        # Create test data
        Execute Sql String    INSERT INTO form_data (email) VALUES ('${test_email}')

        # Verify creation
        ${count}=    Row Count    SELECT COUNT(*) FROM form_data WHERE email = '${test_email}'
        Should Be Equal As Integers    ${count}    1

        Log    ✅ Test passed

    EXCEPT
        Log    ❌ Test failed: ${ERROR}

    FINALLY
        # ALWAYS executes - even on test failure
        Execute Sql String    DELETE FROM form_data WHERE email = '${test_email}'
        Disconnect From Database
        Log    🧹 Cleanup complete

    END
```

**Key Points:**
- FINALLY executes regardless of TRY/EXCEPT outcome
- Perfect for database disconnection
- Ensures cleanup even on assertion failure
- Nesting TRY/EXCEPT/ELSE/FINALLY possible

---

### Nested TRY/FINALLY Pattern

```robotframework
*** Test Cases ***
Nested Cleanup Example
    Connect To Database    psycopg2    ${DB_NAME}    ${DB_USER}    ${DB_PASS}    ${DB_HOST}

    TRY
        # Outer TRY - main test logic
        ${form_id}=    Create Test Form

        TRY
            # Inner TRY - verification
            Verify Form In Database    ${form_id}
            Log    ✅ Verification passed

        FINALLY
            # Inner FINALLY - local cleanup
            Delete Form    ${form_id}
            Log    🧹 Form deleted
        END

    EXCEPT
        Log    ❌ Test failed

    FINALLY
        # Outer FINALLY - database cleanup
        Disconnect From Database
        Log    🧹 Database disconnected
    END
```

---

## 2. Teardown Pattern

### Best For: Automatic cleanup after each test

```robotframework
*** Settings ***
Test Teardown    Clean Up Test Data

*** Test Cases ***
Test One
    [Documentation]    Cleanup runs after this test
    ${test_email}=    Set Variable    test-one-${timestamp}@example.com
    Create Test Form    ${test_email}

Test Two
    [Documentation]    Cleanup runs after this test too
    ${test_email}=    Set Variable    test-two-${timestamp}@example.com
    Create Test Form    ${test_email}

*** Keywords ***
Clean Up Test Data
    [Documentation]    Called automatically after each test

    Log    Running teardown cleanup...

    TRY
        # Clean up test data created by tests
        Execute Sql String    DELETE FROM form_data WHERE email LIKE '%@test-*.example.com'
        Log    ✅ Test data cleaned up

    EXCEPT
        Log    ⚠️  Cleanup failed (non-critical): ${ERROR}
        # Don't fail test if cleanup fails
    END
```

---

### Teardown with Conditional Cleanup

```robotframework
*** Settings ***
Test Teardown    Clean Up If Needed

*** Variables ***
# Track if test created data
${TEST_DATA_CREATED}=    ${FALSE}
${TEST_IDENTIFIER}=    ${EMPTY}

*** Test Cases ***
Test With Optional Cleanup
    ${TEST_IDENTIFIER}=    Set Variable    test-${timestamp}

    # Create test data
    Execute Sql String    INSERT INTO form_data (email) VALUES ('${TEST_IDENTIFIER}@test.com')

    # Mark that cleanup is needed
    Set Suite Variable    ${TEST_DATA_CREATED}    ${TRUE}

*** Keywords ***
Clean Up If Needed
    [Documentation]    Only cleanup if test created data

    IF    ${TEST_DATA_CREATED}
        Log    Cleaning up test data...

        TRY
            Execute Sql String    DELETE FROM form_data WHERE email LIKE '${TEST_IDENTIFIER}@%'
            Log    ✅ Cleanup complete
        EXCEPT
            Log    ⚠️  Cleanup failed: ${ERROR}
        END

        # Reset flag
        Set Suite Variable    ${TEST_DATA_CREATED}    ${FALSE}
    ELSE
        Log    No cleanup needed (test didn't create data)
    END
```

---

## 3. Suite-Level Cleanup

### Best For: Cleanup after entire test suite

```robotframework
*** Settings ***
Suite Setup     Initialize Test Suite
Suite Teardown  Clean Up Suite Data

*** Variables ***
# Track all test data created during suite
@{CREATED_IDS}    @{EMPTY}

*** Test Cases ***
Test One
    [Documentation]    Track created ID for suite cleanup

    ${form_id}=    Create Test Form    test-1@example.com

    # Add to cleanup list
    Append To List    ${CREATED_IDS}    ${form_id}
    Set Suite Variable    ${CREATED_IDS}    ${CREATED_IDS}

Test Two
    [Documentation]    Track another ID

    ${form_id}=    Create Test Form    test-2@example.com

    # Add to cleanup list
    Append To List    ${CREATED_IDS}    ${form_id}
    Set Suite Variable    ${CREATED_IDS}    ${CREATED_IDS}

*** Keywords ***
Clean Up Suite Data
    [Documentation]    Clean up all data created during suite

    Log    Suite teardown: cleaning up ${CREATED_IDS} IDs...

    Connect To Database    psycopg2    ${DB_NAME}    ${DB_USER}    ${DB_PASS}    ${DB_HOST}

    TRY
        FOR    ${form_id}    IN    @{CREATED_IDS}
            TRY
                Execute Sql String    DELETE FROM form_data WHERE id = ${form_id}
                Log    ✅ Deleted form ${form_id}
            EXCEPT
                Log    ⚠️  Failed to delete form ${form_id}: ${ERROR}
            END
        END

        Log    Suite cleanup complete

    FINALLY
        Disconnect From Database
    END
```

---

## 4. Tag-Based Cleanup

### Best For: Selective cleanup based on test tags

```robotframework
*** Settings ***
Suite Teardown  Tag Based Cleanup

*** Variables ***
# Tag-based cleanup tracking
${CREATED_BY_SMOKE}=    @{EMPTY}
${CREATED_BY_REGRESSION}=    @{EMPTY}

*** Test Cases ***
Smoke Test
    [Tags]    smoke
    [Documentation]    Smoke test creates tracked data

    ${form_id}=    Create Test Form    smoke@example.com
    Append To List    ${CREATED_BY_SMOKE}    ${form_id}
    Set Suite Variable    ${CREATED_BY_SMOKE}    ${CREATED_BY_SMOKE}

Regression Test
    [Tags]    regression
    [Documentation]    Regression test creates different data

    ${form_id}=    Create Test Form    regression@example.com
    Append To List    ${CREATED_BY_REGRESSION}    ${form_id}
    Set Suite Variable    ${CREATED_BY_REGRESSION}    ${CREATED_BY_REGRESSION}

*** Keywords ***
Tag Based Cleanup
    [Documentation]    Clean up based on which tests ran

    # Check if smoke tests ran
    ${smoke_count}=    Get Length    ${CREATED_BY_SMOKE}
    IF    ${smoke_count} > 0
        Log    Cleaning up ${smoke_count} smoke test records...
        Delete Forms    @{CREATED_BY_SMOKE}
    END

    # Check if regression tests ran
    ${regression_count}=    Get Length    ${CREATED_BY_REGRESSION}
    IF    ${regression_count} > 0
        Log    Cleaning up ${regression_count} regression test records...
        Delete Forms    @{CREATED_BY_REGRESSION}
    END

Delete Forms
    [Arguments]    @{form_ids}
    Connect To Database    psycopg2    ${DB_NAME}    ${DB_USER}    ${DB_PASS}    ${DB_HOST}

    FOR    ${form_id}    IN    @{form_ids}
        Execute Sql String    DELETE FROM form_data WHERE id = ${form_id}
        Log    Deleted form ${form_id}
    END

    Disconnect From Database
```

---

## 5. Cleanup by Pattern Matching

### Best For: Cleaning up test data by pattern

```robotframework
*** Keywords ***
Clean Up By Email Pattern
    [Documentation]    Remove all test data matching email pattern
    [Arguments]    ${email_pattern}

    Connect To Database    psycopg2    ${DB_NAME}    ${DB_USER}    ${DB_PASS}    ${DB_HOST}

    TRY
        ${before_count}=    Row Count    SELECT COUNT(*) FROM form_data WHERE email LIKE '${email_pattern}'

        Execute Sql String    DELETE FROM form_data WHERE email LIKE '${email_pattern}'

        ${after_count}=    Row Count    SELECT COUNT(*) FROM form_data WHERE email LIKE '${email_pattern}'

        ${deleted}=    Evaluate    ${before_count} - ${after_count}
        Log    ✅ Deleted ${deleted} records matching pattern: ${email_pattern}

    FINALLY
        Disconnect From Database
    END
```

**Usage:**
```robotframework
*** Test Cases ***
Test With Pattern Cleanup
    # Create data with known pattern
    Execute Sql String    INSERT INTO form_data (email) VALUES ('rf-test-123@test.com')

    # Clean up all test data
    [Teardown]    Clean Up By Email Pattern    %@test.com
```

---

## 6. Transaction Rollback Cleanup

### Best For: Tests that should leave no trace

```robotframework
*** Test Cases ***
Test With Transaction Rollback
    [Documentation]    All changes rolled back at end

    Connect To Database    psycopg2    ${DB_NAME}    ${DB_USER}    ${DB_PASS}    ${DB_HOST}

    # Start transaction
    Begin Transaction

    # Create test data (not committed yet)
    Execute Sql String    INSERT INTO form_data (first_name, email) VALUES ('Test', 'test@example.com')

    # Verify data exists
    ${count}=    Row Count    SELECT COUNT(*) FROM form_data WHERE email = 'test@example.com'
    Should Be Equal As Integers    ${count}    1

    # Rollback instead of DELETE
    Rollback Transaction

    # Verify data is gone
    ${count}=    Row Count    SELECT COUNT(*) FROM form_data WHERE email = 'test@example.com'
    Should Be Equal As Integers    ${count}    0

    Log    ✅ Transaction rolled back - no data left

    Disconnect From Database
```

**Benefits:**
- Very fast cleanup (single ROLLBACK command)
- No orphaned data if test crashes
- Atomic operation

**Caveats:**
- Can't test commit behavior
- Requires transaction support
- Not suitable for all tests

---

## 7. Cleanup Failure Handling

### Pattern: Graceful Cleanup Failure

```robotframework
*** Keywords ***
Safe Cleanup
    [Documentation]    Cleanup that doesn't fail the test
    [Arguments]    ${cleanup_id}

    Log    Attempting cleanup for: ${cleanup_id}

    TRY
        Execute Sql String    DELETE FROM form_data WHERE id = ${cleanup_id}
        Log    ✅ Cleanup successful

    EXCEPT    OperationalError
        Log    ⚠️  Cleanup failed (non-critical): ${ERROR}
        # Don't fail test

    EXCEPT
        Log    ⚠️  Unexpected cleanup error: ${ERROR}
        # Log but don't fail test

    END
```

**Usage:**
```robotframework
*** Test Cases ***
Test With Safe Cleanup
    ${form_id}=    Create Test Form

    # Test code here...

    [Teardown]    Safe Cleanup    ${form_id}
    # Test won't fail even if cleanup fails
```

---

## 8. Recursive Cleanup

### Pattern: Cleanup Related Tables

```robotframework
*** Keywords ***
Clean Up Form With Relations
    [Documentation]    Clean up form and related records
    [Arguments]    ${form_id}

    Connect To Database    psycopg2    ${DB_NAME}    ${DB_USER}    ${DB_PASS}    ${DB_HOST}

    TRY
        # Delete in reverse dependency order
        Execute Sql String    DELETE FROM instructions WHERE form_id = ${form_id}
        Log    Deleted instructions

        Execute Sql String    DELETE FROM attachments WHERE form_data_id = ${form_id}
        Log    Deleted attachments

        Execute Sql String    DELETE FROM form_data WHERE id = ${form_id}
        Log    Deleted form

        Log    ✅ Complete cleanup for form ${form_id}

    EXCEPT
        Log    ❌ Cleanup failed: ${ERROR}
        # Consider manual cleanup or notification

    FINALLY
        Disconnect From Database
    END
```

---

## 9. Cleanup Verification

### Pattern: Verify Cleanup Worked

```robotframework
*** Keywords ***
Clean Up And Verify
    [Documentation]    Cleanup and verify data is gone
    [Arguments]    ${table}    ${where_clause}

    Connect To Database    psycopg2    ${DB_NAME}    ${DB_USER}    ${DB_PASS}    ${DB_HOST}

    TRY
        # Get count before cleanup
        ${before}=    Row Count    SELECT COUNT(*) FROM ${table} WHERE ${where_clause}

        # Perform cleanup
        Execute Sql String    DELETE FROM ${table} WHERE ${where_clause}

        # Verify cleanup worked
        ${after}=    Row Count    SELECT COUNT(*) FROM ${table} WHERE ${where_clause}

        IF    ${after} > 0
            Fail    Cleanup failed: ${after} records remaining
        END

        Log    ✅ Verified cleanup: deleted ${before} records

    FINALLY
        Disconnect From Database
    END
```

---

## 10. Automated Cleanup Scheduling

### Pattern: Scheduled Cleanup

```robotframework
*** Keywords ***
Scheduled Cleanup
    [Documentation]    Periodic cleanup of old test data
    [Arguments]    ${days_old}=7

    Connect To Database    psycopg2    ${DB_NAME}    ${DB_USER}    ${DB_PASS}    ${DB_HOST}

    TRY
        # Delete test data older than N days
        Execute Sql String
        ...    DELETE FROM form_data
        ...    WHERE email LIKE '%@test.example.com'
        ...    AND created_at < NOW() - INTERVAL '${days_old} days'

        Log    ✅ Cleaned up test data older than ${days_old} days

    EXCEPT
        Log    ❌ Scheduled cleanup failed: ${ERROR}

    FINALLY
        Disconnect From Database
    END
```

---

## Cleanup Patterns Summary

| Pattern | Use Case | Benefit |
|---------|----------|---------|
| FINALLY block | Guaranteed cleanup | Always executes |
| Teardown | Automatic cleanup | Runs after each test |
| Suite cleanup | Batch cleanup | Single cleanup for all tests |
| Tag-based | Selective cleanup | Different cleanup per test type |
| Pattern matching | Bulk cleanup | Remove by wildcard pattern |
| Transaction rollback | Instant rollback | Fast, atomic cleanup |
| Safe cleanup | Non-critical cleanup | Test won't fail if cleanup fails |
| Recursive cleanup | Related tables | Cleans all dependencies |
| Verification | Ensure cleanup | Confirms data is gone |

---

## Anti-Patterns

### ❌ Don't: Cleanup in Test Body

```robotframework
*** Test Cases ***
Bad Cleanup
    Create Test Form
    # Test code...
    Delete Test Form    # Cleanup in test body
```

### ✅ Do: Cleanup in Teardown/FINALLY

```robotframework
*** Settings ***
Test Teardown    Delete Test Form

*** Test Cases ***
Good Cleanup
    Create Test Form
    # Test code...
    # Cleanup happens automatically
```

---

### ❌ Don't: Assume Cleanup Succeeded

```robotframework
# BAD - Assumes cleanup worked
Execute Sql String    DELETE FROM form_data WHERE id = ${form_id}
# Continues without verification
```

### ✅ Do: Verify Cleanup

```robotframework
# GOOD - Verifies cleanup
Execute Sql String    DELETE FROM form_data WHERE id = ${form_id}
${count}=    Row Count    SELECT COUNT(*) FROM form_data WHERE id = ${form_id}
Should Be Equal As Integers    ${count}    0
```

---

## Best Practices Checklist

Before using cleanup strategies, verify:

- [ ] FINALLY block used for critical cleanup (disconnect)
- [ ] Teardown used for data cleanup
- [ ] Cleanup verified (data actually removed)
- [ ] Cleanup failures don't fail tests (unless critical)
- [ ] Recursive cleanup handles related tables
- [ ] Unique test data identifiers prevent conflicts
- [ ] Suite cleanup for batch operations
- [ ] Pattern matching for bulk cleanup
- [ ] Cleanup logged for debugging
- [ ] Transaction rollback used where appropriate

---

## References

- [Best Practices Guide](../BEGINNER/01_BestPractices.md)
- [Connection Management](00_ConnectionManagement.md)
- [PostgreSQL DELETE Documentation](https://www.postgresql.org/docs/sql-dml.html#SQL-DELETE)
