# Advanced Locators and Selector Strategies

## Learning Objectives
- [ ] Master CSS selectors
- [ ] Use XPath effectively
- [ ] Handle dynamic elements
- [ ] Choose optimal selector strategies

## Prerequisites
- Completed BEGINNER topics
- Know basic element finding

---

## Selector Strategy Priority

**Best to Worst:**

1. **data-testid** (Recommended) ⭐
   ```
   [data-testid="firstName-input"]
   ```
   - Stable, semantic, purpose-built for testing

2. **ID Selector**
   ```
   #firstName-input
   ```
   - Usually stable, but can be auto-generated

3. **Name Attribute**
   ```
   [name="firstName"]
   ```
   - Reasonably stable for forms

4. **Class Selector**
   ```
   .submit-button
   ```
   - Can change with CSS refactoring

5. **Text Content**
   ```
   "Submit"
   ```
   - Fragile with translations/changes

6. **XPath** ⚠️
   ```
   //button[@type="submit"]
   ```
   - Fragile, complex, hard to maintain

---

## data-testid Best Practice

### Define in Application

```javascript
// React component
<input
  data-testid="firstName-input"
  type="text"
  name="firstName"
  className="form-input input-text"
  id="firstName"  // Auto-generated, may change
/>
```

### Use in Tests

```robotframework
# Good - stable
${FIRST_NAME}=    Set Variable    [data-testid="firstName-input"]

# Bad - fragile
${FIRST_NAME}=    Set Variable    .form-input:first-child
```

### Naming Convention

```robotframework
# Pattern: [data-testid="<page>-<component>-<element>"]

# Form page
[data-testid="form-page-container"]
[data-testid="form-first-name-input"]
[data-testid="form-submit-button"]

# List page
[data-testid="list-container"]
[data-testid="list-item-123-name"]   # Dynamic ID
[data-testid="list-refresh-button"]
```

---

## CSS Selectors Deep Dive

### Basic Selectors

```robotframework
# Element type
button
input
div

# ID
#submit-button

# Class
.submit-button
.form-input

# Attribute
[type="submit"]
[data-testid="firstName-input"]

# Combined
button.submit-button
input[type="email"]
[data-testid="form"] > button
```

### Hierarchy Selectors

```robotframework
# Descendant (any level)
[data-testid="form"] [data-testid="submit-button"]

# Direct child (immediate child only)
[data-testid="form"] > [data-testid="submit-button"]

# Adjacent sibling
[data-testid="label"] + [data-testid="input"]

# General sibling
[data-testid="label"] ~ [data-testid="input"]
```

### Combinators

```robotframework
# AND (multiple conditions)
input[type="email"].required

[data-testid="form"] .active.visible

# OR (comma separated)
button#submit, button#save

# NOT
:not(.hidden)
:not([disabled])
```

### Pseudo-classes

```robotframework
# Position
:first-child
:last-child
:nth-child(2)
:nth-of-type(3)

# State
:checked
:disabled
:enabled
:focus
:visible
```

---

## Attribute Selectors

### Exact Match

```robotframework
# Exact value
[data-testid="submit-button"]
[type="submit"]
[class="btn primary"]

# Multiple attributes
input[name="email"][type="email"][required]
```

### Partial Match

```robotframework
# Starts with
[data-testid^="list-item-"]         # list-item-1, list-item-2
[class^="btn-"]                     # btn-primary, btn-secondary

# Ends with
[data-testid$="-name"]               # item-name, user-name
[class$="-button"]                  # submit-button, cancel-button

# Contains
[data-testid*="submit"]              # submit-button, form-submit-btn
[class*="active"]                    # active-item, active-page
```

---

## Dynamic Elements

### Dynamic IDs

```robotframework
# Problem: ID changes each time
<div id="item-12345">...</div>
<div id="item-67890">...</div>

# Solution: Partial match
[data-testid^="item-"]

# Solution: Attribute contains
[id^="item-"]
[id*="item"]
```

### Dynamic Classes

```robotframework
# Problem: Dynamic classes
<div class="item active-12345 visible">...</div>

# Solution: Stable attribute
[data-testid="item-12345"]

# Solution: Partial class match
[class*="item"]
[class^="item"][class*="active"]
```

### Index-Based Selection

```robotframework
# Get nth matching element
[data-testid^="list-item-"] >> nth=0
[data-testid^="list-item-"] >> nth=1

# Last element
[data-testid^="list-item-"] >> nth=-1

# All elements (in loop)
${count}=    Get Element Count    [data-testid^="list-item-"]
FOR    ${i}    IN RANGE    ${count}
    ${element}=    Get Element    [data-testid^="list-item-"] >> nth=${i}
    # Process element
END
```

---

## XPath Selectors

### When to Use XPath

XPath is **fragile** but sometimes necessary:
- When no stable attributes exist
- Complex traversal needed
- Text-based selection

### Basic XPath

```robotframework
# Any element
//button

# Element with attribute
//button[@type="submit"]

# Text content
//button[text()="Submit"]

# Contains text
//button[contains(text(), "Submit")]

# Contains attribute
//input[contains(@data-testid, "name")]
```

### Hierarchy XPath

```robotframework
# Descendant
//form[@id="login-form"]//input

# Child
//form[@id="login-form"]/input

# Following sibling
//label/following-sibling::input

# Preceding sibling
//input/preceding-sibling::label

# Parent
//button/parent::form
```

### Advanced XPath

```robotframework
# Position
//li[1]
//li[last()]
//li[position()=2]

# Multiple conditions
//input[@type="email" and @required]
//button[@disabled or @readonly]

# Contains with attribute
//*[contains(@class, "submit")]

# Text matching
//*[text()="Submit Form"]
//*[contains(text(), "Submit")]
```

### XPath vs CSS

| Task | CSS | XPath |
|------|-----|-------|
| ID | `#id` | `//*[@id="id"]` |
| Class | `.class` | `//*[contains(@class, "class")]` |
| Attribute | `[attr="val"]` | `//*[@attr="val"]` |
| Child | `parent > child` | `//parent/child` |
| Text content | Not native | `//*[text()="val"]` |

---

## Practical Selector Examples

### Form Elements

```robotframework
# Input by testid
[data-testid="firstName-input"]

# Input by name (fallback)
[name="firstName"]

# Checkbox by state
[data-testid="agree-terms"][checked]
input[type="checkbox"]:checked

# Radio button
input[name="gender"][value="male"]:checked

# Select dropdown
select[name="country"] > option[value="CZ"]
```

### Buttons and Links

```robotframework
# Submit button
button[type="submit"]
[data-testid="submit-button"]

# Link by href
a[href="/page2"]
a[href*="/page"]

# Link by text
a >> "Click here"
//a[text()="Click here"]

# Button with icon
button >> svg.icon-check
```

### Lists and Tables

```robotframework
# List items
[data-testid^="list-item-"]
ul.items > li

# Table rows
table#users tbody tr
[data-testid="user-row"]

# Specific cell
table#users tr[data-user-id="123"] td[data-column="email"]
```

### Dynamic Content

```robotframework
# Loading indicator (appears/disappears)
[data-testid="loading"]

# Error message
[data-testid="error-message"]
.alert-error

# Success toast
.toast-success >> "Operation completed"
```

---

## Application-Specific Selectors

### Form Page

```robotframework
# Form container
[data-testid="form-page-container"]

# All inputs
[data-testid="firstName-input"]
[data-testid="lastName-input"]
[data-testid="phone-input"]
[data-testid="email-input"]

# Gender dropdown
[data-testid="genderPicker"]
[data-testid="gender-option-male"]
[data-testid="gender-option-female"]
[data-testid="gender-option-other"]

# Submit
[data-testid="submitButton"]
```

### Page2 (List)

```robotframework
# List container
[data-testid="list-container"]

# List items (dynamic)
[data-testid^="list-item-"]
[data-testid^="list-item-"][data-testid$="-name"]
[data-testid^="list-item-"][data-testid$="-email"]

# Actions per item
[data-testid^="list-item-"][data-testid$="-delete"]

# Empty state
[data-testid="list-empty-state"]
```

### Page3 (Orders)

```robotframework
# Orders list
[data-testid="orders-list"]

# Order cards
[data-testid^="order-card-"]

# Status badges
[data-testid^="order-status-"]

# Stats
[data-testid="stat-box-total"]
[data-testid="stat-box-pending"]
```

### Page4 (Dispatch)

```robotframework
# Split view
[data-testid="dispatch-split-view"]

# Pending orders
[data-testid="pending-orders-section"]
[data-testid^="pending-order-card-"]

# Couriers
[data-testid="available-couriers-section"]
[data-testid^="courier-card-"]
```

---

## Selector Optimization

### Good vs Bad

```robotframework
# ❌ BAD - Too specific, fragile
html body div#app div.container form.form-horizontal div.form-group input.form-control.input-text

# ❌ BAD - Index-based, breaks with UI changes
div.form-group > input:nth-child(1)

# ✅ GOOD - Stable testid
[data-testid="firstName-input"]

# ✅ GOOD - Semantic but still specific
form[data-testid="login-form"] > input[name="email"]

# ✅ GOOD - Attribute-based
input[type="email"][required]
```

### Selector Performance

| Selector | Speed | Notes |
|----------|-------|-------|
| ID (`#id`) | Fastest | Native browser optimization |
| Class (`.class`) | Fast | Good performance |
| Attribute (`[attr]`) | Medium | Depends on complexity |
| data-testid | Medium | Slightly slower than ID |
| XPath | Slowest | Complex evaluation |

---

## Self-Check Questions

1. What's the recommended selector strategy?
2. When should you use XPath?
3. How do you select elements with dynamic IDs?
4. What's the difference between `>` and space in CSS selectors?

---

## Exercise: Create Locators File

**Task:** Create a locators resource file for Page2 (List page).

**Acceptance Criteria:**
- [ ] Define all list page selectors
- [ ] Use data-testid when available
- [ ] Follow naming convention
- [ ] Group by functionality

**Starter Code:**
```robotframework
# locators/page2_locators.resource
*** Variables ***
# TODO: Add selectors for:
# - Page title
# - List container
# - List items
# - Actions
# - Modals
```

---

## Hints

### Hint 1
Review Application Context for available data-testids on Page2.

### Hint 2
You need selectors for:
- Page title (`page2Title`)
- Loading container
- List container
- List items (dynamic)
- Refresh button
- Back button
- Detail modal

### Hint 3
```robotframework
*** Variables ***
# Page title
${PAGE2_TITLE}            [data-testid="page2Title"]

# Loading
${PAGE2_LOADING}          [data-testid="page2-loading-container"]
${PAGE2_LOADING_TEXT}     [data-testid="page2-loading-text"]

# List
${LIST_CONTAINER}         [data-testid="list-container"]
${LIST_EMPTY_STATE}       [data-testid="list-empty-state"]

# List items (dynamic)
${LIST_ITEMS_TEXT}        [data-testid^="list-item-"][data-testid$="-name"]
${LIST_ITEMS_ID}          [data-testid^="list-item-"][data-testid$="-id"]

# TODO: Add actions and modal selectors
```

### Hint 4 (Full Solution)
```robotframework
# locators/page2_locators.resource
*** Variables ***
# Page title and container
${PAGE2_TITLE}            [data-testid="page2Title"]
${PAGE2_CONTAINER}        [data-testid="page2Title"]    # Same element

# Loading states
${PAGE2_LOADING}          [data-testid="page2-loading-container"]
${PAGE2_LOADING_TEXT}     [data-testid="page2-loading-text"]

# List container
${LIST_CONTAINER}         [data-testid="list-container"]
${LIST_EMPTY_STATE}       [data-testid="list-empty-state"]

# List items (dynamic selectors)
${LIST_ITEMS_TEXT}        [data-testid^="list-item-"][data-testid$="-name"]
${LIST_ITEMS_ID}          [data-testid^="list-item-"][data-testid$="-id"]
${LIST_ITEMS_CHECKBOX}    [data-testid^="list-item-"][data-testid$="-checkbox"]
${LIST_ITEMS_DELETE}      [data-testid^="list-item-"][data-testid$="-delete"]

# Actions
${REFRESH_BUTTON}         [data-testid="refreshButton"]
${BACK_BUTTON}            [data-testid="backButton"]

# Detail modal
${INFO_MODAL}             [data-testid="info-modal"]
${INFO_MODAL_EMAIL}       [data-testid="info-email-value"]
${INFO_MODAL_OK}          [data-testid="info-modal-ok"]

# Delete confirmation modal
${DELETE_MODAL}           [data-testid="deleteConfirmModal"]
${DELETE_CONFIRM}         [data-testid="deleteConfirmModal-confirm"]
${DELETE_CANCEL}          [data-testid="deleteConfirmModal-cancel"]
```

---

## Best Practices z Komunity

### Overview

Tato sekce shrnuje best practices pro selektory v Robot Framework Browser Library získané z komunitních zdrojů:

- **Context7** - Oficiální Browser Library dokumentace
- **Playwright docs** - Podporované selector strategies
- **Komunitní blogy** - Praktické příklady a vzory

---

### Browser Library Selector Strategies

**Zdroj:** Context7 - /marketsquare/robotframework-browser

Browser Library (postavený na Playwright) podporuje více selector strategies:

| Strategy | Prefix | Příklad | Popis |
|----------|--------|---------|-------|
| **CSS** | `css=` nebo žádný | `css=.btn` nebo `.btn` | Default strategie |
| **XPath** | `xpath=` nebo `//` | `xpath=//button` nebo `//button` | XPath výrazy |
| **Text** | `text=` nebo `"..."` | `text=Submit` nebo `"Submit"` | Viditelný text elementu |
| **ID** | `id=` | `id=submit-btn` | Element ID atribut |

#### Implicit Selector Strategy

```robotframework
# CSS je default (nemusíš psát css=)
Click    .submit-button
Click    button[type="submit"]

// XPath když začíná na //
Click    //button[@type="submit"]
Click    xpath=//button[@type="submit"]

# Text když je v uvozovkách
Click    "Submit Form"
Click    text=Submit Form
```

---

### Strict Mode

**Zdroj:** Context7 - /marketsquare/robotframework-browser

Browser Library má **strict mode zapnutý default** - failne když najde více elementů.

```robotframework
# Default chování (strict mode)
Click    .item    # FAIL pokud existuje více .item elementů

# Vypnutí strict mode
Set Strict Mode    false
Click    .item    # Klikne na první matching element
```

**Kdy použít/vypnout strict mode:**

| Situace | Strict Mode | Doporučení |
|---------|-------------|------------|
| Unikátní elementy | ✅ Zapnout | Default - bezpečné |
| Seznamy itemů | ❌ Vypnout | Použij nth= nebo specifický selector |
| Dynamic content | ⚠️ Zvážit | Přidej další atributy pro unikátnost |

**Best practice:** Udržuj strict mode zapnutý a používej specifické selektory.

```robotframework
# ❌ Bad - spoléhá se na první element
Set Strict Mode    false
Click    .list-item

# ✅ Good - specifický selector
Click    .list-item[data-id="123"]
Click    .list-item >> nth=0    # První explicitně
```

---

### Selector Volatility Guidelines

**Zdroj:** Komunitní best practices (icehousecorp, testersdock)

Stability selectorů od nejstabilnějšího po nejvíce fragile:

| Úroveň | Selector | Stabilita | Příklad |
|--------|----------|-----------|---------|
| 1️⃣ **Nejlepší** | `data-testid` | Vývojář definované | `[data-testid="submit-btn"]` |
| 2️⃣ **Výborný** | `id` | Obvykle stabilní | `#submit-btn` |
| 3️⃣ **Dobrý** | `name` | Stabilní pro formuláře | `[name="email"]` |
| 4️⃣ **Přijatelný** | `class` | Mění se s CSS | `.btn-primary` |
| 5️⃣ **Fragile** | Text | Mění se s překlady | `"Submit"` |
| 6️⃣ **Nejhorší** | XPath | Křehký, složitý | `//div[1]/button[2]` |

#### Selector Anti-Patterns

**❌ Vyvaruj se těchto selektorů:**

```robotframework
# Příliš specifický (křehký)
html body div#app div.container form div.form-group input.form-control

# Index-based (rozbitý při UI změnách)
div.form-group > input:nth-child(1)
//li[3]

# Zanořený XPath (těžko udržitelný)
//div[@class='container']/div[@class='row']/div[@class='col']/button

# Text s mezerami (fragile)
"Click here for more information"
```

**✅ Používej tyto selektory:**

```robotframework
# data-testid (nejstabilnější)
[data-testid="submit-button"]

# Sémantický s atributem
button[type="submit"]
input[name="email"][required]

# Partial match pro dynamické ID
[data-testid^="list-item-"]
[data-testid$="-submit-btn"]

# Kombinace pro přesnost
form[data-testid="login-form"] > input[name="email"]
```

---

### Selector Performance

**Zdroj:** Context7 - Playwright docs

Rychlost selectorů od nejrychlejšího po nejpomalejší:

| Selector | Rychlost | Důvod |
|----------|----------|-------|
| ID (`#id`) | 🟢 Nejrychlejší | Native browser optimalizace |
| Class (`.class`) | 🟢 Rychlý | Good performance |
| Attribute (`[attr]`) | 🟡 Střední | Závisí na komplexitě |
| data-testid | 🟡 Střední | O něco pomalejší než ID |
| XPath | 🔴 Nejpomalejší | Složité vyhodnocování |

**Doporučení:** Pro kritické performance testy zvaž ID nebo Class selektory. Pro běžné testy data-testid je přijatelný.

---

### Special Selector Patterns

#### 1. Text Selectors

```robotframework
# Exact text match
"Submit"
text=Submit

# Partial text match
Get Text    //button[contains(text(), "Submit")]

# Regular expressions (Playwright feature)
Click    button >> /Submit|Save/
```

#### 2. Role-Based Selectors

```robotframework
# Podle ARIA role
Click    role=button[name="Submit"]
Click    role=link[name="Learn more"]
```

#### 3. React/Vue Specific

```robotframework
# React selector (vyžaduje React v aplikaci)
Click    _react=SubmitButton[type="submit"]

# Vue selector
Click    _vue=submit-button
```

#### 4. Combinator Selectors

```robotframework
# AND (více podmínek)
input.required.email[type="email"]

# OR (čárka)
button#submit, button#save

# NOT (negace)
button:not(.disabled)
button:not([disabled])

# Child vs Descendant
form > button      # Direct child
form button        # Any descendant
```

#### 5. Pseudo-Classes

```robotframework
# Position
li:first-child
li:last-child
li:nth-child(2)
li:nth-of-type(3)

# State
input:checked
input:disabled
button:enabled
input:visible
```

---

### Dynamic Elements Strategies

**Zdroj:** Komunitní best practices

Pro elementy s dynamickými ID/class:

```robotframework
# Problem: ID se mění
<div id="item-abc123">...</div>
<div id="item-def456">...</div>

# ✅ Solution 1: Partial match starts with
[data-testid^="item-"]

# ✅ Solution 2: Partial match ends with
[data-testid$="-name"]

# ✅ Solution 3: Partial match contains
[data-testid*="submit"]

# ✅ Solution 4: Index-based (explicit)
[data-testid="list-item-"] >> nth=0
[data-testid="list-item-"] >> nth=1

# ✅ Solution 5: Get all a loop
${count}=    Get Element Count    [data-testid^="list-item-"]
FOR    ${i}    IN RANGE    ${count}
    ${item}=    Get Element    [data-testid^="list-item-"] >> nth=${i}
    # Process item
END
```

---

### Best Practices Checklist

Použij tento checklist pro hodnocení selectorů:

- [ ] Používám `data-testid` jako primární selector
- [ ] Selektory jsou v samostatném `.resource` souboru
- [ ] Názvy selektorů jsou popisné (FORM_SUBMIT_BUTTON)
- [ ] Vyvaruji se indexových selektorů (nth-child) v locators
- [ ] Používám specifické selektory místo vypínání strict mode
- [ ] Selektory jsou dostatečně specifické, ale ne příliš komplexní
- [ ] Pro dynamické elementy používám partial match (^, $, *)
- [ ] Selektory jsou nezávislé na UI struktuře (text, pozice)
- [ ] Nepoužívám XPath pokud CSS stačí
- [ ] Kontroluji výkon selektorů při velkých test sadách

---

### Community Sources

#### Oficiální Dokumentace
- **[Browser Library Selectors](https://marketsquare.github.io/robotframework-browser/Browser.html#Locating%20elements)** - Oficiální selector dokumentace
- **[Playwright Selectors](https://playwright.dev/docs/selectors/)** - Podporované selektory a strategie
- **[CSS Selectors Reference](https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_Selectors)** - MDN CSS selektory

#### Články a Blogy
- **[Selector Best Practices](https://www.selenium.dev/documentation/webdriver/elements/locators/)** - Selenium best practices (přenositelné)
- **[CSS vs XPath Selectors](https://www.lambdatest.com/blog/css-selectors-vs-xpath/)** - Srovnání selectorů

#### Nástroje pro Debug
- **[Playwright Inspector](https://playwright.dev/docs/inspector/)** - Nástroj pro testování selektorů
- **[Chromium DevTools](https://developer.chrome.com/docs/devtools/)** - F12 pro inspectování elementů

---

### Tvoje Implementace vs Best Practices

**Co už děláš správně:**
- ✅ Používáš `data-testid` selektory
- ✅ Lokátory v samostatném `.resource` souboru
- ✅ Partial match pro dynamické elementy (`^`, `$`)
- ✅ Popisné názvy lokátorů

**Co můžeš vylepšit:**
- 🔄 Zvážit React/Vue specifické selektory pro aplikaci
- 🔄 Používat role-based selektory pro přístupnost
- 🔄 Přidat specifické selektory místo spoléhání se na první match

---

## References

- [CSS Selectors Guide](https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_Selectors)
- [XPath Syntax](https://www.w3schools.com/xml/xpath_syntax.asp)
- [Playwright Selectors](https://playwright.dev/docs/selectors)
- Project locators: `/RF/UI/locators/`
