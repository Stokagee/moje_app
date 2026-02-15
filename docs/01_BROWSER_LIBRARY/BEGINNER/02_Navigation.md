# Navigation and Waiting Strategies

## Learning Objectives
- [ ] Understand explicit vs implicit waiting
- [ ] Use wait strategies effectively
- [ ] Handle dynamic content
- [ ] Debug timing issues

## Prerequisites
- Completed Element Interactions
- Know basic element interactions

---

## The Waiting Problem

**Why do we need to wait?**

Web applications are **asynchronous**:
- Data loads from API
- Components render dynamically
- Animations complete over time
- Network delays vary

**Bad approach - Hard waits:**
```robotframework
# ❌ DON'T DO THIS
Sleep    3s
Click    [data-testid="button"]
```

**Problems with Sleep:**
- Too short: test fails (element not ready)
- Too long: slow tests
- Unreliable: depends on machine/network speed

---

## Browser Library Auto-Waiting

Browser Library **automatically waits** before most actions!

```robotframework
# Auto-wait for element to be:
# - Attached to DOM
# - Visible
# - Stable (not animating)
# - Enabled (for clickable elements)
Click    [data-testid="submitButton"]
```

**Auto-wait is enabled by default** for:
- `Click`, `Fill Text`, `Type Text`
- `Select Options By`
- `Check Checkbox`, `Uncheck Checkbox`
- Most interaction keywords

**Timeout:** 30 seconds (configurable)

---

## Explicit Waits

### Wait For Elements State

Most commonly used explicit wait:

```robotframework
# Wait for single state
Wait For Elements State    [data-testid="modal"]    visible    timeout=10s

# Wait for multiple states (all must be true)
Wait For Elements State    [data-testid="button"]    visible    enabled    attached

# Wait for state to NOT be true
Wait For Elements State    [data-testid="loading"]    hidden    timeout=5s

# Wait for element to NOT exist
Wait For Elements State    [data-testid="modal"]    detached
```

**State Options:**
| State | Meaning | Use When |
|-------|---------|-----------|
| `attached` | Element in DOM | Element should exist |
| `detached` | Element not in DOM | Element should be removed |
| `visible` | Element visible | Need to interact |
| `hidden` | Element not visible | Should be gone/invisible |
| `stable` | Not animating | Animations complete |
| `enabled` | Can be interacted | Before click/fill |
| `disabled` | Cannot be interacted | Verify disabled state |
| `editable` | Can be edited | Input fields |
| `focused` | Has keyboard focus | Verify focus |

### Wait For Network Idle

```robotframework
# Wait for no network connections (use sparingly)
Wait For Network Idle    timeout=10s

# Wait for specific request to complete
Wait For Network Idle    timeout=30s
```

**Use cases:**
- After form submission (before verification)
- After navigation (page fully loaded)
- Before assertions (data fully loaded)

**Caution:** Very slow, use only when necessary.

### Wait For Load State

```robotframework
# Wait for page load states
Wait For Load State    load               # Window.load event
Wait For Load State    domcontentloaded   # DOM ready (faster)
Wait For Load State    networkidle        # No active connections
```

---

## Waiting Strategies

### Strategy 1: Wait for Target Element

```robotframework
# Good - wait for what you need to interact with
Wait For Elements State    [data-testid="submit-button"]    visible    enabled
Click    [data-testid="submit-button"]
```

### Strategy 2: Wait for Loading to Complete

```robotframework
# Good for data loading screens
Wait For Elements State    [data-testid="loading"]    visible
# Loading indicator appears

Wait For Elements State    [data-testid="loading"]    hidden    timeout=30s
# Loading indicator is gone
```

### Strategy 3: Wait for Response

```robotframework
# After API call, wait for result
Click    [data-testid="submit-button"]

# Wait for success modal
Wait For Elements State    [data-testid="formSuccessModal"]    visible    timeout=10s
```

### Strategy 4: Poll with Retry

```robotframework
# Custom polling logic
FOR    ${i}    IN RANGE    5
    ${visible}=    Run Keyword And Return Status
    ...    Get Element    [data-testid="result"]
    Exit For Loop If    ${visible}
    Sleep    1s
END
```

---

## Application Examples

### Example 1: Form Submission with Wait

```robotframework
*** Test Cases ***
Submit Form And Verify Success
    New Browser    chromium    headless=False
    New Context
    New Page       http://localhost:8081

    # Fill form
    Fill Text    [data-testid="firstName-input"]    Test
    Fill Text    [data-testid="lastName-input"]     User
    Fill Text    [data-testid="email-input"]        test@example.com
    Fill Text    [data-testid="phone-input"]        +420123456789

    # Open gender picker and wait for options
    Click    [data-testid="genderPicker"]
    Wait For Elements State    [data-testid="gender-option-male"]    visible
    Click    [data-testid="gender-option-male"]

    # Submit form
    Click    [data-testid="submitButton"]

    # Wait for success modal (API call completed)
    Wait For Elements State    [data-testid="formSuccessModal"]    visible    timeout=10s

    # Verify modal content
    Get Text    [data-testid="formSuccessModal"]    $=    Success
```

### Example 2: List Page Loading

```robotframework
*** Test Cases ***
Verify List Loads Correctly
    New Browser    chromium    headless=False
    New Context
    New Page       http://localhost:8081

    # Navigate to list page
    Click    [data-testid="menu-item-Page2"]

    # Wait for loading to appear
    Wait For Elements State    [data-testid="page2-loading-container"]    visible

    # Wait for loading to disappear (data loaded)
    Wait For Elements State    [data-testid="page2-loading-container"]    hidden    timeout=10s

    # Verify list is visible
    Wait For Elements State    [data-testid="list-container"]    visible

    # Check if list has items or is empty
    ${empty_exists}=    Run Keyword And Return Status
    ...    Get Element    [data-testid="list-empty-state"]

    IF    ${empty_exists}
        Log    List is empty - expected for fresh database
    ELSE
        ${item_count}=    Get Element Count    [data-testid^="list-item-"]
        Log    Found ${item_count} items in list
    END
```

### Example 3: Dynamic Content Updates

```robotframework
*** Test Cases ***
Refresh List And Verify Update
    New Browser    chromium    headless=False
    New Context
    New Page       http://localhost:8081

    # Navigate to list
    Click    [data-testid="menu-item-Page2"]
    Wait For Elements State    [data-testid="list-container"]    visible

    # Get initial item count
    ${initial_count}=    Get Element Count    [data-testid^="list-item-"]

    # Click refresh button
    Click    [data-testid="refreshButton"]

    # Wait for loading indicator
    Wait For Elements State    [data-testid="page2-loading-container"]    visible

    # Wait for loading to complete
    Wait For Elements State    [data-testid="page2-loading-container"]    hidden    timeout=10s

    # Verify list is still visible
    Wait For Elements State    [data-testid="list-container"]    visible

    # Get new count (may be same or different)
    ${new_count}=    Get Element Count    [data-testid^="list-item-"]
    Log    Item count: ${initial_count} → ${new_count}
```

---

## Timeout Configuration

### Global Timeout

```robotframework
*** Settings ***
Library     Browser    timeout=20s
```

### Per-Call Timeout

```robotframework
# Override global timeout
Wait For Elements State    ${selector}    visible    timeout=5s
```

### Recommended Timeouts

| Operation | Timeout | Reason |
|-----------|---------|--------|
| Element visibility | 5-10s | Quick UI response |
| API response/modal | 10-30s | Depends on backend |
| Loading data | 30s+ | Large datasets |
| Network idle | 60s+ | Many requests |

---

## Common Pitfalls

| Pitfall | Why It Happens | How to Avoid |
|---------|---------------|--------------|
| Test fails randomly | Race condition - element not ready | Use explicit wait before interaction |
| Test is slow | Waiting for network idle unnecessarily | Wait for specific element instead |
| Wrong element interacted | Old element still in DOM | Use unique selectors |
| Element clicked but nothing | Clicked disabled element | Wait for `enabled` state |

---

## Best Practices

1. **Always wait for target state:**
   ```robotframework
   # Good
   Wait For Elements State    ${button}    visible    enabled
   Click    ${button}

   # Bad
   Click    ${button}  # May fail if not ready
   ```

2. **Wait for specific conditions, not time:**
   ```robotframework
   # Good
   Wait For Elements State    [data-testid="loading"]    hidden

   # Bad
   Sleep    3s
   ```

3. **Use appropriate timeouts:**
   ```robotframework
   # Quick UI interaction
   Wait For Elements State    ${button}    visible    timeout=5s

   # API response
   Wait For Elements State    ${modal}    visible    timeout=30s
   ```

4. **Chain waits for complex scenarios:**
   ```robotframework
   # Wait for loading to start, then finish
   Wait For Elements State    [data-testid="loading"]    visible
   Wait For Elements State    [data-testid="loading"]    hidden    timeout=30s
   ```

---

## Self-Check Questions

1. Why is `Sleep` worse than `Wait For Elements State`?
2. What states does Browser Library automatically wait for?
3. How do you wait for an element to disappear?
4. When should you use `Wait For Network Idle`?

---

## Exercise: Async Form Handling

**Task:** Create a test that handles async form submission properly.

**Scenario:**
1. Fill and submit form
2. Wait for API call (loading indicator)
3. Wait for success response (modal)
4. Verify success message

**Acceptance Criteria:**
- [ ] No hardcoded sleeps
- [ ] Proper waits for each state
- [ ] Handles potential delays
- [ ] Clear failure messages

**Starter Code:**
```robotframework
*** Settings ***
Library     Browser

*** Variables ***
${URL}       http://localhost:8081

*** Test Cases ***
Handle Async Form Submission
    [Documentation]    TODO: Implement proper async handling
    [Tags]    beginner    exercise

    # TODO: Your code here

*** Keywords ***
# TODO: Add helper keywords
```

---

## Hints

### Hint 1
Think about what states occur: submit → loading → success modal.

### Hint 2
You need to wait for the success modal, not just sleep.

### Hint 3
Flow:
1. Fill form
2. Click submit
3. Either wait for loading indicator OR wait for success modal directly
4. Verify modal content

### Hint 4
```robotframework
Handle Async Form Submission
    New Browser    chromium    headless=False
    New Context
    New Page       ${URL}

    # Fill form
    Fill Text    [data-testid="firstName-input"]    Async
    Fill Text    [data-testid="lastName-input"]     Test
    Fill Text    [data-testid="email-input"]        async@test.com
    Fill Text    [data-testid="phone-input"]        +420123456789

    # Select gender
    Click    [data-testid="genderPicker"]
    Click    [data-testid="gender-option-male"]

    # Submit and wait for success
    Click    [data-testid="submitButton"]

    # TODO: Wait for success modal properly
```

### Hint 5 (Full Solution)
```robotframework
*** Settings ***
Library     Browser

*** Variables ***
${URL}       http://localhost:8081
${TIMEOUT}    30s

*** Test Cases ***
Handle Async Form Submission
    [Documentation]    Handles async form submission with proper waits
    [Tags]    beginner    exercise    async

    New Browser    chromium    headless=False
    New Context
    New Page       ${URL}

    # Wait for page to be ready
    Wait For Elements State    [data-testid="form-page-container"]    visible

    # Fill form fields
    Fill Text    [data-testid="firstName-input"]    Async
    Fill Text    [data-testid="lastName-input"]     Test
    Fill Text    [data-testid="email-input"]        async@test.com
    Fill Text    [data-testid="phone-input"]        +420123456789

    # Select gender
    Click    [data-testid="genderPicker"]
    Wait For Elements State    [data-testid="gender-option-male"]    visible    timeout=5s
    Click    [data-testid="gender-option-male"]

    # Submit form
    Click    [data-testid="submitButton"]

    # Wait for success modal (API call completes)
    # Using timeout longer than normal to account for async behavior
    Wait For Elements State    [data-testid="formSuccessModal"]    visible    timeout=${TIMEOUT}

    # Verify modal is fully loaded
    Get Element    [data-testid="formSuccessModal-primary"]

    # Take screenshot for verification
    Take Screenshot    filename=async_form_success.png

    [Teardown]    Close Browser
```

---

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Using `Sleep 5s` after submit | Use `Wait For Elements State` for modal |
| Not waiting for dropdown options | Add wait after clicking picker |
| Timeout too short for API | Increase timeout for async operations |
| Waiting for network idle unnecessarily | Wait for target element instead |

---

## References

- [Browser Library - Waits](https://marketsquare.github.io/robotframework-browser/Browser.html#Waiting)
- [Playwright Waits](https://playwright.dev/docs/actionability)
- Application async patterns: `/fe/mojeApp/src/component/pages/`
- Example waits: `/RF/UI/common.resource`
