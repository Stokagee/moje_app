-- ============================================================================
-- RF PROJECT MEMENTO DATABASE SCHEMA
-- Purpose: Comprehensive knowledge base for entire RF test automation project
-- Date: 2024-11-21
-- ============================================================================

-- -----------------------------------------------------------------------------
-- TABLE 1: rf_project_metadata
-- Metadata about the entire RF project
-- -----------------------------------------------------------------------------
CREATE TABLE rf_project_metadata (
    id INTEGER PRIMARY KEY,
    project_name TEXT NOT NULL,
    project_path TEXT NOT NULL,
    description TEXT,
    framework_version TEXT,
    python_version TEXT,
    last_analyzed_date TEXT,
    total_components INTEGER,
    total_test_files INTEGER,
    total_resource_files INTEGER,
    architecture_pattern TEXT,
    primary_target TEXT,
    notes TEXT
);

-- -----------------------------------------------------------------------------
-- TABLE 2: rf_components
-- Main components (API, UI, db, ImageComparisonLibrary)
-- -----------------------------------------------------------------------------
CREATE TABLE rf_components (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    component_name TEXT NOT NULL,
    component_type TEXT NOT NULL,
    component_path TEXT NOT NULL,
    description TEXT,
    architecture_layers TEXT,
    primary_purpose TEXT,
    technology_stack TEXT,
    dependencies TEXT,
    test_count INTEGER,
    resource_count INTEGER,
    total_lines INTEGER,
    is_active BOOLEAN DEFAULT 1,
    notes TEXT
);

-- -----------------------------------------------------------------------------
-- TABLE 3: rf_test_suites
-- All test suites (.robot files)
-- -----------------------------------------------------------------------------
CREATE TABLE rf_test_suites (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    component_id INTEGER NOT NULL,
    suite_name TEXT NOT NULL,
    file_name TEXT NOT NULL,
    file_path TEXT NOT NULL,
    layer_number INTEGER,
    suite_tags TEXT,
    force_tags TEXT,
    default_tags TEXT,
    test_case_count INTEGER,
    setup_keyword TEXT,
    teardown_keyword TEXT,
    description TEXT,
    total_lines INTEGER,
    purpose TEXT,
    notes TEXT,
    FOREIGN KEY (component_id) REFERENCES rf_components(id)
);

-- -----------------------------------------------------------------------------
-- TABLE 4: rf_test_cases
-- Important test cases (key tests only)
-- -----------------------------------------------------------------------------
CREATE TABLE rf_test_cases (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    suite_id INTEGER NOT NULL,
    test_name TEXT NOT NULL,
    test_tags TEXT,
    test_type TEXT,
    priority TEXT,
    description TEXT,
    test_steps TEXT,
    workflows_used TEXT,
    expected_outcome TEXT,
    setup_keyword TEXT,
    teardown_keyword TEXT,
    is_data_driven BOOLEAN DEFAULT 0,
    template_keyword TEXT,
    notes TEXT,
    FOREIGN KEY (suite_id) REFERENCES rf_test_suites(id)
);

-- -----------------------------------------------------------------------------
-- TABLE 5: rf_resources
-- Resource files (.resource)
-- -----------------------------------------------------------------------------
CREATE TABLE rf_resources (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    component_id INTEGER NOT NULL,
    resource_name TEXT NOT NULL,
    file_name TEXT NOT NULL,
    file_path TEXT NOT NULL,
    layer_number INTEGER,
    layer_name TEXT,
    resource_type TEXT,
    primary_purpose TEXT,
    keyword_count INTEGER,
    variable_count INTEGER,
    libraries_imported TEXT,
    resources_imported TEXT,
    total_lines INTEGER,
    description TEXT,
    notes TEXT,
    FOREIGN KEY (component_id) REFERENCES rf_components(id)
);

-- -----------------------------------------------------------------------------
-- TABLE 6: rf_keywords
-- Custom keywords (important ones only)
-- -----------------------------------------------------------------------------
CREATE TABLE rf_keywords (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    resource_id INTEGER,
    keyword_name TEXT NOT NULL,
    keyword_type TEXT,
    layer_number INTEGER,
    arguments TEXT,
    return_value TEXT,
    description TEXT,
    purpose TEXT,
    calls_keywords TEXT,
    used_by_tests TEXT,
    complexity TEXT,
    has_error_handling BOOLEAN DEFAULT 0,
    has_logging BOOLEAN DEFAULT 0,
    notes TEXT,
    FOREIGN KEY (resource_id) REFERENCES rf_resources(id)
);

-- -----------------------------------------------------------------------------
-- TABLE 7: rf_libraries
-- Robot Framework libraries used
-- -----------------------------------------------------------------------------
CREATE TABLE rf_libraries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    library_name TEXT NOT NULL UNIQUE,
    library_type TEXT,
    version TEXT,
    purpose TEXT,
    used_by_components TEXT,
    import_count INTEGER,
    key_keywords TEXT,
    installation_command TEXT,
    documentation_url TEXT,
    notes TEXT
);

-- -----------------------------------------------------------------------------
-- TABLE 8: rf_variables_config
-- Global variables and configuration
-- -----------------------------------------------------------------------------
CREATE TABLE rf_variables_config (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    component_id INTEGER NOT NULL,
    variable_name TEXT NOT NULL,
    variable_value TEXT,
    variable_type TEXT,
    scope TEXT,
    file_path TEXT,
    description TEXT,
    is_sensitive BOOLEAN DEFAULT 0,
    notes TEXT,
    FOREIGN KEY (component_id) REFERENCES rf_components(id)
);

-- -----------------------------------------------------------------------------
-- TABLE 9: rf_pom_layers
-- Explanation of 4-layer POM architecture
-- -----------------------------------------------------------------------------
CREATE TABLE rf_pom_layers (
    id INTEGER PRIMARY KEY,
    layer_number INTEGER NOT NULL UNIQUE,
    layer_name TEXT NOT NULL,
    description TEXT,
    responsibilities TEXT,
    should_contain TEXT,
    should_not_contain TEXT,
    example_files TEXT,
    calls_layer TEXT,
    api_equivalent TEXT,
    ui_equivalent TEXT,
    notes TEXT
);

-- -----------------------------------------------------------------------------
-- TABLE 10: rf_best_practices
-- Best practices from README_CLAUDE.md
-- -----------------------------------------------------------------------------
CREATE TABLE rf_best_practices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category TEXT NOT NULL,
    practice_name TEXT NOT NULL,
    description TEXT,
    why_important TEXT,
    correct_example TEXT,
    incorrect_example TEXT,
    applies_to TEXT,
    priority TEXT,
    educational_notes TEXT,
    notes TEXT
);

-- -----------------------------------------------------------------------------
-- TABLE 11: rf_integration_points
-- Integration between components
-- -----------------------------------------------------------------------------
CREATE TABLE rf_integration_points (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    from_component TEXT NOT NULL,
    to_component TEXT NOT NULL,
    integration_type TEXT,
    description TEXT,
    example_usage TEXT,
    keywords_used TEXT,
    notes TEXT
);

-- -----------------------------------------------------------------------------
-- TABLE 12: rf_dependencies
-- Dependencies between components and files
-- -----------------------------------------------------------------------------
CREATE TABLE rf_dependencies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    dependent_file TEXT NOT NULL,
    dependency_file TEXT NOT NULL,
    dependency_type TEXT,
    is_cross_component BOOLEAN DEFAULT 0,
    notes TEXT
);

-- -----------------------------------------------------------------------------
-- TABLE 13: rf_test_data_sources
-- Test data sources
-- -----------------------------------------------------------------------------
CREATE TABLE rf_test_data_sources (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_name TEXT NOT NULL,
    source_type TEXT,
    file_path TEXT,
    used_by_components TEXT,
    data_format TEXT,
    purpose TEXT,
    example_data TEXT,
    notes TEXT
);

-- -----------------------------------------------------------------------------
-- TABLE 14: rf_command_reference
-- Commands for running tests
-- -----------------------------------------------------------------------------
CREATE TABLE rf_command_reference (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    command_name TEXT NOT NULL,
    command TEXT NOT NULL,
    description TEXT,
    use_case TEXT,
    component TEXT,
    tags_used TEXT,
    expected_output TEXT,
    notes TEXT
);

-- ============================================================================
-- INDEXES for better query performance
-- ============================================================================

CREATE INDEX idx_components_name ON rf_components(component_name);
CREATE INDEX idx_suites_component ON rf_test_suites(component_id);
CREATE INDEX idx_tests_suite ON rf_test_cases(suite_id);
CREATE INDEX idx_resources_component ON rf_resources(component_id);
CREATE INDEX idx_keywords_resource ON rf_keywords(resource_id);
CREATE INDEX idx_libraries_name ON rf_libraries(library_name);
CREATE INDEX idx_variables_component ON rf_variables_config(component_id);
CREATE INDEX idx_pom_layers_number ON rf_pom_layers(layer_number);

-- ============================================================================
-- END OF SCHEMA
-- ============================================================================
