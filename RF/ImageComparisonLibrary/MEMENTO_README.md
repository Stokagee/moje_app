# MEMENTO.DB - ImageComparisonLibrary Knowledge Database

**Created:** 2024-11-21
**Purpose:** Comprehensive knowledge base capturing all important information about ImageComparisonLibrary

## Overview

Memento.db is a SQLite database containing **14 tables** with **113 rows** of structured knowledge about ImageComparisonLibrary version 1.5.0.

## Database Structure

### CORE TABLES (7) - Basic metadata and architecture
1. **project_info** (1 row) - Project metadata, current version, author, license
2. **files** (10 rows) - Project files with responsibilities and descriptions
3. **versions** (5 rows) - Version history from 1.0.0 to 1.5.0
4. **version_changes** (18 rows) - Detailed changes per version
5. **methods** (12 rows) - All public and private methods with line numbers
6. **parameters** (22 rows) - Method parameters with defaults and descriptions
7. **dependencies** (10 rows) - Runtime and dev dependencies

### KNOWLEDGE TABLES (5) - Domain knowledge
8. **keywords** (2 rows) - Robot Framework keywords with examples
9. **algorithms** (2 rows) - phash and dhash characteristics
10. **use_cases** (6 rows) - Common scenarios with recommended settings
11. **troubleshooting** (7 rows) - Common problems and solutions
12. **performance_metrics** (7 rows) - Performance characteristics

### REFERENCE TABLES (2) - Reference information
13. **diff_modes** (2 rows) - contours vs filled visualization modes
14. **best_practices** (7 rows) - Development and usage recommendations

## Quick Start

### Opening the database:
```bash
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
SELECT * FROM project_info;
```

**List all versions:**
```sql
SELECT version_number, release_date, summary FROM versions ORDER BY release_date DESC;
```

**Find parameters for main keyword:**
```sql
SELECT p.param_name, p.default_value, p.description_en
FROM parameters p
JOIN methods m ON p.method_id = m.id
WHERE m.method_name = 'compare_layouts_and_generate_diff';
```

**What changed in v1.5.0?**
```sql
SELECT change_type, title, description
FROM version_changes vc
JOIN versions v ON vc.version_id = v.id
WHERE v.version_number = '1.5.0';
```

## Helper Queries

The file `memento_queries.sql` contains **80+ ready-to-use queries** organized by category:

- Basic info queries
- Method & parameter queries
- Version history queries
- Algorithm & performance queries
- Use case queries
- Troubleshooting queries
- Configuration queries
- Diff modes & best practices
- Dependencies queries
- File structure queries
- Keyword queries
- Advanced queries
- Statistics queries
- Search queries

### Using helper queries:

**Run single query:**
```bash
sqlite3 memento.db "SELECT * FROM project_info;"
```

**Load and execute all queries:**
```bash
sqlite3 memento.db < memento_queries.sql
```

**Export results to CSV:**
```bash
sqlite3 -csv memento.db "SELECT * FROM use_cases;" > use_cases.csv
```

## Common Use Cases

### 1. Find how to detect white elements:
```sql
SELECT use_case_name, recommended_settings, notes
FROM use_cases
WHERE use_case_name LIKE '%white%';
```

### 2. Get all parameters added in v1.5.0:
```sql
SELECT param_name, description_en
FROM parameters
WHERE added_in_version = '1.5.0';
```

### 3. Find solution for dimension error:
```sql
SELECT issue_title, solution
FROM troubleshooting
WHERE issue_title LIKE '%dimension%';
```

### 4. Compare algorithms:
```sql
SELECT algorithm_name, speed_rating, accuracy_rating, typical_time_ms
FROM algorithms;
```

### 5. Get all methods by complexity:
```sql
SELECT method_name, complexity, purpose_en
FROM methods
WHERE method_type = 'private'
ORDER BY complexity DESC;
```

## Database Statistics

| Table | Rows | Description |
|-------|------|-------------|
| project_info | 1 | Project metadata |
| files | 10 | Project files |
| versions | 5 | Version history |
| version_changes | 18 | Changes per version |
| methods | 12 | All methods |
| parameters | 22 | Method parameters |
| dependencies | 10 | Dependencies |
| keywords | 2 | RF keywords |
| algorithms | 2 | Hash algorithms |
| use_cases | 6 | Usage scenarios |
| troubleshooting | 7 | Common issues |
| performance_metrics | 7 | Performance data |
| diff_modes | 2 | Visualization modes |
| best_practices | 7 | Recommendations |
| **TOTAL** | **113** | **All data** |

## Files Included

1. **memento.db** - The SQLite database (main file)
2. **memento_schema.sql** - Database schema (CREATE TABLE statements)
3. **memento_data.sql** - Data population (INSERT statements)
4. **memento_queries.sql** - Helper queries (80+ ready-to-use queries)
5. **MEMENTO_README.md** - This file

## Rebuilding the Database

If you need to rebuild from scratch:

```bash
# Delete old database
rm memento.db

# Create fresh database with schema
sqlite3 memento.db < memento_schema.sql

# Populate with data
sqlite3 memento.db < memento_data.sql

# Verify
sqlite3 memento.db "SELECT COUNT(*) FROM project_info;"
```

## Advanced Usage

### Export entire database to SQL:
```bash
sqlite3 memento.db .dump > memento_backup.sql
```

### Search across all text fields:
```bash
sqlite3 memento.db "
SELECT 'use_cases' as source, use_case_name as title, scenario as content
FROM use_cases WHERE scenario LIKE '%loader%'
UNION ALL
SELECT 'troubleshooting', issue_title, solution
FROM troubleshooting WHERE solution LIKE '%loader%';"
```

### Get relationships:
```bash
sqlite3 memento.db "
SELECT m.method_name, COUNT(p.id) as param_count
FROM methods m
LEFT JOIN parameters p ON m.id = p.method_id
GROUP BY m.method_name
ORDER BY param_count DESC;"
```

## Integration with Python

```python
import sqlite3

# Connect to database
conn = sqlite3.connect('memento.db')
cursor = conn.cursor()

# Query example
cursor.execute("SELECT * FROM project_info")
project = cursor.fetchone()
print(f"Project: {project[1]} v{project[2]}")

# Get all use cases
cursor.execute("SELECT use_case_name, recommended_settings FROM use_cases")
for use_case in cursor.fetchall():
    print(f"{use_case[0]}: {use_case[1]}")

conn.close()
```

## Maintenance

**To update with new version:**
1. Update `project_info` table with new version
2. Add new row to `versions` table
3. Add change records to `version_changes` table
4. Update `methods` if new methods added
5. Add new `parameters` if applicable
6. Update `is_current` flag in versions

## Benefits

- **Fast access** to all library information
- **Structured knowledge** easy to query
- **Version history** tracking
- **Relationships** between entities (methods, parameters, versions)
- **Searchable** full-text content
- **Portable** single-file database
- **No dependencies** - SQLite built into Python

## Author

Dušan Čižmarik
**Database created by:** Claude Code (Anthropic)
**Date:** 2024-11-21

---

*This knowledge base captures the state of ImageComparisonLibrary v1.5.0*
