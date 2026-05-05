*** Settings ***
Documentation     Order lifecycle flow tests.
...               Tests complete flow: Create → Dispatch → Pickup → Deliver.

Library           RequestsLibrary
Library           Collections

Resource          ../resources/auth.resource
Resource          ../endpoints/orders_endpoints.resource
Resource          ../variables.resource

Suite Setup       Suite Setup With Tokens And Courier
Suite Teardown    Delete All Sessions


*** Variables ***
${FLOW_ORDER_ID}       ${EMPTY}
${TEST_COURIER_ID}     ${EMPTY}
${FLOW_COURIER_TOKEN}  ${EMPTY}


*** Keywords ***
Suite Setup With Tokens And Courier
    Create Session    api    ${API_BASE_URL}/api/v1    verify=${API_VERIFY_SSL}

    # Get tokens
    ${admin}=    Get Admin Token
    ${customer}=    Get Customer Token    user_id=100
    Set Suite Variable    ${ADMIN_TOKEN}    ${admin}
    Set Suite Variable    ${CUSTOMER_TOKEN}    ${customer}

    # Create test courier and get ID
    ${resp}=    Create Courier    ${admin}
    IF    ${resp.status_code} < 400
        ${courier_id}=    Set Variable    ${resp.json()}[id]
        Set Suite Variable    ${TEST_COURIER_ID}    ${courier_id}

        # Set location and available
        Set Courier Location    ${admin}    ${courier_id}
        Set Courier Available    ${admin}    ${courier_id}
        Log    Test courier ${courier_id} ready    level=INFO

        # Create courier token with the SAME user_id as the created courier
        # This ensures the token matches the courier assigned to the order
        ${courier_token}=    Get Courier Token    user_id=${courier_id}
        Set Suite Variable    ${FLOW_COURIER_TOKEN}    ${courier_token}
        Log    Courier token created for user_id=${courier_id}    level=INFO
    ELSE
        Log    Warning: Could not create test courier - flow tests will be skipped    level=WARN
        Set Suite Variable    ${TEST_COURIER_ID}    ${EMPTY}
        Set Suite Variable    ${FLOW_COURIER_TOKEN}    ${EMPTY}
    END


*** Test Cases ***
20 Flow Create Order
    [Documentation]    Create order for lifecycle flow test.
    [Tags]    api    orders    flow    post
    Skip If    "${TEST_COURIER_ID}" == "${EMPTY}"    No courier available for flow

    ${resp}=    Create Order    ${CUSTOMER_TOKEN}
    Order Should Be Created    ${resp}

    ${order_id}=    Set Variable    ${resp.json()}[id]
    Set Suite Variable    ${FLOW_ORDER_ID}    ${order_id}
    Log    Flow order created: ${FLOW_ORDER_ID}    level=INFO

21 Flow Dispatch Order
    [Documentation]    Auto-dispatch order to nearest courier.
    [Tags]    api    orders    flow    post
    Skip If    "${FLOW_ORDER_ID}" == "${EMPTY}"    No flow order created

    ${resp}=    Dispatch Order Auto    ${ADMIN_TOKEN}    ${FLOW_ORDER_ID}
    Should Be True    ${resp.status_code} < 400    Dispatch failed: ${resp.text}

    ${result}=    Set Variable    ${resp.json()}
    Log    Dispatch result: ${result}[message]    level=INFO

    # Verify order status changed to ASSIGNED
    ${order_resp}=    Get Order By ID    ${CUSTOMER_TOKEN}    ${FLOW_ORDER_ID}
    Should Be Equal    ${order_resp.json()}[status]    ASSIGNED

    # Get the assigned courier ID from the order and create a token for that courier
    ${assigned_courier_id}=    Set Variable    ${order_resp.json()}[courier_id]
    Log    Order dispatched to courier ID: ${assigned_courier_id}    level=INFO

    # Create a courier token with the ASSIGNED courier's ID
    ${assigned_courier_token}=    Get Courier Token    user_id=${assigned_courier_id}
    Set Suite Variable    ${FLOW_COURIER_TOKEN}    ${assigned_courier_token}
    Log    Using courier token for assigned courier ${assigned_courier_id}    level=INFO

22 Flow Pickup Order
    [Documentation]    Courier picks up the order.
    [Tags]    api    orders    flow    post
    Skip If    "${FLOW_ORDER_ID}" == "${EMPTY}"    No flow order created
    Skip If    "${FLOW_COURIER_TOKEN}" == "${EMPTY}"    No courier token available

    ${resp}=    Pickup Order    ${FLOW_COURIER_TOKEN}    ${FLOW_ORDER_ID}
    Should Be True    ${resp.status_code} < 400    Pickup failed: ${resp.text}

    # Verify order status changed to PICKED
    ${order_resp}=    Get Order By ID    ${CUSTOMER_TOKEN}    ${FLOW_ORDER_ID}
    Should Be Equal    ${order_resp.json()}[status]    PICKED
    Log    Order picked up    level=INFO

23 Flow Deliver Order
    [Documentation]    Courier delivers the order to customer.
    [Tags]    api    orders    flow    post
    Skip If    "${FLOW_ORDER_ID}" == "${EMPTY}"    No flow order created
    Skip If    "${FLOW_COURIER_TOKEN}" == "${EMPTY}"    No courier token available

    ${resp}=    Deliver Order    ${FLOW_COURIER_TOKEN}    ${FLOW_ORDER_ID}
    Should Be True    ${resp.status_code} < 400    Deliver failed: ${resp.text}

    # Verify order status changed to DELIVERED (terminal state)
    ${order_resp}=    Get Order By ID    ${CUSTOMER_TOKEN}    ${FLOW_ORDER_ID}
    Should Be Equal    ${order_resp.json()}[status]    DELIVERED
    Log    Order delivered successfully - flow complete    level=INFO
