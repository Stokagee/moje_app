# /rf-test

Create new Robot Framework test or extend existing.

## Usage
```
/rf-test [endpoint_or_feature]
```

## Workflow
1. Analyze input (request, analysis notes, existing test)
2. Explore context (existing tests, wrappers, BE code)
3. Propose test structure
4. Implement using common wrappers
5. Verify before submission

## Load skill
- rf-test (for detailed workflow and conventions)

## Rules
- Always use common wrappers (API request, Verify Row Count In Database)
- Never call RequestsLibrary/DatabaseLibrary directly
- Use meaningful variable names per convention
- Show proposal before implementation
