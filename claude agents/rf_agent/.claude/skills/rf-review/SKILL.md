# rf-review — Code Review and Quality Control

## When to Use This Skill

Use whenever:
- User enters `/rf:review`
- Wants to evaluate test quality
- Wants to find issues, check convention compliance
- Wants to verify coverage or perform code audit
- User says "check", "evaluate", "what's wrong", "audit", "review"

## Purpose

Review code, find issues and provide structured report. Review DOESN'T CHANGE code — only identifies problems and suggests solutions.

## Workflow

### 1. Review Scope

Find out what to review:
- Specific file → review just that
- Entire feature/folder → review all .robot and .resource files
- Entire project → review structure, common layer, sample of tests

### 2. Review Criteria

Review code systematically by these categories:

#### A) Wrappers and Architecture (CRITICAL)

```bash
# Direct library calls instead of wrappers
grep -rn 'POST On Session\|GET On Session\|DELETE On Session' <scope> --include="*.robot"
grep -rn 'Query\|Execute Sql String' <scope> --include="*.robot"
```

- [ ] All API calls go through `API request`
- [ ] All DB operations go through common_db wrappers
- [ ] No duplication of common wrapper logic

#### B) Naming Conventions (HIGH)

```bash
# Forbidden generic names
grep -rn '\${data}\b\|\${response}\b\|\${result}\b\|\${item}\b\|\${row}\b\|\${value}\b' <scope> --include="*.robot" --include="*.resource"
```

- [ ] Variables have meaningful names per convention
- [ ] API variables: `${api_<action>_<entity>_<type>}`
- [ ] DB variables: `${db_<entity>_<purpose>}`
- [ ] Constants: UPPER_CASE
- [ ] No `${data}`, `${response}`, `${result}`, `${item}`, `${row}`

#### C) Error Handling (HIGH)

- [ ] Non-trivial keywords have TRY/EXCEPT
- [ ] `${context_name}` is filled meaningfully, in English
- [ ] Error messages are in English and descriptive

#### D) Documentation (MEDIUM)

- [ ] Test cases have `[Documentation]`
- [ ] Keywords have `[Documentation]`
- [ ] Documentation supplements name, doesn't repeat it
- [ ] Non-trivial keywords have usage example

#### E) Test Structure (MEDIUM)

- [ ] Suite has Setup and Teardown
- [ ] Tests are independent (don't depend on order)
- [ ] Hardcoded values replaced with variables
- [ ] Test verifies one thing (Single Responsibility)
- [ ] Tags are present (even if TODO)

#### F) Formatting (LOW)

- [ ] 4 space indentation, no tabs
- [ ] Consistent style throughout file
- [ ] Clear section separation

### 3. Output — Review Report

```
## Review: <file or scope>

### Summary
<1-2 sentences overall impression>

### Critical Issues (must fix)
1. **<issue>** — line X
   - What: <description>
   - Why: <why it's a problem>
   - Fix: <how to fix>

### Important Issues (should fix)
1. **<issue>** — line X
   - What: <description>
   - Fix: <how to fix>

### Minor Issues (nice to have)
1. **<issue>** — line X

### What's Good
<what works correctly, which patterns are followed>

### Recommendations
<what could be improved beyond fixes>
```

**Report Rules:**
- Specific — line numbers, code samples
- Prioritized — critical on top, minor at bottom
- Actionable — suggest solution for each issue
- Fair — mention what's good too

### 4. Follow-up

After review offer:
- `/rf:refactor` — to fix found issues
- `/rf:keyword` — if review revealed need for new keyword
- `/rf:test` — if scenario coverage is missing

## What NOT To Do

- DON'T CHANGE code — review only reports
- Don't be vague — always specific line and example
- Don't ignore positives — mentioning what's good motivates
- Don't look for problems where there are none — if code is fine, say so
