*** Settings ***
Documentation     Client Credentials Flow - Machine-to-Machine autentizace
...               Tento test ověřuje:
...               - Získání tokenu bez uživatelského kontextu
...               - Použití M2M tokenu pro přístup k API
...               - Scope-based access control
...               - Token introspekci
...               - Public vs. protected endpointy

Library           RequestsLibrary
Library           Collections

Test Setup        Create Session    m2m    ${BASE_URL}

*** Variables ***
${BASE_URL}            http://localhost:10002
${CLIENT_ID}           demo-service
${CLIENT_SECRET}       demo-secret123
${INVALID_CLIENT_ID}   invalid-client
${INVALID_SECRET}      wrong-secret


*** Test Cases ***
Client Credentials - Complete Flow
    [Documentation]    Kompletní M2M autentizace od získání tokenu po API volání

    # 1. Získat token jako service (bez uživatele!)
    Log To Console     \n=== 1. Get M2M Token ===
    &{form_data}=      Create Dictionary
                       ...                grant_type=client_credentials
                       ...                client_id=${CLIENT_ID}
                       ...                client_secret=${CLIENT_SECRET}
                       ...                scope=read write

    ${response}=       POST On Session    m2m    /oauth2/token
                       ...                data=&{form_data}

    Should Be Equal As Numbers    ${response.status_code}    200

    ${access_token}=    Set Variable    ${response.json()}[access_token]
    ${token_type}=      Set Variable    ${response.json()}[token_type]
    ${expires_in}=      Set Variable    ${response.json()}[expires_in]
    ${scope}=           Set Variable    ${response.json()}[scope]

    Log To Console     Access Token: ${access_token[:30]}...
    Log To Console     Token Type: ${token_type}
    Log To Console     Expires In: ${expires_in} seconds
    Log To Console     Scope: ${scope}

    Should Be Equal    ${token_type}    bearer
    Should Contain    ${scope}    read
    Should Contain    ${scope}    write

    # 2. Volat public endpoint bez tokenu
    Log To Console     \n=== 2. Call Public Endpoint (No Token) ===
    ${public}=         GET On Session    m2m    /api/v1/data

    Should Be Equal As Numbers    ${public.status_code}    200
    Log To Console     Public data: ${public.json()}

    # 3. Volat protected endpoint s tokenem
    Log To Console     \n=== 3. Call Protected Endpoint (With Token) ===
    &{headers}=        Create Dictionary    Authorization=Bearer ${access_token}

    ${secure}=         GET On Session    m2m    /api/v1/secure/data
                       ...                headers=&{headers}

    Should Be Equal As Numbers    ${secure.status_code}    200

    ${message}=        Set Variable    ${secure.json()}[message]
    ${client_name}=    Set Variable    ${secure.json()}[client]

    Log To Console     Secure message: ${message}
    Log To Console     Client name: ${client_name}

    Should Contain    ${message}    read access

    # 4. Získat informace o klientovi
    Log To Console     \n=== 4. Who Am I (Client Info) ===
    ${whoami}=         GET On Session    m2m    /api/v1/whoami
                       ...                headers=&{headers}

    Should Be Equal As Numbers    ${whoami.status_code}    200

    Log To Console     Client info: ${whoami.json()}

    # 5. Vytvořit data (write scope)
    Log To Console     \n=== 5. Create Data (Write Scope) ===
    &{new_data}=       Create Dictionary    name=Test Item    value=123

    ${created}=        POST On Session    m2m    /api/v1/secure/data
                       ...                json=&{new_data}
                       ...                headers=&{headers}

    Should Be Equal As Numbers    ${created.status_code}    200
    Log To Console     Created: ${created.json()}


Client Credentials - Invalid Credentials
    [Documentation]    Ověřit chování při neplatných klient credentials

    Log To Console     \n=== Testing Invalid Client Credentials ===

    &{form_data}=      Create Dictionary
                       ...                grant_type=client_credentials
                       ...                client_id=${INVALID_CLIENT_ID}
                       ...                client_secret=${INVALID_SECRET}
                       ...                scope=read

    ${response}=       POST On Session    m2m    /oauth2/token
                       ...                data=&{form_data}
                       ...                expected_status=anything

    Should Be Equal As Numbers    ${response.status_code}    401
    Log To Console     Invalid credentials correctly rejected (401)


Client Credentials - Invalid Grant Type
    [Documentation]    Ověřit odmítnutí nepodporovaného grant typu

    Log To Console     \n=== Testing Invalid Grant Type ===

    &{form_data}=      Create Dictionary
                       ...                grant_type=password
                       ...                client_id=${CLIENT_ID}
                       ...                client_secret=${CLIENT_SECRET}

    ${response}=       POST On Session    m2m    /oauth2/token
                       ...                data=&{form_data}
                       ...                expected_status=anything

    Should Be Equal As Numbers    ${response.status_code}    400
    Log To Console     Invalid grant type correctly rejected (400)


Client Credentials - Scope Validation
    [Documentation]    Ověřit scope-based access control

    # 1. Získat token pouze se 'read' scope
    Log To Console     \n=== 1. Get Token with Read Scope Only ===
    &{form_data}=      Create Dictionary
                       ...                grant_type=client_credentials
                       ...                client_id=${CLIENT_ID}
                       ...                client_secret=${CLIENT_SECRET}
                       ...                scope=read

    ${response}=       POST On Session    m2m    /oauth2/token
                       ...                data=&{form_data}

    ${access_token}=   Set Variable    ${response.json()}[access_token]

    # 2. Zkusit volat read endpoint (mělo by fungovat)
    Log To Console     \n=== 2. Access Read Endpoint (Should Work) ===
    &{headers}=        Create Dictionary    Authorization=Bearer ${access_token}

    ${secure}=         GET On Session    m2m    /api/v1/secure/data
                       ...                headers=&{headers}

    Should Be Equal As Numbers    ${secure.status_code}    200
    Log To Console     Read access granted

    # 3. Zkusit volat admin endpoint (nemá admin scope - selže)
    Log To Console     \n=== 3. Access Admin Endpoint (Should Fail) ===
    ${admin}=          GET On Session    m2m    /api/v1/secure/admin
                       ...                headers=&{headers}
                       ...                expected_status=anything

    Should Be Equal As Numbers    ${admin.status_code}    403
    Log To Console     Admin access correctly denied (403)


Client Credentials - Token Introspection
    [Documentation]    Ověřit token introspection endpoint

    # 1. Získat token
    Log To Console     \n=== 1. Get Token ===
    &{form_data}=      Create Dictionary
                       ...                grant_type=client_credentials
                       ...                client_id=${CLIENT_ID}
                       ...                client_secret=${CLIENT_SECRET}
                       ...                scope=read

    ${response}=       POST On Session    m2m    /oauth2/token
                       ...                data=&{form_data}

    ${access_token}=   Set Variable    ${response.json()}[access_token]

    # 2. Introspectovat token
    Log To Console     \n=== 2. Introspect Token ===
    &{introspect_body}=    Create Dictionary    token=${access_token}

    ${introspect}=     POST On Session    m2m    /oauth2/introspect
                       ...                json=&{introspect_body}

    Should Be Equal As Numbers    ${introspect.status_code}    200

    ${active}=         Set Variable    ${introspect.json()}[active]
    ${client_id}=      Set Variable    ${introspect.json()}[client_id]
    ${scopes}=         Set Variable    ${introspect.json()}[scopes]

    Log To Console     Token active: ${active}
    Log To Console     Client ID: ${client_id}
    Log To Console     Scopes: ${scopes}

    Should Be Equal    ${active}    ${True}
    Should Be Equal    ${client_id}    ${CLIENT_ID}

    # 3. Introspectovat neplatný token
    Log To Console     \n=== 3. Introspect Invalid Token ===
    &{invalid_body}=   Create Dictionary    token=invalid_token_xyz

    ${invalid}=        POST On Session    m2m    /oauth2/introspect
                       ...                json=&{invalid_body}

    Should Be Equal As Numbers    ${invalid.status_code}    200
    Should Be Equal    ${invalid.json()}[active]    ${False}
    Log To Console     Invalid token correctly identified as inactive


Client Credentials - Protected Endpoint Without Token
    [Documentation]    Ověřit, že chráněný endpoint odmítne request bez tokenu

    Log To Console     \n=== Testing Protected Endpoint Without Token ===

    ${response}=       GET On Session    m2m    /api/v1/secure/data
                       ...                expected_status=anything

    Should Be Equal As Numbers    ${response.status_code}    403
    Log To Console     Request without token correctly rejected (403)


Client Credentials - Protected Endpoint With Invalid Token
    [Documentation]    Ověřit, že chráněný endpoint odmítne neplatný token

    Log To Console     \n=== Testing Protected Endpoint With Invalid Token ===

    &{headers}=        Create Dictionary    Authorization=Bearer invalid_token_xyz

    ${response}=       GET On Session    m2m    /api/v1/secure/data
                       ...                headers=&{headers}
                       ...                expected_status=anything

    Should Be Equal As Numbers    ${response.status_code}    401
    Log To Console     Invalid token correctly rejected (401)


*** Keywords ***
Create Session
    [Arguments]        ${alias}    ${base_url}
    Create Session    ${alias}    ${base_url}    disable_warnings=True
