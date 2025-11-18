*** Settings ***
Resource    ../common.resource

*** Variables ***
${DEVICE}    iPhone 13



*** Test Cases ***
Vyplní Nový Formulář
    #Provision Browser Session    ${BROWSER}    ${HEADLESS}    ${URL}
    #...    ${WIDTH}    ${HEIGHT}
    Provison Device Session    ${BROWSER}    ${HEADLESS}    ${URL}    ${DEVICE}
    ${name}=    First Name
    ${last_name}=    Last Name
    ${phone}=    Phone Number
    ${email}=    Email
    Vyplnit Křestní Jméno    ${name}
    Vyplnit Příjmení    ${last_name}
    Vyplnit Telefoní Číslo    ${phone}
    Vyplní Email    ${email}
    Kliknout Na Možnost Vybrat Pohlaví
    Vybere Pohlaví Dle Libosti
    ${json_obj}=    Načti JSON Data    ${JSON_PATH}
    ${value_from_json}=    Vytáhni Hodnotu Z JSON    ${json_obj}    
    ...    $.users.admin.role
    Vlož Data Z JSON Do Instrukcí    ${value_from_json}
    Nahraje Textový Soubor
    Klikne Na Odeslat Tlačítko
    Potvrdit Modal & Přejít Na Druhou Page
    ${jméno}=    Kliknout Na Jméno    ${name}    ${last_name}
    Log To Console    ${jméno}
    Ověřit Email V Info Modalu    ${email}
    Kliknout NA OK V Info Modalu
    ${id}=    Získat ID Podle Jména    ${jméno}
    Log To Console    ID záznamu je: ${id}
    Vytvoří Session pro API    ${BASE_URL}
    Connect To Test Database
    Verify Row Count In Database    SELECT * FROM form_data WHERE email = '${email}'    ==    1
    DELETE On Session    mysession    /${id}
    Aktualizovat Stránku
    Ověřit Že Jméno Bylo Smazáno    ${jméno}
    Disconnect From Test Database


