# /test-ticket

Analyze Jira ticket and run API test.

## Usage
```
/test-ticket [TICKET-ID]
```

## Workflow
1. Read ticket (summary, description, steps to reproduce)
2. Search knowledge base for context
3. Verify endpoint against Swagger/OpenAPI specification
4. Identify preconditions (auth, test data, system state)
5. Create or modify Bruno test
6. Run test via Bruno CLI
7. Evaluate result (PASS/FAIL/PARTIAL/INSUFFICIENT INFO)
8. Show report in chat and wait for validation

## Load Skills
- api-analysis (for endpoint analysis)
- bruno-testing (for test creation/execution)
- bug-reporting (if FAIL)

## Rules
- Never invent endpoints — verify in specification
- Never send to Jira without validation
- If info is missing, stop and ask
