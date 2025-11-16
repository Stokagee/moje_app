*** Settings ***
Library    RequestsLibrary
Library    FakerLibrary
Library    Collections

*** Variables ***
${BASE_URL}    http://localhost:8000/api/v1/form
${text_for_egg}    Dům
${text_for_negative_egg}    drak
${instructions_for_test}    kajshdkajshdfkjhaskjahskjashdsAKJ



*** Test Cases ***
Create Form Successfully
    Create Session    mysession    ${BASE_URL}
    ${email}=    FakerLibrary.email
    ${phone}=    FakerLibrary.phone_number
    ${first_name}=    FakerLibrary.first_name
    ${last_name}=    FakerLibrary.last_name
    ${json_data}=    Create Dictionary    first_name=${first_name}    last_name=${last_name}    phone=${phone}   gender=muž    email=${email}
    ${response}=    POST On Session    mysession    /    json=${json_data}
    Log    ${response.status_code}
    ${id}    Set Variable    ${response.json()['id']}
    Log To Console    ${id}
    Set Global Variable    ${id}
    ${get_response}=    GET On Session    mysession    /${id}
    Log    ${get_response.status_code}
    Should Be Equal As Strings    ${response.text}    ${get_response.text}

Zkouška Na Pozitivní Easter Egg
    ${easter_egg_text}=    Create Dictionary
        ...    text=${text_for_egg}
    ${easter_egg_response}=    POST On Session    mysession    ${BASE_URL}/evaluate-name    json=${easter_egg_text}
    Should Be Equal As Strings    ${easter_egg_response.status_code}    200
    ${response_for_egg}=    Set Variable    ${easter_egg_response.json()}
    Log To Console    hláška:${response_for_egg}
    ${if_matched}=    Set Variable    ${response_for_egg['matched']}
    ${message}=    Set Variable    ${response_for_egg['message']}
    Log To Console    macthed:${if_matched}
    Should Be Equal    ${if_matched}    ${True}
    Should Contain    ${message}    Tajemství odhaleno

Zkouška Na Negativní Easter Egg
    ${easter_egg_text}=    Create Dictionary
        ...    text=${text_for_negative_egg}
    ${easter_egg_response}=    POST On Session    mysession    ${BASE_URL}/evaluate-name    json=${easter_egg_text}
    Should Be Equal As Strings    ${easter_egg_response.status_code}    200
    ${response_for_egg}=    Set Variable    ${easter_egg_response.json()}
    Log To Console    hláška:${response_for_egg}
    ${if_matched}=    Set Variable    ${response_for_egg['matched']}
    Log To Console    macthed:${if_matched}
    Should Be Equal    ${if_matched}    ${False}

Zkouška Na Přidání Instrukcí
    ${instructions}=    Create Dictionary
    ...    text=${instructions_for_test}
    ${post_instructions}=    PUT On Session    mysession    ${BASE_URL}/${id}/instructions    json=${instructions}
    Should Be Equal As Strings    ${post_instructions.status_code}    200
    ${form_id}=    Set Variable    ${post_instructions.json()['form_id']}
    Log To Console    new instructions id:${form_id}


    DELETE On Session    mysession    /${id}