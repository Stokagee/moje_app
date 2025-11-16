*** Comments ***
# LAYER 4: Easter Egg API Test Cases
#
# Testy pro easter egg/game logic API endpoints


*** Settings ***
Resource    ../workflows/form_workflow.resource
Resource    ../common.resource
Resource    ../variables.resource

Suite Setup     Create API Session    ${DEFAULT_SESSION}    ${API_BASE_URL}
Suite Teardown  Delete All Sessions

Force Tags      api    easter-egg
Default Tags    regression


*** Test Cases ***
Test Pozitivní Easter Egg - Neo
    [Documentation]    Test že "neo" triggeruje easter egg
    [Tags]    smoke    positive    game-logic
    ${result}=    Test Easter Egg For Name
    ...    ${DEFAULT_SESSION}
    ...    neo
    ...    ${True}

    Should Contain    ${result['message']}    ${EASTER_EGG_MSG}
    ...    msg=Easter egg message neobsahuje očekávaný text
    Log Test Result    Easter Egg Neo    PASS    Text "neo" správně matched

Test Pozitivní Easter Egg - Trinity
    [Documentation]    Test že "trinity" triggeruje easter egg
    [Tags]    smoke    positive    game-logic
    ${result}=    Test Easter Egg For Name
    ...    ${DEFAULT_SESSION}
    ...    trinity
    ...    ${True}
    Should Contain    ${result['message']}    ${EASTER_EGG_MSG}

Test Pozitivní Easter Egg - Jan
    [Documentation]    Test že české jméno "jan" triggeruje easter egg
    [Tags]    smoke    positive    game-logic    czech-names
    ${result}=    Test Easter Egg For Name
    ...    ${DEFAULT_SESSION}
    ...    jan
    ...    ${True}
    Should Contain    ${result['message']}    ${EASTER_EGG_MSG}

Test Negativní Easter Egg - Random Text
    [Documentation]    Test že random text NE-triggeruje easter egg
    [Tags]    smoke    negative    game-logic
    ${result}=    Test Easter Egg For Name
    ...    ${DEFAULT_SESSION}
    ...    ${NEGATIVE_EGG_TEXT}
    ...    ${False}
    ${message}=    Get From Dictionary    ${result}    message    default=${None}
    Should Be Equal    ${message}    ${None}
    ...    msg=Negative test vrátil message, ale neměl
    Log Test Result    Easter Egg Negative    PASS    Random text správně ne-matched

Test Case Insensitivity
    [Documentation]    Test že easter egg logic je case-insensitive
    ...    Testuje různé varianty: NEO, Neo, neo, nEo
    [Tags]    validation    case-insensitive
    @{variations}=    Create List    NEO    Neo    neo    nEo
    FOR    ${variation}    IN    @{variations}
        ${result}=    Test Easter Egg For Name
        ...    ${DEFAULT_SESSION}
        ...    ${variation}
        ...    ${True}

        Log Test Data    Case Variation    ${variation} → matched: ${result['matched']}
    END
    Log Test Result    Case Insensitivity    PASS    Všechny case varianty matched

Test Easter Egg S Whitespace
    [Documentation]    Test že whitespace je správně handled
    [Tags]    validation    edge-case
    ${result}=    Test Easter Egg For Name
    ...    ${DEFAULT_SESSION}
    ...    ${SPACE}neo${SPACE}
    ...    ${True}
    Log Test Result    Whitespace Handling    PASS    Whitespace správně trimnut

Test Prázdný String
    [Documentation]    Test že prázdný string NE-triggeruje easter egg
    [Tags]    validation    negative    edge-case
    ${result}=    Test Easter Egg For Name
    ...    ${DEFAULT_SESSION}
    ...    ${EMPTY}
    ...    ${False}

Test Velmi Dlouhý String
    [Documentation]    Test že velmi dlouhý string API zvládne
    [Tags]    validation    edge-case    performance
    ${long_string}=    Evaluate    "a" * 10000
    ${result}=    Test Easter Egg For Name
    ...    ${DEFAULT_SESSION}
    ...    ${long_string}
    ...    ${False}
    Log Test Result    Long String    PASS    API zvládlo dlouhý string bez crash

Test Speciální Znaky
    [Documentation]    Test že speciální znaky jsou správně handled
    [Tags]    validation    edge-case
    @{special_chars}=    Create List    @neo    neo!    neo#123    <neo>    neo&trinity
    FOR    ${text}    IN    @{special_chars}
        ${status}=    Run Keyword And Return Status
        ...    Evaluate Name For Easter Egg    ${DEFAULT_SESSION}    ${text}

        Should Be True    ${status}
        ...    msg=API crashed na speciálních znacích: ${text}

        Log    ✓ Handled: ${text}    level=INFO
    END
    Log Test Result    Special Characters    PASS    Všechny speciální znaky handled

Test Data-Driven Easter Eggs
    [Documentation]    Data-driven test pro více secret words
    [Tags]    data-driven    extended
    @{test_data}=    Create List
    ...    neo,True
    ...    trinity,True
    ...    morpheus,True
    ...    jan,True
    ...    pavla,True
    ...    matrix,True
    ...    random,False
    ...    test,False
    FOR    ${test_case}    IN    @{test_data}
        ${parts}=    Split String    ${test_case}    ,
        ${text}=    Set Variable    ${parts}[0]
        ${should_match}=    Convert To Boolean    ${parts}[1]

        ${result}=    Test Easter Egg For Name
        ...    ${DEFAULT_SESSION}
        ...    ${text}
        ...    ${should_match}

        Log    ✓ ${text}: matched=${result['matched']} (expected=${should_match})    level=INFO
    END
    Log Test Result    Data-Driven Tests    PASS    Všechny test cases prošly
