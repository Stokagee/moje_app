*** Settings ***
Library    DatabaseLibrary
Library    Collections
Library    libraries/Diagnostika.py
Resource   variables.resource
Resource   page/db_keywords.resource

*** Keywords ***
Connect To Test Database
    [Documentation]    Připojení k PostgreSQL test DB
    [Arguments]    ${context_name}=${EMPTY}
    TRY
        Connect To Database 
        ...    ${DB_MODULE}
        ...    db_name=${DB_NAME}
        ...    db_user=${DB_USER}
        ...    db_password=${DB_PASSWORD}
        ...    db_host=${DB_HOST}
        ...    db_port=${DB_PORT}
        ...    alias=${DB_ALIAS}
    EXCEPT    AS    ${err}
        ${msg}=    Set Variable    Selhání připojení k DB --> | ERROR: ${err}
        Fail    ${msg}
    END

Disconnect From Test Database
    [Documentation]    Odpojení od PostgreSQL test DB
    [Arguments]    ${DB_ALIAS}=${DB_ALIAS}    ${context_name}=${EMPTY}
    TRY
        Disconnect From Database    ${DB_ALIAS}
    EXCEPT    AS    ${err}
        ${msg}=    Set Variable    Selhání odpojení od DB --> | ERROR: ${err}
        Fail    ${msg}
    END


Delete All Test Data
    [Documentation]    Smaže všechny testovací data z tabulky users
    [Arguments]    ${context_name}=${EMPTY}
    TRY
        Execute Sql String    DELETE FROM users
    EXCEPT    AS    ${err}
        ${msg}=    Set Variable    Selhání smazání testovacích dat z DB --> | ERROR: ${err}
        Fail    ${msg}
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
    [Arguments]    ${select_statement}    ${assertion_operator}    ${expected_value}    ${alias}=${DB_ALIAS}    ${retry_timeout}=0s    ${context_name}=${EMPTY}
        TRY
            Check Row Count
            ...    ${select_statement}
            ...    ${assertion_operator}
            ...    ${expected_value}
            ...    alias=${alias}
            ...    retry_timeout=${retry_timeout}
            ...    assertion_message=${context_name}
        EXCEPT    AS    ${err}
            ${default_msg}=    Set Variable    Ověření počtu řádků selhalo pro dotaz: "${select_statement}". Očekáváno ${assertion_operator} ${expected_value}.
            Fail    ${default_msg} | ERROR: ${err}
        END

Verify Value In Database
    [Documentation]    Ověří konkrétní hodnotu ve výsledku SQL dotazu.
    ...    **Argumenty:**
    ...    - `select_statement`: SQL SELECT příkaz.
    ...    - `expected_value`: Očekávaná hodnota.
    ...    - `assertion_operator`: Operátor.
    ...    - `row`: Index řádku (výchozí 0).
    ...    - `col`: Index sloupce (výchozí 0).
    ...    - `alias`: Alias DB připojení.
    [Arguments]    ${select_statement}    ${assertion_operator}    ${expected_value}    ${row}=0    ${col}=0    ${alias}=${DB_ALIAS}
        TRY
            Check Query Result
            ...    ${select_statement}
            ...    ${assertion_operator}
            ...    ${expected_value}
            ...    row=${row}
            ...    col=${col}
            ...    alias=${alias}
        EXCEPT    AS    ${err}
            Fail    Ověření hodnoty v DB selhalo pro dotaz: "${select_statement}". Chyba: ${err}
        END


