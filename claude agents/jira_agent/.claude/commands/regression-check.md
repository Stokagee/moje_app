# /regression-check

Run regression tests to verify nothing is broken.

## Usage
```
/regression-check [module|all]
```

## Workflow
1. Determine scope:
   - `[module]` = specific folder (orders, users, auth...)
   - `all` = entire Bruno collection
2. Load regression-testing skill
3. Identify relevant tests
4. Run tests via Bruno CLI
5. Evaluate results
6. Classify failures (Regression / Known issue / Test issue / Environment)
7. Create regression report
8. Show in chat and wait for validation

## Load Skills
- regression-testing (workflow, report templates)
- bruno-testing (CLI syntax)

## Examples
```
/regression-check orders
/regression-check all
/regression-check auth
```

## Rules
- Prioritize failures: Security > Data corruption > Business flow > CRUD > Edge cases
- Compare with previous results if available
