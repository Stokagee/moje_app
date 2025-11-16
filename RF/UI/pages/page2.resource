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
    # Přijímá 2 argumenty: jméno které bylo smazáno a název kontextu pro error zprávy
    [Arguments]    ${smazané_jméno}    ${context_name}=ověření jména po smazání
    
    # === BLOK 1: Získání počtu jmen v listu ===
    TRY
        # Spočítá kolik elementů (jmen) je aktuálně v listu
        # Např. pokud je v listu 8 jmen, ${count} bude 8
        ${count}=    Get Element Count    ${FORM_ROW_LIST_ITEMS_TEXT}
        
    EXCEPT    AS    ${err}
        # Pokud selže Get Element Count (např. element neexistuje, timeout)
        # Udělá screenshot pro debugging
        Take Screenshot
        # Sestaví chybovou zprávu s kontextem a detaily chyby
        ${msg}=    Set Variable    Selhalo '${context_name}' při Get Element Count se nepodařilo najít element | ERROR: ${err}
        # Ukončí test s touto chybovou zprávou
        Fail    ${msg}
    END
    # Konec TRY-EXCEPT bloku pro Get Element Count
    
    # === BLOK 2: Procházení všech jmen v listu ===
    # FOR loop projde každé jméno od pozice 0 až do count-1
    # Pokud count=8, projde pozice: 0, 1, 2, 3, 4, 5, 6, 7
    FOR    ${i}    IN RANGE    ${count}
        
        # Vnořený TRY-EXCEPT pro každou iteraci loopu
        TRY
            # Získá text z elementu na aktuální pozici ${i}
            # nth=${i} znamená "vezmi i-tý element" (0=první, 1=druhý atd.)
            # Např. když i=0, vezme první jméno z listu
            ${text}=    Get Text From Element    ${FORM_ROW_LIST_ITEMS_TEXT} >> nth=${i}    ${context_name}
            
            # Přidá uvozovky kolem načteného textu
            # Důvod: ${smazané_jméno} obsahuje uvozovky z předchozího Catenate
            # Takže pokud ${text}="Paul Black", udělá z toho ""Paul Black""
            ${text_with_quotes}=    Catenate    "${text}"
            
            # Porovná aktuální jméno z listu se smazaným jménem
            # $variable syntax v IF = porovnání hodnot (ne stringů)
            IF    $text_with_quotes == $smazané_jméno
                # SHODA NALEZENA = jméno stále existuje v listu = CHYBA!
                # To znamená, že smazání selhalo
                
                # Udělá screenshot pro debugging
                Take Screenshot
                # Sestaví chybovou zprávu že jméno nebylo smazáno
                ${msg}=    Set Variable    Selhalo '${context_name}' --> Jméno: ${smazané_jméno} stále existuje v listu! Nebylo smazáno.
                # Ukončí test s FAIL - smazání neproběhlo správně
                Fail    ${msg}
            END
            # Pokud IF není TRUE (jména se neshodují), pokračuje na další jméno
            
        EXCEPT    AS    ${err}
            # Pokud selže Get Text From Element (např. element zmizel, timeout)
            # Udělá screenshot
            Take Screenshot
            # Sestaví chybovou zprávu s pozicí kde selhalo
            ${msg}=    Set Variable    Selhalo '${context_name}' při Get Text na pozici ${i} | ERROR: ${err}
            # Ukončí test s touto chybou
            Fail    ${msg}
        END
        # Konec TRY-EXCEPT pro jednu iteraci
        
    END
    # Konec FOR loopu
    
    # === BLOK 3: Success - jméno nenalezeno ===
    # Pokud kód dorazil sem, znamená to:
    # - FOR loop prošel všechna jména (všech ${count} iterací)
    # - Žádné jméno se neshodovalo se smazaným jménem
    # - IF podmínka nikdy nebyla TRUE
    # - Žádný FAIL nebyl vyvolán
    # = Jméno bylo úspěšně smazáno!
    Log To Console     Jméno: ${smazané_jméno} bylo úspěšně smazáno