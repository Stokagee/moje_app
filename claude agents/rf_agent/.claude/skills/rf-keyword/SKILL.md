# rf-keyword — Reusable Keyword Creation

## When to Use This Skill

Use whenever:
- User enters `/rf:keyword`
- You need to create new shared keyword
- You need to create wrapper, helper, utility keyword
- You want to extend existing common layer
- User says "create keyword", "add wrapper", "this repeats — make it a keyword"

## Purpose

Design and implement new reusable keyword or common wrapper in the style of existing project wrappers. Every new keyword = proposal for approval.

## Workflow

### 1. Need Analysis

Before creating new keyword, verify:

```bash
# Does something similar already exist?
grep -r "<search_pattern>" tests/ --include="*.resource"
grep -r "<search_pattern>" tests/ --include="*.robot"

# How do existing wrappers look?
cat tests/common/common_api.resource
cat tests/common/common_db.resource
```

**Decision tree:**

1. Does keyword exist that does the same thing? → **Use it, don't create new.**
2. Does keyword exist that does something similar? → **Extend it or create variant.**
3. Nothing exists? → **Propose new keyword.**

**Where keyword belongs:**

| Keyword is... | Belongs in... |
|---------------|---------------|
| Generic API/DB pattern | `common_api.resource` or `common_db.resource` |
| Specific to feature/endpoint | `<feature>.resource` next to test |
| Multi-step orchestration | `<feature>.resource` |

### 2. Signature Proposal

BEFORE implementation show:

```
Keyword: <Keyword Name>
  Location: <where it belongs>
  Purpose: <what it does and why we need it>
  Arguments:
    - ${arg1}    <description>    default: <value>
    - ${arg2}    <description>    default: <value>
  Returns: <what it returns>
  Usage example:
    ${result}=    <Keyword Name>    arg1=value1    arg2=value2
  Why new keyword:
    <why existing ones can't be used>
```

Wait for user approval.

### 3. Implementation

#### Required pattern — TRY/EXCEPT + context_name + logging

```robotframework
Create User Via API
    [Documentation]    Creates a user with given payload and returns response body.
    ...                If ${custom_payload} is not provided, uses default FakerLibrary data.
    ...
    ...                Example:
    ...                    ${api_user_response_body}=    Create User Via API
    ...                    ${api_user_response_body}=    Create User Via API    custom_payload=${my_payload}
    [Arguments]    ${custom_payload}=${None}
    ${context_name}=    Set Variable    Create user via API
    TRY
        # Prepare payload
        ${api_create_user_request_payload}=    Run Keyword If    '${custom_payload}' != '${None}'
        ...    Set Variable    ${custom_payload}
        ...    ELSE    Create Valid User Payload

        # API call via common wrapper
        ${api_create_user_response}=    API request
        ...    method=POST
        ...    url=/api/users
        ...    body=${api_create_user_request_payload}
        ...    expected_status=anything
        ...    context_name=${context_name}

        ${api_create_user_response_body}=    Set Variable    ${api_create_user_response.json()}

        Run Keyword If    '${LOG_TO_CONSOLE}' == 'True'
        ...    Log To Console    ${context_name}: User created, ID=${api_create_user_response_body}[id]

        RETURN    ${api_create_user_response_body}
    EXCEPT    AS    ${error_message}
        Fail    ${context_name}: Failed to create user. Error: ${error_message}
    END
```

#### Implementation Rules

**Structure:**
- `[Documentation]` — concise, supplements the name. For non-trivial keywords include usage example.
- `[Arguments]` — clear names, reasonable defaults.
- `${context_name}` — always fill meaningfully, in English.
- `TRY/EXCEPT` — clear error message with `${context_name}`.
- `RETURN` — explicit, at end of TRY block.
- Logging via `${LOG_TO_CONSOLE}`.

**Naming:**
- Keyword name in English, but understandable.
- Name itself says what it does.
- Variables inside keyword per convention.

**Dependencies:**
- ALWAYS use common wrappers (`API request`, `Verify Row Count In Database`, etc.).
- NEVER call `RequestsLibrary` or `DatabaseLibrary` directly.

### 4. Quality Check

Before submission verify:

- [ ] Keyword doesn't duplicate existing functionality
- [ ] Uses common wrappers
- [ ] Has TRY/EXCEPT with `${context_name}`
- [ ] Has `[Documentation]` with example (for non-trivial)
- [ ] Variables have meaningful names
- [ ] Logging via `${LOG_TO_CONSOLE}`
- [ ] Reasonable defaults for arguments
- [ ] Keyword does one thing

### 5. Output

```
## Analysis
<what exists, why new keyword>

## Proposal
<signature, where it belongs, usage example>

## Changes
<code>

## Risks
<what could affect existing tests>

## TODO
<what's missing>
```

## What NOT To Do

- Don't create keyword without verifying similar one doesn't exist
- Don't implement without signature approval
- Don't bypass common wrappers
- Don't add libraries without warning
- Don't put keyword in common layer if it's only used in one test
