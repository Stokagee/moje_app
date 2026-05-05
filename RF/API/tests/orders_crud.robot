*** Settings ***
Documentation     CRUD tests for Orders API.
...               Tests: Create, Read (all + by ID), basic operations.

Library           RequestsLibrary
Library           Collections

Resource          ../resources/auth.resource
Resource          ../endpoints/orders_endpoints.resource
Resource          ../variables.resource

Suite Setup       Suite Setup With Tokens
Suite Teardown    Delete All Sessions


*** Variables ***
${ORDER_ID}    ${EMPTY}


*** Keywords ***
Suite Setup With Tokens
    Create Session    api    ${API_BASE_URL}/api/v1    verify=${API_VERIFY_SSL}
    ${admin}=    Get Admin Token
    ${courier}=    Get Courier Token    user_id=10
    ${customer}=    Get Customer Token    user_id=100
    Set Suite Variable    ${ADMIN_TOKEN}    ${admin}
    Set Suite Variable    ${COURIER_TOKEN}    ${courier}
    Set Suite Variable    ${CUSTOMER_TOKEN}    ${customer}


*** Test Cases ***
10 Create Order
    [Documentation]    Create a new order with random data.
    [Tags]    api    orders    crud    post
    ${resp}=    Create Order    ${CUSTOMER_TOKEN}
    Order Should Be Created    ${resp}

    ${order_id}=    Set Variable    ${resp.json()}[id]
    Set Suite Variable    ${ORDER_ID}    ${order_id}
    Log    Order created with ID: ${ORDER_ID}    level=INFO

11 Get All Orders
    [Documentation]    Get list of all orders.
    [Tags]    api    orders    crud    get
    ${resp}=    Get All Orders    ${CUSTOMER_TOKEN}
    Should Be True    ${resp.status_code} < 400    Failed: ${resp.text}
    Log    Retrieved ${resp.json().__len__()} orders    level=INFO

12 Get Order By ID
    [Documentation]    Get specific order by ID.
    [Tags]    api    orders    crud    get
    Skip If    "${ORDER_ID}" == "${EMPTY}"    No order created
    ${resp}=    Get Order By ID    ${CUSTOMER_TOKEN}    ${ORDER_ID}
    Order Should Be Fetched    ${resp}

    ${order}=    Set Variable    ${resp.json()}
    Should Be Equal As Integers    ${order}[id]    ${ORDER_ID}
    Log    Retrieved order ${ORDER_ID}: status=${order}[status]    level=INFO
