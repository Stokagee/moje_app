# Troubleshooting Guide

## Browser Library Issues

### Issue: "No browser found"

**Symptoms:**
```
Error: Executable doesn't exist at ...
```

**Solutions:**
```bash
# Install Playwright browsers
playwright install chromium

# Or install all browsers
playwright install
```

---

### Issue: "Element not found"

**Symptoms:**
```
Error: strict mode violation: ... resolved to 2 elements
```

**Solutions:**
- Use more specific selector
- Use `>> nth=N` to specify index
- Add unique testid attribute

```robotframework
# Instead of:
Click    button

# Use:
Click    [data-testid="submit-button"]
# Or:
Click    button >> nth=0
```

---

### Issue: "Element not clickable"

**Symptoms:**
```
Error: ElementClickInterceptedError
```

**Solutions:**
- Wait for overlay to disappear
- Scroll element into view
- Check if element is enabled

```robotframework
Wait For Elements State    [data-testid="modal"]    hidden
Click    [data-testid="button"]
```

---

### Issue: "Timeout exceeded"

**Symptoms:**
```
Error: Timeout 30000ms exceeded
```

**Solutions:**
- Increase timeout
- Check if element exists
- Verify page is fully loaded

```robotframework
# Increase timeout
Wait For Elements State    ${selector}    visible    timeout=60s

# Or check if element exists first
${exists}=    Run Keyword And Return Status
...    Get Element    ${selector}
```

---

## Requests Library Issues

### Issue: "Connection refused"

**Symptoms:**
```
Error: ConnectionError
```

**Solutions:**
```bash
# Start backend server
cd be && uvicorn app.main:app --reload

# Check URL is correct
${BASE_URL}=    Set Variable    http://localhost:8000/api/v1
```

---

### Issue: "404 Not Found"

**Symptoms:**
```
Status: 404 Not Found
```

**Solutions:**
- Check endpoint path
- Verify base URL
- Check trailing slashes

```robotframework
# Wrong:
GET On Session    api    /form    # Missing /

# Correct:
GET On Session    api    /form/
```

---

### Issue: "JSON decode error"

**Symptoms:**
```
Error: Expecting value: line 1 column 1 (char 0)
```

**Solutions:**
- Verify response is JSON
- Check Content-Type header
- Handle non-JSON responses

```robotframework
# Check Content-Type first
${content_type}=    Get From Dictionary    ${response.headers}    Content-Type
Log    Content-Type: ${content_type}

# Only parse if JSON
IF    '${content_type}' == 'application/json'
    ${json}=    Evaluate    json.loads('${response.text}')
END
```

---

### Issue: "400 Bad Request"

**Symptoms:**
```
Status: 400 Bad Request
```

**Common causes:**
- Missing required fields
- Invalid data format
- Duplicate unique field
- Wrong data type

**Debugging:**
```robotframework
${response}=    POST On Session    api    /form/    json=${data}

# Log response for details
Log    Status: ${response.status_code}
Log    Body: ${response.text}

# Parse error if available
${json}=    Evaluate    json.loads('${response.text}')    modules=json
${detail}=    Get From Dictionary    ${json}    detail
Log    Error detail: ${detail}
```

---

## Database Library Issues

### Issue: "Connection refused"

**Symptoms:**
```
Error: could not connect to server
Connection refused
```

**Solutions:**
```bash
# Start database
docker compose up -d db

# Or start local PostgreSQL
pg_ctl -D /usr/local/var/postgres start

# Check connection details
${DB_HOST}=    Set Variable    localhost
${DB_PORT}=    Set Variable    5432
```

**Robot Framework Debug:**
```robotframework
# Test connection with retry
Connect With Retry
    [Arguments]    ${max_attempts}=3
    FOR    ${attempt}    IN RANGE    ${max_attempts}
        TRY
            Connect To Database    psycopg2    ${DB_NAME}    ${DB_USER}    ${DB_PASS}    ${DB_HOST}
            ${result}=    Query    SELECT 1
            Log    ✅ Connected successfully
            RETURN
        EXCEPT    OperationalError
            Log    ⚠️  Attempt ${attempt + 1} failed: ${ERROR}
            IF    ${attempt} < ${max_attempts} - 1
                Sleep    2s
            END
        END
    END
    Fail    ❌ Could not connect after ${max_attempts} attempts
```

---

### Issue: "Authentication failed"

**Symptoms:**
```
Error: password authentication failed
FATAL: password authentication failed for user "postgres"
```

**Common Causes:**
- Wrong password in variables
- User doesn't exist
- Database not created for user

**Solutions:**
```bash
# Check PostgreSQL users
psql -U postgres -c "\du"

# Create user if needed
psql -U postgres -c "CREATE USER test_user WITH PASSWORD 'test_pass';"

# Grant privileges
psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE moje_app TO test_user;"
```

**Verify Variables:**
```robotframework
# Log credentials (without password)
Log    Connecting to: ${DB_NAME} at ${DB_HOST}:${DB_PORT}
Log    User: ${DB_USER}

# Test with connection string
${conn_str}=    Catenate    host=${DB_HOST} port=${DB_PORT} dbname=${DB_NAME} user=${DB_USER} password=${DB_PASSWORD}
Connect To Database Using Connection String    psycopg2    ${conn_str}
```

---

### Issue: "Relation does not exist"

**Symptoms:**
```
Error: relation "form_data" does not exist
```

**Solutions:**
```sql
-- Check available tables
\dt

-- Or use correct schema
SELECT * FROM public.form_data;

-- Check all schemas
SELECT table_schema, table_name FROM information_schema.tables
WHERE table_name = 'form_data';
```

**Robot Framework:**
```robotframework
# List tables before querying
${tables}=    Query    SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'
Log    Available tables: ${tables}

# Check if table exists
Table Must Exist    form_data
```

---

### Issue: "Column does not exist"

**Symptoms:**
```
Error: column "invalid_column" does not exist
```

**Solutions:**
```sql
-- Check table structure
\d form_data

-- Or query schema
SELECT column_name FROM information_schema.columns
WHERE table_name = 'form_data';

-- List all columns
SELECT * FROM information_schema.columns
WHERE table_name = 'form_data' ORDER BY ordinal_position;
```

**Robot Framework:**
```robotframework
# Verify column exists
${columns}=    Query
...    SELECT column_name
...    FROM information_schema.columns
...    WHERE table_name = 'form_data'

Log    Available columns: ${columns}
```

---

### Issue: "Query timeout"

**Symptoms:**
```
Error: canceling statement due to statement timeout
```

**Solutions:**
```robotframework
# Increase timeout
Query With Timeout
    [Arguments]    ${query}    ${timeout_s}=60

    Execute Sql String    SET statement_timeout = ${timeout_s * 1000}

    TRY
        ${result}=    Query    ${query}
        [Return]    ${result}
    FINALLY
        Execute Sql String    SET statement_timeout = 0
    END
```

**Prevention:**
- Use `LIMIT` on large queries
- Add `WHERE` clauses
- Create indexes on frequently queried columns
- Use `COUNT(*)` instead of `SELECT *`

---

### Issue: "Connection leak"

**Symptoms:**
```
Error: remaining connection slots are reserved
Tests slow down over time
```

**Detection:**
```bash
# Check active connections
psql -U postgres -d moje_app -c "SELECT count(*) FROM pg_stat_activity;"

# See connection details
psql -U postgres -d moje_app -c "SELECT * FROM pg_stat_activity WHERE datname = 'moje_app';"
```

**Solutions:**
```robotframework
# ✅ GOOD: Always disconnect in FINALLY
*** Test Cases ***
Test With Cleanup
    Connect To Database    psycopg2    ${DB_NAME}    ${DB_USER}    ${DB_PASS}    ${DB_HOST}

    TRY
        # Test code
    FINALLY
        # ALWAYS executes
        Disconnect From Database
    END

# ✅ GOOD: Use SUITE scope
*** Settings ***
Suite Setup     Connect To Database    psycopg2    ${DB_NAME}    ${DB_USER}    ${DB_PASS}    ${DB_HOST}
Suite Teardown  Disconnect From Database

# ❌ BAD: Forgetting disconnect
*** Test Cases ***
Bad Test
    Connect To Database    psycopg2    ${DB_NAME}    ${DB_USER}    ${DB_PASS}    ${DB_HOST}
    # Test code...
    # No disconnect!
```

---

### Issue: "Cleanup failed"

**Symptoms:**
```
Test data remains in database after test
Subsequent test runs fail with duplicate data
```

**Detection:**
```robotframework
# Check if test data exists before test
${count}=    Row Count    SELECT COUNT(*) FROM form_data WHERE email LIKE '%@test.example.com'
Log    Found ${count} test records before test
```

**Solutions:**
```robotframework
# ✅ GOOD: Cleanup in FINALLY
*** Test Cases ***
Test With Cleanup
    ${test_email}=    Set Variable    cleanup-test@example.com

    Connect To Database    psycopg2    ${DB_NAME}    ${DB_USER}    ${DB_PASS}    ${DB_HOST}

    TRY
        Execute Sql String    INSERT INTO form_data (email) VALUES ('${test_email}')
        # Test code...
    FINALLY
        Execute Sql String    DELETE FROM form_data WHERE email = '${test_email}'
        Disconnect From Database
    END

# ✅ GOOD: Cleanup verification
Clean Up And Verify
    [Arguments]    ${table}    ${where_clause}

    ${before}=    Row Count    SELECT COUNT(*) FROM ${table} WHERE ${where_clause}
    Execute Sql String    DELETE FROM ${table} WHERE ${where_clause}
    ${after}=    Row Count    SELECT COUNT(*) FROM ${table} WHERE ${where_clause}

    IF    ${after} > 0
        Fail    Cleanup failed: ${after} records remaining
    END

    Log    ✅ Deleted ${before} records
```

---

### Issue: "Test data conflicts"

**Symptoms:**
```
Tests fail when run in parallel
Tests pass individually but fail in suite
```

**Detection:**
```robotframework
# Check for conflicts
${count}=    Row Count    SELECT COUNT(*) FROM form_data WHERE email = '${test_email}'
IF    ${count} > 0
    Warn    Test data already exists: ${test_email}
END
```

**Solutions:**
```robotframework
# ✅ GOOD: Use unique identifiers
*** Keywords ***
Generate Unique Test Email
    ${timestamp}=    Get Time    epoch
    ${process_id}=   Evaluate    os.getpid()    modules=os
    ${email}=        Set Variable    test-${process_id}-${timestamp}@example.com
    [Return]    ${email}

# ✅ GOOD: Use test-specific prefixes
*** Test Cases ***
Test With Isolated Data
    ${test_prefix}=    Set Variable    test-${PROCESS_ID}-${timestamp}
    ${test_email}=    Set Variable    ${test_prefix}@example.com

    # Use prefix in all test data
    [Teardown]    Clean Up By Pattern    ${test_prefix}%

*** Keywords ***
Clean Up By Pattern
    [Arguments]    ${email_pattern}
    Execute Sql String    DELETE FROM form_data WHERE email LIKE '${email_pattern}'
```

---

### Issue: "SQL syntax error"

**Symptoms:**
```
Error: syntax error at or near "..."
```

**Common Causes:**
- Missing quotes around strings
- Wrong column/table name
- Missing commas
- Unescaped single quotes

**Solutions:**
```robotframework
# ✅ GOOD: Use variable interpolation
${query}=    Set Variable    SELECT * FROM form_data WHERE email = '${email}'

# ❌ BAD: Missing quotes
${query}=    Set Variable    SELECT * FROM form_data WHERE email = ${email}

# ✅ GOOD: Escape single quotes
${email}=    Replace String    ${email}    '    ''

# ✅ GOOD: Test query in DB client first
# Before using in Robot Framework, test in psql/DBeaver
```

---

### Issue: "Transaction deadlock"

**Symptoms:**
```
Error: deadlock detected
Tests hang indefinitely
```

**Solutions:**
```robotframework
# Use retry logic
Update With Retry
    [Arguments]    ${form_id}    ${new_status}

    ${max_attempts}=    Set Variable    3

    FOR    ${attempt}    IN RANGE    ${max_attempts}
        TRY
            Execute Sql String    UPDATE form_data SET status = '${new_status}' WHERE id = ${form_id}

            # Verify update
            ${result}=    Query    SELECT status FROM form_data WHERE id = ${form_id}
            Should Be Equal    ${result}[0][status]    ${new_status}

            Log    ✅ Update successful
            RETURN

        EXCEPT    OperationalError
            Log    ⚠️  Update attempt ${attempt + 1} failed: ${ERROR}
            Sleep    0.5s
        END
    END

    Fail    Update failed after ${max_attempts} attempts
```

**Prevention:**
- Keep transactions short
- Access tables in consistent order
- Use TRY/FINALLY for rollback
- Avoid long-held locks

---

### Issue: "Performance degradation"

**Symptoms:**
- Tests become slower over time
- Query times increase

**Detection:**
```robotframework
# Log query performance
${start}=    Get Time    epoch
${result}=    Query    SELECT * FROM form_data WHERE first_name = 'Jan'
${end}=    Get Time    epoch
${elapsed}=    Evaluate    ${end} - ${start}
Log    ⏱️  Query took ${elapsed}ms, returned ${len(${result})} rows
```

**Solutions:**
```robotframework
# ✅ GOOD: Use COUNT for counting
${count}=    Row Count    SELECT COUNT(*) FROM form_data

# ❌ BAD: Count in code
${result}=    Query    SELECT * FROM form_data
${count}=    Get Length    ${result}

# ✅ GOOD: Select only needed columns
${result}=    Query    SELECT id, email FROM form_data WHERE id = ${form_id}

# ❌ BAD: Select all columns
${result}=    Query    SELECT * FROM form_data WHERE id = ${form_id}

# ✅ GOOD: Use LIMIT
${result}=    Query    SELECT id FROM form_data LIMIT 100
```

---

### Database-Specific Diagnostic Checklist

When database tests fail:

- [ ] Database is running (`docker ps` or `pg_ctl status`)
- [ ] Connection details are correct (host, port, database, user, password)
- [ ] Table exists in correct schema
- [ ] Column names are correct
- [ ] SQL syntax is valid (test in psql/DBeaver first)
- [ ] Connection is closed after test (check FINALLY block)
- [ ] Test data is cleaned up (verify DELETE executed)
- [ ] No connection leaks (check active connections count)
- [ ] Query timeout is sufficient for complex queries
- [ ] Test data uses unique identifiers (for parallel execution)

---

### Database Prevention Tips

1. **Always use TRY/FINALLY for guaranteed cleanup**
2. **Use SUITE scope for connection reuse**
3. **Select only needed columns (not SELECT *)**
4. **Use COUNT(*) for counting, not Get Length**
5. **Clean up test data after each test**
6. **Use unique identifiers for test data**
7. **Verify cleanup worked (count = 0)**
8. **Test SQL in DB client before Robot Framework**
9. **Use connection retry logic for unreliable networks**
10. **Log query performance for slow tests**

---

## Docker Issues

### Issue: "Port already in use"

**Symptoms:**
```
Error: port is already allocated
```

**Solutions:**
```bash
# Check what's using port
netstat -ano | findstr :8081

# Or change port in .env
FRONTEND_PORT=3001
```

---

### Issue: "Container exits immediately"

**Symptoms:**
```
docker compose up
# Container starts and stops
```

**Solutions:**
```bash
# Check logs
docker logs moje_app_backend

# Check configuration
docker compose config

# Rebuild if needed
docker compose up --build
```

---

## General Debugging Tips

### Enable Debug Logging

```robotframework
# Run with DEBUG log level
robot --loglevel DEBUG tests/

# Or in settings
*** Settings ***
Library     Browser    timeout=30s    strict=False
```

### Take Screenshots

```robotframework
# Auto-screenshot on failure
[Teardown]    Run Keyword If Test Failed    Take Screenshot

# Or capture page state
Take Screenshot    filename=debug_state.png
```

### Use Breakpoints

```robotframework
*** Keywords ***
Debug Pause
    Pause Execution    # Manual continue required
```

### Inspect Page State

```robotframework
*** Keywords ***
Log Page State
    ${url}=    Get Url
    ${title}=  Get Title
    Log    URL: ${url}
    Log    Title: ${title}

    # Log all elements with testids
    ${elements}=    Get Elements    [data-testid]
    Log    Found ${elements} elements
```

---

## Common Error Messages

### "Variable '${VAR}' not found"

**Cause:** Variable not defined
**Fix:** Define variable in *** Variables *** section or pass as argument

### "No keyword with name 'X' found"

**Cause:** Typo or library not imported
**Fix:** Check spelling, import library

### "Expected keyword but got 'X'"

**Cause:** Syntax error
**Fix:** Check proper section headers and indentation

### "Test case failed"

**Cause:** Assertion failed
**Fix:** Review test logs for specific failure reason

---

## Performance Issues

### Slow Test Execution

**Solutions:**
```bash
# Run tests in parallel
pabot --processes 4 tests/

# Use headless mode
${HEADLESS}=    Set Variable    ${True}

# Reduce waits
Wait For Elements State    ${selector}    visible    timeout=5s
```

### Browser Startup Slow

**Solutions:**
```robotframework
# Reuse browser context
Suite Setup     New Browser    chromium    headless=${True}
Suite Teardown  Close Browser

# Instead of per-test
Test Setup      New Browser    chromium
Test Teardown   Close Browser
```

---

## Environment-Specific Issues

### CI/CD Failures

**Common causes:**
- Missing dependencies
- Environment variables not set
- Browser not installed
- Database not accessible

**Solutions:**
```bash
# Install dependencies in CI
pip install -r requirements.txt

# Set environment variables
export HEADLESS=true

# Use Xvfb for virtual display (Linux)
xvfb-run robot tests/
```

### Local vs Production Differences

**Debugging:**
```robotframework
# Log environment variables
${env}=    Get Environment Variables
Log    Environment: ${env}

# Check URL
${base_url}=    Set Variable If    %{ENVIRONMENT} == 'prod'
...    http://prod.example.com
...    http://localhost:8000
```

---

## Getting Help

### Check Logs
```bash
# View full output
robot --outputdir results/ --loglevel DEBUG tests/

# Check log.html
# Open results/log.html in browser
```

### Verify Setup
```bash
# Test Python installation
python --version

# Test RF installation
robot --version

# Test libraries
python -c "import robotframework; import robotframework_browser; import robotframework_requests"

# Test database connection
psql -h localhost -U postgres -d moje_app
```

### Community Resources
- [Robot Framework Forum](https://forum.robotframework.org/)
- [Browser Library GitHub](https://github.com/MarketSquare/robotframework-browser/issues)
- [StackOverflow](https://stackoverflow.com/questions/tagged/robotframework)

---

## Quick Fixes

| Issue | Quick Fix |
|-------|-----------|
| Import error | Install missing library |
| Port occupied | Change port number |
| Timeout | Increase timeout value |
| Element not found | Check selector, wait for element |
| Connection refused | Start required service |
| 404 error | Verify endpoint URL |
| 500 error | Check server logs |
| JSON parse error | Verify response format |
| SQL error | Test query in DB client |

---

## Prevention Tips

1. **Always verify environment before running tests**
2. **Use version control for dependencies**
3. **Clean up test data after tests**
4. **Use specific, stable selectors**
5. **Add proper waits, not Sleep**
6. **Log meaningful messages**
7. **Take screenshots on failures**
8. **Handle errors gracefully**
9. **Test in isolation before integrating**
10. **Keep tests independent**

---

## Diagnostic Checklist

When tests fail:

- [ ] Check environment (servers running, correct ports)
- [ ] Verify dependencies installed
- [ ] Review test logs for error messages
- [ ] Check application logs for errors
- [ ] Run test in isolation
- [ ] Run with debug output
- [ ] Verify test data exists
- [ ] Check recent code changes
- [ ] Compare with similar working test
- [ ] Simplify test to find root cause
