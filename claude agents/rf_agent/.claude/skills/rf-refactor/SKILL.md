# rf-refactor — Refactoring Without Changing Meaning

## When to Use This Skill

Use whenever:
- User enters `/rf:refactor`
- Wants to clean code, remove duplications
- Wants to unify style, rename variables
- Wants to extract repeated steps into keywords
- User says "clean", "unify", "rename", "simplify", "deduplicate"

## Purpose

Modify existing code to be cleaner, more consistent and more maintainable — WITHOUT changing what tests verify.

## Golden Rule

> After refactoring, every test must verify EXACTLY the same thing as before. No test should start passing or failing because of refactoring.

## Workflow

### 1. Analysis — What's Wrong

Review provided code and look for:

```bash
# Duplicate steps
grep -c "<repeating_pattern>" <file>

# Inconsistent naming
grep -n '\${data}\|\${response}\|\${result}\|\${item}\|\${row}' <file>

# Direct library calls instead of wrappers
grep -n 'RequestsLibrary\|DatabaseLibrary' <file>

# Missing documentation
grep -n '^\*\*\* Keywords \*\*\*' -A 2 <file>

# Hardcoded values
grep -n "http://\|https://\|localhost\|127.0.0.1" <file>
```

**Problem Checklist:**

| Problem | Priority | Example |
|---------|----------|---------|
| Direct library calls instead of wrappers | HIGH | `POST On Session` instead of `API request` |
| Generic variable names | HIGH | `${response}` instead of `${api_create_user_response}` |
| Duplicate steps (3+ repetitions) | MEDIUM | Same setup in every test |
| Missing TRY/EXCEPT in keywords | MEDIUM | Keyword without error handling |
| Missing Documentation | LOW | Keyword without `[Documentation]` |
| Inconsistent formatting | LOW | Mix of tabs and spaces |

### 2. Change Proposal

For EVERY change specify:

```
Change: <what I'm changing>
Reason: <why>
Before: <original code — short excerpt>
After: <new code — short excerpt>
Impact: <none / affects X tests>
```

**Proposal rules:**
- Smallest safe change. Small precise edits > big rewrites.
- If refactor requires changes in many files — propose in parts.
- If unsure whether change alters test meaning — STOP AND ASK.

### 3. Implementation

#### Typical Refactoring Operations

**A) Variable Renaming:**
```robotframework
# BEFORE
${resp}=    API request    method=POST    url=/api/users    body=${data}

# AFTER
${api_create_user_response}=    API request    method=POST    url=/api/users    body=${api_create_user_request_payload}
```

**B) Extraction to Keyword:**
```robotframework
# BEFORE (repeated in 5 tests)
${token}=    API request    method=POST    url=/api/auth/login    body=${login_data}
${auth_header}=    Create Dictionary    Authorization=Bearer ${token.json()}[access_token]

# AFTER (keyword in common or feature resource)
${api_auth_access_token}=    Get Auth Token    email=${test_user_email}    password=${test_user_password}
```

**C) Replacing Direct Call with Wrapper:**
```robotframework
# BEFORE
${resp}=    POST On Session    api    /api/users    json=${body}    expected_status=201

# AFTER
${api_create_user_response}=    API request
...    method=POST
...    url=/api/users
...    body=${api_create_user_request_payload}
...    expected_status=anything
...    context_name=Create user
```

### 4. Verification

After refactoring verify:

- [ ] No test changed its meaning (what it verifies)
- [ ] No test started depending on another test
- [ ] Setup/teardown are preserved or improved
- [ ] All variables have meaningful names
- [ ] All API calls go through common wrappers
- [ ] Code is consistently indented (4 spaces)

### 5. Output

```
## Analysis
<what I found, what problems>

## Proposal
<list of changes with before/after>

## Changes
<code>

## Risks
<what could affect other tests>

## TODO
<what could be improved further, but not doing now>
```

## What NOT To Do

- DON'T CHANGE test meaning — that's a new test, not refactoring
- DON'T CHANGE suite/test setup/teardown without context of entire suite
- DON'T RENAME files without consent
- DON'T DO more than requested — refactoring has clear scope
- DON'T REMOVE tests
