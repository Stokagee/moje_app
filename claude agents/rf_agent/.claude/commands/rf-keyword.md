# /rf-keyword

Create new reusable keyword or common wrapper.

## Usage
```
/rf-keyword [keyword_name]
```

## Workflow
1. Verify keyword doesn't already exist
2. Propose signature (arguments, return value)
3. Wait for approval
4. Implement with TRY/EXCEPT and context_name
5. Add to appropriate resource file

## Load skill
- rf-keyword (for detailed workflow and conventions)

## Rules
- Always use common wrappers inside keyword
- Always add TRY/EXCEPT with context_name
- Always add [Documentation] with example
- Never implement without signature approval
