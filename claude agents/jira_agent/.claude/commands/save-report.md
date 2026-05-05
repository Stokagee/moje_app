# /save-report

Save last report to test-results/ folder.

## Usage
```
/save-report [filename]
```

## Workflow
1. Take last report from chat
2. Create filename:
   - If `[filename]` specified: `test-results/[filename].md`
   - If not specified: `test-results/[TICKET-ID]_[YYYY-MM-DD]_[status].md`
3. Save report as markdown
4. Confirm file path

## Filename Format
```
PROJ-1234_2025-01-15_pass.md
PROJ-5678_2025-01-15_fail.md
PROJ-9012_2025-01-15_partial.md
```

## Rules
- Always use timestamp for uniqueness
- Version reports in Git
