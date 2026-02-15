# Mobile Testing Basics with Appium

## Learning Objectives
- [ ] Understand mobile testing concepts
- [ ] Set up Appium environment
- [ ] Run tests on mobile devices/emulators
- [ ] Use mobile-specific interactions

## Prerequisites
- Completed Browser Library topics
- Android/iOS knowledge helpful

---

## What is Appium?

**Appium** is an open-source automation framework for:
- Native mobile apps (Android, iOS)
- Hybrid mobile apps
- Mobile web apps

**Key Features:**
- Cross-platform (write once, test both Android & iOS)
- Uses WebDriver protocol (same as Selenium)
- Supports multiple programming languages
- Doesn't require app source code modification

**Appium vs Browser Library:**
| Feature | Browser Library | Appium |
|---------|----------------|---------|
| Target | Web browsers | Mobile apps |
| Technology | Playwright | WebDriver |
| Use Case | Web UI testing | Mobile app testing |

---

## Appium Setup

### Install Appium

```bash
# Install Appium server
npm install -g appium

# Install driver (Android)
appium driver install uiautomator2

# For iOS (macOS only)
appium driver install xcuitest
```

### Install Python Client

```bash
pip install Appium-Python-Client
```

### Start Appium Server

```bash
# Start server (default port 4723)
appium

# Or with custom port
appium -p 4724
```

---

## Device Configuration

### Android Emulator Setup

```robotframework
*** Settings ***
Library     AppiumLibrary

*** Variables ***
${PLATFORM_NAME}      Android
${DEVICE_NAME}        emulator-5554
${APP_PACKAGE}        com.example.app
${APP_ACTIVITY}       MainActivity
${AUTOMATION_NAME}     UiAutomator2
${PLATFORM_VERSION}   12

*** Test Cases ***
Launch Android App
    Open Application    http://localhost:4723/wd/hub    ${REMOTE_URL}
    ...    platformName=${PLATFORM_NAME}
    ...    deviceName=${DEVICE_NAME}
    ...    appPackage=${APP_PACKAGE}
    ...    appActivity=${APP_ACTIVITY}
    ...    automationName=${AUTOMATION_NAME}
```

### iOS Simulator Setup

```robotframework
*** Variables ***
${PLATFORM_NAME}      iOS
${DEVICE_NAME}        iPhone 14
${PLATFORM_VERSION}   16.0
${BUNDLE_ID}          com.example.MyApp

*** Test Cases ***
Launch iOS App
    Open Application    http://localhost:4723/wd/hub    ${REMOTE_URL}
    ...    platformName=${PLATFORM_NAME}
    ...    deviceName=${DEVICE_NAME}
    ...    bundleId=${BUNDLE_ID}
    ...    platformVersion=${PLATFORM_VERSION}
```

---

## Remote URL Configuration

### Local Appium Server

```robotframework
*** Variables ***
${REMOTE_URL}    http://localhost:4723/wd/hub
```

### Cloud Services (BrowserStack, Sauce Labs)

```robotframework
*** Variables ***
${REMOTE_URL}    https://USERNAME:ACCESS_KEY@hub-cloud.browserstack.com/wd/hub
```

---

## Mobile-Specific Interactions

### Tap/Click

```robotframework
# Tap element
Click Element    id=submit_button

# Tap at coordinates
Tap    ${x}    ${y}

# Long press
Long Press    id=element    1000    # duration in ms
```

### Swipe Gestures

```robotframework
*** Keywords ***
Swipe Down
    [Documentation]    Swipe down on screen
    ${width}=    Get Window Width
    ${height}=   Get Window Height

    ${start_x}=    Set Variable    ${width} / 2
    ${start_y}=    Set Variable    ${height} * 0.2
    ${end_x}=      Set Variable    ${width} / 2
    ${end_y}=      Set Variable    ${height} * 0.8

    Swipe    ${start_x}    ${start_y}    ${end_x}    ${end_y}    1000
```

### Scroll

```robotframework
# Scroll to element
${element_id}=    Set Variable    id=scroll_target
Scroll    ${element_id}

# Scroll into view (Appium 2+)
${element}=    Scroll To Element    id=footer
```

### Input Text

```robotframework
# Text input
Input Text    id=email_field    user@example.com

# Clear and input
Input Text    id=search_field    query    clear=${True}

# Password input
Input Password    id=password_field    secret123
```

---

## Application Contexts

### Hybrid Apps (WebView)

```robotframework
*** Test Cases ***
Switch To WebView
    # Get all contexts
    ${contexts}=    Get Contexts

    # Switch to WEBVIEW
    Switch To Context    WEBVIEW_1

    # Now use web commands
    Click Element    css=.submit-button

    # Switch back to NATIVE
    Switch To Context    NATIVE_APP
```

### Handling Multiple Windows

```robotframework
*** Test Cases ***
Handle Multiple Windows
    ${window_handles}=    Get Window Handles

    # Switch to specific window
    Switch To Window    ${window_handles}[1]
```

---

## Mobile Locators

### Android Locators

```robotframework
# ID
id=submit_button

# Accessibility
accessibility=Submit

# XPath
//android.widget.Button[@text='Submit']

# UIAutomator
android=new UiSelector().text("Submit")
```

### iOS Locators

```robotframework
# ID
id=submitButton

# Label
ios=label == "Submit"

# Predicate string
ios=predicate == "label == 'Submit'"

# Chain
ios=chain(name == "Button" && value == "Submit")
```

### Cross-Platform Locators

```robotframework
# Strategy: First available strategy wins

# By ID
id=submit_button

# By XPath (cross-platform)
//button[@text="Submit"]

# By accessibility id
accessibility=SubmitButton
```

---

## Application Examples

### Example 1: Basic Mobile Test

```robotframework
*** Settings ***
Library     AppiumLibrary

*** Variables ***
${PLATFORM_NAME}      Android
${APP_PACKAGE}        com.example.mojeapp
${REMOTE_URL}         http://localhost:4723/wd/hub

*** Test Cases ***
Open App And Verify
    [Documentation]    Opens mobile app and verifies main screen

    Open Application    ${REMOTE_URL}
    ...    platformName=${PLATFORM_NAME}
    ...    appPackage=${APP_PACKAGE}

    # Wait for app to load
    Wait Until Page Contains Element    id=main_container

    # Verify main screen
    Page Should Contain Element    id=welcome_text
    Page Should Contain Element    id=start_button

    [Teardown]    Close Application
```

### Example 2: Form Testing

```robotframework
*** Test Cases ***
Fill Mobile Form
    [Documentation]    Fill form on mobile device

    Open Application    ${REMOTE_URL}    ...    (capabilities)

    # Input fields
    Input Text    id=first_name    Jan
    Input Text    id=last_name     Novák
    Input Text    id=email         jan@test.cz

    # Hide keyboard
    Hide Keyboard

    # Submit
    Click Element    id=submit_button

    # Verify success
    Wait Until Page Contains    Success

    [Teardown]    Close Application
```

### Example 3: Swipe and Scroll

```robotframework
*** Keywords ***
Scroll To Element
    [Documentation]    Scroll until element is visible
    [Arguments]    ${locator}

    ${visible}=    Run Keyword And Return Status
    ...    Page Should Contain Element    ${locator}

    FOR    ${i}    IN RANGE    10
        Exit For Loop If    ${visible}

        Swipe    500    800    500    200    1000
        ${visible}=    Run Keyword And Return Status
        ...    Page Should Contain Element    ${locator}
    END

*** Test Cases ***
Scroll And Find Element
    Open Application    ${REMOTE_URL}    ...    (capabilities)

    Scroll To Element    id=footer_element

    Page Should Contain Element    id=footer_element

    [Teardown]    Close Application
```

---

## Common Pitfalls

| Pitfall | Why Happens | Fix |
|---------|------------|-----|
| App not found | Wrong appPackage/bundleId | Verify app package name |
| Element not found | Wrong locator strategy | Use inspector to find correct locator |
| Keyboard covers input | Keyboard not dismissed | Call Hide Keyboard after input |
| Context issues | In NATIVE vs WEBVIEW | Switch to correct context |
| Session not created | Appium server not running | Start Appium server |

---

## Best Practices

1. **Use cross-platform locators when possible:**
   ```robotframework
   # Good
   id=submit_button

   # Avoid (platform-specific)
   //android.widget.Button[@text='Submit']
   ```

2. **Wait for elements explicitly:**
   ```robotframework
   Wait Until Element Is Visible    id=result
   ```

3. **Handle keyboard properly:**
   ```robotframework
   Hide Keyboard
   ```

4. **Clean up sessions:**
   ```robotframework
   [Teardown]    Close Application
   ```

---

## Self-Check Questions

1. What's the difference between Browser Library and Appium?
2. How do you switch between NATIVE and WEBVIEW contexts?
3. What's the Remote URL for local Appium server?
4. How do you handle keyboard on mobile devices?

---

## Exercise: Basic Mobile Test

**Task:** Create a simple mobile test that opens app and verifies elements.

**Scenario:**
1. Open mobile app
2. Verify main screen elements
3. Fill a form field
4. Submit form
5. Verify success

**Acceptance Criteria:**
- [ ] Opens app with correct capabilities
- [ ] Verifies main screen elements
- [ ] Fills form field
- [ ] Handles keyboard
- [ ] Verifies success state

**Starter Code:**
```robotframework
*** Settings ***
Library     AppiumLibrary

*** Variables ***
${REMOTE_URL}    http://localhost:4723/wd/hub
${PLATFORM}      Android

*** Test Cases ***
Basic Mobile Test
    [Documentation]    TODO: Implement mobile test
    # TODO: Your code here

*** Keywords ***
# TODO: Add helper keywords
```

---

## Hints

### Hint 1
Capabilities needed: platformName, deviceName, appPackage, automationName.

### Hint 2
Pattern: Open App → Wait for elements → Interact → Verify → Close App

### Hint 3
```robotframework
Basic Mobile Test
    Open Application    ${REMOTE_URL}
    ...    platformName=${PLATFORM}
    ...    deviceName=emulator-5554
    ...    appPackage=com.example.app
    ...    automationName=UiAutomator2

    Wait Until Page Contains Element    id=main_container
    # TODO: Complete the test
```

### Hint 4 (Full Solution)
```robotframework
*** Settings ***
Library     AppiumLibrary

*** Variables ***
${REMOTE_URL}         http://localhost:4723/wd/hub
${PLATFORM_NAME}       Android
${DEVICE_NAME}         emulator-5554
${APP_PACKAGE}         com.example.mojeapp
${APP_ACTIVITY}        MainActivity
${AUTOMATION_NAME}     UiAutomator2

*** Test Cases ***
Basic Mobile Test
    [Documentation]    Basic mobile app test
    [Tags]    beginner    mobile

    # Open app
    Open Application    ${REMOTE_URL}
    ...    platformName=${PLATFORM_NAME}
    ...    deviceName=${DEVICE_NAME}
    ...    appPackage=${APP_PACKAGE}
    ...    appActivity=${APP_ACTIVITY}
    ...    automationName=${AUTOMATION_NAME}

    # Verify main screen
    Wait Until Page Contains Element    id=main_container
    Page Should Contain Element    id=welcome_text

    # Fill form
    Input Text    id=name_field    Mobile Test

    # Hide keyboard
    Hide Keyboard

    # Submit
    Click Element    id=submit_button

    # Verify success
    Wait Until Page Contains    Success

    [Teardown]    Close Application
```

---

## References

- [Appium Documentation](https://appium.io/docs/en/latest/)
- [AppiumLibrary for Robot Framework](https://github.com/serhatbolsu/robotframework-appiumlibrary)
- [Appium Inspector](https://appium.github.io/appium-inspector/)
- Project mobile setup: `/fe/mojeApp/`
