*** Settings ***
Library    Browser
Library    RPA.FTP
Library    FakerLibrary
Library    Collections
Library    JSONLibrary
Library    OperatingSystem
Library    String
Library    RequestsLibrary
Library    RobotEyes
Library    DateTime
Resource    ../UI/locators/form_page_locators.resource
Resource    ../UI/locators/page2_locators.resource
Resource    ../UI/pages/form_page.resource
Resource    ../UI/pages/page2.resource
Resource    variables.resource

# *** API Connections ***
Resource    ../RF/API/common.resource

# *** DB Connections ***
Resource    ../RF/db/common.resource

*** Keywords ***

Vytvoří Session pro API
    [Arguments]    ${base_url}
    Create Session    mysession    ${base_url}

Upload File
    [Arguments]    ${file}    ${locator}
    Promise To Upload File    ${file}
    Click On The Element    ${locator}

Provision Browser Session
    [Arguments]    ${BROWSER}    ${HEADLESS}    ${URL}    ${WIDTH}    ${HEIGHT}
    New Browser    ${browser}    headless=${headless}        # The browser is defined in the Variables.resource file
    New Context    ignoreHTTPSErrors=True
    New Page    ${URL}
    Set Viewport Size    ${WIDTH}    ${HEIGHT}

Provison Device Session
    [Arguments]    ${BROWSER}    ${HEADLESS}    ${URL}    ${DEVICE}
    ${device_config}=    Get Device    ${DEVICE}
    New Browser    ${BROWSER}    headless=${HEADLESS}
    New Context    &{device_config}    ignoreHTTPSErrors=true
    New Page    ${URL}

Click On The Element
    [Documentation]    Klikne na element na stránce pomocí zadaného selektoru a volitelného názvu kontextu pro lepší chybové hlášení
    [Arguments]    ${locator}    ${context_name}=${EMPTY}
    TRY
        Wait For Elements State    ${locator}    attached    ${TIMEOUT}
        Wait For Elements State    ${locator}    visible     ${TIMEOUT}
        Wait For Elements State    ${locator}    enabled     ${TIMEOUT}
        Click    ${locator}
    EXCEPT    AS    ${err}
        Take Screenshot
        ${msg}=    Set Variable    Selhání když, '${context_name}' --> | selector='${locator}' | ERROR: ${err}
        Fail    ${msg}
    END

Fill Text In Input Field
    [Documentation]    Vyplní zadaný text do pole na stránce pomocí zadaného selektoru a volitelného názvu kontextu pro lepší chybové hlášení
    [Arguments]    ${locator}    ${text}    ${context_name}=${EMPTY}
    TRY
        Wait For Elements State    ${locator}    attached    ${TIMEOUT}
        Wait For Elements State    ${locator}    visible     ${TIMEOUT}
        Wait For Elements State    ${locator}    enabled     ${TIMEOUT}
        Click    ${locator}
        Clear Text    ${locator}
        Fill Text    ${locator}    ${text}
    EXCEPT    AS    ${err}
        Take Screenshot
        ${msg}=    Set Variable    Selhání když, '${context_name}' --> | locator='${locator}' | ERROR: ${err}
        Fail    ${msg}
    END

Get Text From Element
    [Documentation]    Získá text z elementu na stránce pomocí zadaného selektoru a volitelného názvu kontextu pro lepší chybové hlášení
    [Arguments]    ${locator}    ${context_name}=${EMPTY}
    ${text}=    Set Variable    ${EMPTY}
    TRY
        Wait For Elements State    ${locator}    attached    ${TIMEOUT}
        Wait For Elements State    ${locator}    visible     ${TIMEOUT}
        Wait For Elements State    ${locator}    enabled     ${TIMEOUT}
        ${text}=    browser.Get Text    ${locator}
    EXCEPT    AS    ${err}
        Take Screenshot
        ${msg}=    Set Variable    Selhání když, '${context_name}' --> | locator='${locator}' | ERROR: ${err}
        Fail    ${msg}
    END
    RETURN    ${text}

Ověření Přítomnosti Elementu Na Stránce
    [Documentation]    Ověří přítomnost elementu na stránce pomocí zadaného selektoru a volitelného názvu kontextu pro lepší chybové hlášení
    [Arguments]    ${locator}    ${context_name}=${EMPTY}
    TRY
        Wait For Elements State    ${locator}    attached    ${TIMEOUT}
        Wait For Elements State    ${locator}    visible     ${TIMEOUT}
        Wait For Elements State    ${locator}    enabled     ${TIMEOUT}
        
    EXCEPT    AS    ${err}
        Take Screenshot
        ${msg}=    Set Variable    Selhalo  '${context_name}' --> | locator='${locator}' | ERROR: ${err}
        Fail    ${msg}
    END

Ověření Vyplněné Hodnoty Z Elementu
    [Documentation]    Ověření vyplněné hodnoty pro daný field
    [Arguments]    ${locator}    ${starý_text}    ${context_name}
    TRY
        ${ziskany_text}=    Get Text From Element    ${locator}    
        Should Be Equal    ${starý_text}    ${ziskany_text}
    EXCEPT    AS    ${err}
    Take Screenshot
    ${msg}=    Set Variable    Selhání pří ověření, '${context_name}' --> | locator='${locator}' | ERROR: ${err}
                
    END
    RETURN    ${ziskany_text}

Connect To My Database
    [Arguments]    ${db_api}    ${db_name}    ${db_username}    ${db_password}    ${db_host}    ${db_port}
    Connect To Database    ${db_api}    ${db_name}    ${db_username}    ${db_password}    ${db_host}    ${db_port}