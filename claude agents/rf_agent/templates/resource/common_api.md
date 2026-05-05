# Common API Resource Template

Template for creating common_api.resource file.

```robot
*** Settings ***
Documentation     Common API keywords for REST API testing.
...                Provides wrapper keywords for HTTP requests with automatic logging and error handling.
Library           RequestsLibrary
Library           JSONLibrary
Library           Collections
Library           String

*** Variables ***
${LOG_TO_CONSOLE}           False
${DEFAULT_TIMEOUT}          30s

*** Keywords ***
Create API Session
    [Documentation]    Creates an API session with given alias and base URL.
    ...                Session is required before making any API requests.
    ...
    ...                Example:
    ...                    Create API Session    api    http://localhost:8000
    [Arguments]    ${session_alias}    ${base_url}    ${timeout}=${DEFAULT_TIMEOUT}
    ${context_name}=    Set Variable    Create API session
    TRY
        Create Session    ${session_alias}    ${base_url}    timeout=${timeout}    verify=True
        Run Keyword If    '${LOG_TO_CONSOLE}' == 'True'
        ...    Log To Console    ${context_name}: Session '${session_alias}' created for ${base_url}
    EXCEPT    AS    ${error_message}
        Fail    ${context_name}: Failed to create session. Error: ${error_message}
    END

API request
    [Documentation]    Universal REST API wrapper for GET, POST, PUT, DELETE requests.
    ...                Handles logging, error handling, and returns response object.
    ...
    ...                Arguments:
    ...                - method: HTTP method (GET, POST, PUT, DELETE)
    ...                - url: Endpoint URL (relative to base URL)
    ...                - body: Request body (dictionary, optional for GET)
    ...                - headers: Additional headers (dictionary, optional)
    ...                - expected_status: Expected status code or 'anything' (default: anything)
    ...                - context_name: Context for error messages (required)
    ...
    ...                Example:
    ...                    ${api_create_user_response}=    API request
    ...                    ...    method=POST
    ...                    ...    url=/api/users
    ...                    ...    body=${api_create_user_request_payload}
    ...                    ...    expected_status=anything
    ...                    ...    context_name=Create user
    [Arguments]    ${method}    ${url}    ${body}=${None}    ${headers}=${None}    ${expected_status}=anything    ${context_name}=API request
    TRY
        # Prepare headers
        ${api_request_headers}=    Run Keyword If    '${headers}' != '${None}'
        ...    Set Variable    ${headers}
        ...    ELSE    Create Dictionary    Content-Type=application/json

        # Make request based on method
        ${api_response}=    Run Keyword If    '${method}' == 'GET'
        ...    GET On Session    api    ${url}    headers=${api_request_headers}    expected_status=${expected_status}
        ...    ELSE IF    '${method}' == 'POST'
        ...    POST On Session    api    ${url}    json=${body}    headers=${api_request_headers}    expected_status=${expected_status}
        ...    ELSE IF    '${method}' == 'PUT'
        ...    PUT On Session    api    ${url}    json=${body}    headers=${api_request_headers}    expected_status=${expected_status}
        ...    ELSE IF    '${method}' == 'DELETE'
        ...    DELETE On Session    api    ${url}    headers=${api_request_headers}    expected_status=${expected_status}
        ...    ELSE    Fail    ${context_name}: Unsupported HTTP method '${method}'

        # Log if enabled
        Run Keyword If    '${LOG_TO_CONSOLE}' == 'True'
        ...    Log To Console    ${context_name}: ${method} ${url} returned ${api_response.status_code}

        RETURN    ${api_response}
    EXCEPT    AS    ${error_message}
        Fail    ${context_name}: Request failed. Error: ${error_message}
    END

Get Response Body
    [Documentation]    Extracts and returns JSON body from response object.
    [Arguments]    ${api_response}    ${context_name}=Get response body
    TRY
        ${api_response_body}=    Set Variable    ${api_response.json()}
        RETURN    ${api_response_body}
    EXCEPT    AS    ${error_message}
        Fail    ${context_name}: Failed to parse response body. Error: ${error_message}
    END

Verify Response Status
    [Documentation]    Verifies that response status code matches expected value.
    [Arguments]    ${api_response}    ${expected_status_code}    ${context_name}=Verify response status
    ${api_actual_status_code}=    Set Variable    ${api_response.status_code}
    Should Be Equal As Integers    ${api_actual_status_code}    ${expected_status_code}
    ...    msg=${context_name}: Expected status ${expected_status_code} but got ${api_actual_status_code}
```

## Usage

1. Import in test: `Resource  ../common/common_api.resource`
2. Create session in Suite Setup: `Create API Session    api    ${BASE_URL}`
3. Use `API request` for all HTTP calls
