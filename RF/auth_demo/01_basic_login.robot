*** Settings ***
Library    RequestsLibrary
Library    Collections
Library    FakerLibrary
Resource    variables.resource
Suite Setup    Create Session    alias=api    url=${AUTH_BASE_URL}    verify=True

*** Variables ***
${TEST_PASSWORD}     TestPass123!

*** Test Cases ***
Session Login Flow
    [Documentation]    Registrace nového uživatele, s login session, ověření na /me endpoint
    [Tags]    session    smoke    happy-path

    ${TEST_EMAIL}=    Email
    ${TEST_USERNAME}=    User Name

    VAR    &{headres}    Content-Type=application/json
    VAR    &{user_data}    username=${TEST_USERNAME}    email=${TEST_EMAIL}    password=${TEST_PASSWORD}
    ${register_response}=    POST On Session    alias=api    url=${REGISTER_ENDPOINT}    json=${user_data}    headers=${headres}    expected_status=anything
    Status Should Be    200    ${register_response}
    Log    Status: ${register_response.status_code}
    Log    Celá response: ${register_response.json()}
    Log    Response text: ${register_response.text}

    VAR    &{login_headers}    Content-Type=application/x-www-form-urlencoded
    VAR    ${login_bofy}    username=${TEST_USERNAME}&password=${TEST_PASSWORD}
    ${login_response}=    POST On Session    alias=api    url=${SESSION_LOGIN_URL}    data=${login_bofy}    headers=${login_headers}    expected_status=anything
    Status Should Be    200    ${login_response}
    Log    ME response_ ${login_response.json()}

    ${me_response}=    GET On Session    alias=api    url=${SESSION_ME_URL}    expected_status=anything

    Should Be Equal    ${me_response.json()}[username]    ${TEST_USERNAME}
    Log    Test prošel s uživatelem : ${TEST_EMAIL}



*** Keywords ***
