# Performance Patterns (ADVANCED)

## Learning Objectives
- [ ] Optimize SQL queries for performance
- [ ] Minimize database roundtrips
- [ ] Use efficient data retrieval patterns
- [ ] Implement query result caching
- [ ] Apply batch operation patterns
- [ ] Understand parallel execution considerations

---

## Overview

Database testing can become a bottleneck in test suites. These patterns ensure your database tests run efficiently while maintaining reliability.

---

## 1. Query Optimization

### Pattern: Select Specific Columns

**❌ BAD: Select All Columns**
```robotframework
*** Keywords ***
Get Form Email
    [Arguments]    ${form_id}
    # Returns ALL columns - wasteful
    ${result}=    Query    SELECT * FROM form_data WHERE id = ${form_id}
    ${email}=    Set Variable    ${result}[0][email]
    [Return]    ${email}
```

**✅ GOOD: Select Only Needed Columns**
```robotframework
*** Keywords ***
Get Form Email
    [Arguments]    ${form_id}
    # Returns only email - efficient
    ${result}=    Query    SELECT email FROM form_data WHERE id = ${form_id}
    ${email}=    Set Variable    ${result}[0][email]
    [Return]    ${email}
```

**Performance Impact:**
- Reduced network traffic
- Less memory usage
- Faster query execution

---

### Pattern: Use LIMIT for Large Results

**❌ BAD: No Limit**
```robotframework
*** Keywords ***
Get All Forms
    # Could return thousands of rows
    ${result}=    Query    SELECT * FROM form_data
    [Return]    ${result}
```

**✅ GOOD: Use LIMIT**
```robotframework
*** Keywords ***
Get First 100 Forms
    # Limits result size
    ${result}=    Query    SELECT id, email FROM form_data LIMIT 100
    [Return]    ${result}
```

**✅ BETTER: Use COUNT for Existence Check**
```robotframework
*** Keywords ***
Check Forms Exist
    # Just need count, not data
    ${count}=    Row Count    SELECT COUNT(*) FROM form_data
    [Return]    ${count}
```

---

### Pattern: Use WHERE Clause Effectively

**❌ BAD: Fetch Then Filter**
```robotframework
*** Keywords ***
Get Active Forms
    ${result}=    Query    SELECT * FROM form_data

    # Filter in Robot Framework (inefficient)
    @{active}=    Create List
    FOR    ${row}    IN    @{result}
        IF    '${row}[status]' == 'active'
            Append To List    ${active}    ${row}
        END
    END
    [Return]    ${active}
```

**✅ GOOD: Filter in SQL**
```robotframework
*** Keywords ***
Get Active Forms
    # Let database do filtering
    ${result}=    Query    SELECT * FROM form_data WHERE status = 'active'
    [Return]    ${result}
```

---

## 2. Minimize Database Roundtrips

### Pattern: Batch Operations

**❌ BAD: Multiple Queries**
```robotframework
*** Keywords ***
Create Multiple Forms
    # N database calls - slow
    FOR    ${i}    IN RANGE    100
        Execute Sql String    INSERT INTO form_data (email) VALUES ('test${i}@example.com')
    END
```

**✅ GOOD: Single Batch Insert**
```robotframework
*** Keywords ***
Create Multiple Forms Efficiently
    [Documentation]    Batch insert using VALUES clause

    # Build batch insert statement
    ${values}=    Create List
    FOR    ${i}    IN RANGE    100
        ${value}=    Set Variable    ('test${i}@example.com')
        Append To List    ${values}    ${value}
    END

    # Single query with multiple VALUES
    ${values_str}=    Evaluate    ','.join(${values})    modules=string
    ${query}=    Set Variable    INSERT INTO form_data (email) VALUES ${values_str}

    Execute Sql String    ${query}
    Log    Inserted 100 forms in single query
```

---

### Pattern: Fetch Multiple IDs Once

**❌ BAD: Query in Loop**
```robotframework
*** Keywords ***
Verify Multiple Forms
    [Arguments]    @{form_ids}

    FOR    ${form_id}    IN    @{form_ids}
        # N queries - very slow
        ${result}=    Query    SELECT * FROM form_data WHERE id = ${form_id}
        Should Not Be Empty    ${result}
    END
```

**✅ GOOD: Single Query with IN**
```robotframework
*** Keywords ***
Verify Multiple Forms
    [Arguments]    @{form_ids}

    # Convert list to SQL IN clause
    ${id_list}=    Evaluate    ','.join(map(str, ${form_ids}))    modules=string
    ${query}=    Set Variable    SELECT * FROM form_data WHERE id IN (${id_list})

    ${result}=    Query    ${query}

    # Verify all forms exist
    ${count}=    Get Length    ${result}
    Should Be Equal As Integers    ${count}    ${form_ids.__len__}

    [Return]    ${result}
```

---

### Pattern: Use EXISTS Instead of IN

**❌ BAD: IN Subquery**
```robotframework
# Checks all rows (potentially slow)
${result}=    Query
...    SELECT * FROM form_data
...    WHERE id IN (SELECT form_id FROM instructions WHERE text LIKE '%test%')
```

**✅ GOOD: EXISTS Subquery**
```robotframework
# Stops at first match (faster)
${result}=    Query
...    SELECT * FROM form_data f
...    WHERE EXISTS (SELECT 1 FROM instructions i WHERE i.form_id = f.id AND i.text LIKE '%test%')
```

---

## 3. Efficient Counting

### Pattern: Count Efficiently

**❌ BAD: Count All Rows**
```robotframework
*** Keywords ***
Count All Forms
    # Returns all data just to count
    ${result}=    Query    SELECT * FROM form_data
    ${count}=    Get Length    ${result}
    [Return]    ${count}
```

**✅ GOOD: Use COUNT Aggregate**
```robotframework
*** Keywords ***
Count All Forms
    # Database does counting - much faster
    ${count}=    Row Count    SELECT COUNT(*) FROM form_data
    [Return]    ${count}
```

---

### Pattern: Conditional Count

**❌ BAD: Count Then Check**
```robotframework
*** Keywords ***
HasActiveForms
    ${count}=    Row Count    SELECT COUNT(*) FROM form_data
    ${has_active}=    Set Variable    ${count} > 0
    [Return]    ${has_active}
```

**✅ GOOD: Let Database Check**
```robotframework
*** Keywords ***
HasActiveForms
    # Use EXISTS - stops at first match
    ${result}=    Query    SELECT 1 FROM form_data WHERE status = 'active' LIMIT 1
    ${has_active}=    Set Variable    ${len(${result}) > 0
    [Return]    ${has_active}
```

---

## 4. Query Result Caching

### Pattern: Cache Reference Data

```robotframework
*** Settings ***
Suite Setup     Load Reference Data
Suite Teardown  Clear Reference Data

*** Variables ***
# Cached reference data
${REFERENCE_DATA}=    ${EMPTY}

*** Keywords ***
Load Reference Data
    [Documentation]    Cache reference data for suite

    Log    Loading reference data...

    ${result}=    Query
    ...    SELECT id, name FROM couriers WHERE status = 'available'

    Set Suite Variable    ${REFERENCE_DATA}    ${result}
    Log    ✅ Loaded ${len(${result})} reference records

Get Courier Name
    [Arguments]    ${courier_id}
    [Documentation]    Get from cache instead of query

    ${courier}=    Find In Dictionary    ${REFERENCE_DATA}    id    ${courier_id}
    [Return]    ${courier}[name]

Clear Reference Data
    Set Suite Variable    ${REFERENCE_DATA}    ${EMPTY}
```

---

## 5. Index Awareness

### Pattern: Query Using Indexes

```robotframework
*** Keywords ***
Efficient Lookup
    [Documentation]    Query that uses indexes

    # Uses index on email (UNIQUE)
    ${result}=    Query    SELECT id FROM form_data WHERE email = 'test@example.com'

    # Uses index on first_name
    ${result}=    Query    SELECT id FROM form_data WHERE first_name = 'Jan'

    [Return]    ${result}
```

**Note:** Check your schema for indexed columns:
- Primary keys are automatically indexed
- UNIQUE constraints create indexes
- Add indexes for frequently queried columns

---

### Pattern: Avoid Function on Indexed Column

**❌ BAD: Function prevents index use**
```robotframework
# Index on email won't be used
${result}=    Query    SELECT * FROM form_data WHERE LOWER(email) = 'test@example.com'
```

**✅ GOOD: Direct comparison uses index**
```robotframework
# Index can be used
${result}=    Query    SELECT * FROM form_data WHERE email = 'test@example.com'
```

---

## 6. Connection Pooling

### Pattern: Reuse Connection

```robotframework
*** Settings ***
Library     DatabaseLibrary

Suite Setup     Connect To Database
Suite Teardown  Disconnect From Database

*** Test Cases ***
Test One
    # Reuses connection
    ${result}=    Query    SELECT COUNT(*) FROM form_data

Test Two
    # Reuses connection again
    ${result}=    Query    SELECT COUNT(*) FROM couriers
```

**Performance Impact:**
- Avoids connection overhead
- Reduces database load
- Faster test execution

---

## 7. Parallel Execution Considerations

### Pattern: Avoid Write Conflicts

```robotframework
*** Variables ***
# Unique identifier per test process
${TEST_PREFIX}=    ${EMPTY}

*** Test Cases ***
Parallel Safe Test
    [Documentation]    Test safe for parallel execution

    # Generate unique identifier
    ${process_id}=    Evaluate    os.getpid()    modules=os
    ${timestamp}=    Get Time    epoch
    ${TEST_PREFIX}=    Set Variable    test-${process_id}-${timestamp}

    # Use unique identifier in data
    ${test_email}=    Set Variable    ${TEST_PREFIX}@example.com
    Create Test Form    ${test_email}

    # Clean up with unique identifier
    [Teardown]    Clean Up Test Data    ${TEST_PREFIX}
```

---

### Pattern: Database Lock Awareness

```robotframework
*** Keywords ***
Update With Retry
    [Documentation]    Handle potential lock conflicts
    [Arguments]    ${form_id}    ${new_status}

    ${max_attempts}=    Set Variable    3

    FOR    ${attempt}    IN RANGE    ${max_attempts}
        TRY
            Execute Sql String
            ...    UPDATE form_data SET status = '${new_status}' WHERE id = ${form_id}

            # Verify update
            ${result}=    Query    SELECT status FROM form_data WHERE id = ${form_id}
            Should Be Equal    ${result}[0][status]    ${new_status}

            Log    ✅ Update successful
            RETURN    # Success - exit

        EXCEPT    OperationalError
            # Could be lock conflict
            Log    ⚠️  Update attempt ${attempt + 1} failed: ${ERROR}
            Sleep    0.5s
        END
    END

    Fail    Update failed after ${max_attempts} attempts
```

---

## 8. Batch Verification

### Pattern: Verify in Bulk

**❌ BAD: Verify Row by Row**
```robotframework
*** Keywords ***
Verify Forms Exist
    [Arguments]    @{form_ids}

    FOR    ${form_id}    IN    @{form_ids}
        ${result}=    Query    SELECT * FROM form_data WHERE id = ${form_id}
        Should Not Be Empty    ${result}
    END
```

**✅ GOOD: Verify All at Once**
```robotframework
*** Keywords ***
Verify Forms Exist
    [Arguments]    @{form_ids}

    ${id_list}=    Evaluate    ','.join(map(str, ${form_ids}))    modules=string
    ${query}=    Set Variable    SELECT id FROM form_data WHERE id IN (${id_list})

    ${result}=    Query    ${query}
    ${found}=    Get Length    ${result}
    ${expected}=    Get Length    ${form_ids}

    Should Be Equal As Integers    ${found}    ${expected}
```

---

## 9. Query Execution Plan Awareness

### Pattern: Use EXPLAIN for Analysis

```robotframework
*** Keywords ***
Analyze Query Performance
    [Documentation]    Check query execution plan

    ${result}=    Query    EXPLAIN ANALYZE SELECT * FROM form_data WHERE email = 'test@example.com'

    # Log execution plan for analysis
    FOR    ${row}    IN    @{result}
        Log    Plan: ${row}[QUERY PLAN]
    END
```

**When to Use:**
- Test is running slowly
- Need to optimize query
- Understanding index usage

---

## 10. Asynchronous Testing Pattern

### Pattern: Non-Blocking Queries

```robotframework
*** Keywords ***
Background Query Check
    [Documentation]    Check if query completes within timeout

    ${start_time}=    Get Time    epoch

    # Run query with timeout handling
    ${result}=    Query With Timeout
    ...    SELECT * FROM large_table WHERE complex_condition
    ...    timeout_s=30

    ${end_time}=    Get Time    epoch
    ${elapsed}=    Evaluate    ${end_time} - ${start_time}

    Log    Query completed in ${elapsed}ms

    [Return]    ${result}

*** Keywords ***
Query With Timeout
    [Documentation]    Query with timeout protection
    [Arguments]    ${query}    ${timeout_s}=30

    ${start}=    Get Time    epoch

    TRY
        ${result}=    Query    ${query}

        ${end}=    Get Time    epoch
        ${elapsed}=    Evaluate    ${end} - ${start}

        IF    ${elapsed} > ${timeout_s * 1000}
            Warn    Query exceeded ${timeout_s}s timeout (took ${elapsed}ms)

        [Return]    ${result}

    EXCEPT    OperationalError
        ${end}=    Get Time    epoch
        ${elapsed}=    Evaluate    ${end} - ${start}

        IF    ${elapsed} > ${timeout_s * 1000}
            Fail    Query timed out after ${timeout_s}s
        ELSE
            Fail    Query failed: ${ERROR}
        END
    END
```

---

## Performance Monitoring

### Pattern: Log Query Performance

```robotframework
*** Keywords ***
Query With Metrics
    [Documentation]    Execute query and log performance

    ${start}=    Get Time    epoch

    ${result}=    Query    SELECT * FROM form_data WHERE first_name = 'Jan'

    ${end}=    Get Time    epoch
    ${elapsed}=    Evaluate    ${end} - ${start}

    ${row_count}=    Get Length    ${result}

    Log    ⏱️  Query: SELECT * FROM form_data WHERE first_name = 'Jan'
    Log    ⏱️  Rows: ${row_count} | Time: ${elapsed}ms | Rate: ${elapsed / row_count if $row_count > 0 else 0} ms/row

    [Return]    ${result}
```

---

## Performance Best Practices Summary

| Pattern | Benefit | Use When |
|---------|---------|---------|
| Select specific columns | Less data transfer | Need specific fields |
| Use LIMIT | Prevents large results | Don't need all rows |
| Batch operations | Fewer roundtrips | Multiple inserts/updates |
| COUNT aggregate | Faster counting | Just need count |
| EXISTS subquery | Stops at first match | Checking existence |
| Connection reuse | Less overhead | Multiple tests |
| Unique identifiers | Parallel safe | Parallel execution |
| Query verification | Confirm optimization | Performance issues |
| Performance logging | Identify bottlenecks | Slow tests |

---

## Performance Checklist

Before finalizing database tests, verify:

- [ ] Queries select only needed columns
- [ ] LIMIT used for large result sets
- [ ] COUNT(*) used instead of counting in code
- [ ] Batch operations for multiple inserts/updates
- [ ] Single query with IN instead of loop
- [ ] Connection reused across tests (SUITE scope)
- [ ] Unique identifiers for parallel execution
- [ ] Query performance logged for slow tests
- [ ] EXPLAIN ANALYZE used for optimization
- [ ] Cleanup uses efficient patterns (DELETE with pattern)

---

## References

- [PostgreSQL Query Planning](https://www.postgresql.org/docs/sql-explain.html)
- [Database Performance Best Practices](../BEGINNER/01_BestPractices.md)
- [Connection Management](../INTERMEDIATE/00_ConnectionManagement.md)
