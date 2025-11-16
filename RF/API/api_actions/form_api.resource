*** Comments ***
# LAYER 2: API Actions
#
# Tento soubor obsahuje individual API calls - základní operace s API.
# Každý keyword provádí JEDNU API akci (POST, GET, DELETE).
#
# Analogie k UI testům: api_actions/ = pages/


*** Settings ***
Resource    ../common.resource
Library     RequestsLibrary
Library     Collections


*** Keywords ***
Create Form Data
    [Documentation]    Vytvoří nový form data záznam přes POST API
    ...
    ...    Args:
    ...    - session: Session alias (created via Create Session)
    ...    - form_data: Dictionary s form data (first_name, last_name, phone, gender, email)
    ...
    ...    Returns:
    ...    - response: Response object s created data
    ...
    ...    Example:
    ...    | &{data}=    Create Dictionary    first_name=Jan    last_name=Novák    phone=123456789    gender=muž    email=jan@test.com
    ...    | ${response}=    Create Form Data    mysession    ${data}
    [Arguments]    ${session}    ${form_data}

    # Log request
    Log API Request    POST    ${FORM_CREATE_ENDPOINT}    ${form_data}

    # Perform API call
    ${response}=    POST On Session    ${session}    /    json=${form_data}    expected_status=200

    # Log response
    Log API Response    ${response}

    # Verify response structure
    Should Be Equal As Integers    ${response.status_code}    200
    Dictionary Should Contain Key    ${response.json()}    id

    RETURN    ${response}

Get Form Data By ID
    [Documentation]    Získá form data záznam podle ID přes GET API
    ...
    ...    Args:
    ...    - session: Session alias
    ...    - form_id: ID záznamu k získání
    ...
    ...    Returns:
    ...    - response: Response object s form data
    [Arguments]    ${session}    ${form_id}

    # Log request
    Log API Request    GET    ${FORM_GET_BY_ID_ENDPOINT}

    # Perform API call
    ${response}=    GET On Session    ${session}    /${form_id}    expected_status=200

    # Log response
    Log API Response    ${response}

    RETURN    ${response}

Get All Form Data
    [Documentation]    Získá všechny form data záznamy přes GET API
    ...
    ...    Args:
    ...    - session: Session alias
    ...    - skip: Number of records to skip (optional)
    ...    - limit: Max number of records to return (optional)
    ...
    ...    Returns:
    ...    - response: Response object s list form data
    [Arguments]    ${session}    ${skip}=0    ${limit}=100

    # Prepare query params
    &{params}=    Create Dictionary    skip=${skip}    limit=${limit}

    # Log request
    Log API Request    GET    ${FORM_LIST_ENDPOINT}

    # Perform API call
    ${response}=    GET On Session    ${session}    /    params=${params}    expected_status=200

    # Log response
    Log API Response    ${response}

    # Verify response is list
    ${data}=    Set Variable    ${response.json()}
    Should Be True    isinstance($data, list)

    RETURN    ${response}

Delete Form Data
    [Documentation]    Smaže form data záznam podle ID přes DELETE API
    ...
    ...    Args:
    ...    - session: Session alias
    ...    - form_id: ID záznamu ke smazání
    ...
    ...    Returns:
    ...    - response: Response object s delete confirmation
    [Arguments]    ${session}    ${form_id}

    # Log request
    Log API Request    DELETE    ${FORM_DELETE_ENDPOINT}

    # Perform API call
    ${response}=    DELETE On Session    ${session}    /${form_id}    expected_status=200

    # Log response
    Log API Response    ${response}

    # Verify delete message
    ${data}=    Set Variable    ${response.json()}
    Dictionary Should Contain Key    ${data}    message
    Should Contain    ${data['message']}    smazán

    RETURN    ${response}

Evaluate Name For Easter Egg
    [Documentation]    Vyhodnotí text proti tajným jménům (easter egg logic)
    ...
    ...    Args:
    ...    - session: Session alias
    ...    - text: Text k vyhodnocení
    ...
    ...    Returns:
    ...    - response: Response object s matched status a message
    [Arguments]    ${session}    ${text}

    # Prepare payload
    &{payload}=    Create Dictionary    text=${text}

    # Log request
    Log API Request    POST    ${FORM_EVALUATE_NAME_ENDPOINT}    ${payload}

    # Perform API call
    ${response}=    POST On Session    ${session}    /evaluate-name    json=${payload}    expected_status=200

    # Log response
    Log API Response    ${response}

    # Verify response structure
    ${data}=    Set Variable    ${response.json()}
    Dictionary Should Contain Key    ${data}    matched

    RETURN    ${response}

Create Attachment For Form
    [Documentation]    Vytvoří přílohu pro existující form
    ...
    ...    Args:
    ...    - session: Session alias
    ...    - form_id: ID formuláře
    ...    - attachment_data: Dictionary s filename, content_type, data_base64
    ...
    ...    Returns:
    ...    - response: Response object s created attachment
    [Arguments]    ${session}    ${form_id}    ${attachment_data}

    # Log request
    Log API Request    POST    ${FORM_ATTACHMENT_CREATE_ENDPOINT}    ${attachment_data}

    # Perform API call
    ${response}=    POST On Session    ${session}    /${form_id}/attachment    json=${attachment_data}    expected_status=200

    # Log response
    Log API Response    ${response}

    RETURN    ${response}

Get Attachments For Form
    [Documentation]    Získá všechny přílohy pro formulář
    ...
    ...    Args:
    ...    - session: Session alias
    ...    - form_id: ID formuláře
    ...
    ...    Returns:
    ...    - response: Response object s list attachments
    [Arguments]    ${session}    ${form_id}

    # Log request
    Log API Request    GET    ${FORM_ATTACHMENT_LIST_ENDPOINT}

    # Perform API call
    ${response}=    GET On Session    ${session}    /${form_id}/attachments    expected_status=200

    # Log response
    Log API Response    ${response}

    RETURN    ${response}

Create Or Update Instructions
    [Documentation]    Vytvoří nebo updateuje instrukce pro formulář
    ...
    ...    Args:
    ...    - session: Session alias
    ...    - form_id: ID formuláře
    ...    - instructions_text: Text instrukcí
    ...
    ...    Returns:
    ...    - response: Response object s instructions
    [Arguments]    ${session}    ${form_id}    ${instructions_text}

    # Prepare payload
    &{payload}=    Create Dictionary    text=${instructions_text}

    # Log request
    Log API Request    PUT    ${FORM_INSTRUCTION_CREATE_ENDPOINT}    ${payload}

    # Perform API call
    ${response}=    PUT On Session    ${session}    /${form_id}/instructions    json=${payload}    expected_status=200

    # Log response
    Log API Response    ${response}

    RETURN    ${response}

Get Instructions For Form
    [Documentation]    Získá instrukce pro formulář
    ...
    ...    Args:
    ...    - session: Session alias
    ...    - form_id: ID formuláře
    ...
    ...    Returns:
    ...    - response: Response object s instructions (nebo None)
    [Arguments]    ${session}    ${form_id}

    # Log request
    Log API Request    GET    ${FORM_INSTRUCTION_GET_ENDPOINT}

    # Perform API call
    ${response}=    GET On Session    ${session}    /${form_id}/instructions    expected_status=any

    # Log response
    Log API Response    ${response}

    RETURN    ${response}
