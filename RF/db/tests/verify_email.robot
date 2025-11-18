*** Settings ***
Resource    ../common.resource


*** Variables ***
${email_to_verify}    elizabeth21@example.com

*** Test Cases ***
Verify Email In Database
    [Documentation]    Ověří, že email existuje v databázi po registraci uživatele.
    Connect To Test Database
    ${email}=    Set Variable    ${email_to_verify}
    Verify Row Count In Database    SELECT * FROM form_data WHERE email = '${email}'    ==    1