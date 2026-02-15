# UI + API + DB Integration

## Learning Objectives
- [ ] Combine UI, API, and DB testing
- [ ] Create comprehensive test workflows
- [ ] Verify end-to-end scenarios
- [ ] Understand full-stack testing

## Prerequisites
- Completed BEGINNER topics for Browser, Requests, Database
- Understand each library's fundamentals

---

## Why Integration Testing?

**Integration testing** verifies:
- UI correctly calls backend APIs
- Backend persists to database
- Data flows correctly through all layers
- Business rules work end-to-end

**Benefits:**
- Catches integration bugs
- Tests real user workflows
- Validates complete system
- More confidence than unit tests

---

## Test Architecture

```
┌─────────────┐
│  UI Tests    │  Browser Library
│  (Frontend)  │  - Fills forms
└──────┬──────┘  - Verifies UI
       │
       ▼
┌─────────────┐
│  API Tests   │  Requests Library
│  (Backend)   │  - Makes requests
└──────┬──────┘  - Validates responses
       │
       ▼
┌─────────────┐
│  DB Tests    │  Database Library
│  (Database)  │  - Verifies data
└─────────────┘  - Validates schema
```

---

## Pattern 1: Create via UI, Verify in API and DB

### Complete User Flow

```robotframework
*** Settings ***
Library     Browser
Library     RequestsLibrary
Library     DatabaseLibrary

*** Variables ***
${UI_URL}      http://localhost:8081
${API_URL}     http://localhost:8000/api/v1
${DB_NAME}     moje_app

*** Test Cases ***
Create Form Via UI Verify Every Layer
    [Documentation]    Submit form via UI, verify in API and DB

    # Setup
    Connect To Database    psycopg2    ${DB_NAME}    postgres    postgres    localhost
    Create Session    api    ${API_URL}
    New Browser    chromium    headless=False
    New Context
    New Page       ${UI_URL}

    # Prepare test data
    ${first_name}=    Set Variable    Integration
    ${last_name}=     Set Variable    Test
    ${email}=         Set Variable    integration@test.com
    ${phone}=         Set Variable    +420999888777

    # Step 1: Submit via UI
    Fill Text    [data-testid="firstName-input"]    ${first_name}
    Fill Text    [data-testid="lastName-input"]     ${last_name}
    Fill Text    [data-testid="email-input"]        ${email}
    Fill Text    [data-testid="phone-input"]        ${phone}
    Click    [data-testid="genderPicker"]
    Click    [data-testid="gender-option-male"]
    Click    [data-testid="submitButton"]

    # Step 2: Verify success in UI
    Wait For Elements State    [data-testid="formSuccessModal"]    visible
    Log    ✅ UI: Success modal visible

    # Step 3: Verify via API
    # Get all forms and find ours
    ${response}=    GET On Session    api    /form/
    ${json}=    Evaluate    json.loads('${response.text}')    modules=json

    ${found}=    Set Variable    ${FALSE}
    FOR    ${form}    IN    @{json}
        IF    $form['email'] == '${email}'
            ${found}=    Set Variable    ${TRUE}
            ${form_id}=    Set Variable    ${form}[id]
            Log    ✅ API: Found form with ID ${form_id}
            BREAK
        END
    END

    Should Be True    ${found}    msg=Form not found via API

    # Step 4: Verify in Database
    ${result}=    Query
    ...    SELECT first_name, last_name, email FROM form_data
    ...    WHERE id = ${form_id}

    ${row}=    Get From List    ${result}    0
    Should Be Equal    ${row}[first_name]    ${first_name}
    Should Be Equal    ${row}[last_name]     ${last_name}
    Should Be Equal    ${row}[email]         ${email}
    Log    ✅ DB: Data verified in database

    # Cleanup
    DELETE On Session    api    /form/${form_id}
    Disconnect From Database
    Close Browser
```

---

## Pattern 2: Create via API, Verify in UI and DB

### API-First Testing

```robotframework
*** Test Cases ***
Create Via API Verify UI And DB
    [Documentation]    Create form via API, verify appears in UI

    # Setup
    Connect To Database    psycopg2    ${DB_NAME}    postgres    postgres    localhost
    Create Session    api    ${API_URL}
    New Browser    chromium    headless=False
    New Context
    New Page       ${UI_URL}

    # Create via API
    &{data}=    Create Dictionary
    ...    first_name=API
    ...    last_name=Created
    ...    phone=+420111222333
    ...    gender=male
    ...    email=apicreated@test.com

    ${response}=    POST On Session    api    /form/    json=${data}
    ${json}=    Evaluate    json.loads('${response.text}')    modules=json
    ${form_id}=    Set Variable    ${json}[id]

    Log    ✅ API: Created form ID ${form_id}

    # Verify in UI
    Click    [data-testid="menu-item-Page2"]

    Wait For Elements State    [data-testid="page2Title"]    visible

    # Find our form in the list
    ${found}=    Set Variable    ${FALSE}
    ${item_count}=    Get Element Count    [data-testid^="list-item-"][data-testid$="-name"]

    FOR    ${i}    IN RANGE    ${item_count}
        ${item_text}=    Get Text    [data-testid^="list-item-"][data-testid$="-name"] >> nth=${i}
        IF    '${item_text}' == 'API Created'
            ${found}=    Set Variable    ${TRUE}
            Log    ✅ UI: Found form in list
            BREAK
        END
    END

    Should Be True    ${found}    msg=Form not found in UI list

    # Verify in Database
    ${result}=    Query    SELECT COUNT(*) FROM form_data WHERE id = ${form_id}
    ${count}=    Set Variable    ${result}[0][0]

    Should Be Equal As Integers    ${count}    1
    Log    ✅ DB: Form exists in database

    # Cleanup
    DELETE On Session    api    /form/${form_id}
    Disconnect From Database
    Close Browser
```

---

## Pattern 3: Delete via UI, Verify in API and DB

### Full Lifecycle Test

```robotframework
*** Test Cases ***
Delete Via UI Verify Gone From API And DB
    [Documentation]    Delete via UI, verify removed from all layers

    # Setup: Create form first
    Connect To Database    psycopg2    ${DB_NAME}    postgres    postgres    localhost
    Create Session    api    ${API_URL}

    &{data}=    Create Dictionary
    ...    first_name=Delete
    ...    last_name=Me
    ...    phone=+420123456789
    ...    gender=male
    ...    email=deleteme@test.com

    ${create_resp}=    POST On Session    api    /form/    json=${data}
    ${json}=    Evaluate    json.loads('${create_resp.text}')    modules=json
    ${form_id}=    Set Variable    ${json}[id]

    # Verify exists before delete
    ${get_before}=    GET On Session    api    /form/${form_id}
    Should Be Equal As Strings    ${get_before.status_code}    200

    ${db_before}=    Row Count    SELECT COUNT(*) FROM form_data WHERE id = ${form_id}
    Should Be Equal As Integers    ${db_before}    1

    # Delete via UI
    New Browser    chromium    headless=False
    New Context
    New Page    ${UI_URL}

    Click    [data-testid="menu-item-Page2"]
    Wait For Elements State    [data-testid="list-container"]    visible

    # Find and delete our form
    Click    [data-testid^="list-item-"][data-testid$="-name"] >> nth=0

    # Wait for modal
    Wait For Elements State    [data-testid="info-modal"]    visible
    ${delete_button}=    Run Keyword And Return Status
    ...    Get Element    [data-testid^="list-item-"][data-testid$="-delete"]

    IF    ${delete_button}
        Click    [data-testid^="list-item-"][data-testid$="-delete"]
        Wait For Elements State    [data-testid="deleteConfirmModal"]    visible
        Click    [data-testid="deleteConfirmModal-confirm"]
    END

    Wait For Elements State    [data-testid="info-modal"]    hidden    timeout=5s

    Log    ✅ UI: Form deleted

    # Verify via API - should return 404
    ${get_after}=    GET On Session    api    /form/${form_id}    expected_status=404
    Log    ✅ API: Form returns 404

    # Verify in Database - should be gone
    ${db_after}=    Row Count    SELECT COUNT(*) FROM form_data WHERE id = ${form_id}
    Should Be Equal As Integers    ${db_after}    0
    Log    ✅ DB: Form removed from database

    # Cleanup
    Disconnect From Database
    Delete All Sessions
    Close Browser
```

---

## Helper Keywords

### Multi-Layer Verification

```robotframework
*** Keywords ***
Verify Form In All Layers
    [Arguments]    ${form_id}    &{expected_data}

    # API Verification
    ${response}=    GET On Session    api    /form/${form_id}
    Should Be Equal As Strings    ${response.status_code}    200

    ${api_data}=    Evaluate    json.loads('${response.text}')    modules=json

    FOR    ${key}    IN    @{expected_data.keys}
        Should Be Equal    ${api_data}[${key}]    ${expected_data}[${key}]
    END

    Log    ✅ API: Data verified

    # Database Verification
    ${result}=    Query
    ...    SELECT * FROM form_data WHERE id = ${form_id}

    ${row}=    Get From List    ${result}    0

    FOR    ${key}    IN    @{expected_data.keys}
        Should Be Equal    ${row}[${key}]    ${expected_data}[${key}]
    END

    Log    ✅ DB: Data verified
```

### Cleanup All Layers

```robotframework
*** Keywords ***
Cleanup Test Data
    [Arguments]    ${email_pattern}

    # Delete via API
    ${response}=    GET On Session    api    /form/
    ${forms}=    Evaluate    json.loads('${response.text}')    modules=json

    FOR    ${form}    IN    @{forms}
        IF    $form['email'].contains('${email_pattern}')
            DELETE On Session    api    /form/${form}[id]
            Log    Deleted form ${form}[id]
        END
    END

    # Verify in database
    ${count}=    Row Count
    ...    SELECT COUNT(*) FROM form_data
    ...    WHERE email LIKE '%${email_pattern}%'

    Should Be Equal As Integers    ${count}    0
```

---

## Common Patterns

### UI → API → DB Verification

```robotframework
# Use when testing UI submission flow
1. Fill form via UI
2. Submit via UI
3. Get response data via API
4. Verify data in DB
```

### API → UI → DB Verification

```robotframework
# Use when testing API creation
1. Create via API
2. Navigate UI to view
3. Verify visible in UI
4. Verify persisted in DB
```

### DB → API → UI Verification

```robotframework
# Use when testing data integrity
1. Query DB for data
2. Fetch via API
3. Display in UI
4. Verify all match
```

---

## Self-Check Questions

1. Why test integration between layers?
2. What's the benefit of multi-layer verification?
3. How do you ensure test data cleanup?
4. What's the recommended test flow for CRUD operations?

---

## Exercise: Full Integration Test

**Task:** Create comprehensive integration test for form lifecycle.

**Scenario:**
1. Create form via UI
2. Verify in API and DB
3. Update via API
4. Verify in UI and DB
5. Delete via UI
6. Verify removal in API and DB

**Acceptance Criteria:**
- [ ] All layers verified at each step
- [ ] Proper cleanup
- [ ] Comprehensive logging

**Starter Code:**
```robotframework
*** Settings ***
Library     Browser
Library     RequestsLibrary
Library     DatabaseLibrary

*** Variables ***
${UI_URL}      http://localhost:8081
${API_URL}     http://localhost:8000/api/v1
${DB_NAME}     moje_app

*** Test Cases ***
Full Integration Test
    [Documentation]    TODO: Implement full integration test
    # TODO: Your code here
```

---

## Hints

### Hint 1
Flow: Create (UI) → Verify (API, DB) → Update (API) → Verify (UI, DB) → Delete (UI) → Verify (API, DB)

### Hint 2
Use helper keywords for multi-layer verification to avoid repetition.

### Hint 3 (Structure)
```robotframework
Full Integration Test
    # Setup all connections
    Connect To Database
    Create Session    api
    New Browser

    # Create via UI
    # Verify in API and DB

    # Update via API
    # Verify in UI and DB

    # Delete via UI
    # Verify removal

    # Cleanup all
```

---

## References

- Project integration: `/RF/UI/tests/new_form.robot`
- API workflows: `/RF/API/workflows/`
- DB verification: `/RF/db/tests/verify_email.robot`
