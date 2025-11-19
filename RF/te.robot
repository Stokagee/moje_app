*** Settings ***
Resource    ../RF/UI/common.resource

Library    ImageComparisonLibrary
Suite Teardown    Run Keyword And Ignore Error    Cleanup Test Artifacts
*** Variables ***
${TIMEOUT_TEST}    15s
${login_email}    dusan.cizmarik@continero.com
${login_password}    123456
${test_url}    https://dev.artima.ai/Login
${test_width}    1280
${test_height}    720
${BASELINE_IMAGE_PATH}    C:/Users/stoka/Documents/moje_app/RF/libraries/images/baseline/
${SCREENSHOT_PATH}    C:/Users/stoka/Documents/moje_app/RF/libraries/images/screenshot/
${RESULTS_IMAGE_PATH}    C:/Users/stoka/Documents/moje_app/RF/libraries/images/results/
${actual_image}    C:/Users/stoka/Documents/moje_app/RF/libraries/images/baseline/login_page_20251118_174339.png

# *** Locators ***
${LOGIN_EMAIL_INPUT}    [data-testid="login-email-input"]
${LOGIN_PASSWORD_INPUT}    [data-testid="login-password-input"]
${LOGIN_SUBMIT_BUTTON}    [data-testid="login-submit-button"]
${MAIN_DASHBOARD_H1}    "Dashboard"


*** Test Cases ***
Přihlášení Uživatele
    ${actual_time_stamp}=    Get Current Date    result_format=%Y%m%d_%H%M%S
    Provision Browser Session    ${BROWSER}    ${HEADLESS}    ${test_url}    ${test_width}    ${test_height}
    Wait For Load State    domcontentloaded
    Add Style Tag    css    
    ${diff_image_path}=    Set Variable    ${RESULTS_IMAGE_PATH}login_page_diff_${actual_time_stamp}.png
    Vyplnit Email Pro Přihlášení    ${login_email}
    Vyplnit Heslo Pro Přihlášení    ${login_password}
    Kliknout Na Přihlásit Tlačítko
    ${image_for_test}=    Take Screenshot    filename=${SCREENSHOT_PATH}login_page_${actual_time_stamp}.png
    Compare Layouts And Generate Diff   ${BASELINE_IMAGE_PATH}login_page_20251118_174339.png    ${image_for_test}    ${diff_image_path}    
    ...    pixel_tolerance=45    hash_size=16    diff_mode=contours    contour_thickness=3    min_contour_area=1500
     ...    minor_color=(0, 255, 0)    moderate_color=(0, 255, 255)    severe_color=(0, 0, 255)
    Wait For Elements State    ${MAIN_DASHBOARD_H1}    ${TIMEOUT_TEST}


*** Keywords ***
Vyplnit Email Pro Přihlášení
    [Arguments]    ${email}
    Fill Text In Input Field    ${LOGIN_EMAIL_INPUT}    ${email}    jsem chtěl zadat email pro přihlášení

Vyplnit Heslo Pro Přihlášení
    [Arguments]    ${password}
    Fill Text In Input Field    ${LOGIN_PASSWORD_INPUT}    ${password}    jsem chtěl zadat heslo pro přihlášení
Kliknout Na Přihlásit Tlačítko
    Click On The Element    ${LOGIN_SUBMIT_BUTTON}    jsem chtěl kliknout na přihlásit tlačítko

Cleanup Test Artifacts
    [Documentation]    Vyčistí složky s aktuálními a diff obrázky po skončení testů.
    TRY
        # Smažeme všechny soubory ve složce 'current/'
        # ${CURRENT_DIR}* znamená "všechno uvnitř složky CURRENT_DIR"
        Remove Files    ${SCREENSHOT_PATH}*
        
        # Smažeme všechny soubory ve složce 'diff/'
        Remove Files    ${SCREENSHOT_PATH}*
    EXCEPT    AS    ${err}
        Log To Console    Chyba při čištění testovacích artefaktů: ${err}
    END
    Log    Cleanup finished. Current and Diff directories are empty.