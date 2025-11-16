*** Settings ***
Documentation     Tento soubor obsahuje complex API scenarios - kombinace více API actions.
#                 Workflows implementují business logic a complete user scenarios.
Resource    ../common.resource
Library     FakerLibrary


*** Keywords ***
Create And Verify Form Data
    [Documentation]    Workflow: Vytvoří form data a ověří že byl vytvořen
    [Arguments]    ${session}    ${form_data}

    Log Test Step    Vytváření form data přes API

    ${create_response}=    Create Form Data    ${session}    ${form_data}
    ${form_id}=    Set Variable    ${create_response.json()['id']}

    Log Test Data    Created Form ID    ${form_id}

    Log Test Step    Ověření vytvořeného záznamu přes GET

    ${get_response}=    Get Form Data By ID    ${session}    ${form_id}

    Should Be Equal As Strings    ${create_response.text}    ${get_response.text}
    ...    msg=POST response neodpovídá GET response

    Log Test Result    Create And Verify    PASS    Form ID ${form_id} vytvořen a ověřen

    &{result}=    Create Dictionary
    ...    form_id=${form_id}
    ...    form_data=${form_data}
    ...    response=${create_response}

    RETURN    ${result}

Create Form With Random Data
    [Documentation]    Workflow: Vytvoří form s random test data (Faker)
    [Arguments]    ${session}    ${gender}=muž

    Log Test Step    Generování random test dat

    ${first_name}=    FakerLibrary.First Name
    ${last_name}=    FakerLibrary.Last Name
    ${phone}=    FakerLibrary.Phone Number
    ${email}=    FakerLibrary.Email

    &{form_data}=    Create Dictionary
    ...    first_name=${first_name}
    ...    last_name=${last_name}
    ...    phone=${phone}
    ...    gender=${gender}
    ...    email=${email}

    Log Test Data    Generated Form Data    ${form_data}

    ${result}=    Create And Verify Form Data    ${session}    ${form_data}

    RETURN    ${result}

Complete Form Lifecycle
    [Documentation]    Workflow: Kompletní lifecycle - Create → Verify → Delete
    [Arguments]    ${session}

    ${result}=    Create Form With Random Data    ${session}

    Log Test Step    Ověření existence v listu všech formulářů

    ${list_response}=    Get All Form Data    ${session}
    ${all_forms}=    Set Variable    ${list_response.json()}

    ${found}=    Set Variable    ${False}
    FOR    ${form}    IN    @{all_forms}
        IF    ${form['id']} == ${result.form_id}
            ${found}=    Set Variable    ${True}
            BREAK
        END
    END

    Should Be True    ${found}    msg=Vytvořený formulář nebyl nalezen v listu

    Log Test Result    Form Exists In List    PASS    Form ID ${result.form_id} nalezen

    Log Test Step    Mazání formuláře

    ${delete_response}=    Delete Form Data    ${session}    ${result.form_id}

    Log Test Step    Ověření že formulář byl smazán

    ${get_status}=    Run Keyword And Return Status
    ...    Get Form Data By ID    ${session}    ${result.form_id}

    Should Not Be True    ${get_status}
    ...    msg=Formulář stále existuje po smazání

    Log Test Result    Complete Lifecycle    PASS    Create → Verify → Delete proběhlo úspěšně

    RETURN    ${result}

Test Easter Egg For Name
    [Documentation]    Workflow: Otestuje easter egg logic pro dané jméno
    [Arguments]    ${session}    ${text}    ${should_match}

    Log Test Step    Testování easter egg pro text: '${text}'

    ${response}=    Evaluate Name For Easter Egg    ${session}    ${text}
    ${data}=    Set Variable    ${response.json()}

    Log Test Data    Easter Egg Response    ${data}

    ${matched}=    Set Variable    ${data['matched']}
    Should Be Equal    ${matched}    ${should_match}
    ...    msg=Easter egg match status neodpovídá očekávání

    IF    ${matched}
        ${message}=    Set Variable    ${data['message']}
        Should Contain    ${message}    Tajemství odhaleno
        ...    msg=Easter egg message neobsahuje očekávaný text

        Log Test Result    Easter Egg Match    PASS    Text '${text}' matched: ${message}
    ELSE
        Log Test Result    Easter Egg No Match    PASS    Text '${text}' correctly did not match
    END

    RETURN    ${data}

Create Form With Attachment And Instructions
    [Documentation]    Workflow: Vytvoří form s přílohou a instrukcemi
    ...
    ...    Args:
    ...    - session: Session alias
    ...    - form_data: Dictionary s form data
    ...    - attachment_data: Dictionary s attachment (filename, content_type, data_base64)
    ...    - instructions_text: Text instrukcí
    ...
    ...    Returns:
    ...    - Dictionary: {form_id: int, attachment_id: int, instruction_id: int}
    [Arguments]    ${session}    ${form_data}    ${attachment_data}    ${instructions_text}

    ${form_result}=    Create And Verify Form Data    ${session}    ${form_data}
    ${form_id}=    Set Variable    ${form_result.form_id}

    Log Test Step    Přidávání přílohy k formuláři ID ${form_id}

    ${attachment_response}=    Create Attachment For Form    ${session}    ${form_id}    ${attachment_data}
    ${attachment_id}=    Set Variable    ${attachment_response.json()['id']}

    Log Test Data    Created Attachment ID    ${attachment_id}

    Log Test Step    Přidávání instrukcí k formuláři ID ${form_id}

    ${instructions_response}=    Create Or Update Instructions    ${session}    ${form_id}    ${instructions_text}
    ${instruction_id}=    Set Variable    ${instructions_response.json()['id']}

    Log Test Data    Created Instructions ID    ${instruction_id}

    ${attachments_response}=    Get Attachments For Form    ${session}    ${form_id}
    ${attachments_count}=    Get Length    ${attachments_response.json()}
    Should Be True    ${attachments_count} > 0    msg=Příloha nebyla nalezena

    ${instructions_response}=    Get Instructions For Form    ${session}    ${form_id}
    Should Be Equal As Integers    ${instructions_response.status_code}    200
    ...    msg=Instrukce nebyly nalezeny

    Log Test Result    Form With Attachments    PASS    Form, příloha a instrukce vytvořeny

    &{result}=    Create Dictionary
    ...    form_id=${form_id}
    ...    attachment_id=${attachment_id}
    ...    instruction_id=${instruction_id}

    RETURN    ${result}
