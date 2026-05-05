*** Settings ***
Documentation     Tento soubor obsahuje shared utility keywords pro API testing:
#                 session management, logging, response verification.
Library     RequestsLibrary
Library     Collections
Library     JSONLibrary
Library     String
Library     FakerLibrary
Library     TalosForge

Resource    ../../RF/API/endpoints/form_endpoints.resource
Resource    variables.resource

*** Keywords ***
Create API Session
    [Documentation]    Vytvoří API session pro RequestsLibrary
    ...    Args:
    ...    - session_alias: Alias pro session (např. "mysession")
    ...    - base_url: Base URL API (např. "http://localhost:8000/api/v1/form")
    ...    - verify: SSL verification (default=False pro local dev)
    ...
    ...    Returns:
    ...    - session_alias: Alias vytvořené session
    ...
    ...    Example:
    ...    | Create API Session    mysession    http://localhost:8000/api/v1/form
    [Arguments]    ${session_alias}    ${base_url}
    Create Session    ${session_alias}    ${base_url}
    Log    ====> API Session vytvořena: ${session_alias} → ${base_url}    level=INFO    console=${LOG_TO_CONSOLE}
    RETURN    ${session_alias}

API request
    [Documentation]    This is wrapper for REST API request
    [Arguments]    ${method}    ${alias}    ${url}    ${json}=${EMPTY}    ${data}=${EMPTY}    ${params}=${EMPTY}
    ...        ${expected_status}=${None}    ${context_name}=${EMPTY}      ${headers}=${EMPTY}  

    VAR    ${response}    ${None}

    TRY
        IF    '${method}' == 'POST'
            ${response}=    POST On Session    alias=${alias}    url=${url}    data=${data}    json=${json}    headers=${headers}    expected_status=anything
        ELSE IF    '${method}' == 'GET'
            ${response}=    GET On Session    alias=${alias}    url=${url}    params=${params}    headers=${headers}    expected_status=anything
        ELSE IF    '${method}' == 'PATCH'
            ${response}=    PATCH On Session    alias=${alias}    url=${url}    json=${json}    headers=${headers}    expected_status=anything
        ELSE IF    '${method}' == 'PUT'
            ${response}=    PUT On Session    alias=${alias}    url=${url}    json=${json}    headers=${headers}    expected_status=anything
        ELSE IF    '${method}' == 'DELETE'
            ${response}=    DELETE On Session    alias=${alias}    url=${url}    headers=${headers}    expected_status=anything
        END

        Log    \nAPI request: ${method} | end-point ---> ${url}    console=${LOG_to_console}
        Log    \nResponse status: ---> ${response.status_code} <---   console=${LOG_to_console}
        Log    \nResponse body: ${response.text}    console=${LOG_to_console}

        IF    $expected_status is None
            IF    not (200 <= ${response.status_code} < 300)
                Fail    API Failed! '${context_name}': Expected 2xx, GOT ${response.status_code} | Body: ${response.text}
            END
        ELSE IF    $expected_status == 'anything'
            No Operation
        ELSE
            IF    ${response.status_code} != ${expected_status}
                Fail    API Failed! '${context_name}': Expected ${expected_status}, GOT ${response.status_code} | Body: ${response.text}
            END
        END

    EXCEPT    AS    ${err}
        ${err_str}=    Convert To String    ${err}
        IF    'API F' in $err_str
            Fail    ${err}
        END
        Fail    API request failed ('${context_name}'): ${err}
    END

    RETURN    ${response}
