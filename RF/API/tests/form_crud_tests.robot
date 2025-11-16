*** Comments ***
# LAYER 4: API Test Cases
#
# Tento soubor obsahuje high-level test cases používající workflows.
# Testy NEVOLAJÍ přímo api_actions - pouze workflows!


*** Settings ***
Resource    ../common.resource
Resource    ../variables.resource

Suite Setup     Create API Session    ${DEFAULT_SESSION}    ${API_BASE_URL}
Suite Teardown  Delete All Sessions

Force Tags      api    form
Default Tags    regression


*** Test Cases ***
Test Vytvoření Nového Formuláře
    [Documentation]    Test vytvoření formuláře s random daty
    ...    **Test Steps:**
    ...    1. Generuje random test data (Faker)
    ...    2. Vytvoří formulář přes POST API
    ...    3. Ověří existenci přes GET API
    ...    4. Cleanup (delete)
    [Tags]    smoke    happy-path    critical
    ${result}=    Create Form With Random Data    ${DEFAULT_SESSION}
    [Teardown]    Delete Form Data    ${DEFAULT_SESSION}    ${result.form_id}

Test Kompletní CRUD Lifecycle
    [Documentation]    Test kompletního lifecycle: Create → Read → Delete
    ...    **Test Steps:**
    ...    1. Vytvoří formulář
    ...    2. Ověří že existuje v listu všech formulářů
    ...    3. Smaže formulář
    ...    4. Ověří že už neexistuje (GET vrátí 404)
    [Tags]    smoke    crud    critical
    ${result}=    Complete Form Lifecycle    ${DEFAULT_SESSION}
    Log Test Result    CRUD Lifecycle    PASS    Form ${result.form_id} prošel kompletním lifecycle

Test Vytvoření Více Formulářů
    [Documentation]    Test vytvoření multiple formulářů
    ...    Ověřuje že API zvládne batch operace.
    [Tags]    batch    extended
    @{created_ids}=    Create List
    FOR    ${i}    IN RANGE    5
        ${result}=    Create Form With Random Data    ${DEFAULT_SESSION}
        Append To List    ${created_ids}    ${result.form_id}

        Log Test Data    Created Form ${i+1}    ${result.form_id}
    END
    ${list_response}=    Get All Form Data    ${DEFAULT_SESSION}
    ${all_forms}=    Set Variable    ${list_response.json()}
    FOR    ${form_id}    IN    @{created_ids}
        ${found}=    Set Variable    ${False}
        FOR    ${form}    IN    @{all_forms}
            IF    ${form['id']} == ${form_id}
                ${found}=    Set Variable    ${True}
                BREAK
            END
        END
        Should Be True    ${found}    msg=Form ID ${form_id} nebyl nalezen v listu
    END
    Log Test Result    Batch Create    PASS    ${5} formulářů úspěšně vytvořeno
    [Teardown]    Cleanup Multiple Forms    ${DEFAULT_SESSION}    @{created_ids}

Test Validace Duplicitního Emailu
    [Documentation]    Test že API odmítne duplicitní email (UNIQUE constraint)
    ...    **Test Steps:**
    ...    1. Vytvoří formulář s emailem
    ...    2. Pokusí se vytvořit druhý formulář se stejným emailem
    ...    3. Ověří že druhý request selhal
    [Tags]    validation    negative
    ${email}=    Generate Test Email    duplicate_test
    &{form_data_1}=    Create Dictionary
    ...    first_name=Jan
    ...    last_name=První
    ...    phone=123456789
    ...    gender=${DEFAULT_GENDER}
    ...    email=${email}
    ${result_1}=    Create And Verify Form Data    ${DEFAULT_SESSION}    ${form_data_1}
    &{form_data_2}=    Create Dictionary
    ...    first_name=Petr
    ...    last_name=Druhý
    ...    phone=987654321
    ...    gender=${DEFAULT_GENDER}
    ...    email=${email}
    ${status}=    Run Keyword And Return Status
    ...    Create Form Data    ${DEFAULT_SESSION}    ${form_data_2}
    Should Not Be True    ${status}
    ...    msg=API povolilo duplicitní email - to je chyba!
    Log Test Result    Duplicate Email Validation    PASS    API správně odmítlo duplicitní email
    [Teardown]    Delete Form Data    ${DEFAULT_SESSION}    ${result_1.form_id}

Test Smazání Neexistujícího Formuláře
    [Documentation]    Test že DELETE vrátí 404 pro neexistující form
    [Tags]    validation    negative    edge-case
    ${nonexistent_id}=    Set Variable    999999
    ${status}=    Run Keyword And Return Status
    ...    Delete Form Data    ${DEFAULT_SESSION}    ${nonexistent_id}
    Should Not Be True    ${status}
    ...    msg=API nevrátilo 404 pro neexistující ID
    Log Test Result    Delete Nonexistent    PASS    API správně vrátilo 404

Test Vytvoření Formuláře S Přílohou A Instrukcemi
    [Documentation]    Test vytvoření formuláře s attachments a instructions
    ...    **Test Steps:**
    ...    1. Vytvoří formulář
    ...    2. Přidá přílohu (base64)
    ...    3. Přidá instrukce
    ...    4. Ověří že vše existuje
    [Tags]    attachments    extended
    &{form_data}=    Create Dictionary
    ...    first_name=Test
    ...    last_name=Attachments
    ...    phone=123456789
    ...    gender=${DEFAULT_GENDER}
    ...    email=test.attachments@example.com
    ${file_content}=    Set Variable    Test attachment content
    ${base64_content}=    Evaluate    base64.b64encode(b"${file_content}").decode('utf-8')    modules=base64
    &{attachment_data}=    Create Dictionary
    ...    filename=test.txt
    ...    content_type=text/plain
    ...    data_base64=${base64_content}
    ${instructions}=    Set Variable    These are test instructions for the form
    ${result}=    Create Form With Attachment And Instructions
    ...    ${DEFAULT_SESSION}
    ...    ${form_data}
    ...    ${attachment_data}
    ...    ${instructions}
    Log Test Result    Form With Attachments    PASS    Form, příloha a instrukce vytvořeny
    [Teardown]    Delete Form Data    ${DEFAULT_SESSION}    ${result.form_id}

*** Keywords ***
Cleanup Multiple Forms
    [Documentation]    Helper keyword pro cleanup více formulářů
    [Arguments]    ${session}    @{form_ids}

    FOR    ${form_id}    IN    @{form_ids}
        TRY
            Delete Form Data    ${session}    ${form_id}
        EXCEPT
            Log    Nepodařilo se smazat form ID ${form_id}    level=WARN
        END
    END
