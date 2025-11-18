*** Settings ***
Documentation     Příklad použití ImageComparisonLibrary pro vizuální regresní testování.
...               Tato test suite demonstruje základní i pokročilé použití knihovny.

Library           ImageComparisonLibrary

*** Variables ***
${BASELINE_DIR}       ${CURDIR}/baseline_images
${CURRENT_DIR}        ${CURDIR}/current_images
${DIFF_DIR}           ${CURDIR}/results/diffs

*** Test Cases ***
Test 01: Porovnání identických obrázků
    [Documentation]    Test ověřuje, že identické obrázky projdou porovnáním bez chyby.
    [Tags]    smoke    positive
    ${distance}=    Compare Layouts And Generate Diff
    ...    ${BASELINE_DIR}/homepage.png
    ...    ${CURRENT_DIR}/homepage_identical.png
    ...    ${DIFF_DIR}
    Should Be Equal As Integers    ${distance}    0
    Log    Obrázky jsou identické, vzdálenost: ${distance}

Test 02: Porovnání s výchozím nastavením
    [Documentation]    Test používá výchozí nastavení (phash, tolerance=5).
    [Tags]    regression
    Compare Layouts And Generate Diff
    ...    ${BASELINE_DIR}/login_page.png
    ...    ${CURRENT_DIR}/login_page_current.png
    ...    ${DIFF_DIR}

Test 03: Porovnání s vlastní tolerancí
    [Documentation]    Test používá vyšší toleranci pro méně přísné srovnání.
    [Tags]    regression
    ${distance}=    Compare Layouts And Generate Diff
    ...    ${BASELINE_DIR}/dashboard.png
    ...    ${CURRENT_DIR}/dashboard_slight_change.png
    ...    ${DIFF_DIR}
    ...    tolerance=15
    Log    Hammingova vzdálenost: ${distance}

Test 04: Porovnání s dhash algoritmem
    [Documentation]    Test používá dhash algoritmus pro rychlejší srovnání.
    [Tags]    regression    fast
    Compare Layouts And Generate Diff
    ...    ${BASELINE_DIR}/product_page.png
    ...    ${CURRENT_DIR}/product_page_current.png
    ...    ${DIFF_DIR}
    ...    algorithm=dhash
    ...    tolerance=10

Test 05: Rychlé vizuální ověření
    [Documentation]    Test používá méně přísné klíčové slovo pro hrubé srovnání.
    [Tags]    quick-check
    Check Layouts Are Visually Similar
    ...    ${BASELINE_DIR}/homepage.png
    ...    ${CURRENT_DIR}/homepage_minor_changes.png
    ...    ${DIFF_DIR}

Test 06: Vlastní pixel tolerance pro diff
    [Documentation]    Test nastavuje vyšší pixel toleranci pro generování diffu.
    [Tags]    regression
    Compare Layouts And Generate Diff
    ...    ${BASELINE_DIR}/settings_page.png
    ...    ${CURRENT_DIR}/settings_page_current.png
    ...    ${DIFF_DIR}
    ...    pixel_tolerance=20
    ...    tolerance=10

Test 07: Kombinace parametrů
    [Documentation]    Test kombinuje různé parametry pro pokročilé nastavení.
    [Tags]    regression    advanced
    ${distance}=    Compare Layouts And Generate Diff
    ...    ${BASELINE_DIR}/checkout_page.png
    ...    ${CURRENT_DIR}/checkout_page_current.png
    ...    ${DIFF_DIR}
    ...    algorithm=phash
    ...    tolerance=8
    ...    pixel_tolerance=15
    ...    hash_size=16
    Log    Porovnání dokončeno s Hammingovou vzdáleností: ${distance}

Test 08: Očekávané selhání - různé obrázky
    [Documentation]    Test ověřuje, že knihovna správně detekuje významné rozdíly.
    [Tags]    negative
    Run Keyword And Expect Error
    ...    AssertionError: Obrázky se liší nad povolenou toleranci!*
    ...    Compare Layouts And Generate Diff
    ...    ${BASELINE_DIR}/homepage.png
    ...    ${CURRENT_DIR}/homepage_completely_different.png
    ...    ${DIFF_DIR}
    ...    tolerance=5

Test 09: Očekávané selhání - různé rozměry
    [Documentation]    Test ověřuje, že knihovna správně detekuje rozdílné rozměry obrázků.
    [Tags]    negative
    Run Keyword And Expect Error
    ...    AssertionError: Obrázky mají různé rozměry*
    ...    Compare Layouts And Generate Diff
    ...    ${BASELINE_DIR}/homepage.png
    ...    ${CURRENT_DIR}/homepage_different_size.png
    ...    ${DIFF_DIR}

Test 10: Porovnání mobilní verze
    [Documentation]    Test porovnává mobilní verzi stránky.
    [Tags]    mobile    regression
    Check Layouts Are Visually Similar
    ...    ${BASELINE_DIR}/mobile/homepage.png
    ...    ${CURRENT_DIR}/mobile/homepage_current.png
    ...    ${DIFF_DIR}

*** Keywords ***
Setup Test Data
    [Documentation]    Připraví testovací data a adresáře.
    Create Directory    ${BASELINE_DIR}
    Create Directory    ${CURRENT_DIR}
    Create Directory    ${DIFF_DIR}

Cleanup Test Data
    [Documentation]    Vyčistí testovací data po testech.
    Remove Directory    ${DIFF_DIR}    recursive=True
