# Page Object Model (POM)

## Learning Objectives
- [ ] Understand Page Object Model pattern
- [ ] Create reusable page keywords
- [ ] Separate locators from logic
- [ ] Build maintainable test suites

## Prerequisites
- Completed BEGINNER Browser Library topics
- Know basic element interactions

---

## What is Page Object Model?

**Page Object Model (POM)** is a design pattern that creates an object-oriented abstraction for each page of your application.

**Benefits:**
- **Reusability**: Keywords shared across tests
- **Maintainability**: Changes in one place
- **Readability**: Tests read like business logic
- **Separation**: Locators separated from logic

**Without POM:**
```robotframework
# ❌ Everything in test file
*** Test Cases ***
Submit Form
    Fill Text    [data-testid="firstName-input"]    Jan
    Fill Text    [data-testid="lastName-input"]     Novák
    Fill Text    [data-testid="email-input"]        jan@test.cz
    Click    [data-testid="genderPicker"]
    Click    [data-testid="gender-option-male"]
    Click    [data-testid="submitButton"]
    Wait For Elements State    [data-testid="formSuccessModal"]    visible
```

**With POM:**
```robotframework
# ✅ Clean, readable test
*** Test Cases ***
Submit Form
    Fill First Name    Jan
    Fill Last Name     Novák
    Fill Email         jan@test.cz
    Select Gender      male
    Submit Form
    Verify Success
```

---

## POM Structure in This Project

```
RF/UI/
├── locators/              # Layer 1: Pure selector variables
│   ├── form_page_locators.resource
│   └── page2_locators.resource
├── pages/                 # Layer 2: Page-specific keywords
│   ├── form_page.resource
│   └── page2.resource
├── tests/                 # Layer 3: Test cases
│   └── new_form.robot
└── common.resource        # Shared utilities
```

**Separation of Concerns:**

| Layer | Responsibility | Example |
|-------|---------------|---------|
| **Locators** | Selector variables only | `${FORM_NAME_INPUT} = [data-testid="firstName-input"]` |
| **Pages** | Business logic keywords | `Fill First Name` keyword using locator |
| **Tests** | Test scenarios | `Submit Form With Valid Data` test case |
| **Common** | Shared utilities | `Click On The Element` with error handling |

---

## Layer 1: Locators

### Pure Variables, No Logic

```robotframework
*** Variables ***
# form_page_locators.resource

# Form inputs
${FORM_NAME_INPUT}         [data-testid="firstName-input"]
${FORM_LAST_NAME_INPUT}    [data-testid="lastName-input"]
${FORM_PHONE_INPUT}        [data-testid="phone-input"]
${FORM_EMAIL_INPUT}        [data-testid="email-input"]
${FORM_GENDER_PICKER}      [data-testid="genderPicker"]

# Gender options
@{MODAL_GENDER_PICKER}     [data-testid="gender-option-male"]
...                        [data-testid="gender-option-female"]
...                        [data-testid="gender-option-other"]

# Actions
${FORM_SUBMIT_BUTTON}      [data-testid="submitButton"]
${FORM_SUBMIT_MODAL_BTN}   [data-testid="formSuccessModal-primary"]
```

**Rules:**
- ✅ Only selector variables
- ✅ Descriptive names (uppercase convention)
- ❌ No logic or keywords
- ❌ No computations

**Benefits:**
- One place to update selectors
- Easy to search/find
- Can be used by multiple page files

---

## Layer 2: Page Keywords

### Business Logic Abstraction

```robotframework
*** Settings ***
Resource    ../locators/form_page_locators.resource
Resource    ../common.resource

*** Keywords ***
Fill First Name
    [Documentation]    Fills the first name input field
    [Arguments]    ${name}
    Fill Text In Input Field    ${FORM_NAME_INPUT}    ${name}

Fill Last Name
    [Documentation]    Fills the last name input field
    [Arguments]    ${name}
    Fill Text In Input Field    ${FORM_LAST_NAME_INPUT}    ${name}

Fill Email
    [Documentation]    Fills the email input field
    [Arguments]    ${email}
    Fill Text In Input Field    ${FORM_EMAIL_INPUT}    ${email}

Select Gender
    [Documentation]    Selects gender from dropdown
    [Arguments]    ${gender}    # male, female, other
    Click On The Element    ${FORM_GENDER_PICKER}
    ${option_locator}=    Set Variable    [data-testid="gender-option-${gender}"]
    Wait For Elements State    ${option_locator}    visible
    Click On The Element    ${option_locator}

Submit Form
    [Documentation]    Clicks submit button
    Click On The Element    ${FORM_SUBMIT_BUTTON}

Verify Success Modal
    [Documentation]    Verifies success modal is visible
    Wait For Elements State    [data-testid="formSuccessModal"]    visible
```

**Keyword Naming Conventions:**
- Verb + Noun: `Fill First Name`, `Submit Form`
- Action + Context: `Click Delete Button`, `Verify Success Message`
- Business language, not technical: `Select Gender` not `Click Gender Picker`

---

## Layer 3: Test Cases

### Clean, Readable Tests

```robotframework
*** Settings ***
Resource    ../pages/form_page.resource
Resource    ../variables.resource

*** Test Cases ***
Submit Form With Valid Data
    [Documentation]    Tests successful form submission
    [Tags]    smoke    form

    ${first_name}=    Set Variable    Jan
    ${last_name}=     Set Variable    Novák
    ${email}=         Set Variable    jan@test.cz
    ${phone}=         Set Variable    +420123456789

    # Setup
    Open Browser To Form Page

    # Fill form using page keywords
    Fill First Name       ${first_name}
    Fill Last Name        ${last_name}
    Fill Phone            ${phone}
    Fill Email            ${email}
    Select Gender         male

    # Submit and verify
    Submit Form
    Verify Success Modal

    # Cleanup
    [Teardown]    Close Browser
```

**Benefits:**
- Tests read like business requirements
- Easy to understand what's being tested
- Changes to UI don't affect test structure

---

## Complete POM Example

### Locators File

```robotframework
# locators/form_page_locators.resource
*** Variables ***
# Form inputs
${FORM_NAME_INPUT}         [data-testid="firstName-input"]
${FORM_LAST_NAME_INPUT}    [data-testid="lastName-input"]
${FORM_PHONE_INPUT}        [data-testid="phone-input"]
${FORM_EMAIL_INPUT}        [data-testid="email-input"]
${FORM_GENDER_PICKER}      [data-testid="genderPicker"]

# Additional fields
${FORM_INSTRUCTIONS}       [data-testid="instructions-textarea"]
${FORM_FILE_UPLOADER}      [data-testid="file-uploader-dropzone"]

# Buttons
${FORM_SUBMIT_BUTTON}      [data-testid="submitButton"]

# Modals
${FORM_SUCCESS_MODAL}      [data-testid="formSuccessModal"]
${FORM_SUCCESS_OK}         [data-testid="formSuccessModal-primary"]
```

### Page File

```robotframework
# pages/form_page.resource
*** Settings ***
Resource    ../locators/form_page_locators.resource
Resource    ../common.resource
Library     FakerLibrary

*** Keywords ***
# --- Input Fields ---

Fill First Name
    [Documentation]    Fill first name input
    [Arguments]    ${name}
    Fill Text In Input Field    ${FORM_NAME_INPUT}    ${name}    first_name

Fill Last Name
    [Documentation]    Fill last name input
    [Arguments]    ${name}
    Fill Text In Input Field    ${FORM_LAST_NAME_INPUT}    ${name}    last_name

Fill Phone
    [Documentation]    Fill phone input
    [Arguments]    ${phone}
    Fill Text In Input Field    ${FORM_PHONE_INPUT}    ${phone}    phone

Fill Email
    [Documentation]    Fill email input
    [Arguments]    ${email}
    Fill Text In Input Field    ${FORM_EMAIL_INPUT}    ${email}    email

Fill Instructions
    [Documentation]    Fill instructions textarea
    [Arguments]    ${instructions}
    Fill Text In Input Field    ${FORM_INSTRUCTIONS}    ${instructions}    instructions

# --- Gender Selection ---

Select Male
    [Documentation]    Select male gender
    Select Gender Option    male

Select Female
    [Documentation]    Select female gender
    Select Gender Option    female

Select Other
    [Documentation]    Select other gender
    Select Gender Option    other

Select Gender Option
    [Documentation]    Generic gender selection
    [Arguments]    ${gender}
    Click On The Element    ${FORM_GENDER_PICKER}    gender picker
    ${option}=    Set Variable    [data-testid="gender-option-${gender}"]
    Wait For Elements State    ${option}    visible    timeout=5s
    Click On The Element    ${option}    gender option ${gender}

# --- Actions ---

Submit Form
    [Documentation]    Submit the form
    Click On The Element    ${FORM_SUBMIT_BUTTON}    submit button

# --- Verification ---

Verify Success Modal Visible
    [Documentation]    Verify success modal is shown
    Wait For Elements State    ${FORM_SUCCESS_MODAL}    visible    timeout=10s

Click Success Modal OK
    [Documentation]    Click OK on success modal
    Click On The Element    ${FORM_SUCCESS_OK}    modal OK button

# --- High-Level Workflows ---

Fill Complete Form
    [Documentation]    Fill all required form fields
    [Arguments]    ${first_name}    ${last_name}    ${phone}    ${email}    ${gender}=male
    Fill First Name    ${first_name}
    Fill Last Name     ${last_name}
    Fill Phone         ${phone}
    Fill Email         ${email}
    Select Gender Option    ${gender}

Fill Form With Random Data
    [Documentation]    Fill form with Faker data
    ${first_name}=    FakerLibrary.First Name
    ${last_name}=     FakerLibrary.Last Name
    ${email}=         FakerLibrary.Email
    ${phone}=         FakerLibrary.Phone Number
    Fill Complete Form    ${first_name}    ${last_name}    ${phone}    ${email}
    [Return]    ${first_name}    ${last_name}    ${email}
```

### Test File

```robotframework
# tests/form_submission_tests.robot
*** Settings ***
Resource    ../pages/form_page.resource
Resource    ../variables.resource

*** Test Cases ***
Submit Form With Valid Data
    [Documentation]    Test successful form submission
    [Tags]    smoke    form    happy-path

    Open Browser To Form Page

    Fill First Name    Jan
    Fill Last Name     Novák
    Fill Phone         +420123456789
    Fill Email         jan@test.cz
    Select Male

    Submit Form
    Verify Success Modal Visible

    [Teardown]    Close Browser

Submit Form With Random Data
    [Documentation]    Test with randomly generated data
    [Tags]    regression    form

    Open Browser To Form Page

    ${first}    ${last}    ${email}=    Fill Form With Random Data
    Fill Phone    +420123456789
    Submit Form
    Verify Success Modal Visible

    Log    Created form for: ${first} ${last} (${email})

    [Teardown]    Close Browser
```

---

## Common Utilities (common.resource)

```robotframework
*** Settings ***
Library     Browser
Library     Collections

*** Keywords ***
Fill Text In Input Field
    [Documentation]    Enhanced fill with error handling
    [Arguments]    ${locator}    ${text}    ${context_name}=${EMPTY}

    ${context}=    Set Variable If    '${context_name}' == ${EMPTY}    field    ${context_name}

    TRY
        Wait For Elements State    ${locator}    visible    enabled    timeout=5s
        Fill Text    ${locator}    ${text}
        Log    Filled ${context} with: ${text}    level=INFO
    EXCEPT    AS    ${err}
        Take Screenshot    filename=fill_error_${context}.png
        Fail    Failed to fill ${context} (${locator}): ${err}
    END

Click On The Element
    [Documentation]    Enhanced click with error handling
    [Arguments]    ${locator}    ${context_name}=${EMPTY}

    ${context}=    Set Variable If    '${context_name}' == ${EMPTY}    element    ${context_name}

    TRY
        Wait For Elements State    ${locator}    attached    visible    enabled    timeout=5s
        Click    ${locator}
        Log    Clicked on ${context}    level=INFO
    EXCEPT    AS    ${err}
        Take Screenshot    filename=click_error_${context}.png
        Fail    Failed to click ${context} (${locator}): ${err}
    END
```

---

## Refactoring to POM

### Before (Flat Test)

```robotframework
*** Test Cases ***
Create Form And Verify
    New Browser    chromium    headless=False
    New Context
    New Page       http://localhost:8081

    Fill Text    [data-testid="firstName-input"]    Test
    Fill Text    [data-testid="lastName-input"]     User
    Fill Text    [data-testid="email-input"]        test@user.com
    Fill Text    [data-testid="phone-input"]        +420123456789

    Click    [data-testid="genderPicker"]
    Click    [data-testid="gender-option-male"]

    Click    [data-testid="submitButton"]

    Wait For Elements State    [data-testid="formSuccessModal"]    visible
```

### After (POM)

```robotframework
# locators/form_page_locators.resource
${FORM_NAME_INPUT}      [data-testid="firstName-input"]
${FORM_LAST_NAME_INPUT} [data-testid="lastName-input"]
${FORM_EMAIL_INPUT}     [data-testid="email-input"]
${FORM_PHONE_INPUT}     [data-testid="phone-input"]
${FORM_GENDER_PICKER}   [data-testid="genderPicker"]
${GENDER_MALE}          [data-testid="gender-option-male"]
${FORM_SUBMIT}          [data-testid="submitButton"]
${SUCCESS_MODAL}        [data-testid="formSuccessModal"]

# pages/form_page.resource
*** Keywords ***
Fill Form Data
    [Arguments]    ${first}    ${last}    ${email}    ${phone}
    Fill Text    ${FORM_NAME_INPUT}      ${first}
    Fill Text    ${FORM_LAST_NAME_INPUT} ${last}
    Fill Text    ${FORM_EMAIL_INPUT}     ${email}
    Fill Text    ${FORM_PHONE_INPUT}     ${phone}

Select Gender Male
    Click    ${FORM_GENDER_PICKER}
    Click    ${GENDER_MALE}

Submit Form
    Click    ${FORM_SUBMIT}

Verify Success
    Wait For Elements State    ${SUCCESS_MODAL}    visible

# tests/form_test.robot
*** Test Cases ***
Create Form And Verify
    [Setup]    Open Browser
    Fill Form Data    Test    User    test@user.com    +420123456789
    Select Gender Male
    Submit Form
    Verify Success
    [Teardown]   Close Browser
```

---

## Self-Check Questions

1. What are the three layers of POM in this project?
2. Why separate locators from page keywords?
3. What belongs in locators vs pages vs tests?
4. How do POM keywords improve test readability?

---

## Exercise: Convert Test to POM

**Task:** Refactor a flat test to use POM structure.

**Before (Flat):**
```robotframework
*** Test Cases ***
Navigate And Fill List
    New Browser    chromium    headless=False
    New Context
    New Page    http://localhost:8081

    Click    [data-testid="menu-item-Page2"]
    Wait For Elements State    [data-testid="page2Title"]    visible
    Wait For Elements State    [data-testid="page2-loading-container"]    hidden
    Get Element Count    [data-testid^="list-item-"]    >    0
```

**Acceptance Criteria:**
- [ ] Create locators resource file
- [ ] Create page keywords
- [ ] Refactor test to use keywords
- [ ] Follow project conventions

---

## Best Practices z Komunity

### Overview

Tato sekce shrnuje best practices pro Page Object Model v Robot Framework Browser Library získané z komunitních zdrojů:

- **Context7** - Oficiální Browser Library dokumentace
- **icehousecorp.com** - Firemní best practices
- **testersdock.com** - Python-based POM přístup
- **VALA Group** - Browser vs Selenium srovnání
- **BrowserPOM** - Python extension pro POM

---

### Comparison of POM Approaches

Existují 3 hlavní přístupy k POM v Robot Framework:

| Aspect | Robot .resource POM | Python POM | BrowserPOM Extension |
|--------|---------------------|------------|----------------------|
| **Jazyk** | Robot Framework | Python | Python |
| **Struktura** | locators.resource + pages.resource | Locators.py + TestData.py + .robot | PageObject class + UIObject |
| **Složitost** | Nejnižší | Střední | Nejvyšší |
| **Python znalost** | Není potřeba | Potřebná | Pokročilá |
| **Typování** | Dynamické | Statické (Python) | Statické (Python) |
| **IDE Support** | Omezený | Vynikající | Vynikající |
| **Údržba** | Jednoduchá | Střední | Složitější |
| **Pro koho** | Začátečníci, týmy bez Python | Zkušení autokřižáci | Vývojáři |

**Robot .resource POM** (co používáš):
```robotframework
# locators/form_page_locators.resource
*** Variables ***
${FORM_NAME_INPUT}    [data-testid="firstName-input"]

# pages/form_page.resource
*** Keywords ***
Fill First Name
    [Arguments]    ${name}
    Fill Text In Input Field    ${FORM_NAME_INPUT}    ${name}
```

**Python POM** (testersdock):
```python
# Locators.py
LOGIN_USERNAME = "id:txtUsername"
LOGIN_PASSWORD = "id:txtPassword"

# LoginPage.robot
*** Keywords ***
Input Username
    [Arguments]    ${username}
    Input Text    ${LOGIN_USERNAME}    ${username}
```

**BrowserPOM** (Python extension):
```python
from BrowserPOM import PageObject, UIObject

class MainPage(PageObject):
    PAGE_URL = "/index.html"
    search_bar = UIObject("//input[@id='searchBar']")

    @keyword
    def enter_search(self, search):
        self.browser.type_text(str(self.search_bar), search)
```

---

### Key Findings from Community

#### 1. DRY Principle (Don't Repeat Yourself)
**Zdroj:** icehousecorp.com

Opakující se bloky kódu zabalit do higher-level keywords.

**❌ Bad:**
```robotframework
Click On The Element    ${locator}
Wait For Elements State    ${locator}    visible
Click On The Element    ${another_locator}
Wait For Elements State    ${another_locator}    visible
```

**✅ Good:**
```robotframework
Click And Verify    ${locator}
Click And Verify    ${another_locator}

*** Keywords ***
Click And Verify
    [Arguments]    ${locator}
    Click On The Element    ${locator}
    Wait For Elements State    ${locator}    visible
```

#### 2. Parametrizace Keywords
**Zdroj:** icehousecorp.com

Keywords by měly být flexibilní - přijímat parametry místo hardcoding.

**❌ Bad:**
```robotframework
Fill Valid Login Data
    Fill Text    [data-testid="email"]    test@user.com
    Fill Text    [data-testid="password"]    password123
```

**✅ Good:**
```robotframework
Fill Login Data
    [Arguments]    ${email}    ${password}
    Fill Text    [data-testid="email"]    ${email}
    Fill Text    [data-testid="password"]    ${password}
```

#### 3. Implicit Wait místo Sleep
**Zdroj:** icehousecorp.com, VALA Group

Vždy čekat na element stav, ne pevný čas.

**❌ Bad:**
```robotframework
Sleep    3s
Click    [data-testid="button"]
```

**✅ Good:**
```robotframework
Wait For Elements State    [data-testid="button"]    visible    enabled    timeout=5s
Click    [data-testid="button"]
```

#### 4. Documentation Efficiency
**Zdroj:** icehousecorp.com

Používat `[Documentation]` efektivně - neopakovat název souboru.

**❌ Bad:**
```robotframework
[Documentation]    This file contains keywords for the form page.
```

**✅ Good:**
```robotframework
[Documentation]    Form page keywords for user registration and submission.
    ...    Includes validation, error handling, and data loading from JSON.
```

#### 5. Tags pro Selektivní Spouštění
**Zdroj:** icehousecorp.com

Používat tags pro organizaci testů.

```robotframework
*** Test Cases ***
Submit Valid Form
    [Tags]    smoke    regression    happy-path
    # Test steps...

Submit Invalid Email
    [Tags]    regression    validation    negative
    # Test steps...
```

Spouštění:
```bash
# Pouze smoke testy
robot --include smoke tests/

# Vše kromě negative
robot --exclude negative tests/
```

#### 6. Variables ve Variables
**Zdroj:** icehousecorp.com

Proměnné mohou obsahovat jiné proměnné pro multi-environment podporu.

```robotframework
*** Variables ***
${env}    ${EMPTY}
&{URLS}    STAGE=http://staging.example.com
...        PROD=http://prod.example.com

*** Keywords ***
Open Login Page
    ${url}=    Set Variable    ${URLS}[${env}]
    New Page    ${url}
```

Spouštění:
```bash
robot -v env:STAGE tests/
robot -v env:PROD tests/
```

---

### Checklist pro Hodnocení POM Implementace

Použij tento checklist k hodnocení své POM implementace:

#### Struktura (Structure)
- [ ] Locators jsou odděleny od business logiky
- [ ] Každá stránka má svůj vlastní soubor
- [ ] Common keywords jsou v samostatném souboru
- [ ] Test cases jsou odděleny od page keywords

#### Locators
- [ ] Používáš `data-testid` selektory
- [ ] Lokátory jsou v samostatném `.resource` souboru
- [ ] Názvy lokátorů jsou popisné a konzistentní
- [ ] Žádné hardcoded selektory v testech

#### Page Keywords
- [ ] Keywords mají smysluplné názvy (verb + noun)
- [ ] Keywords jsou parametrizované
- [ ] Opakující se logika je zabalena do higher-level keywords
- [ ] Keywords mají dokumentaci

#### Error Handling
- [ ] Používáš TRY-EXCEPT pattern
- [ ] Screenshot při selhání
- [ ] Smyšlené chybové zprávy s kontextem
- [ ] Implicit wait před akcemi

#### Test Organization
- [ ] Testy používají Tags
- [ ] Test Setup/Teardown definován
- [ ] Testy čitelné jako business scénáře
- [ ] Žádný duplicitní kód

#### Maintainability
- [ ] Jeden zdroj pravdy pro každý element
- [ ] Změna selectoru vyžaduje úpravu na jednom místě
- [ ] Sdílené utilities v common.resource
- [ ] Test data externalizovaná

---

### Community Sources

#### Oficiální Dokumentace
- **[Browser Library](https://marketsquare.github.io/robotframework-browser/)** - Oficiální dokumentace s příklady
- **[Playwright Selectors](https://playwright.dev/docs/selectors/)** - Podporované selektory a strategie

#### Blogy a Články
- **[Ice House Indonesia - POM Best Practices](https://icehousecorp.com/test-automation-with-robot-framework-page-object-model-best-practices/)** - DRY, parametrizace, implicit wait
- **[VALA Group - Browser Library](https://valagroup.medium.com/turning-the-page-on-front-end-automation-robot-framework-browser-library-2cd3e8a8dd74)** - Browser vs Selenium, rychlost, device descriptors
- **[TestersDock - POM Implementation](https://testersdock.com/robot-framework-page-object-model/)** - Python-based POM se složkami

#### GitHub Projekty
- **[robotframework-browser](https://github.com/marketsquare/robotframework-browser)** - Oficiální Browser Library repo
- **[robotframework-browserpom](https://github.com/hasanalpzengin/robotframework-browserpom)** - Python POM extension
- **[ncbi/robotframework-pageobjects](https://github.com/ncbi/robotframework-pageobjects)** - POM knihovna od NCBI

#### Komunita
- **[Robot Framework Slack](https://robotframework-slack-invite.herokuapp.com/)** - Aktivní komunita pro pomoc
- **[Robot Framework Forum](https://forum.robotframework.org/)** - Oficiální fórum

---

### Tvoje Implementace vs Best Practices

**Co už děláš správně:**
- ✅ Oddělené locators/ a pages/ složky
- ✅ common.resource se sdílenými utilities
- ✅ TRY-EXCEPT error handling
- ✅ `data-testid` selektory
- ✅ Screenshot při selhání
- ✅ Test Tags

**Co můžeš vylepšit:**
- 🔄 Zvážit Python POM pro větší projekty
- 🔄 Přidat více implicit waits do page keywords
- 🔄 Používat variables ve variables pro environment switching

---

## References

- Project POM: `/RF/UI/locators/`, `/RF/UI/pages/`
- Locators example: `/RF/UI/locators/form_page_locators.resource`
- Page example: `/RF/UI/pages/form_page.resource`
- Test example: `/RF/UI/tests/new_form.robot`
