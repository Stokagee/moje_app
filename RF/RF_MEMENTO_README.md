# RF MEMENTO.DB - Complete Robot Framework Project Knowledge Base

**Created:** 2024-11-21
**Purpose:** Comprehensive knowledge database for entire RF Test Automation Suite

## Overview

RF memento.db is a SQLite database containing **14 tables** with **101 rows** of structured knowledge about the complete RF test automation project, including API tests, UI tests, database verification, and custom ImageComparisonLibrary.

## Database Structure

### CORE TABLES (6) - Project structure and tests
1. **rf_project_metadata** (1 row) - Project info, RF 7.2.2, 4-layer POM architecture
2. **rf_components** (4 rows) - API, UI, db, ImageComparisonLibrary components
3. **rf_test_suites** (8 rows) - All .robot test files
4. **rf_test_cases** (5 rows) - Key test cases with tags and priorities
5. **rf_resources** (14 rows) - All .resource files (locators, pages, workflows, common)
6. **rf_keywords** (11 rows) - Important custom keywords

### KNOWLEDGE TABLES (5) - Libraries and best practices
7. **rf_libraries** (5 rows) - Browser, RequestsLibrary, FakerLibrary, DatabaseLibrary, ImageComparisonLibrary
8. **rf_variables_config** (10 rows) - All configuration variables (URLs, credentials, settings)
9. **rf_pom_layers** (4 rows) - Explanation of 4-layer POM architecture
10. **rf_best_practices** (10 rows) - Best practices from README_CLAUDE.md
11. **rf_test_data_sources** (5 rows) - FakerLibrary, files, hardcoded data

### REFERENCE TABLES (3) - Integration and dependencies
12. **rf_integration_points** (4 rows) - UI↔API, UI↔db, API↔db, UI↔ImageComparisonLibrary
13. **rf_dependencies** (10 rows) - File dependencies and imports
14. **rf_command_reference** (10 rows) - Commands for running tests

## Quick Start

### Opening the database:
```bash
cd C:\Users\stoka\Documents\moje_app\RF
sqlite3 memento.db
```

### Enable formatted output:
```sql
.mode column
.headers on
.width auto
```

### Basic queries:

**Get project info:**
```sql
SELECT * FROM rf_project_metadata;
```

**List all components:**
```sql
SELECT component_name, primary_purpose, test_count, resource_count
FROM rf_components
ORDER BY component_name;
```

**Understand POM layers:**
```sql
SELECT layer_number, layer_name, description, example_files
FROM rf_pom_layers
ORDER BY layer_number;
```

**Find smoke tests:**
```sql
SELECT s.suite_name, s.file_path, s.test_case_count
FROM rf_test_suites s
WHERE s.suite_tags LIKE '%smoke%';
```

**Check for violations:**
```sql
SELECT component_name, notes
FROM rf_components
WHERE notes LIKE '%VIOLATION%';
```

## Helper Queries File

The file `rf_memento_queries.sql` contains **100+ ready-to-use queries** organized into categories:

- Project Overview (3 queries)
- Test Suite Queries (5 queries)
- Test Case Queries (5 queries)
- Resource Queries (5 queries)
- Keyword Queries (6 queries)
- Library Queries (4 queries)
- Variable & Configuration (4 queries)
- POM Architecture (3 queries)
- Best Practices (5 queries)
- Integration (3 queries)
- Dependency Analysis (4 queries)
- Test Data Sources (3 queries)
- Command Reference (4 queries)
- Statistics (6 queries)
- Validation & Quality (5 queries)
- Advanced Analysis (4 queries)
- Full Project Summary (1 query)

### Using helper queries:

**Run specific query:**
```bash
sqlite3 memento.db "SELECT * FROM rf_components;"
```

**Export to CSV:**
```bash
sqlite3 -csv memento.db "SELECT * FROM rf_test_suites;" > test_suites.csv
```

**Interactive mode:**
```bash
sqlite3 memento.db
.mode column
.headers on
SELECT * FROM rf_pom_layers;
```

## Common Use Cases

### 1. Understand project structure:
```sql
SELECT
    c.component_name,
    COUNT(s.id) as suite_count,
    SUM(s.test_case_count) as total_tests
FROM rf_components c
LEFT JOIN rf_test_suites s ON c.id = s.component_id
GROUP BY c.component_name;
```

### 2. Find workflows:
```sql
SELECT
    r.resource_name,
    k.keyword_name,
    k.purpose
FROM rf_keywords k
JOIN rf_resources r ON k.resource_id = r.id
WHERE k.keyword_type = 'workflow';
```

### 3. Check security issues:
```sql
SELECT
    c.component_name,
    v.variable_name,
    v.file_path,
    v.notes
FROM rf_variables_config v
JOIN rf_components c ON v.component_id = c.id
WHERE v.is_sensitive = 1;
```

### 4. Get command to run smoke tests:
```sql
SELECT command_name, command, description
FROM rf_command_reference
WHERE tags_used LIKE '%smoke%';
```

### 5. Find POM violations:
```sql
SELECT
    suite_name,
    notes as violation
FROM rf_test_suites
WHERE notes LIKE '%VIOLATION%';
```

## Project Statistics

| Category | Count | Details |
|----------|-------|---------|
| **Components** | 4 | API, UI, db, ImageComparisonLibrary |
| **Test Suites** | 8 | 3 API + 1 UI + 2 db + 1 ICL + 1 root |
| **Resources** | 14 | 5 API + 7 UI + 3 db |
| **Keywords** | 11 | Workflows, actions, utilities |
| **Libraries** | 5 | 4 external + 1 custom |
| **Variables** | 10 | URLs, credentials, config |
| **Best Practices** | 10 | Must-have + recommended |
| **Commands** | 10 | Smoke, regression, parallel, etc. |
| **TOTAL ROWS** | **101** | Complete project knowledge |

## Component Overview

### API Testing ✅ PERFECT
- **Architecture:** 4-layer POM (perfect implementation)
- **Tests:** 3 suites, smoke + regression tags
- **Libraries:** RequestsLibrary, FakerLibrary
- **Quality:** ✅ Tags, ✅ Structured logging, ✅ Workflows, ✅ Error handling

### UI Testing ⚠️ NEEDS REFACTORING
- **Architecture:** 3-layer POM (**workflows/ missing!**)
- **Tests:** 1 suite
- **Libraries:** Browser (Playwright), FakerLibrary, ImageComparisonLibrary
- **Issues:**
  - ❌ **Missing workflows/ layer** (Layer 3)
  - ❌ **No tags** on tests
  - ❌ **Uses Log To Console** (not structured logging)
  - ❌ **Missing test documentation**
- **Needs:** Create workflows/, add tags, use structured logging

### Database Testing ⚠️ SECURITY WARNING
- **Architecture:** Custom DB keywords
- **Tests:** 2 suites
- **Libraries:** DatabaseLibrary, psycopg2
- **Issue:** ❌ **Hardcoded password in db/variables.resource** - MUST FIX!

### ImageComparisonLibrary ✅ EXCELLENT
- **Type:** Custom Robot Framework library
- **Version:** 1.5.0
- **Features:** Perceptual hashing, visual diffs, morphological dilation
- **Quality:** ✅ Unit tests, ✅ Documentation, ✅ Own memento.db
- **Location:** Has own `ImageComparisonLibrary/memento.db` with detailed library info

## 4-Layer POM Architecture

```
LAYER 4: Tests
   ↓ (calls workflows ONLY)
LAYER 3: Workflows
   ↓ (calls page actions / API actions)
LAYER 2: Pages / API Actions
   ↓ (uses locators / endpoints)
LAYER 1: Locators / Endpoints
```

### Layer Details:

**Layer 1: Locators/Endpoints**
- **API:** `endpoints/form_endpoints.resource` (URL constants)
- **UI:** `locators/form_page_locators.resource`, `locators/page2_locators.resource`
- **Content:** ONLY variables, NO logic
- **Status:** ✅ Both API and UI implement correctly

**Layer 2: Pages/API Actions**
- **API:** `api_actions/form_api.resource` (POST, GET, DELETE)
- **UI:** `pages/form_page.resource`, `pages/page2.resource`
- **Content:** Atomic operations, one action per keyword
- **Status:** ✅ Both API and UI implement correctly

**Layer 3: Workflows**
- **API:** `workflows/form_workflow.resource` ✅ Perfect
- **UI:** **MISSING!** ❌ This is the main violation
- **Content:** Complex scenarios, combines Layer 2 actions
- **Status:** ✅ API perfect, ❌ UI needs creation

**Layer 4: Tests**
- **API:** `tests/form_crud_tests.robot` ✅ Calls workflows only
- **UI:** `tests/new_form.robot` ❌ Calls pages directly (should call workflows)
- **Content:** High-level test cases
- **Status:** ✅ API perfect, ❌ UI violates by skipping Layer 3

## Key Best Practices (From Database)

### MUST-HAVE (priority: must)

1. **4-Layer POM Structure** - Tests → Workflows → Actions → Locators
2. **Structured Test Tags** - Every test MUST have tags for selective execution
3. **TRY-EXCEPT with Screenshots** - Error handling in all page actions
4. **Test Isolation via Teardown** - Cleanup in every test
5. **Never Hardcode Credentials** - Use environment variables

### RECOMMENDED (priority: should)

6. **Structured Logging** - Custom log keywords, not Log To Console
7. **Use API for Cleanup** - UI creates, API cleans (faster, reliable)
8. **FakerLibrary for Data** - Random unique data on every run
9. **Test Documentation** - [Documentation] explaining what and why
10. **Device Emulation** - Test responsive design with mobile viewports

## Integration Points

1. **UI → API (cleanup):** UI creates form → API DELETE cleans up
2. **UI → db (verification):** UI submits → DB query verifies record
3. **API → db (verification):** API creates → DB query verifies persistence
4. **UI → ImageComparisonLibrary:** Screenshot → Visual regression check

## Security Issues ⚠️

**FOUND:** Hardcoded password in `db/variables.resource`:
```robot
${DB_PASSWORD}    f0rt4n3
```

**FIX REQUIRED:**
```robot
${DB_PASSWORD}    %{DB_PASSWORD}    # From environment variable
```

Or use `.env` file with BuiltIn library.

## Common Commands

**API Smoke Tests (fast ~30s):**
```bash
robot --include smoke RF/API/tests/
```

**All API Tests:**
```bash
robot RF/API/tests/
```

**UI Tests Headless (for CI/CD):**
```bash
robot --variable HEADLESS:True RF/UI/tests/
```

**Tests by Tag:**
```bash
robot --include critical --exclude wip RF/
```

**Parallel Execution (requires pabot):**
```bash
pabot --processes 4 RF/API/tests/
```

## Files Included

1. **memento.db** - The SQLite database (main file)
2. **rf_memento_schema.sql** - Database schema (CREATE TABLE statements)
3. **rf_memento_data.sql** - Data population (INSERT statements)
4. **rf_memento_queries.sql** - Helper queries (100+ ready-to-use queries)
5. **RF_MEMENTO_README.md** - This file

## Rebuilding Database

If needed:
```bash
cd C:\Users\stoka\Documents\moje_app\RF
rm memento.db
sqlite3 memento.db < rf_memento_schema.sql
sqlite3 memento.db < rf_memento_data.sql
sqlite3 memento.db "SELECT COUNT(*) FROM rf_components;"
```

## Python Integration

```python
import sqlite3

conn = sqlite3.connect('RF/memento.db')
cursor = conn.cursor()

# Get all components
cursor.execute("SELECT component_name, primary_purpose FROM rf_components")
for component in cursor.fetchall():
    print(f"{component[0]}: {component[1]}")

# Find workflows
cursor.execute("""
    SELECT r.resource_name, k.keyword_name
    FROM rf_keywords k
    JOIN rf_resources r ON k.resource_id = r.id
    WHERE k.keyword_type = 'workflow'
""")
for row in cursor.fetchall():
    print(f"{row[0]} → {row[1]}")

conn.close()
```

## Educational Value

This database serves as:

✅ **Onboarding Tool** - New team members understand project structure
✅ **Quality Check** - Find violations and issues systematically
✅ **Best Practices Reference** - Learn from API tests, fix UI tests
✅ **Documentation** - Living documentation that stays updated
✅ **Analysis Tool** - Dependency graphs, statistics, trends

## Identified Issues & Recommendations

### Critical (Fix Now)
- ❌ **Security:** Hardcoded password in db/variables.resource
- ❌ **POM Violation:** UI tests missing workflows/ layer

### High Priority
- ❌ **UI Tests:** No tags (add smoke, critical, regression)
- ❌ **UI Tests:** Missing documentation
- ❌ **UI Tests:** Using Log To Console (change to structured logging)

### Recommended
- ℹ️ **API Tests:** Some tests missing documentation
- ℹ️ **All Tests:** Consider parallel execution with pabot
- ℹ️ **Configuration:** Externalize environment-specific variables

## Related Documentation

- **ImageComparisonLibrary Details:** See `ImageComparisonLibrary/memento.db`
- **Best Practices:** See `README_CLAUDE.md` in RF/
- **Installation:** See `README.md` in RF/
- **Main Project:** See `CLAUDE.md` in project root

## Version History

**1.0.0** (2024-11-21) - Initial release
- Complete RF project structure captured
- 14 tables with 101 rows
- 100+ helper queries
- Identified 2 critical issues (security, POM violation)
- Documented all 4 components
- Full POM layer explanation

## Author

**Project:** RF Test Automation Suite by Dušan Čižmarik
**Database:** Created by Claude Code (Anthropic)
**Date:** 2024-11-21

---

*This knowledge base captures the complete state of RF Test Automation Suite including API, UI, db, and ImageComparisonLibrary components.*
