*** Settings ***
Documentation     Setup tests for Orders API.
...               Creates auth tokens and test courier for subsequent tests.
...               MUST run first before other orders_* tests.

Library           RequestsLibrary
Library           Collections

Resource          ../resources/auth.resource
Resource          ../endpoints/orders_endpoints.resource
Resource          ../variables.resource

Suite Setup       Create Session    api    ${API_BASE_URL}/api/v1    verify=${API_VERIFY_SSL}
Suite Teardown    Delete All Sessions


*** Variables ***
${ADMIN_TOKEN}        ${EMPTY}
${COURIER_TOKEN}      ${EMPTY}
${CUSTOMER_TOKEN}     ${EMPTY}
${TEST_COURIER_ID}    ${EMPTY}


*** Test Cases ***
00A Get Admin Token
    [Documentation]    Get admin JWT token with full permissions.
    [Tags]    setup    auth    api
    ${token}=    Get Admin Token
    Should Not Be Empty    ${token}
    Set Suite Variable    ${ADMIN_TOKEN}    ${token}
    Log    Admin token obtained    level=INFO

00B Get Courier Token
    [Documentation]    Get courier JWT token for pickup/deliver operations.
    [Tags]    setup    auth    api
    ${token}=    Get Courier Token    user_id=10
    Should Not Be Empty    ${token}
    Set Suite Variable    ${COURIER_TOKEN}    ${token}
    Log    Courier token obtained    level=INFO

00C Get Customer Token
    [Documentation]    Get customer JWT token for basic order operations.
    [Tags]    setup    auth    api
    ${token}=    Get Customer Token    user_id=100
    Should Not Be Empty    ${token}
    Set Suite Variable    ${CUSTOMER_TOKEN}    ${token}
    Log    Customer token obtained    level=INFO

00D Create Test Courier
    [Documentation]    Create a test courier for flow tests.
    [Tags]    setup    courier    api
    ${resp}=    Create Courier    ${ADMIN_TOKEN}
    Should Be True    ${resp.status_code} < 400    Courier creation failed: ${resp.text}
    ${courier_id}=    Set Variable    ${resp.json()}[id]
    Set Suite Variable    ${TEST_COURIER_ID}    ${courier_id}
    Log    Test courier created with ID: ${TEST_COURIER_ID}    level=INFO

00E Set Courier Location
    [Documentation]    Set test courier GPS location (Prague center).
    [Tags]    setup    courier    api
    Skip If    "${TEST_COURIER_ID}" == "${EMPTY}"    No courier created
    ${resp}=    Set Courier Location    ${ADMIN_TOKEN}    ${TEST_COURIER_ID}
    Should Be True    ${resp.status_code} < 400    Failed to set location: ${resp.text}
    Log    Courier location set    level=INFO

00F Set Courier Available
    [Documentation]    Set test courier status to available for dispatch.
    [Tags]    setup    courier    api
    Skip If    "${TEST_COURIER_ID}" == "${EMPTY}"    No courier created
    ${resp}=    Set Courier Available    ${ADMIN_TOKEN}    ${TEST_COURIER_ID}
    Should Be True    ${resp.status_code} < 400    Failed to set status: ${resp.text}
    Log    Courier status set to available    level=INFO
