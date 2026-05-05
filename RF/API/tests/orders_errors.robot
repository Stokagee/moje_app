*** Settings ***
Documentation     Error scenario tests for Orders API.
...               Tests authentication and validation errors.

Library           RequestsLibrary
Library           Collections

Resource          ../resources/auth.resource
Resource          ../endpoints/orders_endpoints.resource
Resource          ../variables.resource

Suite Setup       Create Session    api    ${API_BASE_URL}/api/v1    verify=${API_VERIFY_SSL}
Suite Teardown    Delete All Sessions


*** Test Cases ***
30 Error Create Order No Auth
    [Documentation]    Create order without authentication token.
    ...    Expected: 401 Unauthorized
    [Tags]    api    orders    errors    auth

    ${body}=    Generate Order Body
    ${headers}=    Create Dictionary    Content-Type=application/json

    ${resp}=    POST On Session    api    /orders/    json=${body}    headers=${headers}    expected_status=anything

    Order Should Be Unauthorized    ${resp}
    Should Contain    ${resp.json()}[detail]    authenticated
    Log    Correctly rejected with 401    level=INFO

31 Error Invalid Data
    [Documentation]    Create order with invalid data (empty required fields).
    ...    Expected: 422 Unprocessable Entity
    [Tags]    api    orders    errors    validation

    ${customer}=    Get Customer Token

    # Invalid body - missing required fields
    ${invalid_body}=    Create Dictionary
    ...    customer_name=${EMPTY}
    ...    customer_phone=invalid

    ${headers}=    Get Auth Headers    ${customer}
    ${resp}=    POST On Session    api    /orders/    json=${invalid_body}    headers=${headers}    expected_status=anything

    Order Should Be Validation Error    ${resp}
    Log    Correctly rejected with 422: ${resp.text}    level=INFO

32 Error Invalid Token
    [Documentation]    Access orders with invalid JWT token.
    ...    Expected: 401 Unauthorized
    [Tags]    api    orders    errors    auth

    ${headers}=    Create Dictionary
    ...    Authorization=Bearer invalid_token_here_12345
    ...    Content-Type=application/json

    ${resp}=    GET On Session    api    /orders/    headers=${headers}    expected_status=anything

    Order Should Be Unauthorized    ${resp}
    Log    Correctly rejected invalid token    level=INFO

33 Error Courier Pickup Not Assigned
    [Documentation]    Courier tries to pickup order not assigned to them.
    ...    Expected: 403 Forbidden
    [Tags]    api    orders    errors    rbac

    # Create order (will be in CREATED status, not assigned)
    ${customer}=    Get Customer Token
    ${courier}=    Get Courier Token    user_id=999

    ${create_resp}=    Create Order    ${customer}
    Skip If    ${create_resp.status_code} >= 400    Order creation failed
    ${order_id}=    Set Variable    ${create_resp.json()}[id]

    # Try pickup without assignment
    ${resp}=    Pickup Order    ${courier}    ${order_id}

    # Should get 400 (not assigned) or 403 (not owner)
    Should Be True    ${resp.status_code} in [400, 403, 404]
    Log    Correctly rejected pickup of unassigned order    level=INFO
