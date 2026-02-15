# GET Requests and Response Handling

## Learning Objectives
- [ ] Make GET requests with parameters
- [ ] Handle pagination
- [ ] Filter and sort results
- [ ] Validate response structure

## Prerequisites
- Completed API Basics
- Understand HTTP methods

---

## GET Request Fundamentals

### Simple GET

```robotframework
*** Settings ***
Library     RequestsLibrary

*** Variables ***
${BASE_URL}    http://localhost:8000/api/v1

*** Test Cases ***
Simple Get Request
    Create Session    api    ${BASE_URL}

    ${response}=    GET On Session    api    /form/

    Log    Status: ${response.status_code}
    Log    Body: ${response.text}

    Should Be Equal As Strings    ${response.status_code}    200
```

### GET with Expected Status

```robotframework
# Expect specific status
${response}=    GET On Session    api    /form/    expected_status=200

# Expect any 2xx (success)
${response}=    GET On Session    api    /form/    expected_status=anything
```

---

## Query Parameters

### URL Parameters

```robotframework
*** Test Cases ***
Get With Query Parameters
    Create Session    api    ${BASE_URL}

    # Method 1: In URL
    ${response}=    GET On Session    api    /form/?skip=0&limit=10

    # Method 2: As params dictionary
    &{params}=    Create Dictionary    skip=0    limit=10
    ${response}=    GET On Session    api    /form/    params=${params}
```

### Common Query Parameters

```robotframework
# Pagination
&{params}=    Create Dictionary    skip=0    limit=20

# Filtering
&{params}=    Create Dictionary    status=pending    date=2024-01-01

# Sorting
&{params}=    Create Dictionary    sort=created_at    order=desc

# Combined
&{params}=    Create Dictionary
...    skip=0
...    limit=10
...    status=active
...    sort=name
```

---

## Pagination

### Understanding Pagination

```robotframework
*** Test Cases ***
Get All Forms With Pagination
    Create Session    api    ${BASE_URL}

    # Set page size
    &{params}=    Create Dictionary    skip=0    limit=50

    # Get first page
    ${response}=    GET On Session    api    /form/    params=${params}
    ${json}=    Evaluate    json.loads('${response.text}')    modules=json

    ${page_count}=    Get Length    ${json}
    Log    Page 1: ${page_count} items

    # Get next page
    &{params2}=    Create Dictionary    skip=50    limit=50
    ${response2}=    GET On Session    api    /form/    params=${params2}
    ${json2}=    Evaluate    json.loads('${response2.text}')    modules=json

    ${page2_count}=    Get Length    ${json2}
    Log    Page 2: ${page2_count} items
```

### Pagination Pattern

```robotframework
*** Keywords ***
Get All Items Paginated
    [Arguments]    ${session}    ${endpoint}    ${page_size}=50

    @{all_items}=    Create List
    ${skip}=    Set Variable    0
    ${has_more}=    Set Variable    ${True}

    WHILE    ${has_more}
        &{params}=    Create Dictionary    skip=${skip}    limit=${page_size}
        ${response}=    GET On Session    ${session}    ${endpoint}    params=${params}

        Should Be Equal As Strings    ${response.status_code}    200
        ${json}=    Evaluate    json.loads('${response.text}')    modules=json

        ${count}=    Get Length    ${json}

        IF    ${count} == 0
            ${has_more}=    Set Variable    ${False}
        ELSE
            Append To List    ${all_items}    @{json}
            ${skip}=    Evaluate    ${skip} + ${count}
        END
    END

    [Return]    @{all_items}
```

---

## Response Handling

### Parse JSON Response

```robotframework
*** Test Cases ***
Parse And Validate Response
    Create Session    api    ${BASE_URL}

    ${response}=    GET On Session    api    /form/

    # Parse JSON
    ${json}=    Evaluate    json.loads('${response.text}')    modules=json

    # Check if list
    ${is_list}=    Evaluate    isinstance(${json}, list)
    Log    Response is list: ${is_list}

    # Get count
    ${count}=    Get Length    ${json}
    Log    Total items: ${count}
```

### Access Nested Data

```robotframework
# Response structure:
# {
#   "id": 1,
#   "first_name": "Jan",
#   "address": {
#     "street": "Main St",
#     "city": "Prague"
#   }
# }

${json}=    Evaluate    json.loads('${response.text}')    modules=json

# Access top-level field
${id}=    Get From Dictionary    ${json}    id

# Access nested field
${address}=    Get From Dictionary    ${json}    address
${city}=    Get From Dictionary    ${address}    city

# Direct access (simpler)
${city}=    Set Variable    ${json}[address][city]
```

### Handle Empty Responses

```robotframework
*** Test Cases ***
Handle Empty List Response
    Create Session    api    ${BASE_URL}

    ${response}=    GET On Session    api    /form/
    ${json}=    Evaluate    json.loads('${response.text}')    modules=json

    ${count}=    Get Length    ${json}

    IF    ${count} == 0
        Log    No forms found - database is empty
    ELSE
        Log    Found ${count} forms
        # Process items...
    END
```

---

## Application Examples

### Example 1: Get Forms with Pagination

```robotframework
*** Test Cases ***
Get All Forms Paginated
    [Documentation]    Retrieve all forms using pagination

    Create Session    api    ${BASE_URL}

    # First page
    &{params}=    Create Dictionary    skip=0    limit=10
    ${response}=    GET On Session    api    /form/    params=${params}

    Should Be Equal As Strings    ${response.status_code}    200

    ${json}=    Evaluate    json.loads('${response.text}')    modules=json

    # Verify response structure
    ${is_list}=    Evaluate    isinstance(${json}, list)
    Should Be True    ${is_list}

    # Get item count
    ${count}=    Get Length    ${json}
    Log    Retrieved ${count} forms

    # Verify each item has required fields
    FOR    ${item}    IN    @{json}
        ${keys}=    Get Dictionary Keys    ${item}
        Should Contain    ${keys}    id
        Should Contain    ${keys}    first_name
        Should Contain    ${keys}    email
    END
```

### Example 2: Get Specific Resource

```robotframework
*** Test Cases ***
Get Form By ID
    [Documentation]    Retrieve specific form by ID

    Create Session    api    ${BASE_URL}

    # First, create a form to get its ID
    &{data}=    Create Dictionary
    ...    first_name=Get
    ...    last_name=Test
    ...    phone=+420123456789
    ...    gender=male
    ...    email=get-test@example.com

    ${create_resp}=    POST On Session    api    /form/    json=${data}
    ${create_json}=    Evaluate    json.loads('${create_resp.text}')    modules=json
    ${form_id}=    Set Variable    ${create_json}[id]

    # Get the form by ID
    ${get_resp}=    GET On Session    api    /form/${form_id}

    Should Be Equal As Strings    ${get_resp.status_code}    200

    ${json}=    Evaluate    json.loads('${get_resp.text}')    modules=json

    # Verify all fields
    Should Be Equal    ${json}[id]           ${form_id}
    Should Be Equal    ${json}[first_name]   Get
    Should Be Equal    ${json}[last_name]    Test
    Should Be Equal    ${json}[email]        get-test@example.com

    # Cleanup
    DELETE On Session    api    /form/${form_id}
```

### Example 3: Filter and Validate

```robotframework
*** Test Cases ***
Filter Forms By Name
    [Documentation]    Find forms matching specific name

    Create Session    api    ${BASE_URL}

    # Get all forms
    ${response}=    GET On Session    api    /form/

    ${json}=    Evaluate    json.loads('${response.text}')    modules=json

    # Filter for specific name
    @{filtered}=    Create List
    FOR    ${item}    IN    @{json}
        IF    $item['first_name'] == 'Jan'
            Append To List    ${filtered}    ${item}
        END
    END

    ${count}=    Get Length    ${filtered}
    Log    Found ${count} forms with first_name='Jan'

    # Verify at least one exists
    Should Be True    ${count} >= 0
```

---

## Response Validation Patterns

### Validate Status Code

```robotframework
*** Keywords ***
Validate Success Response
    [Arguments]    ${response}

    # Check status is 2xx
    ${status}=    Set Variable    ${response.status_code}
    Should Be True    ${status} >= 200 and ${status} < 300
    ...    msg=Expected success status, got ${status}

Validate Error Response
    [Arguments]    ${response}    ${expected_status}=400

    Should Be Equal As Strings    ${response.status_code}    ${expected_status}
```

### Validate JSON Structure

```robotframework
*** Keywords ***
Validate Form Response Structure
    [Arguments]    ${json}

    # Check required fields exist
    ${keys}=    Get Dictionary Keys    ${json}
    Should Contain    ${keys}    id
    Should Contain    ${keys}    first_name
    Should Contain    ${keys}    last_name
    Should Contain    ${keys}    email
    Should Contain    ${keys}    phone
    Should Contain    ${keys}    gender

    # Check field types
    ${id_type}=    Evaluate    type(${json}[id]).__name__
    Should Be Equal    ${id_type}    int

    ${email_type}=    Evaluate    type(${json}[email]).__name__
    Should Be Equal    ${email_type}    str
```

### Validate Data Values

```robotframework
*** Keywords ***
Validate FormData
    [Arguments]    ${json}    &{expected_data}

    # Compare each field
    FOR    ${key}    IN    @{expected_data.keys}
        ${actual}=    Get From Dictionary    ${json}    ${key}
        ${expected}=    Get From Dictionary    ${expected_data}    ${key}
        Should Be Equal    ${actual}    ${expected}    msg=Field ${key} mismatch
    END
```

---

## Common Pitfalls

| Pitfall | Why It Happens | Fix |
|---------|---------------|-----|
| Empty response | Wrong endpoint or no data | Check database has data |
| JSON parse error | Response not JSON | Verify Content-Type header |
| Wrong data type | Type mismatch | Use correct type comparison |
| Missing field | API changed | Check API documentation |

---

## Self-Check Questions

1. How do you add query parameters to GET request?
2. What's the difference between `skip=0&limit=10` in URL vs params dict?
3. How do you handle pagination in API tests?
4. How do you validate JSON response structure?

---

## Exercise: GET with Filtering

**Task:** Create a test that gets forms and filters them.

**Scenario:**
1. Create 3 forms with different first names
2. GET all forms
3. Filter/verify specific forms exist
4. Cleanup test data

**Acceptance Criteria:**
- [ ] Creates multiple test forms
- [ ] Retrieves all forms
- [ ] Filters and verifies specific data
- [ ] Cleans up all created forms

**Starter Code:**
```robotframework
*** Settings ***
Library     RequestsLibrary

*** Variables ***
${BASE_URL}    http://localhost:8000/api/v1

*** Test Cases ***
Get And Filter Forms
    [Documentation]    TODO: Implement GET with filtering
    # TODO: Your code here

*** Keywords ***
# TODO: Add helper keywords
```

---

## Hints

### Hint 1
Create forms with distinctive first names for easy filtering.

### Hint 2
Use FOR loop to iterate through response and filter by name.

### Hint 3
```robotframework
Get And Filter Forms
    Create Session    api    ${BASE_URL}

    # Create 3 forms with different names
    @{form_ids}=    Create List
    ${names}=    Create List    Alpha    Beta    Gamma

    FOR    ${name}    IN    @{names}
        &{data}=    Create Dictionary    first_name=${name}    last_name=Test    ...
        ${resp}=    POST On Session    api    /form/    json=${data}
        ${json}=    Evaluate    json.loads('${resp.text}')    modules=json
        Append To List    ${form_ids}    ${json}[id]
    END

    # Get all forms
    ${get_resp}=    GET On Session    api    /form/
    ${all_forms}=    Evaluate    json.loads('${get_resp.text}')    modules=json

    # TODO: Filter and verify
```

### Hint 4 (Full Solution)
```robotframework
*** Settings ***
Library     RequestsLibrary

*** Variables ***
${BASE_URL}    http://localhost:8000/api/v1

*** Test Cases ***
Get And Filter Forms
    [Documentation]    Creates multiple forms and filters by name
    [Tags]    beginner    exercise    get

    Create Session    api    ${BASE_URL}

    # Create test data with distinctive names
    @{test_names}=    Create List    Alpha    Beta    Gamma
    @{created_ids}=    Create List

    FOR    ${name}    IN    @{test_names}
        &{data}=    Create Dictionary
        ...    first_name=${name}
        ...    last_name=TestUser
        ...    phone=+420123456789
        ...    gender=male
        ...    email=${name}@test.com

        ${response}=    POST On Session    api    /form/    json=${data}
        ${json}=    Evaluate    json.loads('${response.text}')    modules=json

        Append To List    ${created_ids}    ${json}[id]
        Log    Created form: ${name} (ID: ${json}[id])
    END

    # Get all forms
    ${get_response}=    GET On Session    api    /form/
    Should Be Equal As Strings    ${get_response.status_code}    200

    ${all_forms}=    Evaluate    json.loads('${get_response.text}')    modules=json

    # Filter for our test names
    @{filtered_forms}=    Create List
    FOR    ${form}    IN    @{all_forms}
        ${first_name}=    Get From Dictionary    ${form}    first_name

        # Check if name matches our test data
        IF    $first_name in @{test_names}
            Append To List    ${filtered_forms}    ${form}
            Log    Found match: ${first_name}
        END
    END

    # Verify we found all 3 forms
    ${filtered_count}=    Get Length    ${filtered_forms}
    Should Be Equal    ${filtered_count}    3    msg=Should find all 3 test forms

    # Verify each has correct data
    FOR    ${form}    IN    @{filtered_forms}
        Should Contain    @{test_names}    ${form}[first_name]
        Should Be Equal    ${form}[last_name]    TestUser
    END

    [Teardown]    Clean Up Test Forms    ${created_ids}

*** Keywords ***
Clean Up Test Forms
    [Arguments]    @{form_ids}

    FOR    ${form_id}    IN    @{form_ids}
        ${response}=    DELETE On Session    api    /form/${form_id}
        Log    Deleted form ID: ${form_id}
    END
```

---

## References

- [HTTP GET Method](https://developer.mozilla.org/en-US/docs/Web/HTTP/Methods/GET)
- [REST API Pagination](https://api.openai.com/docs/api-reference/pagination)
- Project: `/RF/API/tests/create_form.robot`
- Backend: `/be/app/api/endpoints/form_data.py`
