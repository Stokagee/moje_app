# API Testing Basics

## Learning Objectives
- [ ] Understand REST API concepts
- [ ] Make simple HTTP requests
- [ ] Validate responses
- [ ] Handle JSON data

## Prerequisites
- Completed GETTING_STARTED
- Basic understanding of HTTP

---

## What is API Testing?

**API (Application Programming Interface)** testing verifies:
- Endpoints respond correctly
- Request/response formats match
- Data validation works
- Error handling is proper

**Why API Testing?**
- Faster than UI testing
- More stable (less UI changes)
- Catches backend bugs early
- Easier to automate

---

## HTTP Methods

| Method | Purpose | Example | Idempotent |
|--------|---------|---------|------------|
| GET | Retrieve data | `GET /form/` | Yes |
| POST | Create resource | `POST /form/` | No |
| PUT | Update (replace) | `PUT /form/1` | Yes |
| PATCH | Update (modify) | `PATCH /form/1` | No |
| DELETE | Remove resource | `DELETE /form/1` | Yes |

**Idempotent:** Multiple identical requests have same effect as one request.

---

## HTTP Status Codes

| Code | Category | Meaning | Example Use |
|------|----------|---------|-------------|
| 2xx | Success | Request worked | 200 OK, 201 Created |
| 3xx | Redirect | Further action needed | 301, 302 |
| 4xx | Client Error | Invalid request | 400 Bad Request, 404 Not Found |
| 5xx | Server Error | Server failed | 500 Internal Server Error |

**Common Codes:**
- `200 OK` - GET/PUT/PATCH success
- `201 Created` - POST success
- `204 No Content` - DELETE success
- `400 Bad Request` - Invalid data
- `404 Not Found` - Resource doesn't exist
- `500 Internal Server Error` - Server bug

---

## First API Request

### Basic GET Request

```robotframework
*** Settings ***
Library     RequestsLibrary

*** Variables ***
${BASE_URL}    http://localhost:8000/api/v1

*** Test Cases ***
Get All Forms
    [Documentation]    Retrieve all form submissions

    # Create session
    Create Session    mysession    ${BASE_URL}

    # Make GET request
    ${response}=    GET On Session    mysession    /form/

    # Log response
    Log    Status: ${response.status_code}
    Log    Body: ${response.text}

    # Verify status
    Should Be Equal As Strings    ${response.status_code}    200
```

### Understanding Response

```robotframework
${response}=    GET On Session    mysession    /form/

# Status code (integer)
${status}=    Set Variable    ${response.status_code}    # 200

# Response body (string)
${body}=    Set Variable    ${response.text}           # JSON string
${json}=    Evaluate    json.loads('${body}')           # Python dict

# Headers (dictionary)
${headers}=    Set Variable    ${response.headers}

# Content type
${content_type}=    Get From Dictionary    ${headers}    Content-Type
```

---

## POST Request (Create Data)

### Creating a Form

```robotframework
*** Test Cases ***
Create New Form
    [Documentation]    Create a form submission via API

    Create Session    mysession    ${BASE_URL}

    # Prepare request data
    &{data}=    Create Dictionary
    ...    first_name=Jan
    ...    last_name=Novák
    ...    phone=+420123456789
    ...    gender=male
    ...    email=jan.novak@example.com

    # Send POST request
    ${response}=    POST On Session    mysession    /form/    json=${data}

    # Verify response
    Should Be Equal As Strings    ${response.status_code}    201

    # Parse response body
    ${json}=    Evaluate    json.loads('${response.text}')    modules=json

    # Verify returned data
    Should Be Equal    ${json}[first_name]    Jan
    Should Be Equal    ${json}[last_name]     Novák
    Should Be Equal    ${json}[email]         jan.novak@example.com

    # Log created ID
    ${form_id}=    Set Variable    ${json}[id]
    Log    Created form with ID: ${form_id}
```

---

## Response Validation

### Status Code Validation

```robotframework
# Exact match
Should Be Equal As Strings    ${response.status_code}    200

# Range check (2xx = success)
${status}=    Set Variable    ${response.status_code}
Should Be True    ${status} >= 200 and ${status} < 300
```

### JSON Validation

```robotframework
*** Test Cases ***
Validate Response Structure
    ${response}=    GET On Session    api    /form/1

    # Parse JSON
    ${json}=    Evaluate    json.loads('${response.text}')    modules=json

    # Check field exists
    ${keys}=    Get Dictionary Keys    ${json}
    Should Contain    ${keys}    id
    Should Contain    ${keys}    first_name
    Should Contain    ${keys}    email

    # Check field values
    Should Be Equal    ${json}[first_name]    Jan
    Should Match Regexp    ${json}[email]    ^[\\w@.]+$
```

### Content-Type Validation

```robotframework
*** Test Cases ***
Validate Response Headers
    ${response}=    POST On Session    api    /form/    json=${data}

    # Check status
    Should Be Equal As Strings    ${response.status_code}    201

    # Check Content-Type header
    ${content_type}=    Get From Dictionary    ${response.headers}    Content-Type
    Should Contain    ${content_type}    application/json
```

---

## Working with JSON

### Parse JSON Response

```robotframework
${response}=    GET On Session    api    /form/
${json}=    Evaluate    json.loads('${response.text}')    modules=json

# Access fields
${first_item}=    Get From Dictionary    ${json}    0
${name}=    Get From Dictionary    ${first_item}    first_name
```

### Build JSON Request

```robotframework
# Method 1: Create Dictionary
&{data}=    Create Dictionary    name=Jan    email=jan@test.com
${response}=    POST On Session    api    /form/    json=${data}

# Method 2: JSON string
${body}=    Set Variable    {"name":"Jan","email":"jan@test.com"}
${response}=    POST On Session    api    /form/    data=${body}    headers=${headers}
```

### Update JSON

```robotframework
# Parse
${json}=    Evaluate    json.loads('${response.text}')    modules=json

# Modify
Set To Dictionary    ${json}    first_name    Updated Name

# Convert back to string
${updated_body}=    Evaluate    json.dumps(${json})    modules=json
```

---

## Application Examples

### Example 1: Get All Forms

```robotframework
*** Test Cases ***
Get All Form Submissions
    [Documentation]    Retrieve all forms from API

    Create Session    api    ${BASE_URL}

    ${response}=    GET On Session    api    /form/

    # Verify success
    Should Be Equal As Strings    ${response.status_code}    200

    # Parse JSON
    ${json}=    Evaluate    json.loads('${response.text}')    modules=json

    # Check it's a list
    ${type}=    Evaluate    type(${json}).__name__
    Should Be Equal    ${type}    list

    # Log count
    ${count}=    Get Length    ${json}
    Log    Found ${count} forms
```

### Example 2: Create and Verify

```robotframework
*** Test Cases ***
Create Form And Verify
    [Documentation]    Create form via API and verify it exists

    Create Session    api    ${BASE_URL}

    # Create form
    &{data}=    Create Dictionary
    ...    first_name=API
    ...    last_name=Test
    ...    phone=+420123456789
    ...    gender=male
    ...    email=api-test@example.com

    ${response}=    POST On Session    api    /form/    json=${data}

    # Extract ID from response
    ${json}=    Evaluate    json.loads('${response.text}')    modules=json
    ${form_id}=    Set Variable    ${json}[id]

    # Get the form by ID
    ${get_response}=    GET On Session    api    /form/${form_id}

    # Verify
    Should Be Equal As Strings    ${get_response.status_code}    200
    ${get_json}=    Evaluate    json.loads('${get_response.text}')    modules=json
    Should Be Equal    ${get_json}[first_name]    API

    # Cleanup
    DELETE On Session    api    /form/${form_id}
```

### Example 3: Error Handling

```robotframework
*** Test Cases ***
Duplicate Email Should Fail
    [Documentation]    Test that duplicate email is rejected

    Create Session    api    ${BASE_URL}

    &{data}=    Create Dictionary
    ...    first_name=Jan
    ...    last_name=Novák
    ...    phone=+420123456789
    ...    gender=male
    ...    email=duplicate@test.com

    # Create first form
    ${response1}=    POST On Session    api    /form/    json=${data}
    Should Be Equal As Strings    ${response1.status_code}    201

    # Try to create duplicate
    ${response2}=    POST On Session    api    /form/    json=${data}

    # Should fail with 400
    Should Be Equal As Strings    ${response2.status_code}    400

    # Verify error message
    ${json}=    Evaluate    json.loads('${response2.text}')    modules=json
    Should Contain    ${json}[detail]    exists
```

---

## Common Pitfalls

| Pitfall | Why It Happens | Fix |
|---------|---------------|-----|
| 404 errors | Wrong endpoint URL | Check base URL + endpoint |
| 400 errors | Invalid request data | Validate JSON structure |
| Connection refused | Server not running | Start backend: `uvicorn app.main:app` |
| JSON parsing errors | Response not JSON | Check Content-Type header |

---

## Best Practices

1. **Always create session first:**
   ```robotframework
   Create Session    alias    ${base_url}
   ```

2. **Use descriptive session names:**
   ```robotframework
   Create Session    form_api    ${BASE_URL}
   Create Session    order_api    ${BASE_URL}
   ```

3. **Validate status before parsing:**
   ```robotframework
   Should Be Equal As Strings    ${response.status_code}    200
   ${json}=    Evaluate    json.loads('${response.text}')
   ```

4. **Clean up test data:**
   ```robotframework
   [Teardown]    DELETE On Session    api    /form/${created_id}
   ```

---

## Self-Check Questions

1. What's the difference between GET and POST?
2. What does status code 201 mean?
3. How do you parse JSON response?
4. Why use sessions instead of individual requests?

---

## Exercise: Complete API Test

**Task:** Create a test that performs full CRUD on form data.

**Acceptance Criteria:**
- [ ] Create a form via POST
- [ ] Read it back via GET
- [ ] Verify data integrity
- [ ] Delete the form
- [ ] Verify deletion

**Starter Code:**
```robotframework
*** Settings ***
Library     RequestsLibrary

*** Variables ***
${BASE_URL}    http://localhost:8000/api/v1

*** Test Cases ***
Complete Form CRUD
    [Documentation]    TODO: Implement CRUD test
    # TODO: Your code here

*** Keywords ***
# TODO: Add helper keywords
```

---

## Hints

### Hint 1
Order: Create → GET by ID → Verify → DELETE → Verify deleted

### Hint 2
Use the returned ID from POST for subsequent GET and DELETE.

### Hint 3
```robotframework
Complete Form CRUD
    Create Session    api    ${BASE_URL}

    # POST - Create
    &{data}=    Create Dictionary    first_name=CRUD    last_name=Test    ...
    ${post_resp}=    POST On Session    api    /form/    json=${data}
    ${json}=    Evaluate    json.loads('${post_resp.text}')    modules=json
    ${id}=    Set Variable    ${json}[id]

    # TODO: Complete GET, verify, DELETE
```

### Hint 4 (Full Solution)
```robotframework
*** Settings ***
Library     RequestsLibrary

*** Variables ***
${BASE_URL}    http://localhost:8000/api/v1

*** Test Cases ***
Complete Form CRUD
    [Documentation]    Full CRUD lifecycle test
    [Tags]    beginner    exercise    crud

    # Setup
    Create Session    api    ${BASE_URL}

    # Prepare data
    &{data}=    Create Dictionary
    ...    first_name=CRUD
    ...    last_name=Test
    ...    phone=+420123456789
    ...    gender=male
    ...    email=crud-test@example.com

    # CREATE - POST new form
    ${post_response}=    POST On Session    api    /form/    json=${data}
    Should Be Equal As Strings    ${post_response.status_code}    201

    # Extract ID from response
    ${post_json}=    Evaluate    json.loads('${post_response.text}')    modules=json
    ${form_id}=    Set Variable    ${post_json}[id]
    Log    Created form with ID: ${form_id}

    # READ - GET form by ID
    ${get_response}=    GET On Session    api    /form/${form_id}
    Should Be Equal As Strings    ${get_response.status_code}    200

    # Verify returned data matches input
    ${get_json}=    Evaluate    json.loads('${get_response.text}')    modules=json
    Should Be Equal    ${get_json}[first_name]    CRUD
    Should Be Equal    ${get_json}[last_name]     Test
    Should Be Equal    ${get_json}[email]         crud-test@example.com

    # DELETE - Remove form
    ${delete_response}=    DELETE On Session    api    /form/${form_id}
    Should Be Equal As Strings    ${delete_response.status_code}    200

    # VERIFY DELETED - GET should return 404
    ${verify_response}=    GET On Session    api    /form/${form_id}    expected_status=404

    Log    ✅ CRUD test completed successfully
```

---

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Forgetting Create Session | Always create session before requests |
| Not validating status | Check status_code before parsing JSON |
| Missing required fields | Include all required fields in POST data |
| Wrong endpoint path | Use `/form/` not `/form` (trailing slash matters) |

---

## References

- [RequestsLibrary Docs](https://github.com/arketii/robotframework-requests)
- [REST API Tutorial](https://restfulapi.net/)
- Project: `/RF/API/tests/create_form.robot`
- Backend API: `/be/app/api/endpoints/form_data.py`
