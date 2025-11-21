-- MEMENTO.DB HELPER QUERIES - ImageComparisonLibrary
-- Created: 2024-11-21
-- Purpose: Ready-to-use SQL queries for common information retrieval tasks

-- ============================================================================
-- BASIC INFO QUERIES
-- ============================================================================

-- Get current project info
SELECT * FROM project_info;

-- Get current version info
SELECT * FROM versions WHERE is_current = 1;

-- List all versions with dates
SELECT version_number, release_date, summary
FROM versions
ORDER BY release_date DESC;

-- ============================================================================
-- METHOD & PARAMETER QUERIES
-- ============================================================================

-- List all public keywords (Robot Framework)
SELECT method_name, purpose_en, returns
FROM methods
WHERE method_type = 'public'
ORDER BY method_name;

-- Find all parameters for compare_layouts_and_generate_diff
SELECT p.param_name, p.param_type, p.default_value, p.description_en
FROM parameters p
JOIN methods m ON p.method_id = m.id
WHERE m.method_name = 'compare_layouts_and_generate_diff'
ORDER BY p.id;

-- Find all parameters for check_layouts_are_visually_similar
SELECT p.param_name, p.param_type, p.default_value, p.description_en
FROM parameters p
JOIN methods m ON p.method_id = m.id
WHERE m.method_name = 'check_layouts_are_visually_similar'
ORDER BY p.id;

-- List all private methods with complexity
SELECT method_name, purpose_en, complexity, returns
FROM methods
WHERE method_type = 'private'
ORDER BY complexity DESC, method_name;

-- Find methods by complexity level
SELECT method_name, method_type, purpose_en, start_line, end_line
FROM methods
WHERE complexity = 'high'
ORDER BY method_name;

-- ============================================================================
-- VERSION HISTORY QUERIES
-- ============================================================================

-- What changed in version 1.5.0?
SELECT vc.change_type, vc.category, vc.title, vc.description, vc.impact
FROM version_changes vc
JOIN versions v ON vc.version_id = v.id
WHERE v.version_number = '1.5.0'
ORDER BY vc.change_type, vc.category;

-- What changed in version 1.4.0?
SELECT vc.change_type, vc.category, vc.title, vc.description
FROM version_changes vc
JOIN versions v ON vc.version_id = v.id
WHERE v.version_number = '1.4.0'
ORDER BY vc.change_type;

-- All changes across all versions
SELECT v.version_number, vc.change_type, vc.title, vc.description
FROM version_changes vc
JOIN versions v ON vc.version_id = v.id
ORDER BY v.release_date DESC, vc.change_type;

-- Count changes by type per version
SELECT v.version_number, vc.change_type, COUNT(*) as change_count
FROM version_changes vc
JOIN versions v ON vc.version_id = v.id
GROUP BY v.version_number, vc.change_type
ORDER BY v.version_number DESC, vc.change_type;

-- When was parameter X added?
SELECT param_name, added_in_version, description_en
FROM parameters
WHERE param_name = 'element_fill_expansion';

-- ============================================================================
-- ALGORITHM & PERFORMANCE QUERIES
-- ============================================================================

-- Compare phash vs dhash
SELECT algorithm_name, speed_rating, accuracy_rating, typical_time_ms, recommended_for
FROM algorithms
ORDER BY algorithm_name;

-- Performance metrics for phash
SELECT operation, typical_time_ms, memory_usage, notes
FROM performance_metrics
WHERE algorithm = 'phash' OR algorithm IS NULL
ORDER BY operation;

-- All performance metrics
SELECT operation, algorithm, image_resolution, typical_time_ms, memory_usage
FROM performance_metrics
ORDER BY CAST(REPLACE(SUBSTR(typical_time_ms, 1, INSTR(typical_time_ms || '-', '-') - 1), '+', '') AS INTEGER);

-- ============================================================================
-- USE CASE QUERIES
-- ============================================================================

-- Find use case for white elements
SELECT use_case_name, scenario, recommended_settings, notes
FROM use_cases
WHERE use_case_name LIKE '%white%' OR scenario LIKE '%white%';

-- Find use case for element position shift
SELECT use_case_name, scenario, recommended_settings, example_code
FROM use_cases
WHERE use_case_name LIKE '%shift%' OR use_case_name LIKE '%position%';

-- All use cases with settings
SELECT use_case_name, recommended_settings, notes
FROM use_cases
ORDER BY use_case_name;

-- ============================================================================
-- TROUBLESHOOTING QUERIES
-- ============================================================================

-- Find solution for dimension error
SELECT issue_title, cause, solution
FROM troubleshooting
WHERE issue_title LIKE '%dimension%';

-- Find solution for missing diff
SELECT issue_title, symptoms, cause, solution, related_parameter
FROM troubleshooting
WHERE issue_title LIKE '%diff%';

-- All troubleshooting issues
SELECT issue_title, symptoms, solution, related_parameter
FROM troubleshooting
ORDER BY issue_title;

-- Find issues related to specific parameter
SELECT issue_title, symptoms, solution
FROM troubleshooting
WHERE related_parameter LIKE '%min_contour_area%';

-- ============================================================================
-- CONFIGURATION QUERIES
-- ============================================================================

-- Get default values for all parameters of main keyword
SELECT param_name, default_value, description_en
FROM parameters
WHERE method_id = 1 AND default_value IS NOT NULL
ORDER BY param_name;

-- Find parameters added in specific version
SELECT param_name, description_en, added_in_version
FROM parameters
WHERE added_in_version = '1.5.0'
ORDER BY param_name;

-- Parameters with min/max constraints
SELECT param_name, param_type, default_value, min_value, max_value, example_values
FROM parameters
WHERE min_value IS NOT NULL OR max_value IS NOT NULL
ORDER BY param_name;

-- ============================================================================
-- DIFF MODES & BEST PRACTICES
-- ============================================================================

-- Compare diff modes
SELECT mode_name, description, visual_style, when_to_use
FROM diff_modes
ORDER BY added_in_version;

-- Get best practices by category
SELECT category, practice_title, description, do_this, dont_do_this
FROM best_practices
WHERE category = 'Testing'
ORDER BY practice_title;

-- All best practices
SELECT category, practice_title, description
FROM best_practices
ORDER BY category, practice_title;

-- ============================================================================
-- DEPENDENCIES QUERIES
-- ============================================================================

-- List runtime dependencies
SELECT package_name, version_constraint, purpose
FROM dependencies
WHERE dependency_type = 'runtime'
ORDER BY package_name;

-- List dev dependencies
SELECT package_name, purpose
FROM dependencies
WHERE dependency_type = 'dev'
ORDER BY package_name;

-- All dependencies with types
SELECT package_name, version_constraint, dependency_type, purpose
FROM dependencies
ORDER BY dependency_type, package_name;

-- ============================================================================
-- FILE STRUCTURE QUERIES
-- ============================================================================

-- List all files by line count
SELECT file_name, line_count, responsibility
FROM files
WHERE line_count IS NOT NULL
ORDER BY line_count DESC;

-- Find core implementation files
SELECT file_path, responsibility, description
FROM files
WHERE file_path LIKE '%core.py%' OR file_path LIKE '%__init__%';

-- ============================================================================
-- KEYWORD QUERIES
-- ============================================================================

-- Compare strict vs relaxed keywords
SELECT keyword_name, strictness_level, default_algorithm, default_tolerance, typical_use_case
FROM keywords
ORDER BY strictness_level;

-- Get Robot Framework example for keyword
SELECT keyword_name, rf_example
FROM keywords
WHERE keyword_name LIKE '%Compare%';

-- ============================================================================
-- ADVANCED QUERIES
-- ============================================================================

-- Full method info with all parameters
SELECT
    m.method_name,
    m.method_type,
    m.purpose_en,
    p.param_name,
    p.default_value,
    p.description_en
FROM methods m
LEFT JOIN parameters p ON m.id = p.method_id
WHERE m.method_name = 'compare_layouts_and_generate_diff'
ORDER BY p.id;

-- Changes related to specific parameter across versions
SELECT
    v.version_number,
    vc.change_type,
    vc.title,
    vc.description
FROM version_changes vc
JOIN versions v ON vc.version_id = v.id
WHERE vc.related_parameter LIKE '%element_fill%'
ORDER BY v.release_date DESC;

-- Methods and their complexity distribution
SELECT complexity, COUNT(*) as method_count
FROM methods
GROUP BY complexity
ORDER BY
    CASE complexity
        WHEN 'low' THEN 1
        WHEN 'medium' THEN 2
        WHEN 'high' THEN 3
    END;

-- Parameters added per version
SELECT added_in_version, COUNT(*) as param_count
FROM parameters
WHERE added_in_version IS NOT NULL
GROUP BY added_in_version
ORDER BY added_in_version DESC;

-- ============================================================================
-- STATISTICS QUERIES
-- ============================================================================

-- Count rows in each table
SELECT 'project_info' as table_name, COUNT(*) as row_count FROM project_info
UNION ALL
SELECT 'files', COUNT(*) FROM files
UNION ALL
SELECT 'versions', COUNT(*) FROM versions
UNION ALL
SELECT 'version_changes', COUNT(*) FROM version_changes
UNION ALL
SELECT 'methods', COUNT(*) FROM methods
UNION ALL
SELECT 'parameters', COUNT(*) FROM parameters
UNION ALL
SELECT 'dependencies', COUNT(*) FROM dependencies
UNION ALL
SELECT 'keywords', COUNT(*) FROM keywords
UNION ALL
SELECT 'algorithms', COUNT(*) FROM algorithms
UNION ALL
SELECT 'use_cases', COUNT(*) FROM use_cases
UNION ALL
SELECT 'troubleshooting', COUNT(*) FROM troubleshooting
UNION ALL
SELECT 'performance_metrics', COUNT(*) FROM performance_metrics
UNION ALL
SELECT 'diff_modes', COUNT(*) FROM diff_modes
UNION ALL
SELECT 'best_practices', COUNT(*) FROM best_practices
ORDER BY table_name;

-- Total database statistics
SELECT
    (SELECT COUNT(*) FROM project_info) as project_info_rows,
    (SELECT COUNT(*) FROM files) as files_rows,
    (SELECT COUNT(*) FROM versions) as versions_rows,
    (SELECT COUNT(*) FROM version_changes) as version_changes_rows,
    (SELECT COUNT(*) FROM methods) as methods_rows,
    (SELECT COUNT(*) FROM parameters) as parameters_rows,
    (SELECT COUNT(*) FROM dependencies) as dependencies_rows,
    (SELECT COUNT(*) FROM keywords) as keywords_rows,
    (SELECT COUNT(*) FROM algorithms) as algorithms_rows,
    (SELECT COUNT(*) FROM use_cases) as use_cases_rows,
    (SELECT COUNT(*) FROM troubleshooting) as troubleshooting_rows,
    (SELECT COUNT(*) FROM performance_metrics) as performance_metrics_rows,
    (SELECT COUNT(*) FROM diff_modes) as diff_modes_rows,
    (SELECT COUNT(*) FROM best_practices) as best_practices_rows;

-- ============================================================================
-- SEARCH QUERIES (Full-text search examples)
-- ============================================================================

-- Search all use cases for keyword
SELECT use_case_name, scenario, recommended_settings
FROM use_cases
WHERE scenario LIKE '%loader%' OR use_case_name LIKE '%loader%';

-- Search troubleshooting for keyword
SELECT issue_title, solution
FROM troubleshooting
WHERE issue_title LIKE '%detect%' OR symptoms LIKE '%detect%' OR solution LIKE '%detect%';

-- Search parameters by description
SELECT param_name, description_en, default_value
FROM parameters
WHERE description_en LIKE '%tolerance%';

-- Search best practices by keyword
SELECT category, practice_title, description
FROM best_practices
WHERE description LIKE '%coverage%' OR practice_title LIKE '%coverage%';

-- ============================================================================
-- USAGE EXAMPLES
-- ============================================================================

-- To use these queries:
--   1. Open database: sqlite3 memento.db
--   2. Run query: copy-paste any query above
--   3. Or load this file: .read memento_queries.sql (executes all queries)
--
-- For formatted output:
--   .mode column
--   .headers on
--   .width auto
--
-- For specific query:
--   sqlite3 memento.db "SELECT * FROM project_info;"
--
-- Export results to CSV:
--   sqlite3 -csv memento.db "SELECT * FROM use_cases;" > use_cases.csv
