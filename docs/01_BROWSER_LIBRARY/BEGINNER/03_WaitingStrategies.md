# Waiting Strategies

## Learning Objectives
- [ ] Understand when to use explicit waits
- [ ] Handle loading states properly
- [ ] Debug timing issues
- [ ] Choose appropriate wait strategies

## Prerequisites
- Completed Navigation and Element Interactions

---

## Why Waiting Matters

**Browser Library auto-waits** for most actions, but sometimes you need **explicit waits** for:
- Multi-step operations
- Loading indicators
- Async API calls
- Dynamic content
- State transitions

---

## Wait For Elements State - Deep Dive

### Single State Wait

```robotframework
# Wait until element is visible
Wait For Elements State    [data-testid="modal"]    visible    timeout=10s

# Wait until element is hidden
Wait For Elements State    [data-testid="loading"]    hidden

# Wait until element exists in DOM
Wait For Elements State    [data-testid="result"]    attached
```

### Multiple State Wait

```robotframework
# Wait for ALL states to be true
Wait For Elements State    [data-testid="button"]
    ...    visible    enabled    stable    attached

# Wait for element to be ready for interaction
Wait For Elements State    [data-testid="submit-button"]
    ...    visible    enabled    editable
```

### State Combinations

```robotframework
# Common combinations
Wait For Elements State    ${modal}     visible    attached    stable
Wait For Elements State    ${input}     visible    enabled    editable
Wait For Elements State    ${checkbox}  visible    enabled    attached
Wait For Elements State    ${loading}   hidden
Wait For Elements State    ${removed}   detached
```

---

## All Element States Explained

| State | Description | Use Case |
|-------|-------------|----------|
| `attached` | Element is in DOM | Element exists |
| `detached` | Element removed from DOM | Element deleted/hidden |
| `visible` | Element visible on page | Before interaction |
| `hidden` | Element not visible | After dismissal |
| `stable` | Not animating | Animations complete |
| `enabled` | Can be interacted with | Before click |
| `disabled` | Cannot be interacted | Verify disabled |
| `editable` | Can accept input | Before typing |
| `focused` | Has keyboard focus | Verify focus state |
| `checked` | Checkbox/radio checked | Verify selection |

---

## Waiting Patterns

### Pattern 1: Wait Then Act

```robotframework
# Wait for element to be ready, then interact
Wait For Elements State    [data-testid="submit-button"]    visible    enabled
Click    [data-testid="submit-button"]
```

### Pattern 2: Wait for Loading to Complete

```robotframework
# Loading indicator appears
Wait For Elements State    [data-testid="loading"]    visible

# Do action that triggers loading
Click    [data-testid="refresh-button"]

# Wait for loading to finish
Wait For Elements State    [data-testid="loading"]    hidden    timeout=30s
```

### Pattern 3: Wait for State Change

```robotframework
# Element exists initially
Wait For Elements State    [data-testid="status"]    visible
Get Text    [data-testid="status"]    ==    Pending

# Trigger state change
Click    [data-testid="start-button"]

# Wait for state to change
Wait For Elements State    [data-testid="status"]    visible
Get Text    [data-testid="status"]    ==    In Progress

# Wait for final state
Wait For Elements State    [data-testid="status"]    visible
Get Text    [data-testid="status"]    ==    Complete
```

### Pattern 4: Poll with Timeout

```robotframework
# Custom polling logic
FOR    ${i}    IN RANGE    10
    ${status}=    Run Keyword And Ignore Error
    ...    Get Text    [data-testid="status"]

    IF    '${status}[0]' == 'Complete'
        Break
    END

    Sleep    1s
END
```

---

## Application Examples

### Example 1: Form Submission with Loading

```robotframework
*** Test Cases ***
Submit Form With Loading Wait
    New Browser    chromium    headless=False
    New Context
    New Page       http://localhost:8081

    # Fill form
    Fill Text    [data-testid="firstName-input"]    Jan
    Fill Text    [data-testid="lastName-input"]     Novák
    Fill Text    [data-testid="email-input"]        jan@test.cz
    Fill Text    [data-testid="phone-input"]        +420123456789

    # Select gender
    Click    [data-testid="genderPicker"]
    Wait For Elements State    [data-testid="gender-option-male"]    visible
    Click    [data-testid="gender-option-male"]

    # Submit form
    Click    [data-testid="submitButton"]

    # Wait for success modal (this is the critical wait)
    Wait For Elements State    [data-testid="formSuccessModal"]
    ...    visible    stable    timeout=10s

    # Verify success
    Get Element    [data-testid="formSuccessModal-primary"]
```

### Example 2: List Page with Loading States

```robotframework
*** Test Cases ***
Navigate And Wait For List
    New Browser    chromium    headless=False
    New Context
    New Page       http://localhost:8081

    # Navigate to list page
    Click    [data-testid="menu-item-Page2"]

    # Wait for loading (might appear briefly)
    ${has_loading}=    Run Keyword And Return Status
    ...    Wait For Elements State    [data-testid="page2-loading-container"]
    ...    visible    timeout=2s

    IF    ${has_loading}
        # Wait for loading to complete
        Wait For Elements State    [data-testid="page2-loading-container"]
        ...    hidden    timeout=10s
    END

    # Verify list container is visible
    Wait For Elements State    [data-testid="list-container"]    visible
```

### Example 3: Dynamic Element Appearance

```robotframework
*** Test Cases ***
Verify Dynamic Modal
    New Browser    chromium    headless=False
    New Context
    New Page       http://localhost:8081

    # Click list item that triggers modal
    Click    [data-testid="menu-item-Page2"]

    # Wait for list to load
    Wait For Elements State    [data-testid="list-container"]    visible

    # Check if there are items to click
    ${item_count}=    Get Element Count    [data-testid^="list-item-"]

    IF    ${item_count} > 0
        # Click first item name to show detail modal
        Click    [data-testid^="list-item-"][data-testid$="-name"] >> nth=0

        # Wait for modal to appear
        Wait For Elements State    [data-testid="info-modal"]
        ...    visible    stable    timeout=5s

        # Verify modal content
        Get Element    [data-testid="info-email-value"]

        # Close modal
        Click    [data-testid="info-modal-ok"]

        # Wait for modal to disappear
        Wait For Elements State    [data-testid="info-modal"]
        ...    hidden    timeout=5s
    ELSE
        Log    No items in list to test modal
    END
```

---

## Timeout Best Practices

### Set Appropriate Timeouts

```robotframework
# Quick UI operations (buttons, inputs)
Wait For Elements State    ${button}    visible    timeout=5s

# Normal page loads
Wait For Elements State    ${container}    visible    timeout=10s

# API responses, complex operations
Wait For Elements State    ${result}    visible    timeout=30s

# Long-running operations
Wait For Elements State    ${export}    visible    timeout=60s
```

### Global Timeout Configuration

```robotframework
*** Settings ***
# Set default timeout for all waits
Library     Browser    timeout=15s
```

### Per-Keyword Override

```robotframework
# Override global timeout for specific wait
Wait For Elements State    ${slow-element}    visible    timeout=45s
```

---

## Debugging Timing Issues

### Enable Tracing

```robotframework
# Enable tracing to see what's happening
New Browser    chromium    headless=False    tracing=on
# ... perform actions ...
Close Browser
# Tracing saved to trace.zip
```

### Take Screenshots on Timeout

```robotframework
*** Keywords ***
Wait With Screenshot
    [Arguments]    ${selector}    ${state}    ${timeout}=10s

    ${result}=    Run Keyword And Ignore Error
    ...    Wait For Elements State    ${selector}    ${state}    timeout=${timeout}

    IF    '${result}[status]' == 'FAIL'
        Take Screenshot    filename=wait_failure_${state}.png
        Fail    Timeout waiting for ${selector} to be ${state}
    END
```

### Check Element States

```robotframework
*** Keywords ***
Debug Element State
    [Arguments]    ${selector}

    ${states}=    Get Element States    ${selector}
    Log    Element states: ${states}

    ${visible}=    Evaluate    "visible" in """${states}"""
    ${enabled}=    Evaluate    "enabled" in """${states}"""
    ${attached}=    Evaluate    "attached" in """${states}"""

    Log    Visible: ${visible}
    Log    Enabled: ${enabled}
    Log    Attached: ${attached}
```

---

## Common Timing Issues

### Issue 1: Element Found But Not Clickable

```robotframework
# ❌ FAILS: Element exists but covered by modal
Click    [data-testid="submit-button"]

# ✅ FIX: Wait for modal to disappear
Wait For Elements State    [data-testid="modal"]    hidden
Click    [data-testid="submit-button"]
```

### Issue 2: Element Not Yet Rendered

```robotframework
# ❌ FAILS: Element not in DOM after navigation
Go To    http://localhost:8081/page2
Get Element    [data-testid="list-container"]

# ✅ FIX: Wait for element to be attached
Go To    http://localhost:8081/page2
Wait For Elements State    [data-testid="list-container"]    attached
```

### Issue 3: Element Animating

```robotframework
# ❌ FAILS: Button still animating
Click    [data-testid="animated-button"]

# ✅ FIX: Wait for stable state
Wait For Elements State    [data-testid="animated-button"]    stable
Click    [data-testid="animated-button"]
```

---

## Self-Check Questions

1. What's the difference between `visible` and `attached`?
2. Why would you wait for `stable` state?
3. How do you wait for an element to disappear?
4. What timeout should you use for API responses?

---

## Exercise: Robust Async Test

**Task:** Create a test that properly handles all async operations.

**Scenario:**
1. Navigate to list page
2. Handle loading states properly
3. Click an item (if exists)
4. Wait for modal to appear
5. Close modal and verify it's gone

**Acceptance Criteria:**
- [ ] No Sleep statements
- [ ] Proper waits for each state
- [ ] Handles empty list case
- [ ] Debug screenshots on failure

**Starter Code:**
```robotframework
*** Settings ***
Library     Browser

*** Variables ***
${URL}       http://localhost:8081
${TIMEOUT}   10s

*** Test Cases ***
Handle Async Operations Properly
    [Documentation]    TODO: Implement robust async handling
    [Tags]    beginner    exercise

    # TODO: Your code here

*** Keywords ***
# TODO: Add helper keywords
```

---

## Hints

### Hint 1
Flow: Navigate → Wait for list → Check if items → Click item → Wait for modal → Close modal → Wait for modal gone

### Hint 2
Use conditional checks for optional elements (loading, items)

### Hint 3
Key waits:
- List container visible
- Modal visible + stable
- Modal hidden (after close)

### Hint 4
```robotframework
Handle Async Operations Properly
    New Browser    chromium    headless=False
    New Context
    New Page       ${URL}

    # Navigate to list
    Click    [data-testid="menu-item-Page2"]

    # TODO: Handle loading, check items, interact with modal
```

### Hint 5 (Full Solution)
```robotframework
*** Settings ***
Library     Browser

*** Variables ***
${URL}       http://localhost:8081
${TIMEOUT}   10s

*** Test Cases ***
Handle Async Operations Properly
    [Documentation]    Handles all async operations with proper waits
    [Tags]    beginner    exercise    async

    New Browser    chromium    headless=False
    New Context
    New Page       ${URL}

    # Navigate to list page
    Click    [data-testid="menu-item-Page2"]

    # Handle optional loading state
    ${has_loading}=    Run Keyword And Return Status
    ...    Wait For Elements State    [data-testid="page2-loading-container"]
    ...    visible    timeout=2s

    IF    ${has_loading}
        Wait For Elements State    [data-testid="page2-loading-container"]
        ...    hidden    timeout=${TIMEOUT}
    END

    # Verify list is visible
    Wait For Elements State    [data-testid="list-container"]    visible

    # Check for items
    ${item_count}=    Get Element Count    [data-testid^="list-item-"][data-testid$="-name"]

    IF    ${item_count} > 0
        # Click first item to show modal
        Click    [data-testid^="list-item-"][data-testid$="-name"] >> nth=0

        # Wait for modal to appear and be stable
        Wait For Elements State    [data-testid="info-modal"]
        ...    visible    stable    timeout=${TIMEOUT}

        # Verify modal has content
        Get Element    [data-testid="info-email-value"]

        # Close modal
        Click    [data-testid="info-modal-ok"]

        # Wait for modal to disappear
        Wait For Elements State    [data-testid="info-modal"]
        ...    hidden    timeout=${TIMEOUT}
    ELSE
        Log    No items in list - modal test skipped
    END

    [Teardown]    Take Screenshot
```

---

## References

- [Browser Library - Waiting](https://marketsquare.github.io/robotframework-browser/Browser.html#Waiting)
- [Playwright Actionability](https://playwright.dev/docs/actionability)
- Application async patterns: `/fe/mojeApp/src/component/pages/`
