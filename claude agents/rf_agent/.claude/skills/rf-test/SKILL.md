# rf-test — Test Creation and Extension

## When to Use This Skill

Use whenever:
- User enters `/rf:test`
- Wants to create new test
- Wants to extend existing scenario
- Wants to write API test, DB test, or E2E scenario
- User says "write test", "test endpoint", "add scenario"

## Purpose

Create new test or extend existing scenario. Covers all input sources: user request, analysis notes, endpoint specification.

## Workflow

### 1. Input Analysis

Find out where the request comes from and what's available:

| Input | What To Do |
|-------|------------|
| Free-form user request | Ask about endpoint, expected behavior, edge cases |
| Analysis notes | Break down into individual scenarios, verify priorities with user |
| Existing test to extend | Review current test, find what it covers, suggest what to add |

### 2. Context Exploration

BEFORE writing test always:

```bash
# Find existing tests for same endpoint/feature
grep -r "<endpoint_or_feature>" tests/ --include="*.robot" --include="*.resource"

# Review common wrappers — what's available
cat tests/common/common_api.resource
cat tests/common/common_db.resource

# Review BE code for endpoint
find . -name "*.py" -path "*/routes/*" | xargs grep -l "<endpoint>"
```

**Checklist before writing:**
- [ ] I know exact endpoint (method + URL)
- [ ] I know request payload structure
- [ ] I know expected response (status code + body structure)
- [ ] I know if related tests exist
- [ ] I know which common keywords I'll use
- [ ] I know if test needs DB validation

If you don't know any of these — STOP AND ASK.

### 3. Test Design

Before implementation, propose structure:

```
Test: <test name>
  Prerequisites: <what must exist / setup>
  Steps:
    1. <step>
    2. <step>
  Expected: <what I'm verifying>
  Cleanup: <what must be cleaned up>

Keywords needed:
  - <existing keyword> ✓ (exists in common_api.resource)
  - <new keyword> ✗ (must create → /rf:keyword)
```

Show proposal to user BEFORE implementation.

### 4. Implementation

#### .robot File Structure

```robotframework
*** Settings ***
Documentation    Brief description of what this suite tests.
Resource         ../common/common_api.resource
Resource         ../common/common_db.resource
Resource         <feature>.resource
Suite Setup      Prepare Test Environment
Suite Teardown   Cleanup Test Data

*** Test Cases ***
<Feature> - <Scenario> - <Expected outcome>
    [Documentation]    What exactly this test verifies.
    [Tags]             TODO-tag
    <test steps>
```

#### Test Case Naming Rules

- Format: `<Feature> - <Scenario> - <Expected outcome>`
- Example: `User Creation - Valid payload - Returns 201 and user ID`
- Readable without opening test

#### Variable Naming Rules

```robotframework
# API variables
${api_create_user_request_payload}
${api_create_user_response}
${api_create_user_response_body}
${api_create_user_response_status_code}

# DB variables
${db_created_user_record}
${db_user_expected_row_count}

# NEVER use:
# ${data}, ${response}, ${result}, ${item}, ${row}
```

#### Using Wrappers

```robotframework
# API call — ALWAYS via wrapper
${api_create_user_response}=    API request
...    method=POST
...    url=/api/users
...    body=${api_create_user_request_payload}
...    expected_status=anything
...    context_name=Create user

# DB verification — ALWAYS via wrapper
Verify Row Count In Database
...    query=SELECT * FROM users WHERE email='${test_user_email}'
...    expected_count=1
...    operator===
...    context_name=Verify user exists in DB

# NEVER call RequestsLibrary or DatabaseLibrary directly in tests
```

### 5. Pre-Submission Check

- [ ] Test uses ONLY common wrappers
- [ ] Variables have meaningful names per convention
- [ ] Test has Documentation
- [ ] Test has Tags
- [ ] Suite has Setup and Teardown
- [ ] Hardcoded values replaced with variables
- [ ] Error messages in TRY/EXCEPT are in English
- [ ] Test doesn't depend on order of other tests

### 6. Output

```
## Analysis
<what I found, which wrappers/keywords exist>

## Proposal
<test structure, which keywords I'll use/create>

## Changes
<code>

## Risks
<what could affect other tests>

## TODO
<what's missing, what needs verification>
```

## What NOT To Do

- Don't write test without context exploration
- Don't call RequestsLibrary/DatabaseLibrary directly
- Don't use generic variable names
- Don't invent tags — add TODO and ask
- Don't write test dependent on specific DB state without setup/teardown
- Don't skip proposal — always show structure before implementation
