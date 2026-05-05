*** Settings ***
Library           RequestsLibrary
Library           DatabaseLibrary
Library           FakerLibrary
Library           Browser
Library           Collections
Library           jwt
Library           OperatingSystem
Resource          ../common.resource
Resource          ../../db/common.resource
Resource           ../../UI/common.resource

Suite Setup    Suite Setup Options
Suite Teardown    Clear After Suite


*** Variables ***
${base_api_endpoint_url}    http://localhost:20300
${form_endpoint_url}        /api/v1/form/
${BROWSER}                  chromium
${HEADLESS}                 False
${URL}                      http://localhost:20301

# Variables from UI
${main_seznam_button}    [data-testid="menu-item-Page2-text"]

# Database connection variables
${DB_MODULE}    psycopg2
${DB_NAME}       moje_app
${DB_USER}       postgres
${DB_PASSWORD}   postgres
${DB_HOST}       localhost
${DB_PORT}       20343

*** Test Cases ***
Create New Form With Instructions
    [Documentation]    Test case to create a new form with instructions and verify the response.
    ${first_name}=    Random Name Data
    ${last_name}=     Random Last Name Data
    ${email}=         Random Email Data
    ${phone_number}=  Random Phone Number Data
    ${gender}=        Choose Random Gender
    ${attachment}=    Create Attachment For Form

    VAR    &{form_data}    first_name=${first_name}
    ...    last_name=${last_name}
    ...    email=${email}
    ...    phone=${phone_number}
    ...    gender=${gender}

    ${create_new_form_response}=    API request    method=POST    alias=form    url=${form_endpoint_url}    json=${form_data}    expected_status=201    
    Should Be True    ${create_new_form_response.status_code} == 201    Failed to create a new form, expected status code 201 but got ${create_new_form_response.status_code}
    VAR    ${json_from_response}    ${create_new_form_response.json()}
    ${create_new_attachment_response}=    API request    method=POST    alias=form    url=${form_endpoint_url}${json_from_response['id']}/attachment/    json=${attachment}    expected_status=201
    Should Be True    ${create_new_attachment_response.status_code} == 201    Failed to create attachment for form with id ${json_from_response['id']}, expected status code 201 but got ${create_new_attachment_response.status_code}
    Navigate To Page 2
    ${full_name}=    Click On The Name On Page 2    ${first_name}    ${last_name}
    Verify Email In Info Modal    ${email}
    Click On OK In Info Modal
    ${id}=    Get ID By Name    ${full_name}
    ${db_result_for_verify_id}=    Get Single DB Value    SELECT id FROM form_data WHERE id=%s    ${id}
    Should Be Equal As Integers    ${db_result_for_verify_id}    ${id}    Verification of ID in DB failed, no record found with id=${id}
    Delete Form By ID    ${id}
    Refresh Page
    Verify Name Is Deleted    ${first_name}    ${last_name}
    Verify Row Count In Database    SELECT * FROM form_data WHERE id=${id}    ==    0

*** Keywords ***

Random Name Data
    [Documentation]    Generate random name data using FakerLibrary.
    ${first_name}=    First Name
    RETURN    ${first_name}

Random Last Name Data
    [Documentation]    Generate random last name data using FakerLibrary.
    ${last_name}=    Last Name
    RETURN    ${last_name}

Random Email Data
    [Documentation]    Generate random email data using FakerLibrary.
    ${email}=    Email
    RETURN    ${email}

Random Phone Number Data
    [Documentation]    Generate random phone number data using FakerLibrary.
    ${phone_number}=    Phone Number
    RETURN    ${phone_number}

Choose Random Gender
    [Documentation]    Randomly choose a gender from a predefined list.
    VAR    @{genders}    male    female    other
    ${random_index}=    Evaluate    expression=random.randint(0, len(${genders}) - 1)    modules=random
    ${random_gender}=    Get From List    ${genders}    ${random_index}
    RETURN    ${random_gender}

Create Attachment For Form
    [Documentation]    Create a sample attachment for the form.
    ${file_content}=    Get Binary File    path=C:\\Users\\stoka\\Documents\\moje_app\\priloha_demo.txt
    ${encoded_content}=   Evaluate    base64.b64encode($file_content).decode()    modules=base64

    VAR    &{attachment}    filename=priloha_demo.txt
    ...    content_type=text/plain
    ...    data_base64=${encoded_content}
    ...    instructions=Sample attachment instructions
    RETURN    ${attachment}

Open Session Browser And Navigate To Page
    [Documentation]    Open a browser session and navigate to the page.
    TRY
        Open Browser    ${URL}    ${BROWSER}    headless=${HEADLESS}    pause_on_failure=False
    VAR    ${err}    Selhalo otevření prohlížeče | ERROR: ${URL} \n${BROWSER}
    EXCEPT    AS    ${err}
        Fail    Selhalo otevření prohlížeče | ERROR: ${err}
    END

Create New Api Session
    [Documentation]    Create a new API session for making requests.
    TRY
        Create API Session    session_alias=form    base_url=${base_api_endpoint_url}
    VAR    ${err}    Bad base URL: ${base_api_endpoint_url}
    EXCEPT    AS    ${err}
        Fail    Selhalo vytvoření API session | ERROR: ${err}
    END

Suite Setup Options
    [Documentation]    Suite setup to initialize browser session and API session.
    Open Session Browser And Navigate To Page
    Create New Api Session
    Connect To Database    db_module=${DB_MODULE}    db_name=${DB_NAME}    db_user=${DB_USER}    db_password=${DB_PASSWORD}    db_host=${DB_HOST}    db_port=${DB_PORT}

Navigate To Page 2
    Click On The Element    ${main_seznam_button}    Navigate to Page 2

Click On The Name On Page 2
    [Documentation]    Click on the name on Page 2 and return the full name.
    [Arguments]    ${name}    ${last_name}
    ${full_name}=    Catenate    "${name}     ${last_name}"
    Wait For Elements State    ${full_name}    visible    ${TIMEOUT}
    Click    text=${full_name}
    RETURN    ${full_name}

Verify Email In Info Modal
    [Documentation]    Verify that the email displayed in the info modal matches the expected email.
    [Arguments]    ${email}
    ${email_text}=    Get Text From Element    ${PAGE2_INFO_MODAL_EMAIL}    Email v modalu
    Should Be Equal As Strings    ${email_text}    ${email}

Click On OK In Info Modal
    Click On The Element    ${PAGE2_INFO_MODAL_OK_BUTTON}

Get ID By Name
    [Arguments]    ${searched_name}
    
    ${count}=    Get Element Count    ${FORM_ROW_LIST_ITEMS_TEXT}
    
    FOR    ${i}    IN RANGE    ${count}
        ${text}=    Get Text From Element    ${FORM_ROW_LIST_ITEMS_TEXT} >> nth=${i}
        ${text_with_quotes}=    Catenate    "${text}"
        
        IF    $text_with_quotes == $searched_name
            ${testid}=    Get Attribute    ${FORM_ROW_LIST_ITEM_ID} >> nth=${i}    data-testid
            ${parts}=    Split String    ${testid}    -
            ${id}=    Set Variable    ${parts}[2]
            RETURN    ${id}
        END
    END
    VAR    ${err}    Searched name ${searched_name} not found in the list
    Fail    ${err}

Delete Form By ID
    [Arguments]    ${id}
    ${delete_response}=    API request    method=DELETE    alias=form    url=${form_endpoint_url}${id}/    expected_status=200
    Should Be True    ${delete_response.status_code} < 300

Refresh Page
    Click On The Element    ${FORM_REFRESH_BUTTON}    Refresh the page to update the list after deletion

Verify Name Is Deleted
    [Documentation]    Click on the name on Page 2 and return the full name.
    [Arguments]    ${name}    ${last_name}
    ${full_name}=    Catenate    "${name}     ${last_name}"
    TRY
        Wait For Elements State    ${full_name}    visible    5s
        Fail    Name ${full_name} was not deleted successfully, it is still visible on the page.
    EXCEPT
        Log To Console    Name ${full_name} is successfully deleted and not visible on the page.
    END

Clear After Suite
    [Documentation]    Clear any remaining data after the suite execution.
    Disconnect From Database
    Close Browser

Verify Value In Database
    [Documentation]    Ověří konkrétní hodnotu ve výsledku SQL dotazu.
    ...    **Argumenty:**
    ...    - `select_statement`: SQL SELECT příkaz.
    ...    - `expected_value`: Očekávaná hodnota.
    ...    - `assertion_operator`: Operátor.
    ...    - `row`: Index řádku (výchozí 0).
    ...    - `col`: Index sloupce (výchozí 0).
    ...    - `alias`: Alias DB připojení.
    [Arguments]    ${select_statement}    ${assertion_operator}    ${expected_value}    ${row}=0    ${col}=0
        TRY
            Check Query Result
            ...    ${select_statement}
            ...    ${assertion_operator}
            ...    ${expected_value}
            ...    row=${row}
            ...    col=${col}
        EXCEPT    AS    ${err}
            Fail    Ověření hodnoty v DB selhalo pro dotaz: "${select_statement}". Chyba: ${err}
        END
    
Verify Row Count In Database
    [Documentation]    Ověří počet řádků vrácených SQL dotazem.
    ...    **Argumenty:**
    ...    - `select_statement`: SQL SELECT příkaz, který se má spustit.
    ...    - `expected_value`: Očekávaný počet řádků.
    ...    - `assertion_operator`: Operátor pro porovnání. Možné hodnoty: `==`, `!=`, `>`, `<`, `>=`, `<=`.
    ...    - `alias`: Alias databázového připojení (výchozí je ${DB_ALIAS}).
    ...    - `retry_timeout`: Maximální čekání, než ověření selže (výchozí je 0s = bez čekání).
    ...    - `msg`: Vlastní chybová hláška.
    [Arguments]    ${select_statement}    ${assertion_operator}    ${expected_value}    ${retry_timeout}=0s    ${context_name}=${EMPTY}
        TRY
            Check Row Count
            ...    ${select_statement}
            ...    ${assertion_operator}
            ...    ${expected_value}
            ...    retry_timeout=${retry_timeout}
            ...    assertion_message=${context_name}
        EXCEPT    AS    ${err}
            VAR    ${default_msg}    Ověření počtu řádků selhalo pro dotaz: "${select_statement}". Očekáváno ${assertion_operator} ${expected_value}.
            Fail    ${default_msg} | ERROR: ${err}
        END

Get Single DB Value
    [Arguments]    ${query}    @{params}
    TRY
        ${result_set}=    Query    select_statement=${query}    parameters=${params}
    EXCEPT    AS    ${err}
        VAR    ${err_msg}    Cannot execute query: "${query}" with parameters ${params}. ERROR: ${err}
        Fail    ${err_msg}    level=ERROR    console=${LOG_TO_CONSOLE}
        RETURN    ${None}
    END

    TRY
        RETURN    ${result_set}[0][0]
    EXCEPT
        RETURN    ${None}
    END



