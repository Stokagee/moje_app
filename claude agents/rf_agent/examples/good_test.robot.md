# Example: Good API Test

Example of a properly written Robot Framework API test.

```robot
*** Settings ***
Documentation     User management API tests - CRUD operations and validation.
Resource          ../../common/common_api.resource
Resource          ../../common/common_db.resource
Resource          ../users_api.resource
Suite Setup       Prepare User Tests
Suite Teardown    Cleanup User Tests
Test Tags         api    users

*** Variables ***
${api_users_endpoint}           /api/v1/users
${api_users_timeout}            30s

*** Test Cases ***
Users - Create Valid User - Returns 201 And User ID
    [Documentation]    Verify that creating a user with valid payload returns 201
    ...                and the response contains a valid user ID.
    [Tags]             create    positive
    # Given - Prepare test data
    ${api_create_user_request_payload}=    Create Valid User Payload
    # When - Make API request via wrapper
    ${api_create_user_response}=    API request
    ...    method=POST
    ...    url=${api_users_endpoint}
    ...    body=${api_create_user_request_payload}
    ...    expected_status=anything
    ...    context_name=Create new user
    # Then - Verify response status
    ${api_create_user_response_status}=    Set Variable    ${api_create_user_response.status_code}
    Should Be Equal As Integers    ${api_create_user_response_status}    201
    # And - Verify response body
    ${api_create_user_response_body}=    Set Variable    ${api_create_user_response.json()}
    Dictionary Should Contain Key    ${api_create_user_response_body}    id
    Should Not Be Empty    ${api_create_user_response_body}[id]
    # And - Verify database state
    ${db_created_user_id}=    Set Variable    ${api_create_user_response_body}[id]
    Verify Row Count In Database
    ...    query=SELECT * FROM users WHERE id='${db_created_user_id}'
    ...    expected_count=1
    ...    operator===
    ...    context_name=Verify user exists in database

Users - Create Duplicate Email - Returns 409 Conflict
    [Documentation]    Verify that creating a user with existing email returns 409.
    [Tags]             create    negative
    # Given - Create first user
    ${api_create_first_user_response_body}=    Create User Via API
    ${test_duplicate_email}=    Set Variable    ${api_create_first_user_response_body}[email]
    # When - Try to create with same email
    ${api_create_duplicate_request_payload}=    Create Valid User Payload
    ...    custom_email=${test_duplicate_email}
    ${api_create_duplicate_response}=    API request
    ...    method=POST
    ...    url=${api_users_endpoint}
    ...    body=${api_create_duplicate_request_payload}
    ...    expected_status=anything
    ...    context_name=Create user with duplicate email
    # Then - Verify conflict response
    ${api_create_duplicate_response_status}=    Set Variable    ${api_create_duplicate_response.status_code}
    Should Be Equal As Integers    ${api_create_duplicate_response_status}    409

Users - Get By ID - Returns 200 With Correct Data
    [Documentation]    Verify that fetching existing user by ID returns 200 with user data.
    [Tags]             read    positive
    # Given - Create test user
    ${api_create_user_response_body}=    Create User Via API
    ${test_user_id}=    Set Variable    ${api_create_user_response_body}[id]
    ${test_user_expected_name}=    Set Variable    ${api_create_user_response_body}[name]
    # When - Fetch user by ID
    ${api_get_user_response}=    API request
    ...    method=GET
    ...    url=${api_users_endpoint}/${test_user_id}
    ...    expected_status=anything
    ...    context_name=Get user by ID
    # Then - Verify response
    ${api_get_user_response_status}=    Set Variable    ${api_get_user_response.status_code}
    Should Be Equal As Integers    ${api_get_user_response_status}    200
    # And - Verify data matches
    ${api_get_user_response_body}=    Set Variable    ${api_get_user_response.json()}
    Should Be Equal    ${api_get_user_response_body}[name]    ${test_user_expected_name}

Users - Delete Existing User - Returns 204 And Removes From DB
    [Documentation]    Verify that deleting existing user returns 204 and removes from database.
    [Tags]             delete    positive
    # Given - Create user to delete
    ${api_create_user_response_body}=    Create User Via API
    ${test_user_id}=    Set Variable    ${api_create_user_response_body}[id]
    # When - Delete user
    ${api_delete_user_response}=    API request
    ...    method=DELETE
    ...    url=${api_users_endpoint}/${test_user_id}
    ...    expected_status=anything
    ...    context_name=Delete user by ID
    # Then - Verify response
    ${api_delete_user_response_status}=    Set Variable    ${api_delete_user_response.status_code}
    Should Be Equal As Integers    ${api_delete_user_response_status}    204
    # And - Verify deleted from database
    Verify Row Count In Database
    ...    query=SELECT * FROM users WHERE id='${test_user_id}'
    ...    expected_count=0
    ...    operator===
    ...    context_name=Verify user deleted from database

*** Keywords ***
Prepare User Tests
    [Documentation]    Sets up test environment and database connection.
    ${context_name}=    Set Variable    Prepare user tests
    TRY
        Create API Session    api    ${BASE_URL}
        Connect To Test Database
    EXCEPT    AS    ${error_message}
        Fail    ${context_name}: Setup failed. Error: ${error_message}
    END

Cleanup User Tests
    [Documentation]    Removes all test data and disconnects from database.
    ${context_name}=    Set Variable    Cleanup user tests
    TRY
        Delete All Test Data    users
        Disconnect From Test Database
    EXCEPT    AS    ${error_message}
        Log    ${context_name}: Warning - ${error_message}    level=WARN
    END
```

## What makes this test good

1. **Proper test naming**: `Feature - Scenario - Expected Outcome`
2. **Variables following convention**: `${api_create_user_response}`, `${db_created_user_id}`
3. **Using wrappers**: `API request`, `Verify Row Count In Database`
4. **Clear structure**: Given-When-Then pattern
5. **Documentation**: Every test has `[Documentation]`
6. **Tags**: For filtering and categorization
7. **Setup/Teardown**: For test isolation
8. **DB verification**: Not only API response, but also database state
