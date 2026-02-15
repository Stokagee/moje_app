*** Settings ***
Library    RequestsLibrary
Library    Collections
Library    FakerLibrary
Resource    variables.resource
Suite Setup    Create Session    alias=api    url=${AUTH_BASE_URL}    verify=True

*** Variables ***
${pass}    Pass123!


*** Test Cases ***

Zíkat a uložit cookies
    [Documentation]    Zíksat cookies a uložit do suite variable
    [Tags]    smoke    save_cookies

    ${username}=    User Name
    ${email}=    Email    

    VAR    &{user_credentials}    username=${username}    email=${email}    password=${pass}
    VAR    &{headres}    Content-Type=application/json

    ${username_response}=    POST On Session    alias=api    url=${REGISTER_ENDPOINT}    headers=${headres}    json=${user_credentials}    expected_status=anything
    Status Should Be    200    ${username_response}

    VAR    &{login_headers}    Content-Type=application/x-www-form-urlencoded
    VAR    ${login_bofy}    username=${username}&password=${pass}
    ${login_response}=    POST On Session    alias=api    url=${SESSION_LOGIN_URL}    data=${login_bofy}    headers=${login_headers}    expected_status=anything
    Status Should Be    200    ${login_response}
    Log    ME response_ ${login_response.json()}

    VAR    ${json}    ${login_response.cookies}

    Log To Console    ${json}[session_id]

    VAR    ${SAVED_COOKIES}    {json}[session_id]    scope=SUITE
