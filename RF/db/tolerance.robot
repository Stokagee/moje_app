*** Comments ***
Práce s request a db library s claude code úkoly.
Učím se základúm db library.

*** Settings ***
Documentation    Vytvoření a následné smazání formuláře
Library    DatabaseLibrary
Library    RequestsLibrary
Library    FakerLibrary
Suite Setup    Connect To Database    db_module=${DB_MODULE}    db_name=${DB_NAME}    db_user=${DB_USER}    
...    db_password=${DB_PASSWORD}    db_host=${DB_HOST}    db_port=${DB_PORT}
Suite Teardown   Disconnect From Database

*** Variables ***
${BASE_URL_FOR_API}     http://localhost:20300
${DB_NAME}    moje_app
${DB_MODULE}    psycopg2
${DB_USER}    postgres
${DB_PASSWORD}    postgres
${DB_HOST}    localhost
${DB_PORT}    20343
${pohlavi}          male
${telefoni_cislo}    123456789

*** Test Cases ***

Pripojeni API
    [Setup]    Create Session    alias=api    url=${BASE_URL_FOR_API}
    TRY
        ${krestni_jmeno}=      First Name
        ${prijmeni}=           Last Name
        ${emailova_adresa}=    Email

        VAR    &{formular}    first_name=${krestni_jmeno}   last_name=${prijmeni}   phone=${telefoni_cislo}    gender=${pohlavi}    email=${emailova_adresa}    scope=global

        ${form_id_for_delete}=    Pripojeni pres api    ${formular}
        Sleep    1
        Ověř Že Courtney Gibbs Existuje V DB    ${krestni_jmeno}

        VAR    ${id_for_delete_from_api}    ${form_id_for_delete.json()}[id]

        ${delete_response}=    Smazat ID pres API    ${id_for_delete_from_api}
        Overeni statusu 200 po delete    ${delete_response}

        Ověř Že Záznam Neexistuje V DB    ${id_for_delete_from_api}
        Log To Console    \n====\n ověřeno ID: ${id_for_delete_from_api} není v DB. \n====\n
    EXCEPT    AS    ${err}
        VAR    ${msg}    selhání při | ERROR: ${err}
    FINALLY
        Disconnect From All Databases
    END
        
            


*** Keywords ***

Pripojeni pres api
    [Arguments]    ${json_formular}
    ${response}=    POST On Session    alias=api    url=/api/v1/form/    expected_status=anything    json=${json_formular}
    Log To Console    \n====\n ${response} \n====\n
    Status Should Be    201    ${response}
    RETURN    ${response}

Ověř Že Courtney Gibbs Existuje V DB
    [Arguments]    ${objekt}
    ${result}=    Query
    ...    SELECT id, first_name, last_name, email 
    ...    FROM form_data 
    ...    WHERE id = '${objekt}'
    ${count}=    Get Length    ${result}

    IF    ${count} == 0
        Fail
        Log To Console    \n====\n Form ID ${objekt} neexistuje. \n====\n
    ELSE IF    ${count} > 1
        Fail
        Log To Console    \n====\n Není unikátní. Nalezeno ${count}x. \n====\n
    END
    Log To Console    \n====\n ověřeno ID: ${objekt} není v DB. \n====\n



Smazat ID pres API
    [Arguments]    ${id_for_delete}
    ${response}=    DELETE On Session    alias=api    url=/api/v1/form/${id_for_delete}
    Log To Console    \n====\n ověřeno ID: ${id_for_delete} není v DB. \n====\n
    RETURN    ${response}

Overeni statusu 200 po delete
    [Arguments]    ${expected_status}
    Status Should Be    200    ${expected_status}

Ověř Že Záznam Neexistuje V DB
    [Arguments]    ${id}=${EMPTY}    ${email}=${EMPTY}
    Check Row Count    SELECT * FROM form_data WHERE id = '${id}'    ==    0
    Log To Console    \n====\n ověřeno ID: ${id} není v DB. \n====\n
