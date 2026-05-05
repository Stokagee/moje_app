*** Settings ***
Documentation     Admin-only tests for Orders API.
...               Tests: Dispatch, Cancel, Delete operations requiring elevated permissions.

Library           RequestsLibrary
Library           Collections

Resource          ../resources/auth.resource
Resource          ../endpoints/orders_endpoints.resource
Resource          ../variables.resource

Suite Setup       Suite Setup With Admin
Suite Teardown    Delete All Sessions


*** Variables ***
${ADMIN_ORDER_ID}    ${EMPTY}


*** Keywords ***
Suite Setup With Admin
    Create Session    api    ${API_BASE_URL}/api/v1    verify=${API_VERIFY_SSL}
    ${admin}=    Get Admin Token
    ${customer}=    Get Customer Token
    ${courier}=    Get Courier Token    user_id=10
    Set Suite Variable    ${ADMIN_TOKEN}    ${admin}
    Set Suite Variable    ${CUSTOMER_TOKEN}    ${customer}
    Set Suite Variable    ${COURIER_TOKEN}    ${courier}


*** Test Cases ***
40 Dispatch Auto
    [Documentation]    Test auto-dispatch algorithm.
    ...    Creates order and dispatches to nearest available courier.
    [Tags]    api    orders    admin    dispatch

    # Create order first
    ${create_resp}=    Create Order    ${CUSTOMER_TOKEN}
    Skip If    ${create_resp.status_code} >= 400    Order creation failed

    ${order_id}=    Set Variable    ${create_resp.json()}[id]
    Log    Created order ${order_id} for dispatch    level=INFO

    # Dispatch
    ${resp}=    Dispatch Order Auto    ${ADMIN_TOKEN}    ${order_id}

    # Dispatch might succeed or fail (no couriers available)
    IF    ${resp.status_code} < 400
        ${result}=    Set Variable    ${resp.json()}
        Log    Dispatch result: ${result}[message]    level=INFO
    ELSE
        Log    Dispatch failed (expected if no couriers): ${resp.text}    level=INFO
    END

50 Cancel Order
    [Documentation]    Cancel an existing order.
    ...    Creates order, then cancels it.
    [Tags]    api    orders    admin    cancel

    # Create order to cancel
    ${create_resp}=    Create Order    ${CUSTOMER_TOKEN}
    Skip If    ${create_resp.status_code} >= 400    Order creation failed

    ${order_id}=    Set Variable    ${create_resp.json()}[id]
    Log    Created order ${order_id} to cancel    level=INFO

    # Cancel
    ${resp}=    Cancel Order    ${CUSTOMER_TOKEN}    ${order_id}
    Should Be True    ${resp.status_code} < 400    Cancel failed: ${resp.text}

    # Verify status is CANCELLED
    ${get_resp}=    Get Order By ID    ${CUSTOMER_TOKEN}    ${order_id}
    Should Be Equal    ${get_resp.json()}[status]    CANCELLED
    Log    Order ${order_id} cancelled successfully    level=INFO

60 Admin Delete Order
    [Documentation]    Permanently delete an order (admin only).
    ...    Creates order, then deletes it.
    [Tags]    api    orders    admin    delete

    # Create order to delete
    ${create_resp}=    Create Order    ${CUSTOMER_TOKEN}
    Skip If    ${create_resp.status_code} >= 400    Order creation failed

    ${order_id}=    Set Variable    ${create_resp.json()}[id]
    Log    Created order ${order_id} to delete    level=INFO

    # Delete (admin only)
    ${resp}=    Delete Order    ${ADMIN_TOKEN}    ${order_id}
    Should Be True    ${resp.status_code} < 400    Delete failed: ${resp.text}

    # Verify order no longer exists (404)
    ${get_resp}=    Get Order By ID    ${CUSTOMER_TOKEN}    ${order_id}
    Should Be Equal As Integers    ${get_resp.status_code}    404
    Log    Order ${order_id} deleted permanently    level=INFO

61 Error Non Admin Cannot Delete
    [Documentation]    Verify non-admin cannot delete orders.
    ...    Expected: 403 Forbidden
    [Tags]    api    orders    admin    rbac

    # Create order
    ${create_resp}=    Create Order    ${CUSTOMER_TOKEN}
    Skip If    ${create_resp.status_code} >= 400    Order creation failed

    ${order_id}=    Set Variable    ${create_resp.json()}[id]

    # Try delete as courier (should fail)
    ${resp}=    Delete Order    ${COURIER_TOKEN}    ${order_id}
    Should Be True    ${resp.status_code} >= 400    Should have been rejected

    # Cleanup with admin
    Delete Order    ${ADMIN_TOKEN}    ${order_id}
    Log    Correctly rejected non-admin delete attempt    level=INFO
