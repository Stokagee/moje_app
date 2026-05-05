*** Settings ***
Documentation     Orders API endpoint keywords.
...               Provides reusable keywords for testing Orders CRUD and lifecycle.

Library           RequestsLibrary
Library           Collections
Library           FakerLibrary    locale=cs_CZ

Resource          ../resources/auth.resource
Resource          ../variables.resource


*** Keywords ***
Generate Order Body
    [Documentation]    Generate random OrderCreate body using FakerLibrary.
    ...    Schema:
    ...    - customer_name: str (2-100 chars)
    ...    - customer_phone: str (9-20 chars)
    ...    - pickup_address: str (3-200 chars)
    ...    - pickup_lat: float (-90 to 90)
    ...    - pickup_lng: float (-180 to 180)
    ...    - delivery_address: str (3-200 chars)
    ...    - delivery_lat: float (-90 to 90)
    ...    - delivery_lng: float (-180 to 180)
    ...    - is_vip: bool (default False)
    ...    - required_tags: list (default [])
    ...
    ...    Returns:
    ...    - body: Dictionary with random order data
    ${customer_name}=    FakerLibrary.Name
    ${customer_phone}=    FakerLibrary.Phone Number

    # Generate addresses
    ${pickup_street}=    FakerLibrary.Street Address
    ${delivery_street}=    FakerLibrary.Street Address
    ${pickup_address}=    Set Variable    ${pickup_street}, Praha
    ${delivery_address}=    Set Variable    ${delivery_street}, Praha

    # Prague coordinates with random offset (within ~5km)
    ${lat_offset}=    Evaluate    random.uniform(-0.05, 0.05)
    ${lng_offset}=    Evaluate    random.uniform(-0.05, 0.05)
    ${pickup_lat}=    Evaluate    round(50.0755 + ${lat_offset}, 6)
    ${pickup_lng}=    Evaluate    round(14.4378 + ${lng_offset}, 6)

    # Delivery slightly different from pickup
    ${lat_offset2}=    Evaluate    random.uniform(-0.05, 0.05)
    ${lng_offset2}=    Evaluate    random.uniform(-0.05, 0.05)
    ${delivery_lat}=    Evaluate    round(50.0755 + ${lat_offset2}, 6)
    ${delivery_lng}=    Evaluate    round(14.4378 + ${lng_offset2}, 6)

    ${body}=    Create Dictionary
    ...    customer_name=${customer_name}
    ...    customer_phone=${customer_phone}
    ...    pickup_address=${pickup_address}
    ...    pickup_lat=${pickup_lat}
    ...    pickup_lng=${pickup_lng}
    ...    delivery_address=${delivery_address}
    ...    delivery_lat=${delivery_lat}
    ...    delivery_lng=${delivery_lng}
    ...    is_vip=${False}
    ...    required_tags=@{EMPTY}
    RETURN    ${body}

Generate Courier Body
    [Documentation]    Generate random CourierCreate body using FakerLibrary.
    ...    Returns:
    ...    - body: Dictionary with random courier data
    ${name}=    FakerLibrary.Name
    ${phone}=    FakerLibrary.Phone Number
    ${email}=    FakerLibrary.Email

    ${body}=    Create Dictionary
    ...    name=${name}
    ...    phone=${phone}
    ...    email=${email}
    RETURN    ${body}

# =============================================================================
# Orders CRUD Operations
# =============================================================================

Create Order
    [Documentation]    Create a new order via POST /orders/.
    ...    Args:
    ...    - token: Bearer token (required)
    ...    - body: OrderCreate body (optional, will generate if not provided)
    ...
    ...    Returns:
    ...    - response: Response object
    [Arguments]    ${token}    ${body}=${None}
    IF    ${body} is None
        ${body}=    Generate Order Body
    END
    ${headers}=    Get Auth Headers    ${token}
    ${resp}=    POST On Session    api    /orders/    json=${body}    headers=${headers}    expected_status=anything
    RETURN    ${resp}

Get All Orders
    [Documentation]    Get all orders via GET /orders/.
    ...    Args:
    ...    - token: Bearer token (required)
    ...    - skip: Pagination offset (default: 0)
    ...    - limit: Max results (default: 100)
    ...
    ...    Returns:
    ...    - response: Response object
    [Arguments]    ${token}    ${skip}=0    ${limit}=100
    ${headers}=    Get Auth Headers    ${token}
    ${params}=    Create Dictionary    skip=${skip}    limit=${limit}
    ${resp}=    GET On Session    api    /orders/    headers=${headers}    params=${params}    expected_status=anything
    RETURN    ${resp}

Get Order By ID
    [Documentation]    Get order by ID via GET /orders/{id}.
    ...    Args:
    ...    - token: Bearer token (required)
    ...    - order_id: Order ID to fetch
    ...
    ...    Returns:
    ...    - response: Response object
    [Arguments]    ${token}    ${order_id}
    ${headers}=    Get Auth Headers    ${token}
    ${resp}=    GET On Session    api    /orders/${order_id}    headers=${headers}    expected_status=anything
    RETURN    ${resp}

# =============================================================================
# Orders Lifecycle Operations
# =============================================================================

Dispatch Order Auto
    [Documentation]    Auto-dispatch order to nearest courier via POST /dispatch/auto/{id}.
    ...    Args:
    ...    - token: Bearer token (admin)
    ...    - order_id: Order ID to dispatch
    ...
    ...    Returns:
    ...    - response: Response object
    [Arguments]    ${token}    ${order_id}
    ${headers}=    Get Auth Headers    ${token}
    ${resp}=    POST On Session    api    /dispatch/auto/${order_id}    headers=${headers}    expected_status=anything
    RETURN    ${resp}

Pickup Order
    [Documentation]    Mark order as picked up via POST /orders/{id}/pickup.
    ...    Requires courier role and ownership.
    ...    Args:
    ...    - token: Bearer token (courier)
    ...    - order_id: Order ID to pickup
    ...
    ...    Returns:
    ...    - response: Response object
    [Arguments]    ${token}    ${order_id}
    ${headers}=    Get Auth Headers    ${token}
    ${resp}=    POST On Session    api    /orders/${order_id}/pickup    headers=${headers}    expected_status=anything
    RETURN    ${resp}

Deliver Order
    [Documentation]    Mark order as delivered via POST /orders/{id}/deliver.
    ...    Requires courier role and ownership.
    ...    Args:
    ...    - token: Bearer token (courier)
    ...    - order_id: Order ID to deliver
    ...
    ...    Returns:
    ...    - response: Response object
    [Arguments]    ${token}    ${order_id}
    ${headers}=    Get Auth Headers    ${token}
    ${resp}=    POST On Session    api    /orders/${order_id}/deliver    headers=${headers}    expected_status=anything
    RETURN    ${resp}

Cancel Order
    [Documentation]    Cancel order via POST /orders/{id}/cancel.
    ...    Args:
    ...    - token: Bearer token
    ...    - order_id: Order ID to cancel
    ...
    ...    Returns:
    ...    - response: Response object
    [Arguments]    ${token}    ${order_id}
    ${headers}=    Get Auth Headers    ${token}
    ${resp}=    POST On Session    api    /orders/${order_id}/cancel    headers=${headers}    expected_status=anything
    RETURN    ${resp}

Delete Order
    [Documentation]    Delete order via DELETE /orders/{id}.
    ...    Requires admin role.
    ...    Args:
    ...    - token: Bearer token (admin)
    ...    - order_id: Order ID to delete
    ...
    ...    Returns:
    ...    - response: Response object
    [Arguments]    ${token}    ${order_id}
    ${headers}=    Get Auth Headers    ${token}
    ${resp}=    DELETE On Session    api    /orders/${order_id}    headers=${headers}    expected_status=anything
    RETURN    ${resp}

# =============================================================================
# Courier Operations
# =============================================================================

Create Courier
    [Documentation]    Create a new courier via POST /couriers/.
    ...    Args:
    ...    - token: Bearer token (admin)
    ...    - body: CourierCreate body (optional, will generate if not provided)
    ...
    ...    Returns:
    ...    - response: Response object
    [Arguments]    ${token}    ${body}=${None}
    IF    ${body} is None
        ${body}=    Generate Courier Body
    END
    ${headers}=    Get Auth Headers    ${token}
    ${resp}=    POST On Session    api    /couriers/    json=${body}    headers=${headers}    expected_status=anything
    RETURN    ${resp}

Set Courier Location
    [Documentation]    Set courier GPS location via PATCH /couriers/{id}/location.
    ...    Args:
    ...    - token: Bearer token (admin)
    ...    - courier_id: Courier ID
    ...    - lat: Latitude (default: Prague center)
    ...    - lng: Longitude (default: Prague center)
    ...
    ...    Returns:
    ...    - response: Response object
    [Arguments]    ${token}    ${courier_id}    ${lat}=50.0755    ${lng}=14.4378
    ${headers}=    Get Auth Headers    ${token}
    ${body}=    Create Dictionary    lat=${lat}    lng=${lng}
    ${resp}=    PATCH On Session    api    /couriers/${courier_id}/location    json=${body}    headers=${headers}    expected_status=anything
    RETURN    ${resp}

Set Courier Available
    [Documentation]    Set courier status to available via PATCH /couriers/{id}/status.
    ...    Args:
    ...    - token: Bearer token (admin)
    ...    - courier_id: Courier ID
    ...
    ...    Returns:
    ...    - response: Response object
    [Arguments]    ${token}    ${courier_id}
    ${headers}=    Get Auth Headers    ${token}
    ${body}=    Create Dictionary    status=available
    ${resp}=    PATCH On Session    api    /couriers/${courier_id}/status    json=${body}    headers=${headers}    expected_status=anything
    RETURN    ${resp}

# =============================================================================
# Assertion Keywords
# =============================================================================

Order Should Be Created
    [Documentation]    Verify order was created successfully (status code 201).
    ...    Args:
    ...    - response: Response object
    [Arguments]    ${response}
    Should Be Equal As Integers    ${response.status_code}    201
    Dictionary Should Contain Key    ${response.json()}    id

Order Should Be Fetched
    [Documentation]    Verify order was fetched successfully (status code 200).
    ...    Args:
    ...    - response: Response object
    [Arguments]    ${response}
    Should Be Equal As Integers    ${response.status_code}    200
    Dictionary Should Contain Key    ${response.json()}    id

Order Should Be Unauthorized
    [Documentation]    Verify request was unauthorized (status code 401).
    ...    Args:
    ...    - response: Response object
    [Arguments]    ${response}
    Should Be Equal As Integers    ${response.status_code}    401

Order Should Be Validation Error
    [Documentation]    Verify validation error (status code 422).
    ...    Args:
    ...    - response: Response object
    [Arguments]    ${response}
    Should Be Equal As Integers    ${response.status_code}    422
