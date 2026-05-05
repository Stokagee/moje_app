# Bug Reporting — SKILL.md

Load this skill when creating a bug report from test results.
Contains severity guidelines, templates, and examples.

## When to Load This Skill

- Phase 5 workflow (Report) — when test failed (FAIL)
- `/bug-report` command
- Whenever you need to create or improve a bug report

## Severity Matrix

| Severity | Criteria | Examples |
|----------|----------|----------|
| **Critical** | Application not working / data loss / security breach / blocks release | Production data being deleted; API returns other users' data; main flow completely broken; auth bypass |
| **High** | Main function not working, no workaround | Order creation always fails; payment endpoint returns 500; login doesn't work for all users |
| **Medium** | Main function not working but has workaround; or secondary function not working | Filtering doesn't work but listing does; export fails but data is available via UI; specific data format causes error |
| **Low** | Cosmetic, minor UX, edge case with minimal impact | Typo in error message; inconsistent naming in response; edge case with unusual characters |

### How to Determine Severity

1. **Who is affected?** All users → higher severity. Specific group → lower.
2. **What's the impact?** Data loss / security → Critical. Function not working → High. Inconvenience → Medium/Low.
3. **Is there a workaround?** Yes → reduce by one level. No → keep.
4. **Does it block release?** Yes → at least High.

## Template — FAIL Bug Report

```
**Ticket:** [JIRA-ID]
**Summary:** [Verb] + [what's broken] + [where/when]
**Severity:** Critical / High / Medium / Low
**Component:** [service/module name]
**Environment:** [staging / local / ...]

### Description
[1–2 sentences — what the problem is and its impact on user/system]

### Steps to Reproduce
1. [Exact API call — method, URL, headers, body]
2. [Environment and authentication]
3. [Preconditions — test data, system state, permissions]

### Expected Result
[What should happen according to specification / ticket]

### Actual Result
[What actually happened — status code, response body, error message]

### Response
```json
{response body — shortened to relevant part}
\```

### Analysis
[Root cause analysis — if determinable]
[What might be wrong on backend]
[Connection to other bugs — if exists]

### Bruno test
[Path to .bru file that ran the test]
[How to rerun: bru run ...]

### Recommendation
[What you recommend — fix, more testing, escalation]

### Knowledge base update
[What new you learned — propose adding to KB? YES/NO]
```

## Rules for Writing Bug Reports

### Summary — How to Write It

**Format:** `[Verb] [what's broken] [where/when/under what conditions]`

Good:
- `POST /orders returns 500 when name contains special characters`
- `GET /users/{id} returns 404 for existing user after password change`
- `Auth token refresh fails silently, subsequent requests return 401`

Bad:
- `Server error` — too vague
- `It doesn't work` — doesn't say what, where, when
- `Bug in orders` — no detail
- `PROJ-1234 regression` — doesn't say what's happening

### Steps to Reproduce — Rules

1. **Be precise** — include exact HTTP request (method, URL, headers, body)
2. **Include preconditions** — what must be set up beforehand
3. **Include environment** — where it happens
4. **Include auth** — what token / credentials
5. **Be reproducible** — anyone should be able to reproduce the bug

Good:
```
1. Authenticate: POST {{base_url}}/auth/login
   Body: {"username": "testuser", "password": "test123"}
2. Send: POST {{base_url}}/api/v1/orders
   Headers: Authorization: Bearer {{token}}, Content-Type: application/json
   Body: {"name": "Test <script>alert(1)</script>", "amount": 100}
3. Observe: Response returns 500 Internal Server Error
```

Bad:
```
1. Login
2. Create order with special chars
3. Error
```

### Expected vs Actual — Rules

- **Expected**: Always reference specification or ticket
- **Actual**: Include exact status code, response body, timing
- **Don't interpret** — write what you see, not what you think is happening

### Response — What to Include

- Entire response body (if short) or relevant portion
- Status code
- Relevant response headers (e.g., `X-Request-ID` for tracking)
- **Never** include sensitive data (tokens, passwords, personal info)

### Analysis — Root Cause

If you can determine cause from response or error message:
- Stack trace in response → include file and line
- Error message → quote exactly
- Pattern → "Only happens for requests with diacritics"
- Correlation → "Started happening after version X deploy"

If you **cannot** determine cause, say so. Don't make it up.

## Examples

### Good Bug Report — Critical

```
**Ticket:** PROJ-1234
**Summary:** POST /api/v1/orders returns 500 when order name contains HTML tags
**Severity:** Critical
**Component:** order-service
**Environment:** staging

### Description
Creating an order with HTML tags in the name causes Internal Server Error.
Potential security risk (XSS) if input is not sanitized.

### Steps to Reproduce
1. POST https://api.staging.example.com/api/v1/orders
   Headers: Authorization: Bearer {{auth_token}}
   Body: {"name": "<script>alert('xss')</script>", "amount": 100}

### Expected Result
API returns 201 Created with sanitized name,
or 422 with validation error for unsupported characters.

### Actual Result
500 Internal Server Error

### Response
```json
{
  "error": "Internal Server Error",
  "message": "StringIndexOutOfBoundsException",
  "path": "/api/v1/orders"
}
\```

### Analysis
Stack trace indicates StringIndexOutOfBoundsException — likely
missing input sanitization before processing. Endpoint doesn't perform
validation/escaping of HTML tags in `name` field.

### Bruno test
$BRUNO_DIR/orders/PROJ-1234_post-orders-500-html-tags.bru
Run: bru run $BRUNO_DIR/orders/PROJ-1234_post-orders-500-html-tags.bru --env staging

### Recommendation
1. Fix: Add input sanitization/validation for `name` field
2. Verify all text inputs in order-service for same pattern
3. Consider security review for XSS vulnerability

### Knowledge base update
YES — Add to known-issues.md: order-service doesn't sanitize HTML input
```

### Bad Bug Report

```
**Summary:** Orders don't work
**Severity:** High

Orders endpoint is broken. Returns error.
Please fix.
```

Why it's bad:
- Vague summary
- No steps to reproduce
- No request/response details
- No environment
- Not reproducible
- Severity without justification

## Report for PASS Result

```
✅ PASS: [Ticket ID]
What was tested: [1–2 sentences]
Endpoint: [METHOD /path]
Environment: [staging/local]
Bruno collection/test: [path to .bru file]
Result: [status code, key values from response]
Knowledge base update: [YES/NO — if YES, what you propose adding]
```

## Report for PARTIAL Result

```
🔄 PARTIAL: [Ticket ID]
What passed: [what works — specific assertions]
What failed: [what doesn't work — specific failures]
Endpoint: [METHOD /path]
Environment: [staging/local]
Recommendation: [what next — more tests, consult with dev, ...]
```

## Report for INSUFFICIENT INFO

```
⚠️ INSUFFICIENT INFO: [Ticket ID]
What's missing:
- [specific item 1]
- [specific item 2]
Sources searched:
- Knowledge base: [what I searched for]
- Swagger spec: [what I found/didn't find]
- Bruno collection: [existing tests]
Proposed questions for developer:
1. [question 1]
2. [question 2]
```

## Jira Formatting

When preparing report for Jira use:

```
# TODO: Fill in Jira project key and custom fields
# JIRA_PROJECT_KEY: PROJ
#
# Required fields for bug:
# - Summary
# - Description (formatted markdown/wiki)
# - Priority (Critical/High/Medium/Low → map to Jira priorities)
# - Component (if exists in Jira)
# - Labels: bug, api, [service-name]
# - Affects Version: [version where bug occurs]
# - Environment: [staging/local/...]
#
# Optional:
# - Linked Issues: blocks / is caused by PROJ-XXXX
# - Attachments: Bruno test file, response log
```

## Checklist Before Sending

- [ ] Summary is clear, specific, and actionable
- [ ] Severity matches matrix above
- [ ] Steps to Reproduce are complete and reproducible
- [ ] Expected Result references specification
- [ ] Actual Result includes exact status code and response
- [ ] Response body doesn't contain sensitive data
- [ ] Bruno test file exists and is functional
- [ ] Analysis is factual (not speculation)
- [ ] Report is in chat — **waiting for tester validation**
