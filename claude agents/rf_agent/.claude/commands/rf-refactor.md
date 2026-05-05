# /rf-refactor

Refactor Robot Framework code without changing test meaning.

## Usage
```
/rf-refactor [file_or_folder]
```

## Workflow
1. Analyze what's wrong (duplication, inconsistency, bad naming)
2. Propose changes with before/after
3. Implement smallest safe change
4. Verify test meaning didn't change

## Load skill
- rf-refactor (for detailed workflow and conventions)

## Rules
- No change should alter test meaning
- Small precise edits > big rewrites
- If unsure, stop and ask
- Don't change suite/test setup/teardown without context
