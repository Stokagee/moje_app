-- ============================================================================
-- RF PROJECT MEMENTO DATABASE - HELPER QUERIES
-- Date: 2024-11-21
-- Purpose: Ready-to-use SQL queries for common information retrieval tasks
-- ============================================================================

-- ============================================================================
-- PROJECT OVERVIEW QUERIES
-- ============================================================================

-- Get project metadata
SELECT * FROM rf_project_metadata;

-- List all components with basic info
SELECT component_name, component_type, primary_purpose, test_count, resource_count
FROM rf_components
WHERE is_active = 1
ORDER BY component_name;

-- Get component details
SELECT *
FROM rf_components
WHERE component_name = 'API';

-- ============================================================================
-- TEST SUITE QUERIES
-- ============================================================================

-- List all test suites
SELECT
    c.component_name,
    s.suite_name,
    s.file_name,
    s.test_case_count,
    s.suite_tags
FROM rf_test_suites s
JOIN rf_components c ON s.component_id = c.id
ORDER BY c.component_name, s.suite_name;

-- Find test suites by component
SELECT suite_name, file_path, test_case_count, purpose
FROM rf_test_suites
WHERE component_id = (SELECT id FROM rf_components WHERE component_name = 'API')
ORDER BY suite_name;

-- Find test suites by tag
SELECT
    c.component_name,
    s.suite_name,
    s.suite_tags,
    s.purpose
FROM rf_test_suites s
JOIN rf_components c ON s.component_id = c.id
WHERE s.suite_tags LIKE '%smoke%'
ORDER BY c.component_name;

-- Get test suite details with component info
SELECT
    c.component_name,
    s.suite_name,
    s.file_path,
    s.test_case_count,
    s.setup_keyword,
    s.teardown_keyword,
    s.description
FROM rf_test_suites s
JOIN rf_components c ON s.component_id = c.id
WHERE s.suite_name = 'Form CRUD Tests';

-- ============================================================================
-- TEST CASE QUERIES
-- ============================================================================

-- List all test cases with priority
SELECT
    s.suite_name,
    t.test_name,
    t.test_type,
    t.priority,
    t.test_tags
FROM rf_test_cases t
JOIN rf_test_suites s ON t.suite_id = s.id
ORDER BY
    CASE t.priority
        WHEN 'critical' THEN 1
        WHEN 'high' THEN 2
        WHEN 'medium' THEN 3
        WHEN 'low' THEN 4
    END,
    s.suite_name;

-- Find test cases by tag
SELECT
    s.suite_name,
    t.test_name,
    t.test_tags,
    t.description
FROM rf_test_cases t
JOIN rf_test_suites s ON t.suite_id = s.id
WHERE t.test_tags LIKE '%smoke%'
ORDER BY s.suite_name;

-- Get critical tests only
SELECT
    s.suite_name,
    t.test_name,
    t.description,
    t.expected_outcome
FROM rf_test_cases t
JOIN rf_test_suites s ON t.suite_id = s.id
WHERE t.priority = 'critical'
ORDER BY s.suite_name;

-- Find tests using specific workflow
SELECT
    s.suite_name,
    t.test_name,
    t.workflows_used
FROM rf_test_cases t
JOIN rf_test_suites s ON t.suite_id = s.id
WHERE t.workflows_used LIKE '%Create Form With Random Data%'
ORDER BY s.suite_name;

-- ============================================================================
-- RESOURCE QUERIES
-- ============================================================================

-- List all resources by component
SELECT
    c.component_name,
    r.resource_name,
    r.layer_number,
    r.layer_name,
    r.resource_type,
    r.keyword_count
FROM rf_resources r
JOIN rf_components c ON r.component_id = c.id
ORDER BY c.component_name, r.layer_number NULLS LAST, r.resource_name;

-- Find resources by layer
SELECT
    c.component_name,
    r.resource_name,
    r.file_path,
    r.primary_purpose
FROM rf_resources r
JOIN rf_components c ON r.component_id = c.id
WHERE r.layer_number = 3
ORDER BY c.component_name;

-- Find workflows resources
SELECT
    c.component_name,
    r.resource_name,
    r.file_path,
    r.keyword_count,
    r.description
FROM rf_resources r
JOIN rf_components c ON r.component_id = c.id
WHERE r.layer_name = 'workflows'
ORDER BY c.component_name;

-- Get resource details with imports
SELECT
    resource_name,
    file_path,
    layer_number,
    libraries_imported,
    resources_imported,
    description
FROM rf_resources
WHERE resource_name = 'API Common';

-- ============================================================================
-- KEYWORD QUERIES
-- ============================================================================

-- List all keywords by type
SELECT
    r.resource_name,
    k.keyword_name,
    k.keyword_type,
    k.layer_number,
    k.complexity
FROM rf_keywords k
LEFT JOIN rf_resources r ON k.resource_id = r.id
ORDER BY k.keyword_type, k.keyword_name;

-- Find workflows keywords
SELECT
    r.resource_name,
    k.keyword_name,
    k.arguments,
    k.purpose
FROM rf_keywords k
LEFT JOIN rf_resources r ON k.resource_id = r.id
WHERE k.keyword_type = 'workflow'
ORDER BY k.keyword_name;

-- Find keywords with error handling
SELECT
    r.resource_name,
    k.keyword_name,
    k.keyword_type,
    k.has_error_handling,
    k.has_logging
FROM rf_keywords k
LEFT JOIN rf_resources r ON k.resource_id = r.id
WHERE k.has_error_handling = 1
ORDER BY r.resource_name, k.keyword_name;

-- Get keyword details
SELECT
    keyword_name,
    keyword_type,
    arguments,
    return_value,
    description,
    purpose,
    calls_keywords,
    used_by_tests
FROM rf_keywords
WHERE keyword_name = 'Create Form With Random Data';

-- Find complex keywords
SELECT
    r.resource_name,
    k.keyword_name,
    k.keyword_type,
    k.complexity,
    k.purpose
FROM rf_keywords k
LEFT JOIN rf_resources r ON k.resource_id = r.id
WHERE k.complexity = 'complex'
ORDER BY r.resource_name;

-- ============================================================================
-- LIBRARY QUERIES
-- ============================================================================

-- List all libraries
SELECT
    library_name,
    library_type,
    version,
    purpose,
    used_by_components
FROM rf_libraries
ORDER BY library_type, library_name;

-- Find external libraries
SELECT
    library_name,
    version,
    purpose,
    installation_command
FROM rf_libraries
WHERE library_type = 'external'
ORDER BY library_name;

-- Find libraries used by specific component
SELECT
    library_name,
    purpose,
    key_keywords
FROM rf_libraries
WHERE used_by_components LIKE '%UI%'
ORDER BY library_name;

-- Get library details
SELECT *
FROM rf_libraries
WHERE library_name = 'Browser';

-- ============================================================================
-- VARIABLE & CONFIGURATION QUERIES
-- ============================================================================

-- List all variables by component
SELECT
    c.component_name,
    v.variable_name,
    v.variable_value,
    v.variable_type,
    v.description
FROM rf_variables_config v
JOIN rf_components c ON v.component_id = c.id
ORDER BY c.component_name, v.variable_type, v.variable_name;

-- Find sensitive variables (SECURITY CHECK!)
SELECT
    c.component_name,
    v.variable_name,
    v.variable_value,
    v.file_path,
    v.notes
FROM rf_variables_config v
JOIN rf_components c ON v.component_id = c.id
WHERE v.is_sensitive = 1
ORDER BY c.component_name;

-- Find URL configuration
SELECT
    c.component_name,
    v.variable_name,
    v.variable_value,
    v.description
FROM rf_variables_config v
JOIN rf_components c ON v.component_id = c.id
WHERE v.variable_type = 'url'
ORDER BY c.component_name;

-- Get all config for specific component
SELECT
    variable_name,
    variable_value,
    variable_type,
    description
FROM rf_variables_config
WHERE component_id = (SELECT id FROM rf_components WHERE component_name = 'UI')
ORDER BY variable_type, variable_name;

-- ============================================================================
-- POM ARCHITECTURE QUERIES
-- ============================================================================

-- Understand all POM layers
SELECT
    layer_number,
    layer_name,
    description,
    responsibilities,
    example_files
FROM rf_pom_layers
ORDER BY layer_number;

-- Get specific layer details
SELECT
    layer_name,
    description,
    should_contain,
    should_not_contain,
    calls_layer,
    notes
FROM rf_pom_layers
WHERE layer_number = 3;

-- Compare API and UI layer implementations
SELECT
    layer_number,
    layer_name,
    api_equivalent,
    ui_equivalent
FROM rf_pom_layers
ORDER BY layer_number;

-- ============================================================================
-- BEST PRACTICES QUERIES
-- ============================================================================

-- List all best practices
SELECT
    category,
    practice_name,
    priority,
    applies_to
FROM rf_best_practices
ORDER BY
    CASE priority
        WHEN 'must' THEN 1
        WHEN 'should' THEN 2
        WHEN 'recommended' THEN 3
    END,
    category;

-- Find best practices by category
SELECT
    practice_name,
    description,
    why_important,
    correct_example
FROM rf_best_practices
WHERE category = 'POM Architecture'
ORDER BY practice_name;

-- Get "must-have" practices
SELECT
    category,
    practice_name,
    description,
    applies_to
FROM rf_best_practices
WHERE priority = 'must'
ORDER BY category;

-- Find practices for specific test type
SELECT
    category,
    practice_name,
    description,
    correct_example,
    incorrect_example
FROM rf_best_practices
WHERE applies_to LIKE '%API%'
ORDER BY category;

-- Get educational notes
SELECT
    practice_name,
    educational_notes,
    notes
FROM rf_best_practices
WHERE educational_notes IS NOT NULL
ORDER BY practice_name;

-- ============================================================================
-- INTEGRATION QUERIES
-- ============================================================================

-- List all integration points
SELECT
    from_component,
    to_component,
    integration_type,
    description,
    keywords_used
FROM rf_integration_points
ORDER BY from_component, to_component;

-- Find integrations for specific component
SELECT
    to_component,
    integration_type,
    description,
    example_usage
FROM rf_integration_points
WHERE from_component = 'UI'
ORDER BY to_component;

-- Get integration details
SELECT *
FROM rf_integration_points
WHERE from_component = 'UI' AND to_component = 'API';

-- ============================================================================
-- DEPENDENCY QUERIES
-- ============================================================================

-- List all dependencies
SELECT
    dependent_file,
    dependency_file,
    dependency_type,
    is_cross_component
FROM rf_dependencies
ORDER BY is_cross_component DESC, dependent_file;

-- Find cross-component dependencies
SELECT
    dependent_file,
    dependency_file,
    dependency_type,
    notes
FROM rf_dependencies
WHERE is_cross_component = 1
ORDER BY dependent_file;

-- Find violations (Layer 4 calling Layer 2 directly)
SELECT
    dependent_file,
    dependency_file,
    notes
FROM rf_dependencies
WHERE notes LIKE '%VIOLATION%'
ORDER BY dependent_file;

-- Find dependencies for specific file
SELECT
    dependency_file,
    dependency_type
FROM rf_dependencies
WHERE dependent_file LIKE '%form_crud_tests.robot%'
ORDER BY dependency_type;

-- ============================================================================
-- TEST DATA QUERIES
-- ============================================================================

-- List all test data sources
SELECT
    source_name,
    source_type,
    data_format,
    used_by_components,
    purpose
FROM rf_test_data_sources
ORDER BY source_type, source_name;

-- Find data sources by component
SELECT
    source_name,
    source_type,
    purpose,
    example_data
FROM rf_test_data_sources
WHERE used_by_components LIKE '%API%'
ORDER BY source_name;

-- Get data source details
SELECT *
FROM rf_test_data_sources
WHERE source_name = 'FakerLibrary';

-- ============================================================================
-- COMMAND REFERENCE QUERIES
-- ============================================================================

-- List all commands
SELECT
    command_name,
    component,
    use_case,
    command
FROM rf_command_reference
ORDER BY component, command_name;

-- Find commands by component
SELECT
    command_name,
    command,
    description,
    expected_output
FROM rf_command_reference
WHERE component = 'API'
ORDER BY command_name;

-- Find commands by tag
SELECT
    command_name,
    command,
    description
FROM rf_command_reference
WHERE tags_used LIKE '%smoke%'
ORDER BY command_name;

-- Get command details
SELECT
    command_name,
    command,
    description,
    use_case,
    expected_output,
    notes
FROM rf_command_reference
WHERE command_name = 'Run API Smoke Tests';

-- ============================================================================
-- STATISTICS QUERIES
-- ============================================================================

-- Count rows in all tables
SELECT 'rf_project_metadata' as table_name, COUNT(*) as row_count FROM rf_project_metadata
UNION ALL SELECT 'rf_components', COUNT(*) FROM rf_components
UNION ALL SELECT 'rf_test_suites', COUNT(*) FROM rf_test_suites
UNION ALL SELECT 'rf_test_cases', COUNT(*) FROM rf_test_cases
UNION ALL SELECT 'rf_resources', COUNT(*) FROM rf_resources
UNION ALL SELECT 'rf_keywords', COUNT(*) FROM rf_keywords
UNION ALL SELECT 'rf_libraries', COUNT(*) FROM rf_libraries
UNION ALL SELECT 'rf_variables_config', COUNT(*) FROM rf_variables_config
UNION ALL SELECT 'rf_pom_layers', COUNT(*) FROM rf_pom_layers
UNION ALL SELECT 'rf_best_practices', COUNT(*) FROM rf_best_practices
UNION ALL SELECT 'rf_integration_points', COUNT(*) FROM rf_integration_points
UNION ALL SELECT 'rf_dependencies', COUNT(*) FROM rf_dependencies
UNION ALL SELECT 'rf_test_data_sources', COUNT(*) FROM rf_test_data_sources
UNION ALL SELECT 'rf_command_reference', COUNT(*) FROM rf_command_reference
ORDER BY table_name;

-- Component statistics
SELECT
    component_name,
    test_count,
    resource_count,
    total_lines,
    architecture_layers
FROM rf_components
WHERE is_active = 1
ORDER BY total_lines DESC;

-- Test distribution by component
SELECT
    c.component_name,
    COUNT(s.id) as suite_count,
    SUM(s.test_case_count) as total_tests
FROM rf_components c
LEFT JOIN rf_test_suites s ON c.id = s.component_id
GROUP BY c.component_name
ORDER BY total_tests DESC;

-- Resource distribution by layer
SELECT
    layer_number,
    layer_name,
    COUNT(*) as resource_count,
    SUM(keyword_count) as total_keywords
FROM rf_resources
WHERE layer_number IS NOT NULL
GROUP BY layer_number, layer_name
ORDER BY layer_number;

-- Keyword complexity distribution
SELECT
    complexity,
    COUNT(*) as keyword_count
FROM rf_keywords
WHERE complexity IS NOT NULL
GROUP BY complexity
ORDER BY
    CASE complexity
        WHEN 'low' THEN 1
        WHEN 'simple' THEN 1
        WHEN 'medium' THEN 2
        WHEN 'complex' THEN 3
        WHEN 'high' THEN 3
    END;

-- Library usage statistics
SELECT
    library_type,
    COUNT(*) as library_count
FROM rf_libraries
GROUP BY library_type
ORDER BY library_count DESC;

-- ============================================================================
-- VALIDATION & QUALITY QUERIES
-- ============================================================================

-- Find missing tags in test suites
SELECT
    c.component_name,
    s.suite_name,
    s.file_path,
    'Missing tags' as issue
FROM rf_test_suites s
JOIN rf_components c ON s.component_id = c.id
WHERE s.suite_tags IS NULL OR s.suite_tags = ''
ORDER BY c.component_name;

-- Find test cases without priority
SELECT
    s.suite_name,
    t.test_name,
    'Missing priority' as issue
FROM rf_test_cases t
JOIN rf_test_suites s ON t.suite_id = s.id
WHERE t.priority IS NULL
ORDER BY s.suite_name;

-- Find keywords without error handling
SELECT
    r.resource_name,
    k.keyword_name,
    k.keyword_type,
    'Missing error handling' as issue
FROM rf_keywords k
LEFT JOIN rf_resources r ON k.resource_id = r.id
WHERE k.has_error_handling = 0 AND k.keyword_type IN ('workflow', 'page_action')
ORDER BY r.resource_name;

-- Find sensitive variables (security check)
SELECT
    c.component_name,
    v.variable_name,
    v.file_path,
    'Sensitive data - review security' as warning
FROM rf_variables_config v
JOIN rf_components c ON v.component_id = c.id
WHERE v.is_sensitive = 1
ORDER BY c.component_name;

-- Find POM violations
SELECT
    component_name,
    notes as violation
FROM rf_components
WHERE notes LIKE '%VIOLATION%'
UNION ALL
SELECT
    suite_name,
    notes
FROM rf_test_suites
WHERE notes LIKE '%VIOLATION%'
UNION ALL
SELECT
    keyword_name,
    notes
FROM rf_keywords
WHERE notes LIKE '%VIOLATION%'
ORDER BY violation;

-- ============================================================================
-- ADVANCED ANALYSIS QUERIES
-- ============================================================================

-- Find most used keywords
SELECT
    k.keyword_name,
    k.keyword_type,
    k.used_by_tests,
    r.resource_name
FROM rf_keywords k
LEFT JOIN rf_resources r ON k.resource_id = r.id
WHERE k.used_by_tests IS NOT NULL
ORDER BY LENGTH(k.used_by_tests) DESC
LIMIT 10;

-- Component dependency graph
SELECT DISTINCT
    d.dependent_file,
    d.dependency_file,
    d.dependency_type
FROM rf_dependencies d
ORDER BY d.dependent_file;

-- Find reusable workflows
SELECT
    k.keyword_name,
    k.purpose,
    k.used_by_tests,
    r.resource_name
FROM rf_keywords k
LEFT JOIN rf_resources r ON k.resource_id = r.id
WHERE k.keyword_type = 'workflow'
ORDER BY LENGTH(k.used_by_tests) DESC;

-- Educational gaps (missing best practices)
SELECT
    c.component_name,
    COUNT(DISTINCT bp.category) as practices_applied,
    'Check if all best practices are followed' as note
FROM rf_components c
CROSS JOIN rf_best_practices bp
WHERE bp.applies_to LIKE '%' || c.component_name || '%' OR bp.applies_to = 'All tests'
GROUP BY c.component_name
ORDER BY practices_applied;

-- ============================================================================
-- FULL PROJECT SUMMARY
-- ============================================================================

SELECT
    'Project' as item,
    project_name as name,
    framework_version as version,
    architecture_pattern as info
FROM rf_project_metadata
UNION ALL
SELECT
    'Components',
    CAST(COUNT(*) AS TEXT),
    GROUP_CONCAT(component_name, ', '),
    NULL
FROM rf_components
WHERE is_active = 1
UNION ALL
SELECT
    'Test Suites',
    CAST(COUNT(*) AS TEXT),
    NULL,
    NULL
FROM rf_test_suites
UNION ALL
SELECT
    'Libraries',
    CAST(COUNT(*) AS TEXT),
    GROUP_CONCAT(library_name, ', '),
    NULL
FROM rf_libraries;

-- ============================================================================
-- USAGE EXAMPLES
-- ============================================================================

-- To use these queries:
--   1. Open database: sqlite3 memento.db
--   2. Enable formatting: .mode column, .headers on, .width auto
--   3. Run any query from above
--
-- Quick commands:
--   sqlite3 memento.db "SELECT * FROM rf_project_metadata;"
--   sqlite3 -csv memento.db "SELECT * FROM rf_test_suites;" > test_suites.csv
--
-- Interactive mode:
--   sqlite3 memento.db
--   .mode column
--   .headers on
--   SELECT * FROM rf_components;
--
-- ============================================================================
