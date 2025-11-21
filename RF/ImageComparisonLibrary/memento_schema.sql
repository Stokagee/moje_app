-- MEMENTO.DB SCHEMA - ImageComparisonLibrary Knowledge Database
-- Created: 2024-11-21
-- Purpose: Structured knowledge base capturing all important information about ImageComparisonLibrary

-- ============================================================================
-- CORE TABLES - Basic metadata and architecture
-- ============================================================================

-- 1. PROJECT_INFO - Basic project metadata (single row)
CREATE TABLE project_info (
    id INTEGER PRIMARY KEY,
    project_name TEXT NOT NULL,
    current_version TEXT NOT NULL,
    author TEXT,
    author_email TEXT,
    license TEXT,
    python_min_version TEXT,
    description TEXT,
    repository_url TEXT,
    pypi_package_name TEXT,
    robot_library_scope TEXT,
    last_updated DATE
);

-- 2. FILES - Project files catalog
CREATE TABLE files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_path TEXT NOT NULL UNIQUE,
    file_name TEXT NOT NULL,
    line_count INTEGER,
    responsibility TEXT,
    description TEXT
);

-- 3. VERSIONS - Version history
CREATE TABLE versions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    version_number TEXT NOT NULL UNIQUE,
    release_date DATE,
    is_current BOOLEAN DEFAULT 0,
    backward_compatible BOOLEAN DEFAULT 1,
    summary TEXT
);

-- 4. VERSION_CHANGES - Detailed changes per version
CREATE TABLE version_changes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    version_id INTEGER NOT NULL,
    change_type TEXT CHECK(change_type IN ('added', 'changed', 'fixed', 'removed')),
    category TEXT,
    title TEXT NOT NULL,
    description TEXT,
    related_method TEXT,
    related_parameter TEXT,
    impact TEXT,
    FOREIGN KEY (version_id) REFERENCES versions(id)
);

-- 5. METHODS - All methods in the library
CREATE TABLE methods (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    method_name TEXT NOT NULL,
    method_type TEXT CHECK(method_type IN ('public', 'private')),
    file_name TEXT DEFAULT 'core.py',
    start_line INTEGER,
    end_line INTEGER,
    purpose_en TEXT,
    purpose_cz TEXT,
    signature TEXT,
    returns TEXT,
    complexity TEXT CHECK(complexity IN ('low', 'medium', 'high'))
);

-- 6. PARAMETERS - Method parameters
CREATE TABLE parameters (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    method_id INTEGER,
    param_name TEXT NOT NULL,
    param_type TEXT,
    default_value TEXT,
    description_en TEXT,
    description_cz TEXT,
    min_value TEXT,
    max_value TEXT,
    example_values TEXT,
    added_in_version TEXT,
    FOREIGN KEY (method_id) REFERENCES methods(id)
);

-- 7. DEPENDENCIES - Runtime and dev dependencies
CREATE TABLE dependencies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    package_name TEXT NOT NULL,
    version_constraint TEXT,
    dependency_type TEXT CHECK(dependency_type IN ('runtime', 'dev')),
    purpose TEXT
);

-- ============================================================================
-- KNOWLEDGE TABLES - Domain knowledge database
-- ============================================================================

-- 8. KEYWORDS - Robot Framework keywords
CREATE TABLE keywords (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    keyword_name TEXT NOT NULL,
    method_id INTEGER,
    strictness_level TEXT CHECK(strictness_level IN ('strict', 'relaxed')),
    default_algorithm TEXT,
    default_tolerance INTEGER,
    default_pixel_tolerance INTEGER,
    typical_use_case TEXT,
    rf_example TEXT,
    FOREIGN KEY (method_id) REFERENCES methods(id)
);

-- 9. ALGORITHMS - Hashing algorithms
CREATE TABLE algorithms (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    algorithm_name TEXT NOT NULL UNIQUE,
    algorithm_type TEXT,
    speed_rating TEXT CHECK(speed_rating IN ('fast', 'medium', 'slow')),
    typical_time_ms TEXT,
    accuracy_rating TEXT,
    use_case TEXT,
    description_en TEXT,
    description_cz TEXT,
    recommended_for TEXT
);

-- 10. USE_CASES - Typical usage scenarios
CREATE TABLE use_cases (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    use_case_name TEXT NOT NULL,
    scenario TEXT,
    recommended_settings TEXT,
    example_code TEXT,
    notes TEXT
);

-- 11. TROUBLESHOOTING - Common issues and solutions
CREATE TABLE troubleshooting (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    issue_title TEXT NOT NULL,
    symptoms TEXT,
    cause TEXT,
    solution TEXT,
    related_parameter TEXT
);

-- 12. PERFORMANCE_METRICS - Performance characteristics
CREATE TABLE performance_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    operation TEXT NOT NULL,
    algorithm TEXT,
    image_resolution TEXT,
    typical_time_ms TEXT,
    memory_usage TEXT,
    notes TEXT
);

-- ============================================================================
-- REFERENCE TABLES - Reference information
-- ============================================================================

-- 13. DIFF_MODES - Diff visualization modes
CREATE TABLE diff_modes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    mode_name TEXT NOT NULL UNIQUE,
    description TEXT,
    visual_style TEXT,
    when_to_use TEXT,
    implementation_method TEXT,
    added_in_version TEXT
);

-- 14. BEST_PRACTICES - Recommendations and best practices
CREATE TABLE best_practices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category TEXT,
    practice_title TEXT NOT NULL,
    description TEXT,
    example_code TEXT,
    do_this TEXT,
    dont_do_this TEXT
);

-- ============================================================================
-- INDEXES for better query performance
-- ============================================================================

CREATE INDEX idx_version_changes_version_id ON version_changes(version_id);
CREATE INDEX idx_parameters_method_id ON parameters(method_id);
CREATE INDEX idx_keywords_method_id ON keywords(method_id);
CREATE INDEX idx_methods_type ON methods(method_type);
CREATE INDEX idx_versions_current ON versions(is_current);
