# Your First Robot Framework Test

## Learning Objectives
- [ ] Understand basic Robot Framework syntax
- [ ] Write a simple test
- [ ] Run and interpret results
- [ ] Use basic Browser Library keywords

## Prerequisites
- Completed installation guide
- Active virtual environment
- Browser Library installed

---

## Robot Framework Syntax Overview

### File Structure

```robotframework
*** Settings ***        # Import libraries, set metadata
*** Variables ***       # Define variables
*** Test Cases ***      # Define test cases
*** Keywords ***        # Define custom keywords
```

### Basic Elements

**Settings Section:**
```robotframework
*** Settings ***
Library     Browser        # Import library
Documentation    A simple test suite    # Suite documentation
```

**Test Cases Section:**
```robotframework
*** Test Cases ***
My First Test
    [Documentation]    This test does something simple
    Log    Hello, Robot Framework!
```

**Comments:**
```robotframework
# This is a comment
Log    Something    # Inline comment
```

---

## Writing Your First Test

### Exercise: Simple Browser Test

Create file `my_first_test.robot`:

```robotframework
*** Settings ***
Library     Browser

*** Variables ***
${URL}       https://example.com

*** Test Cases ***
Open Example Website
    [Documentation]    Opens a website and checks title
    [Tags]    beginner    smoke

    New Page    ${URL}
    Get Title    ==    Example Domain

    Take Screenshot
```

**Breakdown:**
| Line | Meaning |
|------|---------|
| `Library     Browser` | Import Browser Library for UI automation |
| `${URL}` | Variable definition |
| `New Page    ${URL}` | Opens URL in browser |
| `Get Title    ==    ...` | Assertion: title must equal "Example Domain" |
| `Take Screenshot` | Captures screenshot for debugging |

---

## Running Your Test

### Basic Run

```bash
robot my_first_test.robot
```

**Output:**
```
==============================================================================
My First Test
==============================================================================
Open Example Website                                                    | PASS |
------------------------------------------------------------------------------
My First Test                                                           | PASS |
1 test, 1 passed, 0 failed
==============================================================================
```

### Run with Specific Browser

```bash
robot --variable BROWSER:firefox my_first_test.robot
```

### Run with Output Options

```bash
# Detailed output
robot --loglevel DEBUG my_first_test.robot

# Don't create log files
robot --outputdir /tmp my_first_test.robot

# Run specific test
robot --test "Open Example Website" my_first_test.robot
```

---

## Understanding Test Results

After running, Robot Framework creates:

1. **log.html** - Detailed execution log
2. **report.html** - Summary report
3. **output.xml** - Machine-readable results

Open `log.html` in your browser to see:
- Each test step with timing
- Screenshot links (if taken)
- Error messages (if failed)

---

## Test Against Real Application

Let's write a test for our application:

Create `first_app_test.robot`:

```robotframework
*** Settings ***
Library     Browser

*** Variables ***
${URL}       http://localhost:8081

*** Test Cases ***
Navigate To Application
    [Documentation]    Opens the app and checks navigation

    New Page    ${URL}

    # Wait for page to load
    Wait For Elements State    [data-testid="form-page-container"]    visible

    # Check we're on the right page
    Get Title    *=    moj

    Take Screenshot    filename=app_home.png

Verify Form Elements Exist
    [Documentation]    Checks form inputs are present

    New Page    ${URL}

    # Verify form fields exist
    Get Element    [data-testid="firstName-input"]
    Get Element    [data-testid="lastName-input"]
    Get Element    [data-testid="email-input"]
    Get Element    [data-testid="phone-input"]
    Get Element    [data-testid="genderPicker"]
    Get Element    [data-testid="submitButton"]

    Log    All form elements found!    level=INFO
```

**New Keywords Used:**

| Keyword | Purpose |
|---------|---------|
| `Wait For Elements State` | Waits for element to reach specified state |
| `Get Element` | Verifies element exists (fails if not found) |
| `Get Title    *=    moj` | Partial match: title contains "moj" |

---

## Common Syntax Errors

| Error | Cause | Fix |
|-------|-------|-----|
| `Variable '${URL}' not found` | Missing variable definition | Add to `*** Variables ***` section |
| `No keyword with name 'NewPage'` | Wrong separator | Use `New Page` (with space) |
| `Library 'Browser' not found` | Library not imported | Add `Library    Browser` in Settings |
| `Test case failed: Expected == but got` | Assertion failed | Fix expected value or code |

---

## Best Practices

1. **Always use documentation:**
   ```robotframework
   [Documentation]    Clear description of what test does
   ```

2. **Use tags for organization:**
   ```robotframework
   [Tags]    smoke    regression    form
   ```

3. **Take screenshots for debugging:**
   ```robotframework
   Take Screenshot    filename=descriptive_name.png
   ```

4. **Log meaningful messages:**
   ```robotframework
   Log    User created successfully: ${user_id}    level=INFO
   ```

---

## Self-Check Questions

1. What are the four main sections of a Robot Framework file?
2. How do you import a library?
3. What's the difference between `==` and `*=` in assertions?
4. What files are created after running a test?

---

## Exercise: Extend the Test

Try adding to `first_app_test.robot`:

```robotframework
Fill And Submit Form
    [Documentation]    Fills form with test data

    New Page    ${URL}

    # Fill form fields
    Fill Text    [data-testid="firstName-input"]    Jan
    Fill Text    [data-testid="lastName-input"]     Novák
    Fill Text    [data-testid="phone-input"]        +420123456789
    Fill Text    [data-testid="email-input"]        jan@test.cz

    # Select gender
    Click    [data-testid="genderPicker"]
    Click    [data-testid="gender-option-male"]

    # Submit
    Click    [data-testid="submitButton"]

    # Verify success
    Wait For Elements State    [data-testid="formSuccessModal"]    visible
```

Run it and see what happens!

---

## References

- [Robot Framework User Guide - Syntax](https://robotframework.org/robotframework/latest/RobotFrameworkUserGuide.html#executing-test-cases)
- [Browser Library Keywords](https://marketsquare.github.io/robotframework-browser/Browser.html)
- Application UI: `/fe/mojeApp/src/component/pages/FormPage.js`
- Example test: `/RF/UI/tests/new_form.robot`
