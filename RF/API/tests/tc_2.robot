*** Settings ***
Library           RequestsLibrary
Library           DatabaseLibrary
Library           FakerLibrary
Library           Collections
Library           jwt
Library    OperatingSystem
Resource          ../common.resource
Resource          ../../db/common.resource

Suite Setup    Connect To Database    db_module=${DB_MODULE}    db_name=${DB_NAME}    db_user=${DB_USER}    
...    db_password=${DB_PASSWORD}    db_host=${DB_HOST}    db_port=${DB_PORT}    alias=${DB_ALIAS}
Suite Teardown   Disconnect From Database

*** Variables ***
${BASE_URL_API}    http://localhost:20300
${COURIERS_URL_API}    /api/v1/couriers/
${ORDERS_URL_API}     /api/v1/orders/

${POST_TOKEN_OAUTH_2}    http://localhost:5101/oauth2/token
${SECRET_KEY}    super-secret-key-change-in-production-123!

${DB_MODULE}    psycopg2
${DB_NAME}       moje_app
${DB_USER}       postgres
${DB_PASSWORD}   postgres
${DB_HOST}       localhost
${DB_PORT}       20343

${CLIENT_CERT}       ${CURDIR}${/}..${/}..${/}certs${/}client.crt
${CLIENT_KEY}        ${CURDIR}${/}..${/}..${/}certs${/}client.key
${CA_CERT}           ${CURDIR}${/}..${/}..${/}certs${/}ca.crt
${MTLS_BASE_URL}     https://localhost
${MTLS_URL}         https://localhost/api/v1/orders/

*** Test Cases ***
Create Courier and Verify in Database
    [Documentation]    This test case creates a courier via API and verifies its existence in the database.
    ${token}=    Get Auth Token With Role    role=admin    user_id=1
    VAR    &{headers}    Authorization=Bearer ${token}

    ${email}=    Email
    ${name}=     Name
    ${phone}=    PhoneNumber
    VAR    @{tags}    bike    vip
    VAR    &{courier}    email=${email}    name=${name}    phone=${phone}    tags=${tags}
    Create Session    alias=courier_api    url=${BASE_URL_API}
    ${resp}=    API request    method=POST    alias=courier_api    url=${COURIERS_URL_API}    json=${courier}    headers=${headers}    expected_status=anything
    Should Be True    ${resp.status_code} < 300    Check for 2xx status code
    VAR    ${json}    ${resp.json()}
    VAR    ${email_for_verify}    ${json}[email]
    ${query}=    Query    SELECT email FROM couriers WHERE email='${email}'
    Log    \nSQL Query: ${query}    console=${LOG_TO_CONSOLE}
    Should Be Equal    ${email_for_verify}    ${email}    Verify created courier in DB

Get Orders 
    [Documentation]    This test case retrieves orders via API and verifies the response.
    ${token}=    Get Auth Token
    VAR    &{headers}    Authorization=Bearer ${token}
    Create Session    alias=courier_api    url=${BASE_URL_API}
    ${resp}=    API request    method=GET    alias=courier_api    url=${ORDERS_URL_API}    headers=${headers}    expected_status=anything    
    Should Be True    ${resp.status_code} < 300    Check for 2xx
    Log    \nResponse JSON: ${resp.json()}    console=${LOG_TO_CONSOLE}

Delete Order As Courier - Should Fail
    [Documentation]    This test case attempts to delete an order as a courier and expects failure.
    ${token}=    Get Auth Token
    VAR    &{headers}    Authorization=Bearer ${token}
    Create Session    alias=courier_api    url=${BASE_URL_API}
    ${resp}=    API request    method=DELETE    alias=courier_api    url=${ORDERS_URL_API} + '1/'    headers=${headers}    expected_status=anything
    Should Be True    ${resp.status_code} >= 400    Expecting client error status code (4xx)

Delete Order As Admin - Should Succeed
    [Documentation]    This test case deletes an order as an admin and expects success.
    ${token}=    Get Auth Token With Role    role=admin    user_id=2
    VAR    &{headers}    Authorization=Bearer ${token}

    ${name}=    Name
    ${customer_phone}=    PhoneNumber
    ${pickup_address}=    Address
    ${delivery_address}=    Address


    VAR    &{order_data}    customer_name=${name}    customer_phone=${customer_phone}    pickup_address=${pickup_address}    pickup_lat=${{50.0}}
    ...    pickup_lng=${{14.0}}   delivery_address=${delivery_address}    delivery_lat=${{50.1}}    delivery_lng=${{14.1}}

    ${create_resp}=    API request    method=POST    alias=courier_api    url=${ORDERS_URL_API}    json=${order_data}    headers=${headers}    expected_status=anything
    Should Be True    ${create_resp.status_code} < 300    Check for successful order creation (2xx)
    VAR    ${order_id}    ${create_resp.json()}[id]

    Log    \nCreated Order ID: ${order_id}    console=${LOG_TO_CONSOLE}

    ${resp_delete}=    API request    method=DELETE    alias=courier_api    url=${ORDERS_URL_API}${order_id}    headers=${headers}    expected_status=anything
    Should Be True    ${resp_delete.status_code} < 300    Expecting successful deletion (2xx)

Create Order With CSRF Token
    [Documentation]    This test case creates an order using a CSRF token and verifies the response.
    ${csrf_token}=    Get CSRF Token
    ${token}=    Get Auth Token With Role    role=admin    user_id=2
    VAR    &{headers}    Authorization=Bearer ${token}    X-CSRF-Token=${csrf_token}

    ${name}=    Name
    ${customer_phone}=    PhoneNumber

    VAR    &{order_data}
    ...    customer_name=${name}
    ...    customer_phone=${customer_phone}
    ...    pickup_address=Test Pickup
    ...    pickup_lat=${{50.0}}
    ...    pickup_lng=${{14.0}}
    ...    delivery_address=Test Delivery
    ...    delivery_lat=${{50.1}}
    ...    delivery_lng=${{14.1}}

    ${resp}=    API request    method=POST    alias=courier_api    url=${ORDERS_URL_API}    json=${order_data}    headers=${headers}    expected_status=anything
    Should Be True    ${resp.status_code} < 300    Check for successful order creation (2xx)
    Log    \nResponse JSON: ${resp.json()}    console=${LOG_TO_CONSOLE}

mTLS - With Certificate Should Succeed
    [Documentation]    This test case makes a GET request to an mTLS endpoint using client certificates.
    [Tags]    mtls    skip
    ${token}=    Get Auth Token With Role    role=admin    user_id=2

    # Skip mTLS test if certificates don't exist
    ${cert_exists}=    Run Keyword And Return Status    File Should Exist    ${CLIENT_CERT}
    Skip If    not ${cert_exists}    Client certificate not found at ${CLIENT_CERT}

    # PowerShell command for mTLS request - using escaped braces
    ${ps_cmd}=    Catenate    SEPARATOR=${SPACE}
    ...    powershell -Command
    ...    "& { $cert = New-Object System.Security.Cryptography.X509Certificates.X509Certificate2('${CLIENT_CERT}', '');"
    ...    Invoke-RestMethod -Uri '${MTLS_URL}'"
    ...    -Method Get"
    ...    -Headers \\@{'Authorization'='Bearer ${token}'}"
    ...    -Certificate $cert } | ConvertTo-Json"

    Log    \nExecuting: ${ps_cmd}    console=${LOG_TO_CONSOLE}

    ${output}=    Run    ${ps_cmd}

    Log    \nResponse: ${output}    console=${LOG_TO_CONSOLE}


*** Keywords ***
Get Auth Token
    [Documentation]    This keyword retrieves an authentication token from the OAuth2 endpoint.
    VAR    &{payload}    sub=admin1    user_id=2    role=admin    scopes=orders:read orders:write orders:admin
    ...    exp=${{datetime.datetime.utcnow() + datetime.timedelta(hours=1)}}    iat=${{datetime.datetime.utcnow()}}
    ${token}=    Evaluate    jwt.encode(${payload}, '${SECRET_KEY}', algorithm='HS256')    modules=jwt,datetime
    RETURN    ${token}

Get Auth Token With Role
    [Arguments]    ${role}    ${user_id}
    [Documentation]    Generuje JWT token se specifickou rolí
    ${payload}=    Create Dictionary
    ...    sub=${role}1
    ...    user_id=${user_id}
    ...    role=${role}
    ...    scopes=orders:read orders:write
    ...    exp=${{datetime.datetime.utcnow() + datetime.timedelta(hours=1)}}
    ...    iat=${{datetime.datetime.utcnow()}}

    ${token}=    Evaluate    jwt.encode(${payload}, '${SECRET_KEY}', algorithm='HS256')    modules=jwt,datetime
    RETURN    ${token}

Get CSRF Token
    [Documentation]    This keyword retrieves a CSRF token from the API.
    Create Session    alias=courier_api    url=${BASE_URL_API}
    ${token}=    Get Auth Token With Role    admin    2
    VAR    &{headers}    Authorization=Bearer ${token}

    ${resp}=    API request    method=GET    alias=courier_api    url=/api/v1/auth/csrf-token    headers=${headers}    expected_status=anything
    Should Be True    ${resp.status_code} < 300    Check for successful response (2xx)
    VAR    ${csrf_token}    ${resp.json()}[csrf_token]
    Log    \nRetrieved CSRF Token: ${csrf_token}    console=${LOG_TO_CONSOLE}
    RETURN    ${csrf_token}