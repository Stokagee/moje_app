*** Settings ***
Library    Browser
Suite Setup    New Browser    chromium    headless=False
Test Setup    New Context    viewport={"width": 1000, "height": 8000}
Test Teardown    Close Context
Suite Teardown    Close Browser

*** Variables ***

${url}    https://www.saucedemo.com/
${user_name}    [data-test="username"]
${password}    [data-test="password"]
&{credentials}    username=standard_user    password=secret_sauce
${back_pack_item}    css=btn.btn_primary.btn_small.btn_inventory

*** Test Cases ***
Task 3: First Interaction - Type Text & Click
    [Setup]    New Page    ${url}
    Get Title    ==    Swag Labs
    get login form elements
    Get Login Button Text


*** Keywords ***

get login form elements
    ${username_field}=    Get Element    [data-test="username"]
    ${password_field}=    Get Element    [data-test="password"]
    ${login_button}=    Get Element    [name="login-button"]

    Log To Console    \n===\n ${username_field} \n===\n
    Log To Console    \n===\n ${password_field} \n===\n
    Log To Console    \n===\n ${login_button} \n===\n

    RETURN    ${username_field}    ${password_field}    ${login_button}


Get Login Button Text
    ${text}=    Get Text    text=Login
    RETURN    ${text}
