# /explore

Exploratory testing of endpoint — systematic API behavior exploration.

## Usage
```
/explore [endpoint]
```

## Workflow
1. Understand endpoint (from ticket, specification, knowledge base)
2. Load exploratory-testing skill
3. Select 2–3 techniques:
   - Boundary Value Analysis
   - Negative Testing
   - Auth Testing
   - Injection Testing
   - Special Characters
   - Response Consistency
   - Performance Smoke
   - Idempotence Testing
4. Run tests and record findings
5. Classify each finding (Bug / Observation / Question)
6. Create exploratory report
7. Show in chat

## Load Skills
- exploratory-testing (techniques, heuristics)
- bruno-testing (for running tests)
- bug-reporting (for reporting bugs)

## Examples
```
/explore POST /api/v1/orders
/explore GET /api/v1/users/{id}
/explore /auth/login
```

## Rules
- Don't test on production
- Don't perform destructive operations on shared data
- This is not a full penetration test
- For endpoints without specification — ask first
