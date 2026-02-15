# Data-Driven Testing

## Learning Objectives
- [ ] Understand data-driven testing concepts
- [ ] Use external data files
- [ ] Parameterize test cases
- [ ] Handle multiple data sets

## Prerequisites
- Completed BEGINNER topics for all libraries
- Understand basic test structure

---

## What is Data-Driven Testing?

**Data-driven testing (DDT)** separates test logic from test data.

**Benefits:**
- Test same logic with multiple data sets
- Easy to add new test cases
- Data maintained separately from tests
- Reusable test templates

**Without DDT:**
```robotframework
*** Test Cases ***
Test Login Valid User
    # Test with specific data
    Login    valid@example.com    password123

Test Login Invalid User
    # Duplicate logic with different data
    Login    invalid@example.com    wrongpass
```

**With DDT:**
```robotframework
*** Test Cases ***
Test Login
    [Documentation]    Login with multiple accounts
    [Template]    Login
    ...    ${email}    ${password}
    ...    valid@example.com    password123
    ...    invalid@example.com    wrongpass
```

---

## Test Templates

### Basic Template

```robotframework
*** Settings ***
Library     Browser

*** Variables ***
${URL}       http://localhost:8081

*** Test Cases ***
Fill Form With Data
    [Documentation]    Fill form using data-driven approach
    [Template]    Fill Form Template
    ...    ${first_name}    ${last_name}    ${email}
    ...    Jan    Novák    jan@test.com
    ...    Petr    Svoboda    petr@test.com
    ...    Marie    Dvořáková    marie@test.com

*** Keywords ***
Fill Form Template
    [Arguments]    ${first_name}    ${last_name}    ${email}

    New Page    ${URL}

    Fill Text    [data-testid="firstName-input"]    ${first_name}
    Fill Text    [data-testid="lastName-input"]     ${last_name}
    Fill Text    [data-testid="email-input"]        ${email}
    Fill Text    [data-testid="phone-input"]        +420123456789

    Select Gender    male
    Click    [data-testid="submitButton"]

    Wait For Elements State    [data-testid="formSuccessModal"]    visible

    [Teardown]    Close Browser
```

---

## External Data Files

### CSV Data File

```csv
# testdata.csv
first_name,last_name,email,phone
Jan,Novák,jan@test.com,+420111222333
Petr,Svoboda,petr@test.com,+420444555666
Marie,Dvořáková,marie@test.com,+420777888999
```

### JSON Data File

```json
[
    {
        "first_name": "Jan",
        "last_name": "Novák",
        "email": "jan@test.com",
        "phone": "+420111222333"
    },
    {
        "first_name": "Petr",
        "last_name": "Svoboda",
        "email": "petr@test.com",
        "phone": "+420444555666"
    }
]
```

### YAML Data File

```yaml
# testdata.yaml
- first_name: Jan
  last_name: Novák
  email: jan@test.com
  phone: "+420111222333"

- first_name: Petr
  last_name: Svoboda
  email: petr@test.com
  phone: "+420444555666"
```

---

## Reading Data Files

### CSV with CSVLibrary

```robotframework
*** Settings ***
Library     CSVLibrary

*** Variables ***
${DATA_FILE}    testdata.csv

*** Test Cases ***
Test With CSV Data
    ${test_data}=    Read File As CSV    ${DATA_FILE}

    FOR    ${row}    IN    @{test_data}
        Log    First: ${row}[0]    Last: ${row}[1]
        Run Keyword    Test Form Submission
        ...    ${row}[0]    ${row}[1]    ${row}[2]    ${row}[3]
    END
```

### JSON with JSONLibrary

```robotframework
*** Settings ***
Library     JSONLibrary

*** Variables ***
${DATA_FILE}    testdata.json

*** Test Cases ***
Test With JSON Data
    ${json_data}=    Load Json From File    ${DATA_FILE}

    FOR    ${item}    IN    @{json_data}
        Log    Testing: ${item}[first_name] ${item}[last_name]
        Run Keyword    Test Form Submission
        ...    ${item}[first_name]    ${item}[last_name]    ${item}[email]    ${item}[phone]
    END
```

### Using FakerLibrary

```robotframework
*** Settings ***
Library     FakerLibrary

*** Test Cases ***
Generate Random Test Data
    [Documentation]    Use Faker to generate multiple test datasets

    # Generate 5 random test datasets
    FOR    ${i}    IN RANGE    5
        ${first_name}=    FakerLibrary.First Name
        ${last_name}=     FakerLibrary.Last Name
        ${email}=         FakerLibrary.Email
        ${phone}=         FakerLibrary.Phone Number

        Log    Test ${i}: ${first_name} ${last_name}

        Run Keyword    Test Form Submission
        ...    ${first_name}    ${last_name}    ${email}    ${phone}
    END
```

---

## Application Examples

### Example 1: API Testing with Data

```robotframework
*** Settings ***
Library     RequestsLibrary
Library     JSONLibrary

*** Variables ***
${BASE_URL}    http://localhost:8000/api/v1
${DATA_FILE}    testdata.json

*** Test Cases ***
Create Multiple Forms From JSON
    [Documentation]    Create forms from external JSON file

    ${test_data}=    Load Json From File    ${DATA_FILE}

    Create Session    api    ${BASE_URL}

    FOR    ${item}    IN    @{test_data}
        Log    Creating form: ${item}[first_name] ${item}[last_name]

        &{data}=    Create Dictionary
        ...    first_name=${item}[first_name]
        ...    last_name=${item}[last_name]
        ...    phone=${item}[phone]
        ...    gender=male
        ...    email=${item}[email]

        ${response}=    POST On Session    api    /form/    json=${data}

        Should Be Equal As Strings    ${response.status_code}    201

        ${json}=    Evaluate    json.loads('${response.text}')    modules=json
        Log    ✅ Created form ID: ${json}[id]
    END
```

### Example 2: Dynamic Data Generation

```robotframework
*** Settings ***
Library     Browser
Library     FakerLibrary

*** Test Cases ***
Test With Generated Data
    [Documentation]    Generate test data on the fly

    ${test_count}=    Set Variable    3

    FOR    ${i}    IN RANGE    ${test_count}
        # Generate unique data
        ${first_name}=    FakerLibrary.First Name
        ${last_name}=     FakerLibrary.Last Name
        ${email}=         FakerLibrary.Email
        ${phone}=         FakerLibrary.Phone Number

        # Add unique suffix
        ${unique_email}=    Set Variable    test${i}_${email}

        Log    Test iteration ${i}: ${unique_email}

        Run Keyword    Submit Form With Data
        ...    ${first_name}    ${last_name}    ${unique_email}    ${phone}
    END
```

### Example 3: Boundary Testing

```robotframework
*** Test Cases ***
Boundary Testing Phone Length
    [Documentation]    Test phone number length validation

    # Valid phone numbers
    @{valid_phones}=    Create List
    ...    +420123456    # Too short - should fail
    ...    +420123456789012345    # Valid
    ...    +42012345678901234567890    # Too long - should fail

    FOR    ${phone}    IN    @{valid_phones}
        Log    Testing phone: ${phone} (${phone.__len__} chars)

        # Should handle gracefully
        ${result}=    Run Keyword And Ignore Error
        ...    Submit Form With Phone    ${phone}

        Log    Result: ${result}[status]
    END
```

---

## Data Patterns

### Smoke Test Data

```robotframework
*** Variables ***
# Minimal valid data for quick smoke tests
${SMOKE_FIRST}=    Test
${SMOKE_LAST}=     User
${SMOKE_EMAIL}=    smoke@test.com
${SMOKE_PHONE}=    +420123456789
```

### Edge Cases

```robotframework
*** Test Cases ***
Test Edge Cases
    [Documentation]    Test boundary conditions

    # Empty strings
    Run Keyword    Test Form Field    first_name    ${EMPTY}

    # Very long strings
    ${long_string}=    Generate Random String    1000
    Run Keyword    Test Form Field    first_name    ${long_string}

    # Special characters
    Run Keyword    Test Form Field    first_name    Jan-Pavel
    Run Keyword    Test Form Field    last_name     Dvořáková

    # Unicode characters
    Run Keyword    Test Form Field    first_name    我愛
    Run Keyword    Test Form Field    last_name     François
```

---

## Self-Check Questions

1. What's the benefit of data-driven testing?
2. How do you use Test Templates?
3. What file formats can store test data?
4. How do you generate random test data?

---

## Exercise: Data-Driven Form Tests

**Task:** Create data-driven form tests using external JSON data.

**Scenario:**
1. Create JSON file with test data
2. Read JSON in test
3. Submit forms for each dataset
4. Verify each submission

**Acceptance Criteria:**
- [ ] External JSON data file created
- [ ] JSON loaded in test
- [ ] Multiple datasets tested
- [ ] Results logged

**Starter Code:**
```robotframework
*** Settings ***
Library     Browser
Library     JSONLibrary

*** Variables ***
${URL}       http://localhost:8081
${DATA_FILE}    form_data.json

*** Test Cases ***
DataDriven Form Tests
    [Documentation]    TODO: Implement DDT
    # TODO: Your code here

*** Keywords ***
# TODO: Add helper keywords
```

---

## References

- [Robot Framework Data-Driven Testing](https://robotframework.org/robotframework/latest/RobotFrameworkUserGuide.html#data-driven-testing)
- [CSVLibrary](https://github.com/seleniumlibrary/CSVLibrary)
- [JSONLibrary](https://github.com/robotframework-thirdparty/robotframework-jsonlibrary)
- Project examples: `/RF/API/tests/`
