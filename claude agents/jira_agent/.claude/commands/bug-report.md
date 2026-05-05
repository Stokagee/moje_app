# /bug-report

Create bug report from last failed test.

## Usage
```
/bug-report
```

## Workflow
1. Take last FAIL result from test
2. Load bug-reporting skill
3. Fill template:
   - Ticket ID
   - Summary (Verb + what's broken + where/when)
   - Severity (according to matrix)
   - Steps to Reproduce (exact request)
   - Expected vs Actual result
   - Response body
   - Analysis (root cause if known)
   - Bruno test path
4. Show in chat and wait for validation

## Load Skills
- bug-reporting (templates, severity guidelines)

## Rules
- Never send to Jira automatically
- Always include exact reproducible request
- Response must not contain sensitive data
