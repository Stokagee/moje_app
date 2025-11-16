*** Settings ***
Resource    ../common.resource

*** Keywords ***

Vyplnit Křestní Jméno
    [Arguments]    ${name}
    Fill Text In Input Field    ${FORM_NAME_INPUT}    ${name}

Vyplnit Příjmení
    [Arguments]    ${surname}
    Fill Text In Input Field    ${FORM_LAST_NAME_INPUT}    ${surname}

Vyplnit Telefoní Číslo
    [Arguments]    ${phone}
    Fill Text In Input Field    ${FORM_PHONE_INPUT}    ${phone}

Kliknout Na Možnost Vybrat Pohlaví
    Click On The Element    ${FORM_GENDER_PICKER}

Vybere Pohlaví Dle Libosti
    ${random_gender}=    Evaluate    random.randint(0, 2)    modules=random
    Click On The Element    ${MODAL_GENDER_PICKER}[${random_gender}]

Načti JSON Data
    [Arguments]    ${file_path}
    ${json_obj}=    Load Json From File    ${file_path}
    RETURN    ${json_obj}

Vytáhni Hodnotu Z JSON
    [Arguments]    ${json_obj}    ${json_value}
    ${json_data}=    Get Value From Json    ${json_obj}    ${json_value}
    RETURN    ${json_data[0]}
    
Vlož Data Z JSON Do Instrukcí
    [Arguments]    ${text}
    Fill Text In Input Field    ${FORM_INSTRUCTIONS_FIELD}    ${text}

Nahraje Textový Soubor
    Upload File    ${DOKUMENT_PATH}    ${FORM_FILE_UPLOADER_BUTTON}

Klikne Na Odeslat Tlačítko
    Click On The Element    ${FORM_SUMBIT_BUTTON}

Vyplní Email    
    [Arguments]    ${email}
    Fill Text In Input Field    ${FORM_EMAIL_INPUT}    ${email}

Potvrdit Modal & Přejít Na Druhou Page
    Click On The Element    ${FORM_SUBMIT_MODAL_NEXT_BUTTON}

Ověří Vyplněné Jméno
    [Arguments]    ${stary_text}
    Ověření Vyplněné Hodnoty Z Elementu    ${FORM_NAME_INPUT}    ${stary_text}    $context_name

