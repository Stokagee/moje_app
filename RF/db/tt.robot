*** Settings ***
Library    RobotEyes
Library    OperatingSystem

Suite Teardown    Run Keyword And Ignore Error    Remove Files    test_*.png

*** Variables ***
${BASELINE_IMG}    test_baseline.png
${CURRENT_IMG}    test_current.png
${DIFF_IMG}    test_diff.png

*** Test Cases ***
Isolate RobotEyes Problem
    [Documentation]    Minimalistický test pro izolaci problému s RobotEyes.

    # Krok 1: Vytvoříme dva jednoduché, identické obrázky pro test
    # Použijeme vestavěnou knihovnu OperatingSystem k vytvoření prázdných souborů
    Create File    ${BASELINE_IMG}
    Create File    ${CURRENT_IMG}
    Log    Vytvořeny prázdné testovací soubory.

    # Krok 2: Zkusíme zavolat klíčové slovo se správnými argumenty
    # Tento řádek by měl projít, protože porovnáváme dva prázdné, ale existující soubory
    TRY
        RobotEyes.Compare Two Images    ${BASELINE_IMG}    ${CURRENT_IMG}    ${DIFF_IMG}    tolerance=5
        Log    RobotEyes.Compare Two Images PROŠEL! Problém je jinde ve vašem původním testu.
    EXCEPT    AS    ${err}
        Log    CHYBA v RobotEyes.Compare Two Images: ${err}
        Fail    Test selhal přímo na volání RobotEyes. Chyba: ${err}
    END