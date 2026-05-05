# /rf-review

Perform code review of Robot Framework code.

## Usage
```
/rf-review [file_or_folder]
```

## Workflow
1. Determine review scope (file, folder, project)
2. Go through review criteria:
   - Wrappers and architecture (CRITICAL)
   - Naming conventions (HIGH)
   - Error handling (HIGH)
   - Documentation (MEDIUM)
   - Test structure (MEDIUM)
   - Formatting (LOW)
3. Create structured report
4. Suggest follow-up actions

## Load skill
- rf-review (for detailed workflow and criteria)

## Rules
- Review DOESN'T CHANGE code — only reports
- Always include specific line and example
- Mention what's good too
- If code is fine, say so
