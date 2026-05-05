# Common DB Resource Template

Template for creating common_db.resource file.

```robot
*** Settings ***
Documentation     Common database keywords for PostgreSQL testing.
...                Provides wrapper keywords for database operations with automatic cleanup and error handling.
Library           DatabaseLibrary
Library           Collections

*** Variables ***
${DB_HOST}              localhost
${DB_PORT}              5432
${DB_NAME}              test_db
${DB_USER}              postgres
${DB_PASSWORD}          postgres
${DB_ALIAS}             testdb
${LOG_TO_CONSOLE}       False

*** Keywords ***
Connect To Test Database
    [Documentation]    Establishes connection to PostgreSQL test database.
    ...                Uses environment variables or defaults for connection parameters.
    ...
    ...                Example:
    ...                    Connect To Test Database
    ${context_name}=    Set Variable    Connect to test database
    TRY
        Connect To Database
        ...    psycopg2
        ...    ${DB_NAME}
        ...    ${DB_USER}
        ...    ${DB_PASSWORD}
        ...    ${DB_HOST}
        ...    ${DB_PORT}
        Run Keyword If    '${LOG_TO_CONSOLE}' == 'True'
        ...    Log To Console    ${context_name}: Connected to ${DB_NAME}@${DB_HOST}:${DB_PORT}
    EXCEPT    AS    ${error_message}
        Fail    ${context_name}: Failed to connect. Error: ${error_message}
    END

Disconnect From Test Database
    [Documentation]    Closes the database connection.
    ${context_name}=    Set Variable    Disconnect from test database
    TRY
        Disconnect From Database
        Run Keyword If    '${LOG_TO_CONSOLE}' == 'True'
        ...    Log To Console    ${context_name}: Disconnected from database
    EXCEPT    AS    ${error_message}
        Log    ${context_name}: Warning - ${error_message}    level=WARN
    END

Delete All Test Data
    [Documentation]    Deletes all rows from specified table(s).
    ...                Use in teardown to clean up test data.
    ...
    ...                Example:
    ...                    Delete All Test Data    users    orders
    [Arguments]    @{table_names}
    ${context_name}=    Set Variable    Delete all test data
    TRY
        FOR    ${table_name}    IN    @{table_names}
            Execute Sql String    DELETE FROM ${table_name}
            Run Keyword If    '${LOG_TO_CONSOLE}' == 'True'
            ...    Log To Console    ${context_name}: Cleared table ${table_name}
        END
    EXCEPT    AS    ${error_message}
        Log    ${context_name}: Warning - ${error_message}    level=WARN
    END

Verify Row Count In Database
    [Documentation]    Verifies that query returns expected number of rows.
    ...                Supports comparison operators: ==, !=, <, >, <=, >=
    ...
    ...                Arguments:
    ...                - query: SQL SELECT query
    ...                - expected_count: Expected number of rows
    ...                - operator: Comparison operator (default: ==)
    ...                - context_name: Context for error messages
    ...
    ...                Example:
    ...                    Verify Row Count In Database
    ...                    ...    query=SELECT * FROM users WHERE email='test@test.com'
    ...                    ...    expected_count=1
    ...                    ...    operator===
    ...                    ...    context_name=Verify user exists
    [Arguments]    ${query}    ${expected_count}    ${operator}===    ${context_name}=Verify row count
    TRY
        ${db_query_result}=    Query    ${query}
        ${db_actual_count}=    Get Length    ${db_query_result}

        Run Keyword If    '${LOG_TO_CONSOLE}' == 'True'
        ...    Log To Console    ${context_name}: Found ${db_actual_count} rows, expected ${operator} ${expected_count}

        Run Keyword If    '${operator}' == '=='
        ...    Should Be Equal As Integers    ${db_actual_count}    ${expected_count}
        ...    msg=${context_name}: Expected ${expected_count} rows, got ${db_actual_count}
        ...    ELSE IF    '${operator}' == '!='
        ...    Should Not Be Equal As Integers    ${db_actual_count}    ${expected_count}
        ...    msg=${context_name}: Expected NOT ${expected_count} rows, got ${db_actual_count}
        ...    ELSE IF    '${operator}' == '>'
        ...    Should Be True    ${db_actual_count} > ${expected_count}
        ...    msg=${context_name}: Expected more than ${expected_count} rows, got ${db_actual_count}
        ...    ELSE IF    '${operator}' == '<'
        ...    Should Be True    ${db_actual_count} < ${expected_count}
        ...    msg=${context_name}: Expected less than ${expected_count} rows, got ${db_actual_count}
        ...    ELSE IF    '${operator}' == '>='
        ...    Should Be True    ${db_actual_count} >= ${expected_count}
        ...    msg=${context_name}: Expected at least ${expected_count} rows, got ${db_actual_count}
        ...    ELSE IF    '${operator}' == '<='
        ...    Should Be True    ${db_actual_count} <= ${expected_count}
        ...    msg=${context_name}: Expected at most ${expected_count} rows, got ${db_actual_count}
    EXCEPT    AS    ${error_message}
        Fail    ${context_name}: Verification failed. Error: ${error_message}
    END

Verify Value In Database
    [Documentation]    Verifies that a specific column value exists in query result.
    ...
    ...                Arguments:
    ...                - query: SQL SELECT query (must return single row)
    ...                - column_name: Name of column to check
    ...                - expected_value: Expected value
    ...                - context_name: Context for error messages
    ...
    ...                Example:
    ...                    Verify Value In Database
    ...                    ...    query=SELECT * FROM users WHERE id=1
    ...                    ...    column_name=email
    ...                    ...    expected_value=test@test.com
    ...                    ...    context_name=Verify user email
    [Arguments]    ${query}    ${column_name}    ${expected_value}    ${context_name}=Verify value in database
    TRY
        ${db_query_result}=    Query    ${query}
        ${db_row_count}=    Get Length    ${db_query_result}

        Should Be Equal As Integers    ${db_row_count}    1
        ...    msg=${context_name}: Expected 1 row, got ${db_row_count}

        ${db_actual_value}=    Set Variable    ${db_query_result}[0][${column_name}]
        Should Be Equal    ${db_actual_value}    ${expected_value}
        ...    msg=${context_name}: Expected '${expected_value}', got '${db_actual_value}'

        Run Keyword If    '${LOG_TO_CONSOLE}' == 'True'
        ...    Log To Console    ${context_name}: Verified ${column_name}='${expected_value}'
    EXCEPT    AS    ${error_message}
        Fail    ${context_name}: Verification failed. Error: ${error_message}
    END

Execute SQL And Return Value
    [Documentation]    Executes SQL query and returns single value.
    [Arguments]    ${query}    ${context_name}=Execute SQL
    TRY
        ${db_query_result}=    Query    ${query}
        ${db_result_value}=    Set Variable    ${db_query_result}[0][0]
        RETURN    ${db_result_value}
    EXCEPT    AS    ${error_message}
        Fail    ${context_name}: Query failed. Error: ${error_message}
    END
```

## Usage

1. Import in test: `Resource  ../common/common_db.resource`
2. Connect in Suite Setup: `Connect To Test Database`
3. Disconnect in Suite Teardown: `Disconnect From Test Database`
4. Use wrappers for all DB operations
