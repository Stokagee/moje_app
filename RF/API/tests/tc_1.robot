*** Settings ***
Resource    ../common.resource
Resource    ../resources/auth.resource
Library           Collections

Test Setup    Create Session    api    ${API_BASE_URL}/api/v1    verify=${False}

*** Variables ***
${is_vip}    False
${pickup_lat}    50.0815
${pickup_long}   14.4195
${delivery_lat}    50.0755
${delivery_long}   14.4378
${phone}    +420123456789
${params}    ?skip=0&limit=10
${AUTH_TOKEN}    ${EMPTY}

*** Test Cases ***
Create flow
    [Documentation]    Create basic order with valid data and verify response status code and content.
    # First get auth token
    ${token}=    Get Customer Token
    Set Suite Variable    ${AUTH_TOKEN}    ${token}

    # First create an order to work with
    ${order_id}=    Create Basic Order
    Set Suite Variable    ${ORDER_ID}    ${order_id}

    #Creating an order of minimum length
    #Creating an order maximum length
    #Order List Pagination
    Order details with courier    ${order_id}


*** Keywords ***
Create Basic Order
    [Documentation]    Create a basic order and return its ID.
    ${headers}=    Create Dictionary    Authorization=Bearer ${AUTH_TOKEN}

    ${json}    Generate Data From Schema    method=POST    endpoint=/api/v1/orders/    openapi_url=http://localhost:20300/openapi.json    target=api
    ...    amount=1

    ${response}=    POST On Session    api    /orders/    json=${json}    headers=${headers}    expected_status=anything
    Status Should Be    201    ${response}
    VAR    ${status_json}    ${response.json()}[status]
    VAR    ${order_id}    ${response.json()}[id]
    Log    ====> Created order ${order_id} with status: ${status_json}    level=INFO    console=${LOG_TO_CONSOLE}
    RETURN    ${order_id}

Creating an order of minimum length
    ${json}    Generate Data From Schema    method=POST    endpoint=/api/v1/orders/    openapi_url=http://localhost:20300/openapi.json    target=api
    ...    amount=1
    VAR    ${min_name}    ${json}[customer_name][0:2]

    Log    ====> Generated JSON for minimum length order: ${json}    level=INFO    console=${LOG_TO_CONSOLE}

    Set To Dictionary    ${json}    customer_name=${min_name}

    ${response}=    API request    method=POST    alias=${DEFAULT_SESSION}    url=/api/v1/orders/    json=${json}    expected_status=anything    context_name=Creating an order of minimum length
    Status Should Be    201    ${response}
    VAR    ${status_json}    ${response.json()}[status]
    Log    ====> Response status: ${status_json}    level=INFO    console=${LOG_TO_CONSOLE}

Creating an order maximum length
    ${json}    Generate Data From Schema    method=POST    endpoint=/api/v1/orders/    openapi_url=http://localhost:20300/openapi.json    target=api
    ...    amount=1
    
    VAR    ${max_name}    ${json}[customer_name][0:2]
    ${base_name}    Evaluate    '${max_name}' * 100

    Log    ====> Generated JSON for maximum length order: ${json}    level=INFO    console=${LOG_TO_CONSOLE}

    Set To Dictionary    ${json}    customer_name=${base_name}

    ${response}=    API request    method=POST    alias=${DEFAULT_SESSION}    url=/api/v1/orders/    json=${json}    expected_status=201    context_name=Creating an order of maximum length
    Status Should Be    201    ${response}
    VAR    ${status_json}    ${response.json()}[status]
    Log    ====> Response status: ${status_json}    level=INFO    console=${LOG_TO_CONSOLE}

Order List Pagination
    ${response}=    API request    method=GET    alias=${DEFAULT_SESSION}    url=/api/v1/orders/    params=${params}    expected_status=200    context_name=Order List Pagination
    Status Should Be    200    ${response}
    VAR    ${orders}    ${response.json()}
    Log    ====> Total orders retrieved: ${orders}    level=INFO    console=${LOG_TO_CONSOLE}
    Length Should Be    ${orders}    10    msg=Expected 10 orders in paginated response, but got ${orders}

Order details with courier
    [Arguments]    ${order_id}
    ${headers}=    Create Dictionary    Authorization=Bearer ${AUTH_TOKEN}
    ${response}=    GET On Session    api    /orders/${order_id}    headers=${headers}    expected_status=anything
    Status Should Be    200    ${response}
    VAR    ${order_details}    ${response.json()}
    Log    ====> Order details: ${order_details}    level=INFO    console=${LOG_TO_CONSOLE}