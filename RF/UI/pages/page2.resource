*** Settings ***
Resource    ../common.resource

*** Keywords ***

Získat ID Podle Jména
    [Arguments]    ${hledané_jméno}
    
    ${count}=    Get Element Count    ${FORM_ROW_LIST_ITEMS_TEXT}
    
    FOR    ${i}    IN RANGE    ${count}
        ${text}=    Get Text From Element    ${FORM_ROW_LIST_ITEMS_TEXT} >> nth=${i}
        ${text_with_quotes}=    Catenate    "${text}"
        
        IF    $text_with_quotes == $hledané_jméno
            ${testid}=    Get Attribute    ${FORM_ROW_LIST_ITEM_ID} >> nth=${i}    data-testid
            ${parts}=    Split String    ${testid}    -
            ${id}=    Set Variable    ${parts}[2]
            RETURN    ${id}
        END
    END
    Fail    Jméno ${hledané_jméno} nenalezeno

Kliknout Na Jméno
    [Arguments]    ${name}    ${last_name}
    ${celé_jméno}=    Catenate    "${name}     ${last_name}"
    Wait For Elements State    ${celé_jméno}    visible    ${TIMEOUT}
    Click    text=${celé_jméno}
    RETURN    ${celé_jméno}

Ověřit Email V Info Modalu
    [Arguments]    ${email}
    ${email_text}=    Get Text From Element    ${PAGE2_INFO_MODAL_EMAIL}    Email v modalu
    Should Be Equal As Strings    ${email_text}    ${email}

Kliknout NA OK V Info Modalu
    Click On The Element    ${PAGE2_INFO_MODAL_OK_BUTTON}

Aktualizovat Stránku
    Click On The Element    ${FORM_REFRESH_BUTTON}    Kliknutí na refresh button
    Sleep    2

Ověřit Že Jméno Bylo Smazáno
    [Documentation]    Ověří že jméno již není v listu po smazání
    [Arguments]    ${smazané_jméno}    ${context_name}=${EMPTY}
    TRY
        ${count}=    Get Element Count    ${FORM_ROW_LIST_ITEMS_TEXT}
        
    EXCEPT    AS    ${err}
        Take Screenshot
        ${msg}=    Set Variable    Selhalo '${context_name}' při Get Element Count se nepodařilo najít element | ERROR: ${err}
        Fail    ${msg}
    END

    FOR    ${i}    IN RANGE    ${count}
        TRY
            ${text}=    Get Text From Element    ${FORM_ROW_LIST_ITEMS_TEXT} >> nth=${i}    ${context_name}
            
            ${text_with_quotes}=    Catenate    "${text}"

            IF    $text_with_quotes == $smazané_jméno
                Take Screenshot
                ${msg}=    Set Variable    Selhalo '${context_name}' --> Jméno: ${smazané_jméno} stále existuje v listu! Nebylo smazáno.

                Fail    ${msg}
            END
            
        EXCEPT    AS    ${err}

            Take Screenshot

            ${msg}=    Set Variable    Selhalo '${context_name}' při Get Text na pozici ${i} | ERROR: ${err}

            Fail    ${msg}
        END
    END

    Log To Console     Jméno: ${smazané_jméno} bylo úspěšně smazáno