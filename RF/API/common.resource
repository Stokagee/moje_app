

*** Settings ***
Documentation     Tento soubor obsahuje shared utility keywords pro API testing:
#                 session management, logging, response verification.
Library     RequestsLibrary
Library     Collections
Library     JSONLibrary
Library     String
Resource    ../../RF/API/workflows/form_workflow.resource
Resource    ../../RF/API/api_actions/form_api.resource
Resource    ../../RF/API/endpoints/form_endpoints.resource

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
    [Arguments]    ${session_alias}    ${base_url}    ${verify}=${False}
    Create Session    ${session_alias}    ${base_url}    verify=${verify}
    Log    🌐 API Session vytvořena: ${session_alias} → ${base_url}    level=INFO
    RETURN    ${session_alias}

Log API Request
    [Documentation]    Loguje API request pro debugging
    ...    Args:
    ...    - method: HTTP method (GET, POST, PUT, DELETE)
    ...    - endpoint: API endpoint
    ...    - data: Request body (optional)
    [Arguments]    ${method}    ${endpoint}    ${data}=${None}
    Log    🌐 API REQUEST: ${method} ${endpoint}    level=INFO
    IF    ${data} != ${None}
        ${json_str}=    Evaluate    json.dumps(${data}, indent=2, ensure_ascii=False)    modules=json
        Log    📦 Request Body:\n${json_str}    level=INFO
    END

Log API Response
    [Documentation]    Loguje API response pro debugging
    ...    Args:
    ...    - response: Response object z RequestsLibrary
    [Arguments]    ${response}
    ${status}=    Set Variable    ${response.status_code}
    IF    ${status} >= 200 and ${status} < 300
        ${symbol}=    Set Variable    ✅
    ELSE IF    ${status} >= 400
        ${symbol}=    Set Variable    ❌
    ELSE
        ${symbol}=    Set Variable    ⚠️
    END
    Log    ${symbol} API RESPONSE: Status ${status}    level=INFO
    TRY
        ${json_response}=    Set Variable    ${response.json()}
        ${json_str}=    Evaluate    json.dumps(${json_response}, indent=2, ensure_ascii=False)    modules=json
        Log    📦 Response Body:\n${json_str}    level=INFO
    EXCEPT
        Log    Response body is not JSON or empty    level=WARN
    END

Log Test Step
    [Documentation]    Loguje test step s INFO level
    [Arguments]    ${step_description}
    Log    🔹 ${step_description}    level=INFO
    Log To Console    \n[STEP] ${step_description}

Log Test Data
    [Documentation]    Loguje test data ve strukturovaném formátu
    [Arguments]    ${data_name}    ${data}
    Log    📊 ${data_name}:    level=INFO
    Log    ${data}    level=INFO
    TRY
        ${json_str}=    Evaluate    json.dumps(${data}, indent=2, ensure_ascii=False)    modules=json
        Log To Console    \n📊 ${data_name}:\n${json_str}
    EXCEPT
        Log To Console    \n📊 ${data_name}: ${data}
    END

Log Test Result
    [Documentation]    Loguje výsledek test action
    [Arguments]    ${action}    ${status}    ${details}=${EMPTY}
    IF    '${status}' == 'PASS'
        ${symbol}=    Set Variable    ✅
        ${level}=    Set Variable    INFO
    ELSE
        ${symbol}=    Set Variable    ❌
        ${level}=    Set Variable    ERROR
    END
    ${msg}=    Set Variable If    '${details}' != '${EMPTY}'
    ...    ${symbol} ${action}: ${status} | ${details}
    ...    ${symbol} ${action}: ${status}
    Log    ${msg}    level=${level}
    Log To Console    ${msg}

Verify Response Status
    [Documentation]    Ověří že response má očekávaný status code
    ...    Args:
    ...    - response: Response object
    ...    - expected_status: Očekávaný status code
    ...    - error_message: Custom error message (optional)
    [Arguments]    ${response}    ${expected_status}    ${error_message}=${EMPTY}
    ${actual_status}=    Set Variable    ${response.status_code}
    ${default_msg}=    Set Variable    Expected status ${expected_status}, got ${actual_status}
    ${msg}=    Set Variable If    '${error_message}' != '${EMPTY}'
    ...    ${error_message}: ${default_msg}
    ...    ${default_msg}
    Should Be Equal As Integers    ${actual_status}    ${expected_status}
    ...    msg=${msg}

Verify Response Contains Keys
    [Documentation]    Ověří že response JSON obsahuje očekávané keys
    ...    Args:
    ...    - response: Response object
    ...    - keys: List required keys
    [Arguments]    ${response}    @{keys}
    ${data}=    Set Variable    ${response.json()}
    FOR    ${key}    IN    @{keys}
        Dictionary Should Contain Key    ${data}    ${key}
        ...    msg=Response neobsahuje required key: '${key}'
    END

Verify Response Field Value
    [Documentation]    Ověří hodnotu konkrétního pole v response
    ...    Args:
    ...    - response: Response object
    ...    - field: Název pole
    ...    - expected_value: Očekávaná hodnota
    [Arguments]    ${response}    ${field}    ${expected_value}
    ${data}=    Set Variable    ${response.json()}
    Dictionary Should Contain Key    ${data}    ${field}
    ...    msg=Response neobsahuje field: '${field}'
    ${actual_value}=    Set Variable    ${data['${field}']}
    Should Be Equal    ${actual_value}    ${expected_value}
    ...    msg=Field '${field}': expected '${expected_value}', got '${actual_value}'

Generate Test Email
    [Documentation]    Generuje unique test email s timestamp
    ...    Returns:
    ...    - email: Unique test email
    ...    Example:
    ...    | ${email}=    Generate Test Email
    ...    | # → test_1234567890@example.com
    [Arguments]    ${prefix}=test
    ${timestamp}=    Get Time    epoch
    ${email}=    Set Variable    ${prefix}_${timestamp}@example.com
    RETURN    ${email}

Wait Until Form Is Deleted
    [Documentation]    Čeká až bude formulář smazán (GET vrátí 404)
    ...    Užitečné pro asynchronní delete operace.
    ...    Args:
    ...    - session: Session alias
    ...    - form_id: ID formuláře
    ...    - timeout: Max čekání v sekundách (default=10s)
    [Arguments]    ${session}    ${form_id}    ${timeout}=10s
    Wait Until Keyword Succeeds    ${timeout}    1s
    ...    Verify Form Is Deleted    ${session}    ${form_id}

Verify Form Is Deleted
    [Documentation]    Helper keyword - ověří že GET vrátí error
    [Arguments]    ${session}    ${form_id}
    ${status}=    Run Keyword And Return Status
    ...    GET On Session    ${session}    /${form_id}    expected_status=404
    Should Be True    ${status}    msg=Form ID ${form_id} stále existuje
