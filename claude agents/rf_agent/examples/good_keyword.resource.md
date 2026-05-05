# Example: Good Keyword Resource

Example of a properly written resource file with keywords.

```robot
*** Settings ***
Documentation     Keywords for user management API tests.
...                Provides reusable keywords for user CRUD operations.
Library           Collections
Library           String
Library           FakerLibrary
Resource          ../common/common_api.resource
Resource          ../common/common_db.resource

*** Variables ***
${api_users_endpoint}           /api/v1/users

*** Keywords ***
Create Valid User Payload
    [Documentation]    Creates a valid user request payload with FakerLibrary data.
    ...                Optionally accepts custom values to override defaults.
    ...
    ...                Arguments:
    ...                - custom_name: Override default name (optional)
    ...                - custom_email: Override default email (optional)
    ...
    ...                Returns: Dictionary with user payload
    ...
    ...                Example:
    ...                    ${api_create_user_request_payload}=    Create Valid User Payload
    ...                    ${api_create_user_request_payload}=    Create Valid User Payload    custom_email=test@test.com
    [Arguments]    ${custom_name}=${None}    ${custom_email}=${None}
    ${test_user_name}=    Run Keyword If    '${custom_name}' != '${None}'
    ...    Set Variable    ${custom_name}
    ...    ELSE    FakerLibrary.Name
    ${test_user_email}=    Run Keyword If    '${custom_email}' != '${None}'
    ...    Set Variable    ${custom_email}
    ...    ELSE    FakerLibrary.Email
    ${api_create_user_request_payload}=    Create Dictionary
    ...    name=${test_user_name}
    ...    email=${test_user_email}
    RETURN    ${api_create_user_request_payload}

Create User Via API
    [Documentation]    Creates a user via API and returns the response body.
    ...                Uses FakerLibrary for data generation.
    ...                This keyword handles the full flow: create payload, call API, return body.
    ...
    ...                Arguments:
    ...                - custom_payload: Override default payload (optional)
    ...
    ...                Returns: Response body as dictionary
    ...
    ...                Example:
    ...                    ${api_user_response_body}=    Create User Via API
    ...                    ${api_user_response_body}=    Create User Via API    custom_payload=${my_payload}
    [Arguments]    ${custom_payload}=${None}
    ${context_name}=    Set Variable    Create user via API
    TRY
        # Prepare payload
        ${api_create_user_request_payload}=    Run Keyword If    '${custom_payload}' != '${None}'
        ...    Set Variable    ${custom_payload}
        ...    ELSE    Create Valid User Payload

        # Make API call via wrapper
        ${api_create_user_response}=    API request
        ...    method=POST
        ...    url=${api_users_endpoint}
        ...    body=${api_create_user_request_payload}
        ...    expected_status=anything
        ...    context_name=${context_name}

        # Verify success
        ${api_create_user_response_status}=    Set Variable    ${api_create_user_response.status_code}
        Should Be Equal As Integers    ${api_create_user_response_status}    201
        ...    msg=${context_name}: Expected 201, got ${api_create_user_response_status}

        ${api_create_user_response_body}=    Set Variable    ${api_create_user_response.json()}
        RETURN    ${api_create_user_response_body}
    EXCEPT    AS    ${error_message}
        Fail    ${context_name}: Failed to create user. Error: ${error_message}
    END

Get User By ID
    [Documentation]    Fetches a user by ID and returns the response body.
    ...
    ...                Arguments:
    ...                - user_id: User ID to fetch
    ...
    ...                Returns: Response body as dictionary
    ...
    ...                Example:
    ...                    ${api_user_response_body}=    Get User By ID    user_id=123
    [Arguments]    ${user_id}
    ${context_name}=    Set Variable    Get user by ID
    TRY
        ${api_get_user_response}=    API request
        ...    method=GET
        ...    url=${api_users_endpoint}/${user_id}
        ...    expected_status=anything
        ...    context_name=${context_name}

        ${api_get_user_response_status}=    Set Variable    ${api_get_user_response.status_code}
        Should Be Equal As Integers    ${api_get_user_response_status}    200
        ...    msg=${context_name}: User ${user_id} not found. Status: ${api_get_user_response_status}

        ${api_get_user_response_body}=    Set Variable    ${api_get_user_response.json()}
        RETURN    ${api_get_user_response_body}
    EXCEPT    AS    ${error_message}
        Fail    ${context_name}: Failed to get user ${user_id}. Error: ${error_message}
    END

Delete User By ID
    [Documentation]    Deletes a user by ID and verifies the deletion.
    ...
    ...                Arguments:
    ...                - user_id: User ID to delete
    ...
    ...                Example:
    ...                    Delete User By ID    user_id=123
    [Arguments]    ${user_id}
    ${context_name}=    Set Variable    Delete user by ID
    TRY
        ${api_delete_user_response}=    API request
        ...    method=DELETE
        ...    url=${api_users_endpoint}/${user_id}
        ...    expected_status=anything
        ...    context_name=${context_name}

        ${api_delete_user_response_status}=    Set Variable    ${api_delete_user_response.status_code}
        Should Be Equal As Integers    ${api_delete_user_response_status}    204
        ...    msg=${context_name}: Expected 204, got ${api_delete_user_response_status}

        # Verify deletion in database
        Verify Row Count In Database
        ...    query=SELECT * FROM users WHERE id='${user_id}'
        ...    expected_count=0
        ...    operator===
        ...    context_name=${context_name} - verify deletion
    EXCEPT    AS    ${error_message}
        Fail    ${context_name}: Failed to delete user ${user_id}. Error: ${error_message}
    END

Verify User Exists In Database
    [Documentation]    Verifies that a user exists in the database.
    ...
    ...                Arguments:
    ...                - user_id: User ID to verify
    ...                - expected_count: Expected number of records (default: 1)
    ...
    ...                Example:
    ...                    Verify User Exists In Database    user_id=123
    [Arguments]    ${user_id}    ${expected_count}=1
    ${context_name}=    Set Variable    Verify user exists in database
    Verify Row Count In Database
    ...    query=SELECT * FROM users WHERE id='${user_id}'
    ...    expected_count=${expected_count}
    ...    operator===
    ...    context_name=${context_name}

Verify User Email In Database
    [Documentation]    Verifies that a user has the expected email in database.
    ...
    ...                Arguments:
    ...                - user_id: User ID to verify
    ...                - expected_email: Expected email value
    ...
    ...                Example:
    ...                    Verify User Email In Database    user_id=123    expected_email=test@test.com
    [Arguments]    ${user_id}    ${expected_email}
    ${context_name}=    Set Variable    Verify user email in database
    Verify Value In Database
    ...    query=SELECT * FROM users WHERE id='${user_id}'
    ...    column_name=email
    ...    expected_value=${expected_email}
    ...    context_name=${context_name}
```

## What makes this resource good

1. **TRY/EXCEPT pattern**: Every non-trivial keyword has error handling
2. **`${context_name}`**: For contextual error messages
3. **Documentation with examples**: `[Documentation]` with Example sections
4. **RETURN instead of Set Suite Variable**: Clean value return
5. **Using wrappers**: `API request`, `Verify Row Count In Database`
6. **Variable naming convention**: `${api_<action>_<entity>_<type>}`
7. **FakerLibrary**: For generating test data
8. **Optional arguments**: With reasonable defaults
