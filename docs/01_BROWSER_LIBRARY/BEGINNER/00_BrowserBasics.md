# Browser Library Basics

## Learning Objectives
- [ ] Understand Browser Library architecture
- [ ] Set up browser sessions
- [ ] Navigate to web pages
- [ ] Close browser properly

## Prerequisites
- Completed Installation guide
- Playwright browsers installed

---

## What is Browser Library?

Browser Library is a **modern web testing library** for Robot Framework built on **Playwright** (not Selenium).

**Key Features:**
- **Fast**: Uses Playwright's efficient browser automation
- **Reliable**: Auto-waiting for elements (no more flaky tests!)
- **Modern**: Supports all major browsers (Chromium, Firefox, WebKit)
- **Powerful**: Network interception, screenshots, PDFs, tracing

**Architecture:**
```
Your Test
    ↓
Browser Library Keywords
    ↓
Playwright (Node.js)
    ↓
Chromium/Firefox/WebKit
```

---

## Basic Browser Session

### Minimal Example

```robotframework
*** Settings ***
Library     Browser

*** Test Cases ***
Open And Close Browser
    New Browser    chromium    headless=False
    New Context    ignoreHTTPSErrors=True
    New Page       https://example.com

    Get Title    ==    Example Domain

    Close Context
    Close Browser
```

**Breakdown:**

| Keyword | Purpose |
|---------|---------|
| `New Browser` | Creates browser instance (chromium/firefox/webkit) |
| `New Context` | Creates incognito-like context (cookies, cache isolation) |
| `New Page` | Opens new tab and navigates to URL |
| `Close Context` | Closes context (clears cookies, cache) |
| `Close Browser` | Closes browser completely |

---

## Browser Options

### Headless vs Headed

```robotframework
# Headless (no GUI) - faster, good for CI
New Browser    chromium    headless=True

# Headed (visible) - debugging, development
New Browser    chromium    headless=False
```

### Browser Types

```robotframework
# Chromium (Chrome/Edge based)
New Browser    chromium

# Firefox
New Browser    firefox

# WebKit (Safari)
New Browser    webkit
```

### Slow Motion (Debugging)

```robotframework
# Slows down each action (milliseconds)
New Browser    chromium    slowMo=500
```

---

## Context Options

### Basic Context

```robotframework
New Context    ignoreHTTPSErrors=True
```

### With Viewport (Device Emulation)

```robotframework
# Desktop size
New Context    viewport={'width': 1920, 'height': 1080}

# Mobile device
${device_config}=    Get Device    iPhone 13
New Context    &{device_config}
```

### Accept Downloads

```robotframework
New Context    acceptDownloads=True
```

---

## Navigation Keywords

### New Page

```robotframework
# Simple navigation
New Page    https://example.com

# With timeout
New Page    https://example.com    timeout=10s

# Wait until specific state
New Page    https://example.com    waitUntil=domcontentloaded
```

**Wait Until Options:**
- `load` - Wait for load event (default)
- `domcontentloaded` - Wait for DOM ready (faster)
- `networkidle` - Wait for no network connections (slowest)

### Go To

```robotframework
# Navigate within same page
Go To    https://example.com/page2

# Go back
Go Back

# Go forward
Go Forward
```

### Get Url

```robotframework
# Verify current URL
${url}=    Get Url
Should Be Equal    ${url}    https://example.com

# Partial match
Get Url    *=    example.com

# Regex match
Get Url    $=    /page
```

---

## Setup and Teardown Patterns

### Per-Test Browser

```robotframework
*** Settings ***
Library     Browser
Test Setup      New Browser    chromium    headless=False
Test Teardown   Close Browser

*** Test Cases ***
Test One
    New Context
    New Page    https://example.com
    # ... test steps ...

Test Two
    New Context
    New Page    https://example.com
    # ... test steps ...
```

### Suite-Level Browser

```robotframework
*** Settings ***
Library     Browser
Suite Setup     New Browser    chromium    headless=${HEADLESS}
Suite Teardown  Close Browser
Test Setup      New Context
Test Teardown   Close Context

*** Test Cases ***
Test One
    New Page    https://example.com
    # ...
```

### Using Variables

```robotframework
*** Variables ***
${BROWSER}       chromium
${HEADLESS}      ${False}
${URL}           http://localhost:8081

*** Settings ***
Library     Browser

*** Test Cases ***
Navigate To App
    New Browser    ${BROWSER}    headless=${HEADLESS}
    New Context
    New Page       ${URL}
```

---

## Application Example: Opening Our App

```robotframework
*** Settings ***
Library     Browser

*** Variables ***
${URL}       http://localhost:8081

*** Test Cases ***
Open Application And Verify
    [Documentation]    Opens the app and verifies page loaded
    [Tags]    beginner    smoke

    # Setup browser
    New Browser    chromium    headless=False
    New Context    viewport={'width': 900, 'height': 600}
    New Page       ${URL}

    # Verify we're on the right page
    Get Url    *=    localhost:8081
    Get Title    *=    moj

    # Verify main container exists
    Get Element    [data-testid="form-page-container"]

    [Teardown]    Close Browser
```

---

## Common Pitfalls

| Pitfall | Why It Happens | How to Avoid |
|---------|---------------|--------------|
| Browser doesn't open | Playwright not installed | Run `playwright install chromium` |
| Page loads forever | Wait for networkidle | Use `waitUntil=load` instead |
| Tests fail on CI | Headed browser on headless server | Always use `headless=${HEADLESS}` variable |
| Cookies leak between tests | Same context reused | Create new context per test |

---

## Best Practices

1. **Always use variables for browser settings:**
   ```robotframework
   ${BROWSER}=    Set Variable If    ${CI}    chromium    firefox
   ```

2. **Close context between tests:**
   ```robotframework
   [Teardown]    Close Context
   ```

3. **Use headless on CI:**
   ```robotframework
   %{"HEADLESS"}    Get Environment Variable    HEADLESS    ${False}
   ```

4. **Set explicit timeouts for slow pages:**
   ```robotframework
   New Page    ${URL}    timeout=30s
   ```

---

## Self-Check Questions

1. What's the difference between `New Browser` and `New Context`?
2. How do you run browser in headless mode?
3. What does `headless=False` mean?
4. Why use `Close Context` instead of just `Close Browser`?

---

## Exercise: Basic Navigation

**Task:** Create a test that navigates through all pages of the application.

**Acceptance Criteria:**
- [ ] Opens http://localhost:8081
- [ ] Verifies FormPage is visible
- [ ] Navigates to Page2 (List)
- [ ] Navigates to Page3 (Orders)
- [ ] Navigates to Page4 (Dispatch)
- [ ] Returns to FormPage

**Starter Code:**
```robotframework
*** Settings ***
Library     Browser

*** Variables ***
${URL}       http://localhost:8081

*** Test Cases ***
Navigate Through All Pages
    [Documentation]    TODO: Implement navigation test
    # TODO: Your code here

*** Keywords ***
# TODO: Add helper keywords if needed
```

---

## Hints

### Hint 1
Think about which menu items you need to click. Check the Application Context for menu selectors.

### Hint 2
You need to:
1. Open browser and navigate to URL
2. Click menu items in order
3. Verify each page is loaded

### Hint 3
Use these selectors:
- `[data-testid="menu-item-Page2"]` - List page
- `[data-testid="menu-item-Page3"]` - Orders page
- `[data-testid="menu-item-Page4"]` - Dispatch page
- `[data-testid="menu-item-FormPage"]` - Back to form

### Hint 4
```robotframework
Navigate Through All Pages
    New Browser    chromium    headless=False
    New Context
    New Page       ${URL}

    Click    [data-testid="menu-item-Page2"]
    Wait For Elements State    [data-testid="page2Title"]    visible

    # TODO: Complete the rest
```

### Hint 5 (Full Solution)
```robotframework
*** Settings ***
Library     Browser

*** Variables ***
${URL}       http://localhost:8081
${TIMEOUT}   5s

*** Test Cases ***
Navigate Through All Pages
    [Documentation]    Navigates through all application pages
    [Tags]    beginner    navigation

    New Browser    chromium    headless=False
    New Context
    New Page       ${URL}

    # Verify starting on FormPage
    Wait For Elements State    [data-testid="form-page-container"]    visible    timeout=${TIMEOUT}

    # Navigate to Page2 (List)
    Click    [data-testid="menu-item-Page2"]
    Wait For Elements State    [data-testid="page2Title"]    visible    timeout=${TIMEOUT}

    # Navigate to Page3 (Orders)
    Click    [data-testid="menu-item-Page3"]
    Wait For Elements State    [data-testid="page3-title"]    visible    timeout=${TIMEOUT}

    # Navigate to Page4 (Dispatch)
    Click    [data-testid="menu-item-Page4"]
    Wait For Elements State    [data-testid="page4-title"]    visible    timeout=${TIMEOUT}

    # Return to FormPage
    Click    [data-testid="menu-item-FormPage"]
    Wait For Elements State    [data-testid="form-page-container"]    visible    timeout=${TIMEOUT}

    [Teardown]    Close Browser
```

---

## References

- [Browser Library Documentation](https://marketsquare.github.io/robotframework-browser/Browser.html)
- [Playwright Documentation](https://playwright.dev/docs/intro)
- Application UI: `/fe/mojeApp/src/component/pages/`
- Project example: `/RF/UI/common.resource`
