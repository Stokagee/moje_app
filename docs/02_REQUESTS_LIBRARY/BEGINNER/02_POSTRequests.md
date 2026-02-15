# POST Requests and Data Creation

## Learning Objectives
- [ ] Create resources via POST
- [ ] Handle JSON request bodies
- [ ] Validate created data
- [ ] Handle validation errors

## Prerequisites
- Completed GET Requests
- Understand JSON structure

---

## POST Request Fundamentals

### Basic POST

```robotframework
*** Settings ***
Library     RequestsLibrary

*** Variables ***
${BASE_URL}    http://localhost:8000/api/v1

*** Test Cases ***
Create New Resource
    Create Session    api    ${BASE_URL}

    # Prepare data
    &{data}=    Create Dictionary
    ...    first_name=Jan
    ...    last_name=Novák
    ...    phone=+420123456789
    ...    gender=male
    ...    email=jan.novak@example.com

    # Send POST request
    ${response}=    POST On Session    api    /form/    json=${data}

    # Verify success
    Should Be Equal As Strings    ${response.status_code}    201

    # Parse response
    ${json}=    Evaluate    json.loads('${response.text}')    modules=json

    # Verify returned data
    Should Be Equal    ${json}[first_name]    Jan
    Should Be Equal    ${json}[email]        jan.novak@example.com
```

---

## Request Body Formats

### JSON Body (Recommended)

```robotframework
# Method 1: Using json parameter (auto-sets Content-Type)
&{data}=    Create Dictionary    name=Jan    email=jan@test.com
${response}=    POST On Session    api    /form/    json=${data}

# Method 2: Using data parameter with explicit headers
${body}=    Set Variable    {"name":"Jan","email":"jan@test.com"}
&{headers}=    Create Dictionary    Content-Type=application/json
${response}=    POST On Session    api    /form/    data=${body}    headers=${headers}
```

### Form Data

```robotframework
# URL-encoded form data
&{data}=    Create Dictionary    username=jan    password=secret
&{headers}=    Create Dictionary    Content-Type=application/x-www-form-urlencoded
${response}=    POST On Session    api    /login    data=${data}    headers=${headers}
```

### Multipart (File Upload)

```robotframework
# File upload
&{files}=    Create Dictionary    file=/path/to/file.pdf
&{data}=    Create Dictionary
${response}=    POST On Session    api    /upload    files=${files}    data=${data}
```

---

## Response Handling

### Created Resource (201)

```robotframework
*** Test Cases ***
Verify Created Resource
    Create Session    api    ${BASE_URL}

    &{data}=    Create Dictionary
    ...    first_name=Test
    ...    last_name=User
    ...    phone=+420123456789
    ...    gender=male
    ...    email=test.user@example.com

    ${response}=    POST On Session    api    /form/    json=${data}

    # Status should be 201 Created
    Should Be Equal As Strings    ${response.status_code}    201

    # Verify Location header (if present)
    ${headers}=    Get From Dictionary    ${response}    headers
    ${location}=    Get From Dictionary    ${headers}    Location
    Log    New resource at: ${location}

    # Parse response body
    ${json}=    Evaluate    json.loads('${response.text}')    modules=json

    # Verify all fields returned
    Should Be Equal    ${json}[first_name]    Test
    Should Be Equal    ${json}[last_name]     User
    Should Be Equal    ${json}[email]         test.user@example.com

    # Verify ID was generated
    ${id}=    Get From Dictionary    ${json}    id
    Should Not Be Empty    ${id}
    Log    Created with ID: ${id}
```

### Validation Error (400)

```robotframework
*** Test Cases ***
Handle Validation Error
    Create Session    api    ${BASE_URL}

    # Missing required field
    &{data}=    Create Dictionary
    ...    first_name=Jan
    # Missing: last_name, phone, email, gender

    ${response}=    POST On Session    api    /form/    json=${data}

    # Should get validation error
    Should Be Equal As Strings    ${response.status_code}    400

    # Parse error response
    ${json}=    Evaluate    json.loads('${response.text}')    modules=json

    # Verify error message
    ${detail}=    Get From Dictionary    ${json}    detail
    Log    Validation error: ${detail}

    Should Not Be Empty    ${detail}
```

---

## Application Examples

### Example 1: Create Form with Complete Data

```robotframework
*** Test Cases ***
Create Form With All Fields
    [Documentation]    Create form submission with all fields

    Create Session    api    ${BASE_URL}

    # Prepare complete data
    &{data}=    Create Dictionary
    ...    first_name=Petr
    ...    last_name=Svoboda
    ...    phone=+420606123456
    ...    gender=male
    ...    email=petr.svoboda@example.cz

    # Create resource
    ${response}=    POST On Session    api    /form/    json=${data}

    # Verify success
    Should Be Equal As Strings    ${response.status_code}    201

    # Parse and verify
    ${json}=    Evaluate    json.loads('${response.text}')    modules=json

    # Verify returned data matches input
    Should Be Equal    ${json}[first_name]    Petr
    Should Be Equal    ${json}[last_name]     Svoboda
    Should Be Equal    ${json}[phone]        +420606123456
    Should Be Equal       ${json}[gender]       male
    Should Be Equal    ${json}[email]         petr.svoboda@example.cz

    # Verify ID is present
    ${id}=    Set Variable    ${json}[id]
    Should Be True    ${id} > 0

    # Cleanup
    DELETE On Session    api    /form/${id}
```

### Example 2: Handle Duplicate Email

```robotframework
*** Test Cases ***
Duplicate Email Should Fail
    [Documentation]    Verify duplicate email is rejected

    Create Session    api    ${BASE_URL}

    # Create first form
    &{data}=    Create Dictionary
    ...    first_name=Jan
    ...    last_name=Novák
    ...    phone=+420123456789
    ...    gender=male
    ...    email=duplicate@example.com

    ${response1}=    POST On Session    api    /form/    json=${data}
    Should Be Equal As Strings    ${response1.status_code}    201
    Log    ✅ First form created

    # Try to create duplicate
    ${response2}=    POST On Session    api    /form/    json=${data}

    # Should fail with 400
    Should Be Equal As Strings    ${response2.status_code}    400

    # Verify error message
    ${json}=    Evaluate    json.loads('${response2.text}')    modules=json
    ${detail}=    Get From Dictionary    ${json}    detail

    Should Contain    ${detail}    exists
    Log    ✅ Duplicate correctly rejected: ${detail}
```

### Example 3: Create with Minimal Data

```robotframework
*** Test Cases ***
Create Form With Required Fields Only
    [Documentation]    Test minimal valid form data

    Create Session    api    ${BASE_URL}

    # Only required fields
    &{data}=    Create Dictionary
    ...    first_name=Min
    ...    last_name=imal
    ...    phone=+420111222333
    ...    gender=other
    ...    email=minimal@test.com

    ${response}=    POST On Session    api    /form/    json=${data}

    # Should succeed
    Should Be Equal As Strings    ${response.status_code}    201

    ${json}=    Evaluate    json.loads('${response.text}')    modules=json

    # Verify only required fields are present
    Should Be Equal    ${json}[first_name]    Min

    # Cleanup
    DELETE On Session    api    /form/${json}[id]
```

### Example 4: Test Invalid Data Types

```robotframework
*** Test Cases ***
Invalid Data Types Should Fail
    [Documentation]    Send invalid data types and verify rejection

    Create Session    api    ${BASE_URL}

    # Invalid phone (not string)
    &{data}=    Create Dictionary
    ...    first_name=Test
    ...    last_name=User
    ...    phone=123456789
    ...    gender=male
    ...    email=invalid@test.com

    ${response}=    POST On Session    api    /form/    json=${data}

    # Should fail validation
    Should Be Equal As Strings    ${response.status_code}    400

    # Verify validation error
    ${json}=    Evaluate    json.loads('${response.text}')    modules=json
    Log    Validation error: ${json}[detail]
```

---

## Data Generation

### Using FakerLibrary

```robotframework
*** Settings ***
Library     RequestsLibrary
Library     FakerLibrary

*** Test Cases ***
Create Form With Faker Data
    Create Session    api    ${BASE_URL}

    # Generate random data
    ${first_name}=    FakerLibrary.First Name
    ${last_name}=     FakerLibrary.Last Name
    ${email}=         FakerLibrary.Email
    ${phone}=         FakerLibrary.Phone Number

    # Build request data
    &{data}=    Create Dictionary
    ...    first_name=${first_name}
    ...    last_name=${last_name}
    ...    phone=${phone}
    ...    gender=male
    ...    email=${email}

    ${response}=    POST On Session    api    /form/    json=${data}

    Should Be Equal As Strings    ${response.status_code}    201
    ${json}=    Evaluate    json.loads('${response.text}')    modules=json

    # Verify data matches
    Should Be Equal    ${json}[first_name]    ${first_name}
    Should Be Equal    ${json}[email]        ${email}

    # Cleanup
    DELETE On Session    api    /form/${json}[id]
```

---

## POST Request Patterns

### Pattern 1: Create and Verify

```robotframework
*** Keywords ***
Create And Verify Form
    [Arguments]    ${session}    &{data}

    # Create
    ${response}=    POST On Session    ${session}    /form/    json=${data}
    Should Be Equal As Strings    ${response.status_code}    201

    # Parse response
    ${json}=    Evaluate    json.loads('${response.text}')    modules=json

    # Verify all fields
    FOR    ${key}    IN    @{data.keys}
        Should Be Equal    ${json}[${key}]    ${data}[${key}]
    END

    # Return ID for cleanup
    [Return]    ${json}[id]
```

### Pattern 2: Create with Retry on Duplicate

```robotframework
*** Keywords ***
Create Form With Retry
    [Arguments]    ${session}    &{data}    ${max_retries}=3

    FOR    ${i}    IN RANGE    ${max_retries}
        # Generate unique email for each attempt
        ${unique_email}=    Set Variable    user_${i}@test.com
        Set To Dictionary    ${data}    email    ${unique_email}

        ${response}=    POST On Session    ${session}    /form/    json=${data}

        # Exit on success
        Exit For Loop If    ${response.status_code} == 201

        # If not duplicate, fail immediately
        Should Not Contain    ${response.text}    exists
        ...    msg=Non-duplicate error occurred
    END

    Should Be Equal As Strings    ${response.status_code}    201
```

---

## Common Pitfalls

| Pitfall | Why It Happens | Fix |
|---------|---------------|-----|
| 400 Bad Request | Invalid/missing data | Check API validation rules |
| Duplicate key | Email already exists | Generate unique test data |
| Wrong Content-Type | Server expects JSON | Use `json=` parameter |
| Missing required fields | Schema validation failed | Include all required fields |

---

## Self-Check Questions

1. What status code indicates successful resource creation?
2. How do you send JSON in POST request?
3. What's the difference between `data=` and `json=` parameters?
4. How do you handle duplicate key errors?

---

## Exercise: POST with Validation

**Task:** Create a comprehensive POST test with validation scenarios.

**Acceptance Criteria:**
- [ ] Create form with valid data
- [ ] Test missing required field
- [ ] Test invalid email format
- [ ] Test duplicate email
- [ ] Verify appropriate error messages

**Starter Code:**
```robotframework
*** Settings ***
Library     RequestsLibrary
Library     FakerLibrary

*** Variables ***
${BASE_URL}    http://localhost:8000/api/v1

*** Test Cases ***
Test POST Validations
    [Documentation]    TODO: Implement POST validation tests
    # TODO: Your code here

*** Keywords ***
# TODO: Add helper keywords
```

---

## Hints

### Hint 1
Create separate test cases or keywords for each validation scenario.

### Hint 2
Test cases: valid data, missing field, invalid email, duplicate email.

### Hint 3
```robotframework
*** Test Cases ***
Test POST Validations
    # 1. Valid data
    Create Form With Valid Data

    # 2. Missing field
    Verify Missing Field Fails

    # 3. Invalid email
    Verify Invalid Email Fails

    # 4. Duplicate
    Verify Duplicate Email Fails
```

### Hint 4 (Full Solution)
```robotframework
*** Settings ***
Library     RequestsLibrary
Library     FakerLibrary

*** Variables ***
${BASE_URL}    http://localhost:8000/api/v1

*** Test Cases ***
Test POST Validations
    [Documentation]    Comprehensive POST validation tests
    [Tags]    beginner    exercise    post    validation

    Create Session    api    ${BASE_URL}

    # Test 1: Valid data should succeed
    ${id1}=    Create Valid Form

    # Test 2: Missing required field should fail
    Verify Missing Field Fails

    # Test 3: Invalid email format should fail
    Verify Invalid Email Fails

    # Test 4: Duplicate email should fail
    Verify Duplicate Email Fails    ${id1}

    [Teardown]    Delete All Sessions

*** Keywords ***
Create Valid Form
    [Documentation]    Creates form with valid data
    [Return]    ${form_id}

    &{data}=    Create Dictionary
    ...    first_name=Valid
    ...    last_name=Test
    ...    phone=+420123456789
    ...    gender=male
    ...    email=valid-test@example.com

    ${response}=    POST On Session    api    /form/    json=${data}

    Should Be Equal As Strings    ${response.status_code}    201

    ${json}=    Evaluate    json.loads('${response.text}')    modules=json
    ${form_id}=    Set Variable    ${json}[id]

    Log    ✅ Created form: ${form_id}
    [Return]    ${form_id}

Verify Missing Field Fails
    [Documentation]    Missing last_name should return 400

    &{data}=    Create Dictionary
    ...    first_name=NoLast
    ...    phone=+420123456789
    ...    gender=male
    ...    email=nolast@example.com

    ${response}=    POST On Session    api    /form/    json=${data}

    Should Be Equal As Strings    ${response.status_code}    400

    ${json}=    Evaluate    json.loads('${response.text}')    modules=json
    Log    ✅ Correctly rejected: ${json}[detail]

Verify Invalid Email Fails
    [Documentation]    Invalid email format should return 400

    &{data}=    Create Dictionary
    ...    first_name=Bad
    ...    last_name=Email
    ...    phone=+420123456789
    ...    gender=male
    ...    email=not-an-email

    ${response}=    POST On Session    api    /form/    json=${data}

    Should Be Equal As Strings    ${response.status_code}    400

    ${json}=    Evaluate    json.loads('${response.text}')    modules=json
    Log    ✅ Correctly rejected invalid email

Verify Duplicate Email Fails
    [Arguments]    ${existing_id}

    [Documentation]    Duplicate email should return 400

    # Get existing form's data
    ${get_resp}=    GET On Session    api    /form/${existing_id}
    ${existing}=    Evaluate    json.loads('${get_resp.text}')    modules=json

    # Try to create with same email
    &{data}=    Create Dictionary
    ...    first_name=Dup
    ...    last_name=licate
    ...    phone=+420999999999
    ...    gender=female
    ...    email=${existing}[email]

    ${response}=    POST On Session    api    /form/    json=${data}

    Should Be Equal As Strings    ${response.status_code}    400

    ${json}=    Evaluate    json.loads('${response.text}')    modules=json
    Should Contain    ${json}[detail]    exists
    Log    ✅ Correctly rejected duplicate email
```

---

## References

- [HTTP POST Method](https://developer.mozilla.org/en-US/docs/Web/HTTP/Methods/POST)
- [JSON Syntax](https://www.json.org/)
- Project: `/RF/API/tests/create_form.robot`
- Backend validation: `/be/app/api/endpoints/form_data.py`
