*** Settings ***
Documentation     Authorization Code Flow - Kompletní OAuth2 Authorization Code flow
...               Tento test ověřuje:
...               - Authorization request s client_id a redirect_uri
...               - Consent stránka pro uživatelské schválení
...               - Získání authorization code
...               - Výměnu code za access token
...               - Použití access tokenu

Library           RequestsLibrary
Library           Collections
Library           String

Test Setup        Create Session    auth    ${BASE_URL}

*** Variables ***
${BASE_URL}            http://localhost:10003
${CLIENT_ID}           demo-client
${CLIENT_SECRET}       demo-client-secret
${REDIRECT_URI}        http://localhost:3000/callback
${USERNAME}            demo
${PASSWORD}            demo123


*** Test Cases ***
Authorization Code - Complete Flow
    [Documentation]    Kompletní Authorization Code flow

    # 1. Požádat o authorization (inicializovat flow)
    Log To Console     \n=== 1. Initiate Authorization ===
    ${state}=          Generate Random String    16    [LOWERLETTERS]

    &{params}=         Create Dictionary
                       ...                client_id=${CLIENT_ID}
                       ...                redirect_uri=${REDIRECT_URI}
                       ...                response_type=code
                       ...                state=${state}
                       ...                scope=read write

    ${auth_response}=  GET On Session    auth    /oauth2/authorize
                       ...                params=&{params}
                       ...                allow_redirects=False

    # Response by měl být 200 (zobrazení consent stránky)
    Should Be Equal As Numbers    ${auth_response.status_code}    200
    Log To Console     Consent page returned (200)

    # 2. Odsouhlasit (simulace uživatele)
    Log To Console     \n=== 2. User Approves Consent ===
    &{approve_data}=   Create Dictionary
                       ...                client_id=${CLIENT_ID}
                       ...                redirect_uri=${REDIRECT_URI}
                       ...                state=${state}
                       ...                scopes=read write
                       ...                username=${USERNAME}
                       ...                password=${PASSWORD}

    ${approve_response}=    POST On Session    auth    /oauth2/approve
                            ...                data=&{approve_data}
                            ...                allow_redirects=False

    # Response by měl být 302 Redirect
    Should Be Equal As Numbers    ${approve_response.status_code}    302

    # Získat redirect URL s code
    ${location}=       Set Variable    ${approve_response.headers}[Location]
    Log To Console     Redirect URL: ${location}

    # Extrakce code z URL
    # URL vypadá: http://localhost:3000/callback?code=xyz&state=abc
    ${code}=           Fetch From Right    ${location}    code=
    ${and_pos}=        Find    ${code}    &
    ${code}=           Run Keyword If    ${and_pos} > 0
                       ...                Get Substring    ${code}    0    ${and_pos}
                       ...                ELSE    Set Variable    ${code}

    Should Not Be Empty    ${code}
    Log To Console     Authorization Code: ${code}

    # Ověřit state v redirect URL
    Should Contain    ${location}    state=${state}

    # 3. Vyměnit code za access token
    Log To Console     \n=== 3. Exchange Code for Token ===
    &{token_data}=     Create Dictionary
                       ...                grant_type=authorization_code
                       ...                code=${code}
                       ...                client_id=${CLIENT_ID}
                       ...                client_secret=${CLIENT_SECRET}
                       ...                redirect_uri=${REDIRECT_URI}

    ${token_response}=    POST On Session    auth    /oauth2/token
                         ...                data=&{token_data}

    Should Be Equal As Numbers    ${token_response.status_code}    200

    ${access_token}=   Set Variable    ${token_response.json()}[access_token]
    ${token_type}=     Set Variable    ${token_response.json()}[token_type]
    ${expires_in}=     Set Variable    ${token_response.json()}[expires_in]
    ${scope}=          Set Variable    ${token_response.json()}[scope]

    Log To Console     Access Token: ${access_token[:30]}...
    Log To Console     Token Type: ${token_type}
    Log To Console     Expires In: ${expires_in} seconds
    Log To Console     Scope: ${scope}

    Should Be Equal    ${token_type}    bearer
    Should Contain    ${scope}    read
    Should Contain    ${scope}    write

    # 4. Použít access token pro získání user info
    Log To Console     \n=== 4. Use Access Token ===
    &{headers}=        Create Dictionary    Authorization=Bearer ${access_token}

    ${userinfo}=       GET On Session    auth    /oauth2/userinfo
                       ...                params=token=${access_token}
                       ...                headers=&{headers}

    Should Be Equal As Numbers    ${userinfo.status_code}    200

    ${user_id}=        Set Variable    ${userinfo.json()}[sub]
    ${username}=       Set Variable    ${userinfo.json()}[username]
    ${email}=          Set Variable    ${userinfo.json()}[email]

    Log To Console     User ID: ${user_id}
    Log To Console     Username: ${username}
    Log To Console     Email: ${email}

    Should Be Equal    ${username}    ${USERNAME}

    # 5. Zkusit použít stejný code znovu (měl by selhat - single use)
    Log To Console     \n=== 5. Verify Code Single-Use ===
    ${reuse_response}=    POST On Session    auth    /oauth2/token
                         ...                data=&{token_data}
                         ...                expected_status=anything

    Should Be Equal As Numbers    ${reuse_response.status_code}    400
    Log To Console     Code reuse correctly prevented (400)


Authorization Code - Invalid Client ID
    [Documentation]    Ověřit chování při neplatném client_id

    Log To Console     \n=== Testing Invalid Client ID ===

    &{params}=         Create Dictionary
                       ...                client_id=invalid-client
                       ...                redirect_uri=${REDIRECT_URI}
                       ...                response_type=code
                       ...                scope=read

    ${response}=       GET On Session    auth    /oauth2/authorize
                       ...                params=&{params}
                       ...                expected_status=anything

    Should Be Equal As Numbers    ${response.status_code}    400
    Log To Console     Invalid client_id correctly rejected (400)


Authorization Code - Invalid Redirect URI
    [Documentation]    Ověřit validaci redirect URI

    Log To Console     \n=== Testing Invalid Redirect URI ===

    &{params}=         Create Dictionary
                       ...                client_id=${CLIENT_ID}
                       ...                redirect_uri=http://evil.com/callback
                       ...                response_type=code
                       ...                scope=read

    ${response}=       GET On Session    auth    /oauth2/authorize
                       ...                params=&{params}
                       ...                expected_status=anything

    Should Be Equal As Numbers    ${response.status_code}    400
    Log To Console     Invalid redirect URI correctly rejected (400)


Authorization Code - Invalid Credentials on Consent
    [Documentation]    Ověřit, že špatné heslo na consent stránce selže

    Log To Console     \n=== Testing Invalid User Credentials ===

    &{approve_data}=   Create Dictionary
                       ...                client_id=${CLIENT_ID}
                       ...                redirect_uri=${REDIRECT_URI}
                       ...                state=random-state
                       ...                scopes=read
                       ...                username=${USERNAME}
                       ...                password=wrong-password

    ${response}=       POST On Session    auth    /oauth2/approve
                       ...                data=&{approve_data}
                       ...                expected_status=anything

    # Should return consent page with error (200)
    Should Be Equal As Numbers    ${response.status_code}    200
    Log To Console     Invalid credentials rejected, consent page shown again


Authorization Code - Token Exchange with Invalid Code
    [Documentation]    Ověřit, že neplatný code nelze vyměnit za token

    Log To Console     \n=== Testing Token Exchange with Invalid Code ===

    &{token_data}=     Create Dictionary
                       ...                grant_type=authorization_code
                       ...                code=invalid_code_xyz
                       ...                client_id=${CLIENT_ID}
                       ...                client_secret=${CLIENT_SECRET}
                       ...                redirect_uri=${REDIRECT_URI}

    ${response}=       POST On Session    auth    /oauth2/token
                       ...                data=&{token_data}
                       ...                expected_status=anything

    Should Be Equal As Numbers    ${response.status_code}    400
    Log To Console     Invalid code correctly rejected (400)


Authorization Code - Token Exchange with Wrong Secret
    [Documentation]    Ověřit, že client secret se musí shodovat

    Log To Console     \n=== Testing Token Exchange with Wrong Secret ===

    # First get a valid code
    ${state}=          Generate Random String    16    [LOWERLETTERS]

    &{approve_data}=   Create Dictionary
                       ...                client_id=${CLIENT_ID}
                       ...                redirect_uri=${REDIRECT_URI}
                       ...                state=${state}
                       ...                scopes=read
                       ...                username=${USERNAME}
                       ...                password=${PASSWORD}

    ${approve_response}=    POST On Session    auth    /oauth2/approve
                            ...                data=&{approve_data}
                            ...                allow_redirects=False

    ${location}=       Set Variable    ${approve_response.headers}[Location]
    ${code}=           Fetch From Right    ${location}    code=
    ${and_pos}=        Find    ${code}    &
    ${code}=           Run Keyword If    ${and_pos} > 0
                       ...                Get Substring    ${code}    0    ${and_pos}
                       ...                ELSE    Set Variable    ${code}

    # Try to exchange with wrong secret
    &{token_data}=     Create Dictionary
                       ...                grant_type=authorization_code
                       ...                code=${code}
                       ...                client_id=${CLIENT_ID}
                       ...                client_secret=wrong-secret
                       ...                redirect_uri=${REDIRECT_URI}

    ${response}=       POST On Session    auth    /oauth2/token
                       ...                data=&{token_data}
                       ...                expected_status=anything

    Should Be Equal As Numbers    ${response.status_code}    401
    Log To Console     Wrong client secret correctly rejected (401)


*** Keywords ***
Create Session
    [Arguments]        ${alias}    ${base_url}
    Create Session    ${alias}    ${base_url}    disable_warnings=True
