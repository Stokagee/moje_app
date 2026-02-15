*** Settings ***
Documentation     Refresh Token Flow - Kompletní testování refresh token toku
...               Tento test ověřuje:
...               - Login vrátí access i refresh token
...               - Access token lze použít pro autentizované requesty
...               - Refresh token získá nový access token bez loginu
...               - Token rotation (starý refresh token je zneplatněn)
...               - Logout zneplatní refresh tokeny

Library           RequestsLibrary
Library           Collections
Library           DateTime

Test Setup        Create Session    auth    ${BASE_URL}

*** Variables ***
${BASE_URL}       http://localhost:10001
${API_V1}         /api/v1
${USERNAME}       testuser
${PASSWORD}       testpass123
${EMAIL}          testuser@example.com


*** Test Cases ***
Refresh Token - Complete Flow
    [Documentation]    Kompletní refresh token cyklus od loginu po logout

    # 1. Register a new user
    Log To Console     \n=== 1. Register User ===
    &{headers}=        Create Dictionary    Content-Type=application/json
    &{register_data}=  Create Dictionary
    ...                username=${USERNAME}
    ...                email=${EMAIL}
    ...                password=${PASSWORD}

    ${register}=       POST On Session    auth    ${API_V1}/auth/register
                       ...                json=&{register_data}
                       ...                headers=&{headers}
                       ...                expected_status=anything

    # Log if user already exists
    Log To Console     Register status: ${register.status_code}

    # 2. Login - získat access i refresh token
    Log To Console     \n=== 2. Login and Get Tokens ===
    &{login_data}=     Create Dictionary
    ...                username=${USERNAME}
    ...                password=${PASSWORD}

    ${response}=       POST On Session    auth    ${API_V1}/auth/login
                       ...                json=&{login_data}
                       ...                headers=&{headers}

    Should Be Equal As Numbers    ${response.status_code}    200

    ${access_token}=     Set Variable    ${response.json()}[access_token]
    ${refresh_token}=    Set Variable    ${response.json()}[refresh_token]
    ${token_type}=       Set Variable    ${response.json()}[token_type]
    ${expires_in}=       Set Variable    ${response.json()}[expires_in]

    Log To Console     Access Token: ${access_token[:30]}...
    Log To Console     Refresh Token: ${refresh_token[:30]}...
    Log To Console     Token Type: ${token_type}
    Log To Console     Expires In: ${expires_in} seconds

    Should Be Equal    ${token_type}    bearer
    Should Be True     ${expires_in} > 0

    # 3. Použít access token pro autentizovaný request
    Log To Console     \n=== 3. Use Access Token ===
    &{auth_headers}=   Create Dictionary
                       ...                Authorization=Bearer ${access_token}

    ${me}=             GET On Session    auth    ${API_V1}/auth/me
                       ...                headers=&{auth_headers}

    Should Be Equal As Numbers    ${me.status_code}    200

    ${user_id}=         Set Variable    ${me.json()}[id]
    ${username}=        Set Variable    ${me.json()}[username]
    ${user_email}=      Set Variable    ${me.json()}[email]

    Log To Console     User ID: ${user_id}
    Log To Console     Username: ${username}
    Log To Console     Email: ${user_email}

    Should Be Equal    ${username}    ${USERNAME}
    Should Be Equal    ${user_email}    ${EMAIL}

    # 4. Refresh - získat nový access token bez loginu
    Log To Console     \n=== 4. Refresh Token ===
    &{refresh_body}=   Create Dictionary    refresh_token=${refresh_token}

    ${refresh_response}=    POST On Session    auth    ${API_V1}/auth/refresh
                            ...                json=&{refresh_body}

    Should Be Equal As Numbers    ${refresh_response.status_code}    200

    ${new_access_token}=    Set Variable    ${refresh_response.json()}[access_token]
    ${new_refresh_token}=   Set Variable    ${refresh_response.json()}[refresh_token]

    Log To Console     New Access Token: ${new_access_token[:30]}...
    Log To Console     New Refresh Token: ${new_refresh_token[:30]}...

    # Nové tokeny by měly být jiné než původní
    Should Not Be Equal    ${new_access_token}    ${access_token}
    Should Not Be Equal    ${new_refresh_token}   ${refresh_token}

    # 5. Použít nový access token
    Log To Console     \n=== 5. Use New Access Token ===
    &{new_auth_headers}=    Create Dictionary
                            ...                Authorization=Bearer ${new_access_token}

    ${me2}=            GET On Session    auth    ${API_V1}/auth/me
                       ...                headers=&{new_auth_headers}

    Should Be Equal As Numbers    ${me2.status_code}    200
    Should Be Equal    ${me2.json()}[username]    ${USERNAME}

    # 6. Ověřit token rotation - starý refresh token by měl být neplatný
    Log To Console     \n=== 6. Verify Token Rotation ===
    ${old_refresh}=    POST On Session    auth    ${API_V1}/auth/refresh
                       ...                json=&{refresh_body}
                       ...                expected_status=anything

    Should Be Equal As Numbers    ${old_refresh.status_code}    401
    Log To Console     Old refresh token correctly revoked (401)

    # 7. Logout - zneplatnit refresh tokeny
    Log To Console     \n=== 7. Logout ===
    ${logout}=         POST On Session    auth    ${API_V1}/auth/logout
                       ...                headers=&{new_auth_headers}

    Should Be Equal As Numbers    ${logout.status_code}    200
    Log To Console     Logout successful

    # 8. Ověřit, že po logoutu nelze refreshovat
    Log To Console     \n=== 8. Verify Refresh After Logout ===
    &{new_refresh_body}=    Create Dictionary    refresh_token=${new_refresh_token}

    ${after_logout}=   POST On Session    auth    ${API_V1}/auth/refresh
                       ...                json=&{new_refresh_body}
                       ...                expected_status=anything

    Should Be Equal As Numbers    ${after_logout.status_code}    401
    Log To Console     Refresh token correctly revoked after logout


Refresh Token - Invalid Token
    [Documentation]    Ověřit chování při neplatném refresh tokenu

    Log To Console     \n=== Testing Invalid Refresh Token ===

    &{headers}=        Create Dictionary    Content-Type=application/json
    &{invalid_body}=   Create Dictionary    refresh_token=invalid_token_xyz

    ${response}=       POST On Session    auth    ${API_V1}/auth/refresh
                       ...                json=&{invalid_body}
                       ...                headers=&{headers}
                       ...                expected_status=anything

    Should Be Equal As Numbers    ${response.status_code}    401
    Log To Console     Invalid token correctly rejected (401)


Refresh Token - Expired Token
    [Documentation]    Ověřit chování při expirovaném refresh tokenu

    Log To Console     \n=== Testing Expired Refresh Token ===
    Log To Console     (V produkci by byl token expirován, zde jen simulace)

    # Zkusíme použít falešný "expirovaný" token
    &{headers}=        Create Dictionary    Content-Type=application/json
    &{expired_body}=   Create Dictionary    refresh_token=expired_token_12345

    ${response}=       POST On Session    auth    ${API_V1}/auth/refresh
                       ...                json=&{expired_body}
                       ...                headers=&{headers}
                       ...                expected_status=anything

    Should Be Equal As Numbers    ${response.status_code}    401
    Log To Console     Expired token correctly rejected (401)


Access Token - Unauthorized Request
    [Documentation]    Ověřit, že bez tokenu nelze přistupovat k chráněným endpointům

    Log To Console     \n=== Testing Unauthorized Request ===

    ${response}=       GET On Session    auth    ${API_V1}/auth/me
                       ...                expected_status=anything

    Should Be Equal As Numbers    ${response.status_code}    403
    Log To Console     Request without token correctly rejected (403)


Access Token - Invalid Token
    [Documentation]    Ověřit chování při neplatném access tokenu

    Log To Console     \n=== Testing Invalid Access Token ===

    &{headers}=        Create Dictionary    Authorization=Bearer invalid_token

    ${response}=       GET On Session    auth    ${API_V1}/auth/me
                       ...                headers=&{headers}
                       ...                expected_status=anything

    Should Be Equal As Numbers    ${response.status_code}    401
    Log To Console     Invalid access token correctly rejected (401)


*** Keywords ***
Create Session
    [Arguments]        ${alias}    ${base_url}
    Create Session    ${alias}    ${base_url}    disable_warnings=True
