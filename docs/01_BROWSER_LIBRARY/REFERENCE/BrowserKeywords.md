# Browser Keywords Quick Reference

## Overview

Quick reference for commonly used Browser Library keywords in this project.

---

## Browser & Context Management

### New Browser
```robotframework
New Browser    ${browser}    headless=${True}    slowMo=0
```
- **Purpose**: Creates browser instance
- **Parameters:**
  - `browser`: chromium, firefox, webkit
  - `headless`: True/False (default: True)
  - `slowMo**: Delay in ms (for debugging)
- **Example:**
  ```robotframework
  New Browser    chromium    headless=False
  New Browser    firefox    headless=True    slowMo=500
  ```

### New Context
```robotframework
New Context    viewport=${None}    ignoreHTTPSErrors=${True}
```
- **Purpose**: Creates isolated context (incognito-like)
- **Parameters:**
  - `viewport`: Dict with width/height
  - `ignoreHTTPSErrors`: True/False
  - `acceptDownloads`: True/False
- **Example:**
  ```robotframework
  New Context    viewport={'width': 1920, 'height': 1080}
  New Context    acceptDownloads=True
  ```

### Get Device
```robotframework
${device}=    Get Device    iPhone 13
```
- **Purpose**: Get device emulation config
- **Common devices:** iPhone 13, iPad Pro, Pixel 5
- **Returns:** Dict with viewport, userAgent, deviceScaleFactor
- **Usage:**
  ```robotframework
  ${device}=    Get Device    iPhone 13
  New Context    &{device}
  ```

### Close Context / Close Browser
```robotframework
Close Context
Close Browser
```
- **Purpose**: Clean up resources
- **When to use:**
  - `Close Context`: Between tests (clears cookies)
  - `Close Browser`: End of suite (closes browser)

---

## Navigation

### New Page
```robotframework
New Page    ${url}    waitUntil=load    timeout=30s
```
- **Purpose**: Opens URL in new tab
- **Parameters:**
  - `url`: Target URL
  - `waitUntil`: load, domcontentloaded, networkidle
  - `timeout**: Timeout in time format
- **Example:**
  ```robotframework
  New Page    http://localhost:8081
  New Page    https://example.com    waitUntil=domcontentloaded
  ```

### Go To
```robotframework
Go To    ${url}
```
- **Purpose**: Navigate within same page
- **Example:**
  ```robotframework
  Go To    http://localhost:8081/page2
  ```

### Go Back / Go Forward
```robotframework
Go Back
Go Forward
```
- **Purpose**: Browser history navigation

### Get Url
```robotframework
${url}=    Get Url
```
- **Returns:** Current page URL
- **Assertions:**
  ```robotframework
  Get Url    ==    http://localhost:8081
  Get Url    *=    localhost
  Get Url    $=    /page2
  ```

---

## Element Finding

### Get Element
```robotframework
${element}=    Get Element    ${selector}
```
- **Purpose:** Find element (fails if not found)
- **Selector types:**
  - CSS: `[data-testid="name"]`, `.class`, `#id`
  - Text: `"Submit button"`
  - XPath: `//button[@type="submit"]`
  - Combined: `[data-testid="form"] >> "Submit"`
- **Indexing:**
  ```robotframework
  Get Element    [data-testid="item"] >> nth=0
  ```

### Get Element Count
```robotframework
${count}=    Get Element Count    ${selector}
```
- **Returns:** Number of matching elements
- **Example:**
  ```robotframework
  ${count}=    Get Element Count    [data-testid^="list-item-"]
  ```

### Get Element States
```robotframework
${states}=    Get Element States    ${selector}
```
- **Returns:** List of element states
- **States:** visible, hidden, attached, detached, enabled, disabled, etc.

---

## Element Interaction

### Fill Text
```robotframework
Fill Text    ${selector}    ${text}    clear=${True}
```
- **Purpose:** Type text into input (clears by default)
- **Parameters:**
  - `selector`: Element selector
  - `text`: Text to type
  - `clear`: Clear field first (default: True)
  - `delay`: Delay between keystrokes
- **Example:**
  ```robotframework
  Fill Text    [data-testid="email-input"]    user@example.com
  Fill Text    textarea    Hello    delay=100ms
  ```

### Type Text
```robotframework
Type Text    ${selector}    ${text}    clear=${False}
```
- **Purpose:** Append text (doesn't clear by default)
- **Use for:** Chat inputs, append scenarios

### Click
```robotframework
Click    ${selector}    button=left    clickCount=1    modifiers=${None}
```
- **Purpose:** Click element
- **Parameters:**
  - `button`: left, right, middle
  - `clickCount`: 1 (single), 2 (double)
  - `modifiers`: Control, Shift, Alt, Meta
  - `force`: Skip actionability checks
- **Example:**
  ```robotframework
  Click    [data-testid="button"]
  Click    [data-testid="item"]    clickCount=2
  Click    [data-testid="link"]    modifiers=Control
  ```

### Select Options By
```robotframework
Select Options By    ${selector}    ${strategy}    @{values}
```
- **Purpose:** Select option(s) from dropdown
- **Strategies:** value, label, index
- **Example:**
  ```robotframework
  Select Options By    [data-testid="country"]    label    Czech Republic
  Select Options By    [data-testid="tags"]    value    tag1    tag2
  ```

### Check Checkbox / Uncheck Checkbox
```robotframework
Check Checkbox    ${selector}
Uncheck Checkbox    ${selector}
```
- **Purpose:** Toggle checkbox state

### Upload File
```robotframework
Upload File    ${selector}    ${path}
```
- **Purpose:** Upload file to input
- **Example:**
  ```robotframework
  Upload File    [data-testid="file-upload"]    /path/to/file.pdf
  ```

---

## Getting Element Information

### Get Text
```robotframework
${text}=    Get Text    ${selector}
```
- **Returns:** Visible text content
- **Assertions:**
  ```robotframework
  Get Text    [data-testid="title"]    ==    Expected Title
  Get Text    [data-testid="status"]    $=    Success
  ```

### Get Property
```robotframework
${value}=    Get Property    ${selector}    ${property}
```
- **Common properties:** value, href, class, id, src
- **Example:**
  ```robotframework
  ${href}=    Get Property    [data-testid="link"]    href
  ${value}=    Get Property    [data-testid="input"]    value
  ```

### Get Attribute
```robotframework
${value}=    Get Attribute    ${selector}    ${attribute}
```
- **Purpose:** Get HTML attribute value
- **Example:**
  ```robotframework
  ${data_id}=    Get Attribute    [data-testid="row"]    data-test-id
  ```

### Get Checkbox State
```robotframework
${checked}=    Get Checkbox State    ${selector}
```
- **Returns:** True/False
- **Example:**
  ```robotframework
  ${checked}=    Get Checkbox State    [data-testid="agree"]
  IF    ${checked}
      Log    Checkbox is checked
  END
  ```

---

## Waiting

### Wait For Elements State
```robotframework
Wait For Elements State    ${selector}    @{states}    timeout=30s
```
- **Purpose:** Wait for element to reach specified state(s)
- **States:** visible, hidden, attached, detached, enabled, disabled, stable, editable, focused, checked
- **Example:**
  ```robotframework
  Wait For Elements State    [data-testid="modal"]    visible    stable
  Wait For Elements State    [data-testid="loading"]    hidden
  Wait For Elements State    [data-testid="button"]    visible    enabled
  ```

### Wait For Network Idle
```robotframework
Wait For Network Idle    timeout=30s
```
- **Purpose:** Wait for no network connections
- **Use sparingly:** Very slow, use only when necessary

### Wait For Load State
```robotframework
Wait For Load State    ${state}    timeout=30s
```
- **States:** load, domcontentloaded, networkidle

---

## Assertions

### Get Text (Assertion)
```robotframework
Get Text    ${selector}    ==    Expected Text
Get Text    ${selector}    *=    contains
Get Text    ${selector}    $=    ends-with
```

### Get Url (Assertion)
```robotframework
Get Url    ==    http://localhost:8081/page
Get Url    *=    localhost:8081
Get Url    $=    /page
```

### Get Title
```robotframework
${title}=    Get Title
Get Title    ==    Expected Title
```

---

## Screenshots

### Take Screenshot
```robotframework
Take Screenshot
Take Screenshot    filename=my_screenshot.png
Take Screenshot    selector=${element}
```
- **Purpose:** Capture screenshot
- **File types:** .png, .jpeg
- **Example:**
  ```robotframework
  Take Screenshot    filename=form_filled.png
  Take Screenshot    selector=[data-testid="modal"]    filename=modal.png
  ```

---

## Special Keywords

### Hover
```robotframework
Hover    ${selector}
```
- **Purpose:** Move mouse over element

### Evaluate
```robotframework
${result}=    Evaluate    JavaScript.code
```
- **Purpose:** Execute JavaScript
- **Example:**
  ```robotframework
  ${scroll}=    Evaluate    element => element.scrollTop    element=${element}
  ```

---

## App-Specific Wrappers

From `/RF/UI/common.resource`:

### Fill Text In Input Field
```robotframework
Fill Text In Input Field    ${locator}    ${text}    ${context_name}=${EMPTY}
```
- **Purpose:** Enhanced fill with error handling and logging
- **Features:**
  - Validates element exists
  - Logs input action
  - Takes screenshot on failure

### Click On The Element
```robotframework
Click On The Element    ${locator}    ${context_name}=${EMPTY}
```
- **Purpose:** Enhanced click with error handling
- **Features:**
  - Waits for element to be ready
  - Validates state (attached, visible, enabled)
  - Takes screenshot on failure

---

## Common Patterns

### Pattern 1: Safe Interaction
```robotframework
Wait For Elements State    ${selector}    visible    enabled
Click    ${selector}
```

### Pattern 2: Fill and Submit
```robotframework
Fill Text    ${input_selector}    ${value}
Click    ${submit_button}
Wait For Elements State    ${success_modal}    visible
```

### Pattern 3: Dynamic List
```robotframework
${count}=    Get Element Count    [data-testid^="list-item-"]
FOR    ${i}    IN RANGE    ${count}
    ${item}=    Get Element    [data-testid^="list-item-"] >> nth=${i}
    Log    Processing item ${i}
END
```

### Pattern 4: Wait for Loading
```robotframework
# Action that triggers loading
Click    [data-testid="refresh"]

# Wait for loading to complete
Wait For Elements State    [data-testid="loading"]    hidden    timeout=30s
```

---

## Selector Quick Reference

| Type | Example | Description |
|------|---------|-------------|
| data-testid | `[data-testid="name"]` | Recommended - stable |
| CSS Class | `.submit-button` | May change |
| CSS ID | `#email-input` | May change |
| Attribute | `[name="email"]` | Sometimes stable |
| Text | `"Submit"` | Can change with localization |
| XPath | `//button[@type="submit"]` | Fragile |
| Combined | `[data-testid="form"] >> "Submit"` | Specific |
| Partial match | `[data-testid^="list-"]` | Starts with |
| Partial match | `[data-testid$="-name"]` | Ends with |

---

## References

- [Full Browser Library Docs](https://marketsquare.github.io/robotframework-browser/Browser.html)
- [Playwright Selectors](https://playwright.dev/docs/selectors)
- Project: `/RF/UI/common.resource`
