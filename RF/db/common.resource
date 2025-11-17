*** Settings ***
Library    DatabaseLibrary
Resource   variables.resource
Resource    ../RF/db/page/db_keywords.resource

*** Keywords ***
Connect To Test Database
    [Documentation]    Připojení k PostgreSQL test DB
    Connect To Database
    ...    ${DB_MODULE}
    ...    db_name=${DB_NAME}
    ...    db_user=${DB_USER}
    ...    db_password=${DB_PASSWORD}
    ...    db_host=${DB_HOST}
    ...    db_port=${DB_PORT}
    ...    alias=${DB_ALIAS}

Delete All Test Data
    [Documentation]    Smaže všechny testovací data z tabulky users
    Execute Sql String    DELETE FROM users;
