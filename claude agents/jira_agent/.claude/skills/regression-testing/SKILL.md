# Regression Testing — SKILL.md

Load this skill when running regression tests, interpreting
bulk results, and creating regression reports.

## When to Load This Skill

- `/regression-check` command
- After deploying new version — verify nothing is broken
- Before release — final regression suite
- When tester requests regression test on specific module

## What is Regression Testing

Regression test verifies that existing functionality hasn't been broken by changes
in code. It doesn't repeat the entire test plan — it runs a subset of tests focused
on areas that could have been affected.

## Workflow

### 1. Determine Regression Scope

Find out from tester or ticket:
- What changed (which module / service / endpoint)
- What areas could have been affected
- Is there a specific regression suite? Or test entire collection?

### 2. Identify Relevant Tests

```bash
# Find all tests for given module
find $BRUNO_DIR -type f -name "*.bru" | grep -i "orders"

# Find tests by tag (if tags are used)
rg "tags:.*regression\|tags:.*smoke" $BRUNO_DIR/ --type-add 'bru:*.bru' --type bru

# Number of tests in collection
find $BRUNO_DIR -type f -name "*.bru" | wc -l

# Number of tests in folder
find $BRUNO_DIR/orders/ -type f -name "*.bru" | wc -l
```

### 3. Run Tests

```bash
# Entire collection
bru run $BRUNO_DIR --env staging

# Specific folder (module)
bru run $BRUNO_DIR/orders/ --env staging

# With JSON report for parsing
bru run $BRUNO_DIR --env staging --output results.json

# Fail on error (exit code != 0 on failure)
bru run $BRUNO_DIR --env staging --failOnError
```

### 4. Evaluate Results

Watch for in output:
- **Requests**: how many passed / total
- **Tests**: how many passed / total
- **Assertions**: how many passed / total
- **Timing**: total time, individual times

### 5. Classify Failures

For each failure determine:

| Classification | Description | Action |
|----------------|-------------|--------|
| **Regression** | Used to work, now doesn't. Caused by change. | Bug report (severity by impact) |
| **Known issue** | Known problem, exists in known-issues.md | Mention in report, skip |
| **Test issue** | Test is poorly written or outdated | Propose test fix |
| **Environment issue** | Problem with environment, data, availability | Note, try again |
| **Flaky** | Sometimes passes, sometimes fails | Note, investigate cause |

### 6. Create Report

## Report Template — Regression

```
## Regression Report: [Module / Collection]
**Date:** [YYYY-MM-DD]
**Environment:** [staging / local]
**Run by:** QA Test Agent
**Reason:** [what changed / before release / after deploy]

### Summary
| Metric      | Value |
|-------------|-------|
| Requests    | X passed / Y total |
| Tests       | X passed / Y total |
| Assertions  | X passed / Y total |
| Total time  | X ms |
| Result      | ✅ PASS / ❌ FAIL / 🔄 PARTIAL |

### Failures (if any)

#### 1. [Test name]
- **File:** [path to .bru]
- **Endpoint:** [METHOD /path]
- **What failed:** [specific assertion / test]
- **Classification:** Regression / Known issue / Test issue / Environment
- **Detail:** [status code, error message]
- **Recommendation:** [bug report / fix test / ignore]

#### 2. ...

### Passed Without Issues
[List of modules/folders that passed completely]

### Recommendation
[Overall recommendation — release ready / fix needed / more testing required]

### Knowledge base update
[Propose adding anything to KB? YES/NO]
```

## Failure Prioritization

When many failures occur, address in this order:

1. **Security related** — auth bypass, data leak → immediately
2. **Data corruption** — incorrect save/delete of data → immediately
3. **Main business flow** — orders, payments, registration → Critical/High
4. **CRUD operations** — basic create/read/update/delete → High/Medium
5. **Edge cases** — unusual inputs, boundaries → Medium/Low
6. **Cosmetic** — incorrect formatting, minor → Low

## Smoke vs Full Regression

### Smoke Test (quick, < 5 minutes)
Purpose: Verify main flows work after deploy.

What to test:
- Login / authentication
- Main CRUD operations (1 happy path per endpoint)
- API health (health check endpoint)

```bash
# If you have smoke tests in separate folder
bru run $BRUNO_DIR/smoke/ --env staging

# Or by tag
# (depends on whether tests are tagged)
```

### Full Regression (complete, may take longer)
Purpose: Complete verification before release.

What to test:
- All endpoints
- Happy path + error handling
- Auth flows
- Edge cases

```bash
bru run $BRUNO_DIR --env staging
```

## Comparing Results

If you have previous results (in `test-results/`), compare:

```bash
# Find last report
ls -la test-results/ | tail -5

# Compare counts
# Previous: 45 passed, 0 failed
# Current: 43 passed, 2 failed
# → 2 new failures = potential regressions
```

## Flaky Tests

If test sometimes passes and sometimes fails:

1. Run it 3 times in a row
2. If 2/3 pass → probably flaky (timing, race condition)
3. Record in known-issues.md
4. Propose test improvement (timeout, retry, more stable test data)

## When to Escalate

- **3+ Critical failures** → escalate immediately, blocks release
- **Auth completely broken** → escalate, cannot test further
- **Environment unavailable** → inform, wait for fix
- **Unknown endpoint in response** → verify with specification or dev team
