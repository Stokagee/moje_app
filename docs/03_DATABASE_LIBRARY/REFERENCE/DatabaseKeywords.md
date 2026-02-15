# Database Library Keywords Reference

## Overview

Complete reference for Robot Framework Database Library keywords used in testing PostgreSQL databases.

---

## Connection Keywords

### Connect To Database

Establishes a connection to a PostgreSQL database.

**Syntax:**
```robotframework
Connect To Database    ${dbapi}    ${database}    ${username}    ${password}    ${host}    ${port}=${5432}
```

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| dbapi | string | Yes | Database module name (e.g., `psycopg2`) |
| database | string | Yes | Database name |
| username | string | Yes | Database user |
| password | string | Yes | Database password |
| host | string | Yes | Database host |
| port | integer | No | Database port (default: 5432) |

**Example:**
```robotframework
*** Keywords ***
Connect To Test Database
    Connect To Database    psycopg2    ${DB_NAME}    ${DB_USER}    ${DB_PASS}    ${DB_HOST}
    Log    Connected to ${DB_NAME}
```

**Best Practice:** Use SUITE scope to share connection across tests.

---

### Disconnect From Database

Closes the active database connection.

**Syntax:**
```robotframework
Disconnect From Database
```

**Example:**
```robotframework
*** Test Cases ***
Test With Database
    Connect To Database    psycopg2    ${DB_NAME}    ${DB_USER}    ${DB_PASS}    ${DB_HOST}

    TRY
        # Test code here
        ${result}=    Query    SELECT * FROM form_data
    FINALLY
        Disconnect From Database
    END
```

**Best Practice:** Always use in FINALLY block for guaranteed cleanup.

---

### Connect To Database Using Connection String

Connect using a connection string instead of individual parameters.

**Syntax:**
```robotframework
Connect To Database Using Connection String    ${dbapi}    ${connection_string}
```

**Example:**
```robotframework
*** Keywords ***
Connect With Custom Settings
    ${conn_str}=    Set Variable    host=localhost port=5432 dbname=test user=postgres password=postgres
    Connect To Database Using Connection String    psycopg2    ${conn_str}
```

---

## Query Keywords

### Query

Executes a SQL SELECT query and returns the results.

**Syntax:**
```robotframework
${result}=    Query    ${sql_statement}    ${suppress}=False
```

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| sql_statement | string | Yes | SQL query to execute |
| suppress | boolean | No | Don't raise error if no rows returned |

**Returns:** List of dictionaries representing result rows.

**Example:**
```robotframework
*** Keywords ***
Get Form By Email
    [Arguments]    ${email}
    ${result}=    Query    SELECT * FROM form_data WHERE email = '${email}'
    ${row}=    Get From List    ${result}    0
    [Return]    ${row}
```

---

### Row Count

Returns the number of rows from a query result.

**Syntax:**
```robotframework
${count}=    Row Count    ${sql_statement}
```

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| sql_statement | string | Yes | SQL query (typically COUNT(*)) |

**Returns:** Integer representing row count.

**Example:**
```robotframework
*** Keywords ***
Count Forms By Gender
    [Arguments]    ${gender}
    ${count}=    Row Count    SELECT COUNT(*) FROM form_data WHERE gender = '${gender}'
    Log    Found ${count} ${gender} forms
    [Return]    ${count}
```

---

### Check If Exists In Database

Verifies if a record exists in the database.

**Syntax:**
```robotframework
Check If Exists In Database    ${table_name}    ${where_clause}
```

**Example:**
```robotframework
*** Keywords ***
Email Should Be Unique
    [Arguments]    ${email}
    ${count}=    Row Count    SELECT COUNT(*) FROM form_data WHERE email = '${email}'
    Should Be Equal As Integers    ${count}    0    msg=Email ${email} already exists
```

---

## Data Modification Keywords

### Execute Sql String

Executes a SQL statement that doesn't return data (INSERT, UPDATE, DELETE).

**Syntax:**
```robotframework
Execute Sql String    ${sql_statement}
```

**Example:**
```robotframework
*** Keywords ***
Clean Up Test Data
    [Arguments]    ${test_email}
    Execute Sql String    DELETE FROM form_data WHERE email = '${test_email}'
    Log    Cleaned up test data
```

---

### Execute Sql Script

Executes a SQL script from a file.

**Syntax:**
```robotframework
Execute Sql Script    ${script_file}
```

**Example:**
```robotframework
*** Keywords ***
Reset Database Schema
    Execute Sql Script    resources/reset_schema.sql
    Log    Database schema reset
```

---

## Table Information Keywords

### Get All Tables

Returns a list of all tables in the database.

**Syntax:**
```robotframework
${tables}=    Get All Tables
```

**Example:**
```robotframework
*** Keywords ***
List All Tables
    ${tables}=    Get All Tables
    Log    Available tables: ${tables}
```

---

### Table Must Exist

Verifies that a table exists, fails if it doesn't.

**Syntax:**
```robotframework
Table Must Exist    ${table_name}
```

**Example:**
```robotframework
*** Test Cases ***
Verify Schema
    Table Must Exist    form_data
    Table Must Exist    attachments
    Table Must Exist    instructions
```

---

### Row Count Is 0

Verifies that a table is empty.

**Syntax:**
```robotframework
Row Count Is 0    ${table_name}
```

**Example:**
```robotframework
*** Test Cases ***
Verify Clean Start
    Row Count Is 0    form_data
    Log    Starting with empty table
```

---

### Row Count Is Greater Than 0

Verifies that a table has at least one row.

**Syntax:**
```robotframework
Row Count Is Greater Than 0    ${table_name}
```

**Example:**
```robotframework
*** Test Cases ***
Verify Data Exists
    Row Count Is Greater Than 0    form_data
    Log    Table has data
```

---

## Transaction Keywords

### Begin Transaction

Starts a database transaction.

**Syntax:**
```robotframework
Begin Transaction
```

**Example:**
```robotframework
*** Keywords ***
Test With Transaction
    Begin Transaction
    TRY
        # Multiple operations
        Create Test Form    ${data}
        Verify Form In Database    ${form_id}
        Commit Transaction
    EXCEPT
        Rollback Transaction
    END
```

---

### Commit Transaction

Commits the current transaction.

**Syntax:**
```robotframework
Commit Transaction
```

---

### Rollback Transaction

Rolls back the current transaction.

**Syntax:**
```robotframework
Rollback Transaction
```

**Example:**
```robotframework
*** Keywords ***
Test With Rollback On Failure
    Begin Transaction
    TRY
        ${result}=    Risky Database Operation
        Commit Transaction
    EXCEPT
        Rollback Transaction
        Log    Transaction rolled back due to error
    END
```

---

## Utility Keywords

### Description

Returns the description of the database connection.

**Syntax:**
```robotframework
${description}=    Description
```

---

### Log Sql

Logs SQL queries for debugging (must be enabled).

**Syntax:**
```robotframework
Log Sql    ${enable}
```

**Example:**
```robotframework
*** Test Cases ***
Debug Query
    Log Sql    ${TRUE}
    ${result}=    Query    SELECT * FROM form_data
    Log Sql    ${FALSE}
```

---

## Common Patterns

### Pattern 1: Select Single Record

```robotframework
*** Keywords ***
Get Form By Id
    [Documentation]    Retrieve single form by ID
    [Arguments]    ${form_id}

    ${result}=    Query    SELECT * FROM form_data WHERE id = ${form_id}

    # Verify record exists
    ${count}=    Get Length    ${result}
    Should Be Equal As Integers    ${count}    1    msg=Form ${form_id} not found

    # Return the row
    ${row}=    Get From List    ${result}    0
    [Return]    ${row}
```

---

### Pattern 2: Check Record Exists

```robotframework
*** Keywords ***
Form Exists
    [Documentation]    Check if form exists
    [Arguments]    ${form_id}

    ${count}=    Row Count    SELECT COUNT(*) FROM form_data WHERE id = ${form_id}
    [Return]    ${count} > 0
```

---

### Pattern 3: Delete by Pattern

```robotframework
*** Keywords ***
Delete Test Forms By Pattern
    [Documentation]    Delete forms matching email pattern
    [Arguments]    ${email_pattern}

    ${query}=    Set Variable    DELETE FROM form_data WHERE email LIKE '${email_pattern}'
    Execute Sql String    ${query}

    ${deleted}=    Row Count    DELETE FROM form_data WHERE email LIKE '${email_pattern}'
    Log    Deleted ${deleted} test forms
```

---

### Pattern 4: Verify Record Count

```robotframework
*** Keywords ***
Verify Expected Count
    [Documentation]    Verify exact record count
    [Arguments]    ${table}    ${expected_count}    ${where_clause}=${EMPTY}

    ${where}=    Set Variable If    '${where_clause}' != ${EMPTY}    WHERE ${where_clause}    ${EMPTY}
    ${query}=    Set Variable    SELECT COUNT(*) FROM ${table} ${where}

    ${actual_count}=    Row Count    ${query}
    Should Be Equal As Integers    ${actual_count}    ${expected_count}

    Log    ✅ Verified ${actual_count} records in ${table}
```

---

### Pattern 5: Batch Insert

```robotframework
*** Keywords ***
Insert Multiple Forms
    [Documentation]    Insert multiple test records
    [Arguments]    @{forms}

    FOR    ${form}    IN    @{forms}
        Execute Sql String
        ...    INSERT INTO form_data (first_name, last_name, email)
        ...    VALUES ('${form}[first_name]', '${form}[last_name]', '${form}[email]')
    END

    Log    Inserted ${forms} records
```

---

## Return Values

### Query Keyword Return Value

Returns a list of dictionaries where each dictionary represents a row.

**Example:**
```robotframework
${result}=    Query    SELECT id, first_name, email FROM form_data

# Result structure:
# [
#   {"id": 1, "first_name": "Jan", "email": "jan@example.com"},
#   {"id": 2, "first_name": "Pavla", "email": "pavla@example.com"}
# ]

# Access first row
${first_row}=    Get From List    ${result}    0

# Access field
${email}=    Set Variable    ${first_row}[email]
```

---

## Error Handling

### Common Exceptions

| Exception | Cause | Handling |
|-----------|-------|-----------|
| OperationalError | Connection failed, table doesn't exist | Check DB is running, verify table name |
| ProgrammingError | Invalid SQL syntax | Test query in DB client first |
| DataError | Constraint violation (unique, foreign key) | Verify test data doesn't conflict |

### TRY/EXCEPT Pattern

```robotframework
*** Keywords ***
Safe Query
    [Documentation]    Query with error handling
    [Arguments]    ${query}

    TRY
        ${result}=    Query    ${query}
        [Return]    ${result}

    EXCEPT    OperationalError
        Log    ❌ Database error: ${ERROR}
        Fail    Database operation failed

    EXCEPT
        Log    ❌ Unexpected error: ${ERROR}
        Fail    Unexpected error
    END
```

---

## Quick Reference Card

### Connection
```robotframework
Connect To Database    psycopg2    ${DB}    ${USER}    ${PASS}    ${HOST}
Disconnect From Database
```

### Query
```robotframework
${result}=    Query    SELECT * FROM table WHERE id = ${id}
${count}=    Row Count    SELECT COUNT(*) FROM table
```

### Modify
```robotframework
Execute Sql String    DELETE FROM table WHERE condition
Execute Sql String    INSERT INTO table (col) VALUES (val)
```

### Verify
```robotframework
Row Count Is 0    table_name
Row Count Is Greater Than 0    table_name
Table Must Exist    table_name
```

---

## See Also

- [Best Practices Guide](01_BestPractices.md)
- [Anti-Patterns Guide](02_AntiPatterns.md)
- [Database Library Documentation](https://github.com/frank-rouvy/RobotFramework-Database-Library)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
