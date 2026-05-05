*** Settings ***
Documentation     Auth keywords for Orders API testing.
...               Provides centralized token management for different user roles.

Library           RequestsLibrary
Library           Collections

Resource          ../variables.resource


*** Keywords ***
Get Test Token
    [Documentation]    Get JWT token from /auth/test-token endpoint.
    ...    Args:
    ...    - username: Test username
    ...    - role: User role (user, courier, admin)
    ...    - user_id: User ID for the token
    ...    - scopes: Space-separated scope string (e.g. "orders:read orders:write")
    ...
    ...    Returns:
    ...    - access_token: JWT Bearer token
    [Arguments]    ${username}    ${role}    ${user_id}    ${scopes}
    ${body}=    Create Dictionary
    ...    username=${username}
    ...    role=${role}
    ...    user_id=${user_id}
    ...    scopes=${scopes}
    ${resp}=    POST On Session    api    /auth/test-token    json=${body}    expected_status=200
    RETURN    ${resp.json()}[access_token]

Get Admin Token
    [Documentation]    Get admin JWT token with full permissions.
    ...    Returns:
    ...    - access_token: JWT Bearer token with admin role
    ${token}=    Get Test Token    test_admin    admin    1    orders:read orders:write orders:admin
    RETURN    ${token}

Get Courier Token
    [Documentation]    Get courier JWT token for pickup/deliver operations.
    ...    Args:
    ...    - user_id: Courier user ID (default: 10)
    ...
    ...    Returns:
    ...    - access_token: JWT Bearer token with courier role
    [Arguments]    ${user_id}=10
    ${token}=    Get Test Token    test_courier    courier    ${user_id}    orders:read orders:write
    RETURN    ${token}

Get Customer Token
    [Documentation]    Get customer JWT token for basic order operations.
    ...    Args:
    ...    - user_id: Customer user ID (default: 100)
    ...
    ...    Returns:
    ...    - access_token: JWT Bearer token with user role
    [Arguments]    ${user_id}=100
    ${token}=    Get Test Token    test_customer    user    ${user_id}    orders:read
    RETURN    ${token}

Get Auth Headers
    [Documentation]    Create Authorization headers with Bearer token.
    ...    Args:
    ...    - token: JWT access token
    ...
    ...    Returns:
    ...    - headers: Dictionary with Authorization and Content-Type
    [Arguments]    ${token}
    ${headers}=    Create Dictionary
    ...    Authorization=Bearer ${token}
    ...    Content-Type=application/json
    RETURN    ${headers}

Create Auth Session
    [Documentation]    Create API session with auth token.
    ...    Sets suite variables for tokens.
    ...
    ...    Sets:
    ...    - ${ADMIN_TOKEN}
    ...    - ${COURIER_TOKEN}
    ...    - ${CUSTOMER_TOKEN}
    Create Session    api    ${API_BASE_URL}/api/v1    verify=${API_VERIFY_SSL}
    ${admin}=    Get Admin Token
    ${courier}=    Get Courier Token
    ${customer}=    Get Customer Token
    Set Suite Variable    ${ADMIN_TOKEN}    ${admin}
    Set Suite Variable    ${COURIER_TOKEN}    ${courier}
    Set Suite Variable    ${CUSTOMER_TOKEN}    ${customer}
