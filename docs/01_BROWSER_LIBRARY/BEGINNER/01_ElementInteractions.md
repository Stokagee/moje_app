# Element Interactions

## Learning Objectives
- [ ] Find elements using selectors
- [ ] Interact with form elements
- [ ] Click buttons and links
- [ ] Type text into inputs

## Prerequisites
- Completed Browser Basics
- Know how to open browser and navigate

---

## Finding Elements

### Selectors

Browser Library supports **multiple selector strategies**:

```robotframework
# CSS Selector (recommended)
Get Element    [data-testid="firstName-input"]
Get Element    .submit-button
Get Element    #email-input
Get Element    input[name="email"]

# XPath
Get Element    //button[@type="submit"]
Get Element    //input[contains(@placeholder, "Email")]

# Text Content
Get Element    "Submit"
Get Element    "Submit" >> nth=0    # Multiple matches

# Combined
Get Element    [data-testid="form"] >> "Submit"
```

### data-testid (Best Practice)

```robotframework
# Most reliable - doesn't change with CSS/JS refactoring
Fill Text    [data-testid="firstName-input"]    Jan
Click        [data-testid="submitButton"]
```

**Why data-testid?**
- Stable across UI changes
- Semantic naming
- Easy to search
- Team convention

---

## Text Input

### Fill Text

```robotframework
# Simple text input
Fill Text    [data-testid="firstName-input"]    Jan

# Clear and type
Fill Text    [data-testid="email-input"]    jan@example.com    clear=True

# Slow typing (for debugging)
Fill Text    [data-testid="phone-input"]    +420123456789    delay=100ms
```

### Type Text

```robotframework
# Append to existing text
Type Text    [data-testid="instructions"]    Some additional text

# Type into specific field
Type Text    textarea    Instructions here    clear=True
```

**Fill Text vs Type Text:**
| Keyword | Clears Field | Use Case |
|---------|--------------|----------|
| `Fill Text` | Yes (default) | Most form inputs |
| `Type Text` | No | Append text, chat interfaces |

---

## Clicking Elements

### Click

```robotframework
# Simple click
Click    [data-testid="submitButton"]

# Click with force (bypass visibility checks)
Click    [data-testid="hidden-button"]    force=True

# Click with specific button
Click    [data-testid="submit-button"]    button=right

# Double click
Click    [data-testid="item"]    clickCount=2
```

### Click with Modifiers

```robotframework
# Ctrl+Click
Click    [data-testid="item"]    modifiers=Control

# Shift+Click
Click    [data-testid="item"]    modifiers=Shift

# Multiple modifiers
Click    [data-testid="item"]    modifiers=Control+Shift
```

---

## Dropdowns and Selects

### Native Select

```robotframework
# Select by value
Select Options By    [data-testid="country-select"]    value     CZ

# Select by label
Select Options By    [data-testid="country-select"]    label     Czech Republic

# Select by index
Select Options By    [data-testid="country-select"]    index     0

# Multiple selection
Select Options By    [data-testid="tags-select"]    label     Tag1    Tag2    Tag3
```

### Custom Dropdown (Like Gender Picker)

```robotframework
# Open dropdown
Click    [data-testid="genderPicker"]

# Select option
Click    [data-testid="gender-option-male"]

# Verify selection
Get Text    [data-testid="genderPicker"]    ==    Male
```

---

## Checkboxes and Radio Buttons

### Checkbox

```robotframework
# Check checkbox
Check Checkbox    [data-testid="agree-terms"]

# Uncheck
Uncheck Checkbox    [data-testid="newsletter"]

# Verify state
Checkbox Should Be Selected    [data-testid="agree-terms"]

# Toggle (check if unchecked, uncheck if checked)
${is_checked}=    Get Checkbox State    [data-testid="agree-terms"]
IF    not ${is_checked}
    Check Checkbox    [data-testid="agree-terms"]
END
```

### Radio Button

```robotframework
# Select radio option
Click    [data-testid="gender-option-male"]

# Verify selection
Radio Button Should Be Set To    gender    male
```

---

## File Upload

### Upload File

```robotframework
# Simple upload
Upload File    [data-testid="file-uploader-dropzone"]    /path/to/file.txt

# Upload with confirmation
Upload File    [data-testid="file-upload"]    /path/to/file.pdf
```

**For base64 uploads (API-based):**
```robotframework
*** Keywords ***
Upload File Via API
    [Arguments]    ${file_path}    ${form_id}

    ${file_content}=    Get File    ${file_path}
    ${base64}=    Evaluate    base64.b64encode(${file_content}).decode('utf-8')    modules=base64

    &{data}=    Create Dictionary
    ...    filename=${file_name}
    ...    content_type=application/pdf
    ...    data_base64=${base64}

    POST On Session    api    /form/${form_id}/attachment    json=${data}
```

---

## Getting Element Information

### Get Text

```robotframework
# Get visible text
${text}=    Get Text    [data-testid="page2Title"]
Log    Page title: ${text}

# Assertion with Get Text
Get Text    [data-testid="success-message"]    ==    Form submitted successfully

# Contains text
Get Text    [data-testid="page-title"]    $=    Form
```

### Get Property

```robotframework
# Get attribute value
${href}=    Get Property    [data-testid="link"]    href
${class}=    Get Property    [data-testid="button"]    class

# Get input value
${value}=    Get Property    [data-testid="email-input"]    value
```

### Get Element Count

```robotframework
# Count matching elements
${count}=    Get Element Count    [data-testid^="list-item-"]
IF    ${count} > 0
    Log    Found ${count} items
ELSE
    Log    List is empty
END
```

### Get Element States

```robotframework
# Check if element exists
${exists}=    Get Element States    [data-testid="modal"]
    ...    contain    visible
    ...    contain    attached

# Check multiple states
${states}=    Get Element States    [data-testid="button"]
IF    "visible" in ${states} and "enabled" in ${states}
    Click    [data-testid="button"]
END
```

---

## Application Example: Fill Form

```robotframework
*** Settings ***
Library     Browser

*** Variables ***
${URL}       http://localhost:8081

*** Test Cases ***
Fill Form Successfully
    [Documentation]    Fills all form fields and submits
    [Tags]    beginner    form

    New Browser    chromium    headless=False
    New Context
    New Page       ${URL}

    # Wait for form to load
    Wait For Elements State    [data-testid="form-page-container"]    visible

    # Fill personal information
    Fill Text    [data-testid="firstName-input"]    Jan
    Fill Text    [data-testid="lastName-input"]     Novák
    Fill Text    [data-testid="phone-input"]        +420123456789
    Fill Text    [data-testid="email-input"]        jan.novak@test.cz

    # Select gender
    Click    [data-testid="genderPicker"]
    Wait For Elements State    [data-testid="gender-option-male"]    visible
    Click    [data-testid="gender-option-male"]

    # Add optional instructions
    Fill Text    [data-testid="instructions-textarea"]    Test instructions

    # Submit form
    Click    [data-testid="submitButton"]

    # Verify success modal
    Wait For Elements State    [data-testid="formSuccessModal"]    visible    timeout=10s

    [Teardown]    Close Browser
```

---

## Common Pitfalls

| Pitfall | Why It Happens | How to Avoid |
|---------|---------------|--------------|
| Element not found | Element not in DOM yet | Use `Wait For Elements State` first |
| Element not clickable | Covered by another element | Scroll into view or use `force=True` |
| Text input doesn't work | Input is disabled | Check `enabled` state first |
| Wrong element clicked | Multiple matches | Use `>> nth=N` or unique selector |

---

## Best Practices

1. **Always wait for element before interaction:**
   ```robotframework
   Wait For Elements State    ${selector}    visible    enabled
   Fill Text    ${selector}    ${text}
   ```

2. **Use data-testid selectors:**
   ```robotframework
   # Good - stable
   [data-testid="firstName-input"]

   # Avoid - can break
   .form-input:first-child
   ```

3. **Chain selectors for specificity:**
   ```robotframework
   # Clear and specific
   [data-testid="form"] >> [data-testid="submit-button"]
   ```

4. **Handle dynamic elements:**
   ```robotframework
   # Dynamic ID - use partial match
   [data-testid^="list-item-"][data-testid$="-name"]
   ```

---

## Self-Check Questions

1. What's the recommended selector strategy for stable tests?
2. How do you select an option from a custom dropdown?
3. What's the difference between `Fill Text` and `Type Text`?
4. How do you check if an element is visible before clicking?

---

## Exercise: Complete Form Workflow

**Task:** Create a test that fills the form with Faker data and verifies success.

**Acceptance Criteria:**
- [ ] Generate random test data using FakerLibrary
- [ ] Fill all required fields
- [ ] Select gender randomly
- [ ] Submit form
- [ ] Verify success modal appears
- [ ] Take screenshot on success

**Starter Code:**
```robotframework
*** Settings ***
Library     Browser
Library     FakerLibrary

*** Variables ***
${URL}       http://localhost:8081

*** Test Cases ***
Submit Form With Random Data
    [Documentation]    TODO: Implement form submission
    [Tags]    beginner    exercise

    # TODO: Generate data, fill form, verify success

*** Keywords ***
# TODO: Add helper keywords
```

---

## Hints

### Hint 1
You need to use `FakerLibrary` to generate random names, email, and phone.

### Hint 2
Required fields are: first_name, last_name, phone, email, gender.

### Hint 3
Structure:
1. Generate fake data
2. Open browser and navigate
3. Fill each field
4. Select gender (open picker, then click option)
5. Click submit
6. Wait for success modal

### Hint 4
```robotframework
*** Test Cases ***
Submit Form With Random Data
    ${first_name}=    FakerLibrary.First Name
    ${last_name}=     FakerLibrary.Last Name
    ${phone}=         FakerLibrary.Phone Number
    ${email}=         FakerLibrary.Email

    New Browser    chromium    headless=False
    New Context
    New Page       ${URL}

    Fill Text    [data-testid="firstName-input"]    ${first_name}
    # TODO: Complete the rest
```

### Hint 5 (Full Solution)
```robotframework
*** Settings ***
Library     Browser
Library     FakerLibrary

*** Variables ***
${URL}       http://localhost:8081

*** Test Cases ***
Submit Form With Random Data
    [Documentation]    Fills form with random data and verifies success
    [Tags]    beginner    exercise    form

    # Generate test data
    ${first_name}=    FakerLibrary.First Name
    ${last_name}=     FakerLibrary.Last Name
    ${phone}=         FakerLibrary.Phone Number
    ${email}=         FakerLibrary.Email

    # Generate random gender (0=male, 1=female, 2=other)
    ${gender_index}=    Evaluate    random.randint(0, 2)    modules=random
    @{genders}=        Create List    male    female    other

    Log    Creating form for: ${first_name} ${last_name} (${email})

    # Setup browser
    New Browser    chromium    headless=False
    New Context
    New Page       ${URL}

    # Wait for form to load
    Wait For Elements State    [data-testid="form-page-container"]    visible

    # Fill required fields
    Fill Text    [data-testid="firstName-input"]    ${first_name}
    Fill Text    [data-testid="lastName-input"]     ${last_name}
    Fill Text    [data-testid="phone-input"]        ${phone}
    Fill Text    [data-testid="email-input"]        ${email}

    # Select gender
    Click    [data-testid="genderPicker"]
    Wait For Elements State    [data-testid="gender-option-${genders}[${gender_index}]]"]    visible
    Click    [data-testid="gender-option-${genders}[${gender_index}]]"]

    # Submit form
    Click    [data-testid="submitButton"]

    # Verify success modal appears
    Wait For Elements State    [data-testid="formSuccessModal"]    visible    timeout=10s

    # Take screenshot for verification
    Take Screenshot    filename=form_success_${email}.png

    [Teardown]    Close Browser
```

---

## Common Mistakes

| Mistake | Why It's Wrong | Fix |
|---------|---------------|-----|
| Not waiting for dropdown | Options not visible yet | Add `Wait For Elements State` after clicking picker |
| Using wrong phone format | Phone validation fails | Faker may give wrong format - use `+420` prefix |
| Wrong testID syntax | Element not found | Must use `[data-testid="..."]` format |

---

## References

- [Browser Library - Interactions](https://marketsquare.github.io/robotframework-browser/Browser.html#Input%20Text)
- Application Form: `/fe/mojeApp/src/component/pages/FormPage.js`
- Form Locators: `/RF/UI/locators/form_page_locators.resource`
- Example Test: `/RF/UI/tests/new_form.robot`
