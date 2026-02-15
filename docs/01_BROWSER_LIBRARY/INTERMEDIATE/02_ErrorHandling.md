# Error Handling and Debugging

## Learning Objectives
- [ ] Handle test failures gracefully
- [ ] Use TRY-EXCEPT patterns
- [ ] Take screenshots on failure
- [ ] Debug browser tests effectively

## Prerequisites
- Completed BEGINNER topics
- Know basic test writing

---

## Why Error Handling Matters

**Without error handling:**
- Tests fail with cryptic messages
- No debugging information
- Hard to reproduce issues
- Lost context when failures occur

**With error handling:**
- Clear failure messages
- Screenshots for debugging
- Detailed error context
- Graceful degradation

---

## TRY-EXCEPT Pattern

### Basic Structure

```robotframework
*** Keywords ***
Safe Click
    [Arguments]    ${selector}

    TRY
        Wait For Elements State    ${selector}    visible    enabled
        Click    ${selector}
    EXCEPT    AS    ${err}
        Log    Click failed: ${err}    level=ERROR
        Take Screenshot
        Fail    Could not click element: ${selector}
    END
```

### Multiple Exception Types

```robotframework
*** Keywords ***
Handle Multiple Errors
    [Arguments]    ${selector}

    TRY
        Wait For Elements State    ${selector}    visible    enabled
        Click    ${selector}
    EXCEPT    AS    ${err}
        # Check error type
        IF    "TimeoutError" in """${err}"""
            Log    Element not found in time    level=WARN
            Take Screenshot    filename=timeout_error.png
        ELSE IF    "ElementClickInterceptedError" in """${err}"""
            Log    Element covered by another element    level=WARN
            Take Screenshot    filename=intercepted_error.png
        ELSE
            Log    Unknown error: ${err}    level=ERROR
            Take Screenshot    filename=unknown_error.png
        END
        Fail    Operation failed: ${err}
    END
```

---

## Application Example: Enhanced Keywords

### From `/RF/UI/common.resource`:

```robotframework
*** Settings ***
Library     Browser
Library     Collections

*** Keywords ***
Click On The Element
    [Documentation]    Enhanced click with comprehensive error handling
    [Arguments]    ${locator}    ${context_name}=${EMPTY}

    # Default context name if not provided
    ${context}=    Set Variable If    '${context_name}' == ${EMPTY}    element    ${context_name}

    TRY
        # Verify element exists and is ready for interaction
        Wait For Elements State    ${locator}    attached    timeout=${TIMEOUT}
        Wait For Elements State    ${locator}    visible     timeout=${TIMEOUT}
        Wait For Elements State    ${locator}    enabled     timeout=${TIMEOUT}

        # Perform the click
        Click    ${locator}

        Log    ✅ Successfully clicked on '${context}' | selector='${locator}'    level=INFO

    EXCEPT    AS    ${err}
        # Capture failure state
        Take Screenshot    filename=click_failure_${context}.png

        # Build detailed error message
        ${msg}=    Set Variable    ❌ Failed to click '${context}' | selector='${locator}' | ERROR: ${err}

        # Log error and fail test
        Log    ${msg}    level=ERROR
        Fail    ${msg}
    END
```

### Fill Text with Error Handling

```robotframework
Fill Text In Input Field
    [Documentation]    Enhanced text input with validation and error handling
    [Arguments]    ${locator}    ${text}    ${context_name}=${EMPTY}

    ${context}=    Set Variable If    '${context_name}' == ${EMPTY}    field    ${context_name}

    TRY
        # Wait for field to be ready
        Wait For Elements State    ${locator}    attached    visible    enabled    editable    timeout=${TIMEOUT}

        # Fill the field
        Fill Text    ${locator}    ${text}

        # Verify value was set
        ${actual_value}=    Get Property    ${locator}    value
        IF    ${actual_value} != ${text}
            Fail    Value mismatch: expected '${text}' but got '${actual_value}'
        END

        Log    ✅ Filled '${context}' with: ${text}    level=INFO

    EXCEPT    AS    ${err}
        Take Screenshot    filename=fill_failure_${context}.png
        ${msg}=    Set Variable    ❌ Failed to fill '${context}' | selector='${locator}' | text='${text}' | ERROR: ${err}
        Log    ${msg}    level=ERROR
        Fail    ${msg}
    END
```

---

## Screenshot Strategies

### Automatic on Failure

```robotframework
*** Settings ***
Suite Teardown    Run Keyword If Test Failed    Take Screenshot

*** Test Cases ***
Test That Might Fail
    # Test steps here
    # If it fails, screenshot is taken automatically
```

### Conditional Screenshots

```robotframework
*** Keywords ***
Take Screenshot If Failed
    [Arguments]    ${condition}    ${filename}=screenshot.png

    IF    ${condition}
        Take Screenshot    filename=${filename}
        Log    Screenshot saved: ${filename}
    END
```

### Named Screenshots

```robotframework
# After key actions
Take Screenshot    filename=after_form_fill.png

# On failure with context
Take Screenshot    filename=error_submitting_form_for_${email}.png

# Full page screenshot
Take Screenshot    filename=full_page.png    fullPage=True
```

### Screenshot of Specific Element

```robotframework
# Screenshot just the modal
Take Screenshot    selector=[data-testid="modal"]    filename=modal.png

# Screenshot specific list item
${item}=    Get Element    [data-testid^="list-item-"] >> nth=0
Take Screenshot    selector=${item}    filename=first_item.png
```

---

## Debugging Techniques

### Enable Tracing

```robotframework
*** Test Cases ***
Debug Test With Tracing
    # Enable tracing (creates trace.zip)
    New Browser    chromium    headless=False    tracing=on

    # ... test steps ...

    [Teardown]
    ...    Close Browser
    ...    # trace.zip created for inspection
```

### Inspect Element States

```robotframework
*** Keywords ***
Debug Element State
    [Arguments]    ${selector}

    ${exists}=    Run Keyword And Return Status
    ...    Get Element    ${selector}

    IF    not ${exists}
        Log    Element not found: ${selector}    level=ERROR
        RETURN
    END

    ${states}=    Get Element States    ${selector}
    Log    Element states: ${states}

    # Check individual states
    FOR    ${state}    IN    @{states}
        Log    State: ${state}    level=DEBUG
    END

    # Get element info
    ${visible}=    Evaluate    "visible" in """${states}"""
    ${enabled}=    Evaluate    "enabled" in """${states}"""
    ${attached}=    Evaluate    "attached" in """${states}"""

    Log    Visible: ${visible} | Enabled: ${enabled} | Attached: ${attached}
```

### Step-by-Step Debugging

```robotframework
*** Test Cases ***
Debug Step By Step
    New Browser    chromium    headless=False    slowMo=1000
    New Context
    New Page    http://localhost:8081

    # Each step delayed by 1 second for visual debugging
    Fill Text    [data-testid="firstName-input"]    Debug
    # Watch what happens...
    Fill Text    [data-testid="lastName-input"]     User
    # Continue...
```

### Pause Execution

```robotframework
*** Keywords ***
Pause For Debugging
    [Documentation]    Pauses execution - useful for inspecting state
    [Arguments]    ${message}=Paused for inspection

    Log    ${message} - Press Enter to continue...    level=WARN
    Pause Execution    # Requires user input to continue
```

---

## Common Error Patterns

### Pattern 1: Element Not Found

```robotframework
*** Keywords ***
Wait For Element Or Fail
    [Arguments]    ${selector}    ${timeout}=10s

    TRY
        Wait For Elements State    ${selector}    attached    timeout=${timeout}
    EXCEPT    AS    ${err}
        Take Screenshot    filename=element_not_found.png
        Log    Element not found: ${selector}    level=ERROR

        # Check if similar elements exist
        ${similar}=    Get Element Count    //*[contains(@data-testid, "${selector}")]
        Log    Found ${similar} similar elements    level=INFO

        Fail    Element not found within ${timeout}: ${selector}
    END
```

### Pattern 2: Timeout Errors

```robotframework
*** Keywords ***
Wait With Retry
    [Arguments]    ${selector}    ${state}=visible    ${max_retries}=3    ${timeout}=5s

    FOR    ${i}    IN RANGE    ${max_retries}
        ${result}=    Run Keyword And Ignore Error
        ...    Wait For Elements State    ${selector}    ${state}    timeout=${timeout}

        Exit For Loop If    '${result}[status]' == 'PASS'

        Log    Retry ${i+1}/${max_retries} for ${selector}    level=WARN
        Sleep    1s
    END

    IF    '${result}[status]' == 'FAIL'
        Take Screenshot    filename=timeout_after_${max_retries}_retries.png
        Fail    Element did not reach state '${state}' after ${max_retries} retries
    END
```

### Pattern 3: Validation Errors

```robotframework
*** Keywords ***
Validate Element Text
    [Arguments]    ${selector}    ${expected_text}

    TRY
        ${actual}=    Get Text    ${selector}
        Should Be Equal    ${actual}    ${expected_text}
        Log    ✅ Text validation passed: "${actual}"    level=INFO
    EXCEPT    AS    ${err}
        Take Screenshot    filename=text_validation_failed.png
        Log    ❌ Expected: "${expected_text}" | Got: "${actual}"    level=ERROR
        Fail    Text validation failed: ${err}
    END
```

---

## Recovery Strategies

### Retry Pattern

```robotframework
*** Keywords ***
Retry On Failure
    [Arguments]    ${keyword}    @{args}    ${retries}=3    ${delay}=1s

    FOR    ${i}    IN RANGE    ${retries}
        ${result}=    Run Keyword And Ignore Error
        ...    ${keyword}    @{args}

        Exit For Loop If    '${result}[status]' == 'PASS'

        Log    Attempt ${i+1} failed, retrying in ${delay}...    level=WARN
        Sleep    ${delay}
    END

    IF    '${result}[status]' == 'FAIL'
        Fail    All ${retries} attempts failed for ${keyword}
    END
```

### Fallback Pattern

```robotframework
*** Keywords ***
Click Element Or Fallback
    [Arguments]    ${primary_selector}    ${fallback_selector}

    ${primary_exists}=    Run Keyword And Return Status
    ...    Get Element    ${primary_selector}

    IF    ${primary_exists}
        Click    ${primary_selector}
        Log    Used primary selector: ${primary_selector}
    ELSE
        Log    Primary not found, trying fallback    level=WARN
        Click    ${fallback_selector}
        Log    Used fallback selector: ${fallback_selector}
    END
```

---

## Self-Check Questions

1. Why use TRY-EXCEPT in test automation?
2. When should you take screenshots?
3. How do you debug timing issues?
4. What's the benefit of slowMo for debugging?

---

## Exercise: Add Error Handling

**Task:** Add error handling to a basic test.

**Before (No error handling):**
```robotframework
*** Test Cases ***
Fill And Submit Form
    New Browser    chromium    headless=False
    New Page    http://localhost:8081
    Fill Text    [data-testid="firstName-input"]    Test
    Click    [data-testid="submitButton"]
```

**Acceptance Criteria:**
- [ ] Add TRY-EXCEPT around interactions
- [ ] Take screenshot on failure
- [ ] Log meaningful error messages
- [ ] Verify element states before action

**Starter Code:**
```robotframework
*** Settings ***
Library     Browser

*** Variables ***
${URL}       http://localhost:8081

*** Test Cases ***
Fill And Submit Form Safely
    [Documentation]    TODO: Add error handling
    # TODO: Your code here

*** Keywords ***
# TODO: Add error handling keywords
```

---

## Hints

### Hint 1
Create reusable keywords for safe interactions.

### Hint 2
Use pattern: TRY → Wait for states → Action → Log success → EXCEPT → Screenshot → Log error → Fail

### Hint 3
```robotframework
*** Keywords ***
Safe Fill Text
    [Arguments]    ${locator}    ${text}    ${field_name}
    TRY
        Wait For Elements State    ${locator}    visible    enabled
        Fill Text    ${locator}    ${text}
        Log    Filled ${field_name} with ${text}
    EXCEPT    AS    ${err}
        Take Screenshot    filename=fill_${field_name}_error.png
        Fail    Failed to fill ${field_name}: ${err}
    END
```

### Hint 4 (Full Solution)
```robotframework
*** Settings ***
Library     Browser

*** Variables ***
${URL}       http://localhost:8081

*** Test Cases ***
Fill And Submit Form Safely
    [Documentation]    Fills form with comprehensive error handling
    [Tags]    exercise    error-handling

    TRY
        # Setup
        New Browser    chromium    headless=False
        New Context
        New Page       ${URL}

        # Wait for page to load
        Wait For Elements State    [data-testid="form-page-container"]    visible

        # Fill form using safe keyword
        Safe Fill Text    [data-testid="firstName-input"]    Test    first name

        # Submit with safe keyword
        Safe Click    [data-testid="submitButton"]    submit button

    EXCEPT    AS    ${err}
        Take Screenshot    filename=test_failure.png
        Log    Test failed with error: ${err}    level=ERROR
        Fail    Test execution failed: ${err}
    END

*** Keywords ***
Safe Fill Text
    [Documentation]    Fill text with error handling
    [Arguments]    ${locator}    ${text}    ${field_name}=field

    TRY
        Wait For Elements State    ${locator}    visible    enabled    editable    timeout=5s
        Fill Text    ${locator}    ${text}
        Log    ✅ Filled ${field_name} with: ${text}
    EXCEPT    AS    ${err}
        Take Screenshot    filename=fill_error_${field_name}.png
        Fail    ❌ Failed to fill ${field_name} (${locator}): ${err}
    END

Safe Click
    [Documentation]    Click with error handling
    [Arguments]    ${locator}    ${element_name}=element

    TRY
        Wait For Elements State    ${locator}    visible    enabled    timeout=5s
        Click    ${locator}
        Log    ✅ Clicked ${element_name}
    EXCEPT    AS    ${err}
        Take Screenshot    filename=click_error_${element_name}.png
        Fail    ❌ Failed to click ${element_name} (${locator}): ${err}
    END
```

---

## Best Practices z Komunity

### Overview

Tato sekce shrnuje best practices pro error handling v Robot Framework Browser Library získané z komunitních zdrojů:

- **icehousecorp.com** - DRY principle, implicit wait
- **VALA Group** - Browser Library specifika
- **TestersDock** - Error recovery patterns
- **Context7** - Browser Library waiting mechaniky

---

### DRY Principle v Error Handling

**Zdroj:** icehousecorp.com

Opakující se error handling bloky zabalit do znovupoužitelných keywords.

**❌ Bad - opakující se TRY-EXCEPT:**
```robotframework
*** Test Cases ***
Test One
    TRY
        Wait For Elements State    ${btn1}    visible
        Click    ${btn1}
    EXCEPT
        Take Screenshot
        Fail
    END

Test Two
    TRY
        Wait For Elements State    ${btn2}    visible
        Click    ${btn2}
    EXCEPT
        Take Screenshot
        Fail
    END
```

**✅ Good - znovupoužitelný keyword:**
```robotframework
*** Test Cases ***
Test One
    Safe Click    ${btn1}

Test Two
    Safe Click    ${btn2}

*** Keywords ***
Safe Click
    [Arguments]    ${locator}    ${context}=element
    TRY
        Wait For Elements State    ${locator}    visible    enabled    timeout=${TIMEOUT}
        Click    ${locator}
        Log    ✅ Clicked ${context}
    EXCEPT    AS    ${err}
        Take Screenshot    filename=click_error_${context}.png
        Fail    ❌ Failed to click ${context}: ${err}
    END
```

---

### Implicit Wait místo Sleep

**Zdroj:** icehousecorp.com, VALA Group

Vždy používat implicit wait přes element state, nikdy pevný Sleep.

**❌ Bad - Sleep:**
```robotframework
# Riskantní - element se může načítat později
Sleep    3s
Click    [data-testid="submit-button"]

# Pokud se načte později - FAIL
```

**✅ Good - Implicit Wait:**
```robotframework
# Bezpečné - čeká na element až 5s
Wait For Elements State    [data-testid="submit-button"]    visible    enabled    timeout=5s
Click    [data-testid="submit-button"]

# Pokud se načti později - počká
```

**Výhody implicit wait:**
- ⚡ Rychlejší testy (nečeká zbytečně když je element brzy)
- 🛡️ Stabilnější testy (počká i když je element pomalý)
- 📊 Jasný timeout (víš kolik maximálně čekat)

---

### Screenshot Organizace

**Zdroj:** icehousecorp.com, komunitní best practices

Organizuj screenshoty s dobrou konvencí pojmenování.

**Naming Convention:**
```robotframework
# Pattern: <action>_<context>_<timestamp>.png
Take Screenshot    filename=click_submit_button_20250121_143022.png

# Pattern: <error_type>_<element>_<test_case>.png
Take Screenshot    filename=timeout_email_input_TestSubmitForm.png

# Pattern: <state>_<page>_<description>.png
Take Screenshot    filename=before_fill_form.png
Take Screenshot    filename=after_submit_success.png
Take Screenshot    filename=error_validation_failed.png
```

**Screenshot úrovně:**
```robotframework
# Celá stránka
Take Screenshot    filename=full_page.png    fullPage=True

# Jen element
Take Screenshot    selector=[data-testid="modal"]    filename=modal.png
Take Screenshot    selector=[data-testid="form"]    filename=form.png

# Viditelná oblast (viewport)
Take Screenshot    filename=viewport.png
```

**Struktura složky:**
```
screenshots/
├── before/          # Před akcemi
├── after/           # Po akcích
├── errors/          # Při selhání
└── debug/           # Pro debugging
```

---

### Enhanced Error Messages

**Zdroj:** icehousecorp.com, komunitní best practices

Poskytuj kontext v chybových zprávách pro rychlejší debugging.

**❌ Bad - generická chyba:**
```robotframework
EXCEPT    AS    ${err}
    Fail    Element not found
END
```

**✅ Good - kontextová chyba:**
```robotframework
EXCEPT    AS    ${err}
    ${msg}=    Set Variable    ❌ Failed to click 'Submit Button' | selector='${SUBMIT_BTN}' | ERROR: ${err}
    Log    ${msg}    level=ERROR
    Fail    ${msg}
END
```

**Template pro error messages:**
```robotframework
*** Keywords ***
Build Error Message
    [Arguments]    ${action}    ${context}    ${selector}    ${error}

    ${emoji}=    Set Variable    ❌
    ${parts}=    Create List    ${emoji}
    ...    Failed to ${action}
    ...    '${context}'
    ...    | selector='${selector}'
    ...    | ERROR: ${error}

    ${msg}=    Evaluate    " | ".join(${parts})
    RETURN    ${msg}

# Použití
${msg}=    Build Error Message    click    Submit Button    ${SUBMIT_BTN}    ${err}
Fail    ${msg}
```

---

### Recovery Patterns

**Zdroj:** testersdock.com, komunitní best practices

Implementuj recovery strategie pro common error scénáře.

#### 1. Retry Pattern

```robotframework
*** Keywords ***
Click With Retry
    [Arguments]    ${locator}    ${retries}=3    ${timeout}=2s

    FOR    ${i}    IN RANGE    ${retries}
        ${result}=    Run Keyword And Ignore Error
        ...    Wait For Elements State    ${locator}    visible    enabled    timeout=${timeout}

        Exit For Loop If    '${result}[status]' == 'PASS'

        Log    Retry ${i+1}/${retries} for ${locator} - element not ready    level=WARN
    END

    IF    '${result}[status]' == 'FAIL'
        Take Screenshot    filename=retry_failed_after_${retries}_attempts.png
        Fail    Element not ready after ${retries} retries: ${locator}
    END

    Click    ${locator}
```

#### 2. Fallback Selector

```robotframework
*** Keywords ***
Click With Fallback
    [Arguments]    ${primary_selector}    ${fallback_selector}    ${context}=element

    ${primary_exists}=    Run Keyword And Return Status
    ...    Get Element    ${primary_selector}

    IF    ${primary_exists}
        Log    Using primary selector: ${primary_selector}
        Click    ${primary_selector}
    ELSE
        Log    Primary not found, trying fallback    level=WARN
        Click    ${fallback_selector}
        Log    Used fallback selector: ${fallback_selector}
    END
```

#### 3. Wait for Multiple States

```robotframework
*** Keywords ***
Wait For Multiple States
    [Arguments]    ${locator}    @{expected_states}    ${timeout}=10s

    FOR    ${state}    IN    @{expected_states}
        Wait For Elements State    ${locator}    ${state}    timeout=${timeout}
    END
```

#### 4. Element Stabilization

```robotframework
*** Keywords ***
Wait For Stable Element
    [Arguments]    ${locator}    ${stable_time}=1s    ${check_interval}=100ms

    ${start_time}=    Get Current Date
    ${was_stable}=    Set Variable    ${FALSE}

    WHILE    not ${was_stable}
        ${first_position}=    Get Element    ${locator}
        Sleep    ${stable_time}
        ${second_position}=    Get Element    ${locator}

        ${positions_equal}=    Are Elements Equal    ${first_position}    ${second_position}
        ${was_stable}=    Set Variable If    ${positions_equal}    ${TRUE}    ${FALSE}

        ${elapsed_time}=    Subtract Date From Date    ${start_time}
        Exit For Loop If    ${elapsed_time} > ${timeout}
    END
```

---

### Wait Strategies Comparison

**Zdroj:** Context7, VALA Group

| Strategy | Využití | Příklad | Speed | Reliability |
|----------|---------|---------|-------|--------------|
| **Wait For Elements State** | Element readiness | `Wait For Elements State    ${btn}    visible` | ⚡ Fast | ⭐⭐⭐⭐⭐ |
| **Sleep** | ❌ Vyvaruj se | `Sleep    5s` | 🐢 Slow | ⭐⭐ |
| **Retry with timeout** | Flaky elements | Custom retry loop | ⚡ Fast | ⭐⭐⭐⭐ |
| **Wait for Network** | API calls | `Wait For Response` | ⚡ Fast | ⭐⭐⭐⭐ |
| **Wait for URL** | Navigation | `Wait For Load State    networkidle` | ⚡ Fast | ⭐⭐⭐⭐ |

**Wait For Elements State states:**
```robotframework
# Viditelnost
Wait For Elements State    ${locator}    visible
Wait For Elements State    ${locator}    hidden

# Interakce
Wait For Elements State    ${locator}    enabled
Wait For Elements State    ${locator}    disabled
Wait For Elements State    ${locator}    editable

# Existence
Wait For Elements State    ${locator}    attached
Wait For Elements State    ${locator}    detached

# Kombinace
Wait For Elements State    ${locator}    visible    enabled    attached
```

---

### Best Practices Checklist

Použij tento checklist pro hodnocení error handling:

#### TRY-EXCEPT Patterns
- [ ] Všechny interakce mají TRY-EXCEPT
- [ ] Screenshot při selhání
- [ ] Kontextová chybová zpráva
- [ ] Specifické element context (co selhalo)

#### Wait Strategies
- [ ] Používám Wait For Elements State místo Sleep
- [ ] Timeouty jsou definovány jako proměnné
- [ ] Více stavů checked (visible + enabled + attached)
- [ ] Rozumný timeout (ne příliš krátký/dlouhý)

#### Recovery
- [ ] Retry mechanism pro flaky elementy
- [ ] Fallback selektory pro alternativní cesty
- [ ] Logování při retry attempts

#### Logging
- [ ] Úspěšné akce logovány (✅)
- [ ] Selhání logovány s kontextem (❌)
- [ ] Warnings pro retry attempts
- [ ] Debug info pro problematické scénáře

#### Screenshots
- [ ] Screenshot při každém FAIL
- [ ] Smysluplný název souboru
- [ ] Organizace ve složkách
- [ ] Full page nebo element screenshot

---

### Community Sources

#### Oficiální Dokumentace
- **[Browser Library Waiting](https://marketsquare.github.io/robotframework-browser/Browser.html#Waiting%20and%20Waiting)** - Oficiální wait dokumentace
- **[Playwright Assertions](https://playwright.dev/docs/assertions)** - Assertion a wait strategie
- **[Playwright Debugging](https://playwright.dev/docs/debug/)** - Debugging nástroje

#### Články a Blogy
- **[Ice House Indonesia - Best Practices](https://icehousecorp.com/test-automation-with-robot-framework-page-object-model-best-practices/)** - DRY, implicit wait
- **[VALA Group - Browser Library](https://valagroup.medium.com/turning-the-page-on-front-end-automation-robot-framework-browser-library-2cd3e8a8dd74)** - Stabilní testy s Browser

#### Komunita
- **[Robot Framework Slack](https://robotframework-slack-invite.herokuapp.com/)** - Aktivní komunita pro help
- **[Stack Overflow - robotframework](https://stackoverflow.com/questions/tagged/robotframework)** - Q&A

---

### Tvoje Implementace vs Best Practices

**Co už děláš správně:**
- ✅ TRY-EXCEPT v common keywords
- ✅ Screenshot při selhání
- ✅ Kontextové chybové zprávy
- ✅ Wait For Elements State před akcemi
- ✅ Emoji indikátory (✅/❌)

**Co můžeš vylepšit:**
- 🔄 Přidat retry pattern pro flaky elementy
- 🔄 Používat více wait states (visible + enabled + attached)
- 🔄 Organizovat screenshoty do podsložek
- 🔄 Přidat fallback selektory pro kritické cesty

---

## References

- Project error handling: `/RF/UI/common.resource`
- [Browser Library Error Handling](https://marketsquare.github.io/robotframework-browser/Browser.html#Waiting%20and%20Waiting)
- [Playwright Debugging](https://playwright.dev/docs/debug)
