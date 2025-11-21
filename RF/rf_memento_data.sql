-- ============================================================================
-- RF PROJECT MEMENTO DATABASE - DATA
-- Date: 2024-11-21
-- Purpose: Data population for RF project knowledge base
-- ============================================================================

-- ============================================================================
-- 1. RF PROJECT METADATA
-- ============================================================================

INSERT INTO rf_project_metadata VALUES (
    1,
    'RF Test Automation Suite',
    'C:\Users\stoka\Documents\moje_app\RF',
    'Comprehensive Robot Framework test suite for form application with API, UI, DB testing and custom image comparison library',
    'Robot Framework 7.2.2',
    'Python 3.10+',
    '2024-11-21T15:00:00Z',
    4,
    8,
    14,
    '4-layer Page Object Model',
    'Form application (React Native frontend + FastAPI backend + PostgreSQL)',
    'Educational project demonstrating best practices in Robot Framework testing'
);

-- ============================================================================
-- 2. RF COMPONENTS
-- ============================================================================

INSERT INTO rf_components VALUES
(1, 'API', 'test_suite', 'API/',
 'API testing component using 4-layer POM pattern',
 '4-layer POM (endpoints → api_actions → workflows → tests)',
 'REST API testing for form CRUD operations and easter egg feature',
 'RequestsLibrary, FakerLibrary, JSONLibrary, Collections',
 'RequestsLibrary (HTTP requests), FakerLibrary (test data)',
 3, 5, 450, 1,
 'Follows 4-layer POM: endpoints/ (Layer 1), api_actions/ (Layer 2), workflows/ (Layer 3), tests/ (Layer 4)'),

(2, 'UI', 'test_suite', 'UI/',
 'UI testing component using 4-layer POM pattern',
 '4-layer POM (locators → pages → workflows → tests)',
 'Web UI testing for form submission and validation',
 'Browser Library (Playwright), FakerLibrary, ImageComparisonLibrary',
 'Browser Library (Playwright-based), FakerLibrary',
 1, 7, 600, 1,
 'Follows 4-layer POM: locators/ (Layer 1), pages/ (Layer 2), workflows/ (missing), tests/ (Layer 4). VIOLATION: workflows/ layer missing - tests call pages directly!'),

(3, 'db', 'test_suite', 'db/',
 'Database verification component',
 'Custom keywords for DB operations',
 'Direct PostgreSQL database verification and validation',
 'DatabaseLibrary, psycopg2',
 'DatabaseLibrary (SQL operations), custom Diagnostika.py library',
 2, 3, 150, 1,
 'Used for integration verification - checks DB state after API/UI operations. SECURITY: Hardcoded password in variables.resource!'),

(4, 'ImageComparisonLibrary', 'library', 'ImageComparisonLibrary/',
 'Custom Robot Framework library for visual regression testing',
 'Custom library (not POM)',
 'Perceptual hashing-based image comparison with visual diff generation',
 'Pillow, imagehash, numpy, opencv-python',
 'PIL (image processing), imagehash (perceptual hashing), cv2 (contour detection)',
 1, 0, 1768, 1,
 'Standalone library with own unit tests. Version 1.5.0. Supports phash/dhash algorithms, contour-based diff visualization, morphological dilation. Has own memento.db in ImageComparisonLibrary/ folder.');

-- ============================================================================
-- 3. RF TEST SUITES
-- ============================================================================

INSERT INTO rf_test_suites VALUES
(1, 1, 'Form CRUD Tests', 'form_crud_tests.robot', 'API/tests/form_crud_tests.robot',
 4, 'api, form, regression', 'api, form', 'regression',
 4, 'Create API Session', 'Delete All Sessions',
 'API test cases using workflows. Tests NEVER call api_actions directly - only workflows!',
 80, 'Comprehensive CRUD testing for form data API',
 'Contains 4 tests: Test Vytvoření Nového Formuláře (smoke), Test Kompletní CRUD Lifecycle (smoke), Test Vytvoření Více Formulářů (batch), Test Validace Duplicitního Emailu (negative)'),

(2, 1, 'Easter Egg Tests', 'easter_egg_tests.robot', 'API/tests/easter_egg_tests.robot',
 4, 'api, game, easter-egg', 'api', 'extended',
 2, NULL, NULL,
 'Tests for easter egg / game logic feature',
 50, 'Testing special name detection and secret message generation',
 'Tests easter egg API endpoint that returns secret messages for specific names'),

(3, 1, 'Create Form', 'create_form.robot', 'API/tests/create_form.robot',
 4, 'api', 'api', NULL,
 1, NULL, NULL,
 'Simple API form creation test',
 30, 'Basic form creation smoke test',
 'Minimal test - likely for quick validation'),

(4, 2, 'New Form', 'new_form.robot', 'UI/tests/new_form.robot',
 4, NULL, NULL, NULL,
 1, 'Provision Device Session', NULL,
 'UI test for form submission with integration to API and DB',
 46, 'End-to-end test: UI form submission → API cleanup → DB verification',
 'VIOLATIONS: No tags, calls page keywords directly (no workflows), uses Log To Console, missing Test Documentation. Uses iPhone 13 device emulation.'),

(5, 3, 'Verify Email', 'verify_email.robot', 'db/tests/verify_email.robot',
 NULL, 'db', NULL, NULL,
 1, NULL, NULL,
 'Database verification test for specific email',
 25, 'Verify that specific email exists in database',
 'Standalone DB check - verifies email in form_data table'),

(6, 3, 'TT', 'tt.robot', 'db/tt.robot',
 NULL, NULL, NULL, NULL,
 NULL, NULL, NULL,
 'Database test',
 15, 'Database test script',
 'Minimal test file in db/ root (not in tests/)'),

(7, 4, 'Example Test Suite', 'example_test_suite.robot', 'ImageComparisonLibrary/example_test_suite.robot',
 NULL, 'image-comparison', NULL, NULL,
 2, NULL, NULL,
 'Usage examples for ImageComparisonLibrary',
 60, 'Demonstrates how to use Compare Layouts And Generate Diff and Check Layouts Are Visually Similar keywords',
 'Educational test suite showing library usage'),

(8, 1, 'TE', 'te.robot', 'RF/te.robot',
 NULL, NULL, NULL, NULL,
 NULL, NULL, NULL,
 'Standalone test in RF root',
 10, 'Test file in root directory',
 'Located directly in RF/ folder (not in component subfolder)');

-- ============================================================================
-- 4. RF TEST CASES (Key test cases only)
-- ============================================================================

INSERT INTO rf_test_cases VALUES
(1, 1, 'Test Vytvoření Nového Formuláře', 'smoke, happy-path, critical', 'happy-path', 'critical',
 'Tests complete form creation workflow using random generated data',
 '1) Create form with random data via workflow, 2) Verify response structure, 3) Verify form_id returned, 4) Log success',
 'Create Form With Random Data',
 'Form created successfully with all fields populated and valid form_id returned',
 NULL, 'Delete Created Form',
 0, NULL,
 'Smoke test - MUST pass. Uses FakerLibrary for data generation.'),

(2, 1, 'Test Kompletní CRUD Lifecycle', 'smoke, critical', 'happy-path', 'critical',
 'Tests complete CRUD cycle: Create → Read → Update → Delete',
 '1) Create form, 2) GET form by ID, 3) Verify data matches, 4) DELETE form, 5) Verify 404 on GET',
 'Complete Form Lifecycle',
 'Form goes through full lifecycle and is properly deleted',
 NULL, NULL,
 0, NULL,
 'Critical integration test - validates entire API CRUD functionality'),

(3, 1, 'Test Vytvoření Více Formulářů', 'batch', 'happy-path', 'medium',
 'Batch creation test - creates multiple forms in sequence',
 '1) Loop 5x: Create form with random data, 2) Collect all form_ids, 3) Verify all created, 4) Cleanup all',
 'Create Form With Random Data (called 5x)',
 '5 forms created successfully with unique data',
 NULL, 'Delete All Created Forms',
 0, NULL,
 'Performance test - validates batch operations and cleanup'),

(4, 1, 'Test Validace Duplicitního Emailu', 'negative, validation', 'negative', 'high',
 'Negative test - attempts to create form with duplicate email',
 '1) Create form with email, 2) Try to create another form with same email, 3) Expect 400 error, 4) Verify error message',
 'Create And Verify Form Data (2x with same email)',
 'Second creation fails with 400 Bad Request and appropriate error message',
 NULL, 'Delete First Form',
 0, NULL,
 'Validates unique email constraint in backend'),

(5, 4, 'Test Vytvoření Nového Formuláře', NULL, 'happy-path', 'critical',
 'End-to-end UI test: Fill form → Submit → Cleanup via API → Verify DB',
 '1) Fill form via UI, 2) Submit form, 3) Extract form_id from success page, 4) DELETE via API, 5) Verify DB row deleted',
 'VIOLATION: Calls page keywords directly (Vyplnit Formulář, Odeslat Formulář) instead of workflows',
 'Form submitted via UI, data saved, cleanup successful, DB verified',
 'Provision Device Session (iPhone 13 emulation)', NULL,
 0, NULL,
 'Integration test combining UI + API + DB. NEEDS REFACTORING: Add workflows/ layer, add tags, use structured logging');

-- ============================================================================
-- 5. RF RESOURCES
-- ============================================================================

INSERT INTO rf_resources VALUES
(1, 1, 'API Common', 'common.resource', 'API/common.resource',
 NULL, 'common', 'keywords',
 'Shared utility keywords for API testing: session management, logging, response verification',
 6, 0, 'RequestsLibrary, Collections, JSONLibrary, String',
 'workflows/form_workflow.resource, api_actions/form_api.resource, endpoints/form_endpoints.resource',
 100,
 'Contains: Create API Session, Log API Request, Log API Response, Log Test Step, Log Test Data, Log Test Result',
 'Essential shared keywords used by all API tests. BEST PRACTICE: Structured logging keywords.'),

(2, 1, 'API Variables', 'variables.resource', 'API/variables.resource',
 NULL, 'config', 'variables',
 'Configuration variables for API testing',
 0, 3, NULL, NULL,
 20,
 'Contains API base URL and other config',
 'Defines ${API_BASE_URL} = http://localhost:8000/api/v1/form'),

(3, 1, 'Form Endpoints', 'form_endpoints.resource', 'API/endpoints/form_endpoints.resource',
 1, 'endpoints', 'variables',
 'LAYER 1: API endpoint URLs - ONLY constants, NO logic!',
 0, 12, NULL, NULL,
 32,
 'Defines all API endpoint URLs as variables: ${FORM_ENDPOINT}, ${FORM_BY_ID_ENDPOINT}, ${DELETE_ENDPOINT}, ${EASTER_EGG_ENDPOINT}',
 'Equivalent to UI locators/ - contains only URLs, no API calls. Follows POM Layer 1 perfectly.'),

(4, 1, 'Form API Actions', 'form_api.resource', 'API/api_actions/form_api.resource',
 2, 'api_actions', 'keywords',
 'LAYER 2: Individual API calls - POST, GET, DELETE operations',
 6, 0, 'RequestsLibrary', '../endpoints/form_endpoints.resource, ../common.resource',
 150,
 'Contains: Create Form Data, Get Form Data By ID, Get All Form Data, Delete Form Data, Evaluate Name For Easter Egg, Update Form Data',
 'Equivalent to UI pages/ - atomic operations, called by workflows. Each keyword does ONE API operation.'),

(5, 1, 'Form Workflow', 'form_workflow.resource', 'API/workflows/form_workflow.resource',
 3, 'workflows', 'keywords',
 'LAYER 3: Complex API scenarios - combines multiple API actions',
 6, 0, 'FakerLibrary', '../common.resource',
 100,
 'Contains: Create And Verify Form Data, Create Form With Random Data, Complete Form Lifecycle, Test Easter Egg For Name, Create Multiple Forms, Delete All Forms',
 'Business logic layer - called by tests. Generates test data using FakerLibrary, combines api_actions into scenarios. BEST PRACTICE: Perfect workflow implementation.'),

(6, 2, 'UI Common', 'common.resource', 'UI/common.resource',
 NULL, 'common', 'keywords',
 'Shared utility keywords for UI testing: browser setup, logging, error handling',
 10, 0, 'Browser, RequestsLibrary, RPA.FTP, FakerLibrary, ImageComparisonLibrary',
 '../libraries/path_utils.py, ../db/common.resource',
 200,
 'Contains: Provision Device Session, Log To Console (VIOLATION: should use structured logging), Nahrát Soubor, Take Screenshot on Error, Connect To Test Database, etc.',
 'Mixed quality: Good error handling (TRY-EXCEPT), but uses Log To Console instead of structured logging. Cross-component imports (db/common.resource) show integration.'),

(7, 2, 'UI Variables', 'variables.resource', 'UI/variables.resource',
 NULL, 'config', 'variables',
 'Configuration variables for UI testing',
 0, 5, NULL, NULL,
 25,
 'Contains: ${URL}, ${BROWSER}, ${HEADLESS}, ${DEVICE}',
 'Defines frontend URL (http://localhost:8081/), browser (chromium), device emulation (iPhone 13)'),

(8, 2, 'Form Page Locators', 'form_page_locators.resource', 'UI/locators/form_page_locators.resource',
 1, 'locators', 'variables',
 'LAYER 1: Form page element selectors - ONLY locators, NO logic!',
 0, 12, NULL, NULL,
 40,
 'Contains locators for form inputs: ${FORM_NAME_INPUT}, ${FORM_SURNAME_INPUT}, ${FORM_PHONE_INPUT}, ${FORM_EMAIL_INPUT}, ${FORM_GENDER_SELECT}, ${FORM_SUBMIT_BUTTON}, ${FORM_FILE_INPUT}',
 'Follows POM Layer 1 perfectly - only variables with selectors.'),

(9, 2, 'Page2 Locators', 'page2_locators.resource', 'UI/locators/page2_locators.resource',
 1, 'locators', 'variables',
 'LAYER 1: Success page (Page2) element selectors',
 0, 8, NULL, NULL,
 30,
 'Contains locators for success page elements after form submission',
 'Layer 1 - only selectors'),

(10, 2, 'Form Page', 'form_page.resource', 'UI/pages/form_page.resource',
 2, 'pages', 'keywords',
 'LAYER 2: Form page actions - fill fields, submit, upload file',
 8, 0, 'Browser', '../locators/form_page_locators.resource, ../common.resource',
 120,
 'Contains: Vyplnit Jméno, Vyplnit Příjmení, Vyplnit Telefon, Vyplnit Email, Vybrat Pohlaví, Nahrát Soubor, Odeslat Formulář, Vyplnit Formulář (combines all fills)',
 'Layer 2 - atomic page actions. Each keyword performs ONE action. GOOD: TRY-EXCEPT error handling with screenshots.'),

(11, 2, 'Page2', 'page2.resource', 'UI/pages/page2.resource',
 2, 'pages', 'keywords',
 'LAYER 2: Success page actions - verify, extract data',
 5, 0, 'Browser', '../locators/page2_locators.resource, ../common.resource',
 80,
 'Contains keywords for interacting with success page after form submission',
 'Layer 2 - page actions for confirmation/success page'),

(12, 3, 'DB Common', 'common.resource', 'db/common.resource',
 NULL, 'common', 'keywords',
 'Database connection and utility keywords',
 4, 0, 'DatabaseLibrary', NULL,
 60,
 'Contains: Connect To Test Database, Disconnect From Test Database, Execute SQL Query, Verify Row Count',
 'Shared DB keywords used by db/ tests and imported by UI/common.resource for integration testing'),

(13, 3, 'DB Variables', 'variables.resource', 'db/variables.resource',
 NULL, 'config', 'variables',
 'Database connection configuration',
 0, 5, NULL, NULL,
 25,
 'Contains DB credentials and connection info',
 'SECURITY WARNING: Hardcoded password ${DB_PASSWORD}=f0rt4n3 should be moved to environment variable!'),

(14, 3, 'DB Keywords', 'db_keywords.resource', 'db/page/db_keywords.resource',
 NULL, 'db_operations', 'keywords',
 'Specific database operation keywords',
 3, 0, 'DatabaseLibrary', '../common.resource',
 50,
 'Contains DB-specific operations beyond basic CRUD',
 'Extended DB functionality for complex queries and validations');

-- ============================================================================
-- 6. RF KEYWORDS (Important keywords only)
-- ============================================================================

INSERT INTO rf_keywords VALUES
(1, 5, 'Create Form With Random Data', 'workflow', 3,
 '[Arguments] ${session} ${gender}=muž',
 'Dictionary with keys: form_id, form_data, response',
 'Workflow: Creates form with random test data using FakerLibrary. Steps: 1) Generate Faker data (first name, last name, email, phone), 2) Call Create And Verify Form Data workflow, 3) Return form_id and data',
 'Complete workflow for creating form with generated test data',
 'Create And Verify Form Data, FakerLibrary keywords (First Name, Last Name, Email, Phone Number), Log Test Step, Log Test Data',
 'Used by: Test Vytvoření Nového Formuláře, Test Kompletní CRUD Lifecycle, Test Vytvoření Více Formulářů',
 'medium', 0, 1,
 'BEST PRACTICE: Perfect Layer 3 workflow. Combines data generation + API actions. Reusable across tests.'),

(2, 5, 'Complete Form Lifecycle', 'workflow', 3,
 '[Arguments] ${session}',
 'NULL',
 'Workflow: Tests full CRUD cycle. Steps: 1) Create form with random data, 2) GET form by ID, 3) Verify data matches, 4) DELETE form, 5) Verify GET returns 404',
 'Complete CRUD lifecycle testing workflow',
 'Create Form With Random Data, Get Form Data By ID, Delete Form Data, Log Test Step',
 'Used by: Test Kompletní CRUD Lifecycle',
 'complex', 0, 1,
 'BEST PRACTICE: Multi-step workflow demonstrating complete business scenario'),

(3, 5, 'Test Easter Egg For Name', 'workflow', 3,
 '[Arguments] ${session} ${first_name} ${last_name}',
 'Boolean (TRUE if easter egg triggered)',
 'Workflow: Tests if name triggers easter egg. Steps: 1) Create form with specific name, 2) Check response for easter_egg flag, 3) Verify secret_message if triggered, 4) Cleanup form',
 'Easter egg detection workflow for game feature',
 'Create And Verify Form Data, Evaluate Name For Easter Egg, Delete Form Data',
 'Used by: Easter egg tests',
 'medium', 0, 1,
 'Tests special game logic feature'),

(4, 4, 'Create Form Data', 'api_action', 2,
 '[Arguments] ${session} ${form_data}',
 'Response object from POST request',
 'Layer 2: Creates form data via POST API. Logs request/response, verifies response structure',
 'Atomic API POST operation for form creation',
 'POST On Session, Log API Request, Log API Response, Should Be Equal As Integers, Dictionary Should Contain Key',
 'Called by: Create And Verify Form Data workflow',
 'simple', 0, 1,
 'BEST PRACTICE: Atomic operation - NEVER called directly from tests, only from workflows. Perfect Layer 2 implementation.'),

(5, 4, 'Get Form Data By ID', 'api_action', 2,
 '[Arguments] ${session} ${form_id}',
 'Response object from GET request',
 'Layer 2: Retrieves form data by ID via GET API',
 'Atomic API GET operation',
 'GET On Session, Log API Request, Log API Response',
 'Called by: Complete Form Lifecycle, verification workflows',
 'simple', 0, 1,
 'Layer 2 - single GET operation'),

(6, 4, 'Delete Form Data', 'api_action', 2,
 '[Arguments] ${session} ${form_id}',
 'Response object from DELETE request',
 'Layer 2: Deletes form data via DELETE API',
 'Atomic API DELETE operation',
 'DELETE On Session, Log API Request, Log API Response',
 'Called by: All cleanup operations, test teardowns, workflows',
 'simple', 0, 1,
 'Critical for test cleanup - ensures test data isolation'),

(7, 10, 'Vyplnit Formulář', 'page_action', 2,
 '[Arguments] ${jméno} ${příjmení} ${telefon} ${email} ${pohlaví}=muž',
 'NULL',
 'Layer 2: Fills entire form by calling individual fill keywords',
 'Composite page action - fills all form fields',
 'Vyplnit Jméno, Vyplnit Příjmení, Vyplnit Telefon, Vyplnit Email, Vybrat Pohlaví',
 'Called by: UI tests (VIOLATION: should be called by workflow, not directly from tests)',
 'medium', 1, 0,
 'Composite action combining multiple fill operations. Has TRY-EXCEPT. NOTE: This is borderline Layer 2/3 - could be moved to workflows/'),

(8, 10, 'Odeslat Formulář', 'page_action', 2,
 NULL,
 'NULL',
 'Layer 2: Clicks submit button and waits for navigation',
 'Submits form',
 'Click ${FORM_SUBMIT_BUTTON}, Wait For Navigation',
 'Called by: UI tests',
 'simple', 1, 0,
 'Simple click action with error handling'),

(9, 1, 'Create API Session', 'utility', NULL,
 '[Arguments] ${base_url}',
 'NULL',
 'Creates RequestsLibrary session for API calls',
 'Session initialization for API testing',
 'Create Session, Log Test Step',
 'Used in: Suite Setup of all API tests',
 'simple', 0, 1,
 'Essential setup keyword - creates HTTP session'),

(10, 1, 'Log Test Step', 'utility', NULL,
 '[Arguments] ${step_description}',
 'NULL',
 'Logs test step in structured format',
 'Structured logging for test steps',
 'Log To Console with formatted output',
 'Used throughout: All API tests and workflows',
 'low', 0, 1,
 'BEST PRACTICE: Structured logging instead of plain Log To Console. Makes test output professional and readable.'),

(11, 6, 'Provision Device Session', 'utility', NULL,
 '[Arguments] ${device_name}=iPhone 13',
 'NULL',
 'Creates browser session with device emulation',
 'Browser setup with mobile device emulation',
 'New Browser, New Page, Set Viewport Size',
 'Used in: Test Setup of UI tests',
 'medium', 1, 0,
 'Enables mobile testing via device emulation. Uses iPhone 13 by default.');

-- ============================================================================
-- 7. RF LIBRARIES
-- ============================================================================

INSERT INTO rf_libraries VALUES
(1, 'Browser', 'external', '19.9.0',
 'Playwright-based library for web UI automation',
 'UI',
 7,
 'New Browser, New Page, Click, Fill Text, Get Text, Wait For Elements State, Take Screenshot, Set Viewport Size',
 'pip install robotframework-browser && rfbrowser init',
 'https://marketsquare.github.io/robotframework-browser/',
 'Requires Playwright browser installation via rfbrowser init. Modern alternative to SeleniumLibrary - faster and more reliable.'),

(2, 'RequestsLibrary', 'external', '0.9.7',
 'HTTP library for REST API testing',
 'API, UI',
 3,
 'Create Session, GET On Session, POST On Session, DELETE On Session, PUT On Session',
 'pip install robotframework-requests',
 'https://marketsquare.github.io/robotframework-requests/',
 'Used for API testing in API/ component and API cleanup in UI/ tests. Essential for RESTful API testing.'),

(3, 'FakerLibrary', 'external', '5.0.0',
 'Generate fake test data (names, emails, phones)',
 'API, UI',
 4,
 'First Name, Last Name, Email, Phone Number, Address, Company',
 'pip install robotframework-faker',
 'https://guykisel.github.io/robotframework-faker/',
 'Essential for data-driven testing with random data. Ensures unique test data on every run. Based on Python Faker library.'),

(4, 'DatabaseLibrary', 'external', 'latest',
 'Database testing and verification library',
 'db, UI',
 2,
 'Connect To Database, Disconnect From Database, Execute Sql String, Check Row Count, Check Query Result, Query',
 'pip install robotframework-databaselibrary && pip install psycopg2',
 'https://github.com/MarketSquare/Robotframework-Database-Library',
 'Used for DB verification after API/UI operations. Requires DB driver (psycopg2 for PostgreSQL). Cross-component integration.'),

(5, 'ImageComparisonLibrary', 'custom', '1.5.0',
 'Custom library for perceptual hash-based image comparison',
 'UI',
 1,
 'Compare Layouts And Generate Diff, Check Layouts Are Visually Similar',
 'pip install -e RF/ImageComparisonLibrary/',
 'See ImageComparisonLibrary/README.md and ImageComparisonLibrary/memento.db',
 'Project-specific library. Supports phash/dhash algorithms, contour visualization, morphological dilation for element detection. Educational example of custom RF library development.');

-- ============================================================================
-- 8. RF VARIABLES CONFIG
-- ============================================================================

INSERT INTO rf_variables_config VALUES
(1, 1, '${API_BASE_URL}', 'http://localhost:8000/api/v1/form', 'url', 'component',
 'API/variables.resource',
 'Base URL for form API endpoints',
 0, 'Changed to different host/port for different environments (dev/staging/prod)'),

(2, 2, '${URL}', 'http://localhost:8081/', 'url', 'component',
 'UI/variables.resource',
 'Frontend URL (Expo web mode)',
 0, 'Default port for Expo web development. Port 8081 is Expo default.'),

(3, 2, '${BROWSER}', 'chromium', 'config', 'component',
 'UI/variables.resource',
 'Browser engine for Playwright',
 0, 'Options: chromium, firefox, webkit. Chromium recommended for best compatibility.'),

(4, 2, '${HEADLESS}', 'False', 'config', 'component',
 'UI/variables.resource',
 'Run browser in headless mode (no GUI)',
 0, 'Set to True for CI/CD, False for local debugging'),

(5, 2, '${DEVICE}', 'iPhone 13', 'config', 'component',
 'UI/variables.resource',
 'Device emulation for mobile testing',
 0, 'Enables mobile viewport and user agent. Can be changed to other devices (iPad, Pixel, etc.)'),

(6, 3, '${DB_HOST}', '10.8.0.1', 'config', 'component',
 'db/variables.resource',
 'PostgreSQL database host IP',
 0, 'Database server address'),

(7, 3, '${DB_PORT}', '5432', 'config', 'component',
 'db/variables.resource',
 'PostgreSQL database port',
 0, 'Default PostgreSQL port'),

(8, 3, '${DB_NAME}', 'czechittas', 'config', 'component',
 'db/variables.resource',
 'PostgreSQL database name',
 0, 'Application database name'),

(9, 3, '${DB_USER}', 'fortanix', 'credential', 'component',
 'db/variables.resource',
 'PostgreSQL database username',
 0, 'DB username for connection'),

(10, 3, '${DB_PASSWORD}', 'f0rt4n3', 'credential', 'component',
 'db/variables.resource',
 'PostgreSQL database password',
 1, 'SECURITY WARNING: Hardcoded password! Should be moved to environment variable or secret manager in production!');

-- ============================================================================
-- 9. RF POM LAYERS
-- ============================================================================

INSERT INTO rf_pom_layers VALUES
(1, 1, 'Locators/Endpoints',
 'Element selectors (UI) or API endpoint URLs (API) - ONLY constants, NO logic',
 'Store all selectors/URLs as variables. No keywords, no logic, no imports of action libraries (Browser/RequestsLibrary)',
 'Variables only: ${FORM_NAME_INPUT}=data-testid=firstNameInput, ${API_BASE_URL}=http://localhost:8000/api/v1/form',
 'Keywords, logic, loops, conditions, API calls, Browser actions, test data',
 'UI: locators/form_page_locators.resource, locators/page2_locators.resource | API: endpoints/form_endpoints.resource',
 'Layer 2 calls Layer 1 (page actions use locators, API actions use endpoints)',
 'endpoints/form_endpoints.resource',
 'locators/form_page_locators.resource',
 'Foundation layer - changes here affect all upper layers. Keep selectors stable. Use data-testid attributes for UI locators.'),

(2, 2, 'Pages/API Actions',
 'Atomic operations - single action per keyword (click, fill, POST, GET). Each keyword does ONE thing.',
 'Implement page-specific actions (UI) or individual API calls (API). Include error handling (TRY-EXCEPT) and logging. Return values if needed.',
 'Simple keywords with arguments: Vyplnit Jméno [Arguments] ${name} | Create Form Data [Arguments] ${session} ${data}',
 'Complex workflows, multiple operations, business logic, test data generation, calling multiple Layer 2 keywords',
 'UI: pages/form_page.resource, pages/page2.resource | API: api_actions/form_api.resource',
 'Layer 3 calls Layer 2 (workflows call page actions/API actions), Layer 2 calls Layer 1 (actions use locators/endpoints)',
 'api_actions/form_api.resource',
 'pages/form_page.resource',
 'Action layer - implements atomic operations. MUST have TRY-EXCEPT for error handling. MUST log operations. Called ONLY by workflows, NEVER directly by tests.'),

(3, 3, 'Workflows',
 'Complex business scenarios - combines multiple Layer 2 actions into meaningful user journeys',
 'Implement complete user flows, generate test data (FakerLibrary), combine actions into scenarios. Reusable across tests.',
 'Multi-step keywords: Vyplnit A Odeslat Formulář [Arguments] ${use_faker}=${True} | Create Form With Random Data [Arguments] ${session} ${gender}=muž',
 'Direct Browser/API library calls, hardcoded locators/URLs, test assertions (Should Be Equal)',
 'UI: workflows/form_submission_workflow.resource (MISSING!) | API: workflows/form_workflow.resource',
 'Layer 4 calls Layer 3 (tests call workflows), Layer 3 calls Layer 2 (workflows call actions)',
 'workflows/form_workflow.resource',
 'workflows/form_submission_workflow.resource (CURRENTLY MISSING IN PROJECT!)',
 'Business logic layer - reusable across tests. Current UI tests VIOLATE this by calling Layer 2 directly! NEEDS REFACTORING: Create UI workflows/ directory and move business logic from tests.'),

(4, 4, 'Tests',
 'High-level test cases - uses ONLY workflows (Layer 3). Readable, maintainable, focused on WHAT to test, not HOW.',
 'Write readable test cases that call workflows. Include tags, documentation, test setup/teardown. No direct page actions or API calls.',
 'Test cases calling workflows: ${result}= Create Form With Random Data ${session} | Vyplnit A Odeslat Formulář use_faker=${True}',
 'Direct calls to Layer 2 (pages/api_actions), hardcoded data in tests, complex logic in tests, missing tags',
 'API: tests/form_crud_tests.robot, tests/easter_egg_tests.robot | UI: tests/new_form.robot',
 'Tests call ONLY Layer 3 (workflows). NEVER call Layer 2 or Layer 1 directly.',
 'tests/form_crud_tests.robot (PERFECT EXAMPLE)',
 'tests/new_form.robot (VIOLATION EXAMPLE - calls Layer 2 directly)',
 'Top layer - test cases should be simple and readable. Current API tests: PERFECT. Current UI tests: VIOLATION - need refactoring to add workflows/ and use them.');

-- ============================================================================
-- 10. RF BEST PRACTICES
-- ============================================================================

INSERT INTO rf_best_practices VALUES
(1, 'POM Architecture', '4-Layer POM Structure',
 'Tests MUST follow 4-layer abstraction: Tests (4) → Workflows (3) → Pages/Actions (2) → Locators/Endpoints (1)',
 'Ensures maintainability, reusability, readability. Changes in UI/API affect only specific layers. Tests remain stable.',
 'Test calls workflow → workflow calls page action → page action uses locator. Example: Test: Create Form With Random Data → Workflow: Create And Verify Form Data → Action: Create Form Data → Endpoint: ${FORM_ENDPOINT}',
 'Test directly calls Click ${FORM_SUBMIT_BUTTON} or POST On Session ${url}. VIOLATION: Bypassing layers.',
 'All tests (API and UI)',
 'must',
 'Students must understand separation of concerns. Each layer has specific responsibility. API tests follow this perfectly. UI tests VIOLATE - educational opportunity to show refactoring!',
 'Current status: API ✅ Perfect, UI ❌ Missing workflows/'),

(2, 'Tagging Strategy', 'Structured Test Tags',
 'EVERY test MUST have tags for selective execution and reporting. Use meaningful, hierarchical tags.',
 'Enables: smoke-only runs (--include smoke), regression suites (--include regression), feature-specific runs (--include api --include form), CI/CD integration',
 '[Tags] smoke happy-path critical | Force Tags api form | Default Tags regression',
 'No tags, or only generic tags like "test" or "temp"',
 'All tests',
 'must',
 'Tags enable smart test execution: robot --include smoke for quick checks (~30s), --include critical before release, --exclude wip for stable runs',
 'Current status: API tests ✅ Perfect tagging, UI tests ❌ No tags!'),

(3, 'Logging', 'Structured Logging Keywords',
 'Use custom logging keywords (Log Test Step, Log API Request, Log Test Data) instead of plain Log To Console',
 'Professional structured output, better debugging, educational value. Makes logs readable and parseable.',
 'Log Test Step "Creating form with random data" | Log Test Data "Form Data" ${data} | Log API Response ${response}',
 'Log To Console ${id} | Log ${data} (unstructured, hard to parse)',
 'All tests and keywords',
 'should',
 'Shows students production-ready logging. Console logs are for debugging, structured logs are for production. Enable JSON logging for CI/CD integration.',
 'Current status: API ✅ Uses structured logging, UI ❌ Uses Log To Console'),

(4, 'Error Handling', 'TRY-EXCEPT with Screenshots',
 'ALL page actions and API calls MUST have TRY-EXCEPT with Take Screenshot (UI) and descriptive error messages',
 'When test fails, screenshot shows WHAT failed. Descriptive message says WHERE and WHY. Critical for debugging flaky tests.',
 'TRY\n    Wait For Elements State ${locator} visible\n    Click ${locator}\nEXCEPT\n    Take Screenshot failure_{keyword}\n    Fail "Click failed on ${locator}: ${ERROR}"',
 'Just: Click ${locator} (no error handling, no screenshot, hard to debug)',
 'All page actions (Layer 2) and workflows (Layer 3)',
 'must',
 'Students learn defensive programming. Screenshot is invaluable for debugging. Error message should include: what action, what element, what expected.',
 'Current status: Both UI and API implement this well in common.resource'),

(5, 'Test Data Management', 'Use FakerLibrary for Random Data',
 'Generate unique random test data on every run using FakerLibrary. NEVER hardcode test data in tests.',
 'Ensures test data uniqueness, prevents conflicts, enables parallel execution, validates dynamic data handling',
 '${first_name}= First Name | ${email}= Email | Use these in workflows/tests',
 'Hardcoded data: ${first_name}= John | ${email}= john@test.com (causes conflicts, not reusable)',
 'All tests requiring form data',
 'should',
 'Educational: Shows modern testing practices. Faker generates realistic data. Alternative: CSV files for specific test cases.',
 'Current status: API ✅ Perfect Faker usage, UI ✅ Also uses Faker'),

(6, 'Test Isolation', 'Cleanup in Test Teardown',
 'EVERY test that creates data MUST clean up in [Teardown]. Use Test Teardown or Suite Teardown.',
 'Ensures test independence. Tests can run in any order. Prevents data pollution. Critical for CI/CD.',
 '[Teardown] Delete Created Form ${form_id} | Suite Teardown: Delete All Sessions',
 'No teardown, or manual cleanup (unreliable if test fails before cleanup)',
 'All tests',
 'must',
 'Students learn proper test lifecycle. Teardown runs EVEN IF test fails. Use Run Keyword And Ignore Error for optional cleanup.',
 'Current status: API ✅ Perfect teardown usage, UI ✅ Uses API cleanup'),

(7, 'Documentation', 'Test Documentation and Comments',
 'EVERY test MUST have [Documentation] explaining WHAT it tests and WHY',
 'Enables test suite as living documentation. New team members understand test purpose. Test reports are readable.',
 '[Documentation] Tests complete CRUD lifecycle: Create form → GET → Verify → DELETE → Verify 404',
 'No documentation, or just test name',
 'All tests',
 'should',
 'Documentation appears in reports. Should explain: test purpose, expected outcome, special setup/conditions.',
 'Current status: API ✅ Some tests have docs, UI ❌ Missing documentation'),

(8, 'Cross-Component Integration', 'Use API for Cleanup in UI Tests',
 'UI tests should create data via UI (user flow), but clean up via API (faster, more reliable)',
 'Separates concerns: UI for creation (validates user experience), API for cleanup (speed). Prevents cascade failures.',
 'UI: Submit form → Get form_id from success page → API: DELETE /form/${form_id} → Verify UI updated',
 'UI: Submit form → Navigate back → Click delete button → Confirm (slow, flaky, tests too much)',
 'UI tests',
 'should',
 'Best practice in modern testing. API cleanup is: faster (~100ms vs ~2s), more reliable (no UI wait issues), focused (UI tests focus on creation).',
 'Current status: UI tests ✅ Already implement this pattern'),

(9, 'Security', 'Never Hardcode Credentials',
 'NEVER hardcode passwords, API keys, tokens in code. Use environment variables or secret managers.',
 'Security risk. Credentials in git history. Impossible to rotate secrets. Fails compliance audits.',
 'Use: ${DB_PASSWORD}= Get Environment Variable DB_PASSWORD | Or: BuiltIn.Set Global Variable from .env file',
 'Hardcoded: ${DB_PASSWORD}= f0rt4n3 (CURRENT VIOLATION!)',
 'All tests and resources',
 'must',
 'Educational: Students learn security basics. Show .env files, environment variables, secret management. CRITICAL FIX needed in db/variables.resource!',
 'Current status: ❌ VIOLATION in db/variables.resource - password hardcoded!'),

(10, 'Mobile Testing', 'Use Device Emulation for Responsive Testing',
 'Test mobile views using device emulation (viewport + user agent), not just desktop',
 'Validates responsive design. Catches mobile-specific bugs. Cheaper than real device testing for initial validation.',
 'Set Viewport Size width=390 height=844 | Or use Browser presets: New Page emulate_device=iPhone 13',
 'Only testing desktop view (misses mobile bugs)',
 'UI tests for responsive applications',
 'recommended',
 'Educational: Modern apps must work on mobile. Device emulation is fast and cheap. Real device testing comes later (Appium/BrowserStack).',
 'Current status: UI tests ✅ Use iPhone 13 emulation');

-- ============================================================================
-- 11. RF INTEGRATION POINTS
-- ============================================================================

INSERT INTO rf_integration_points VALUES
(1, 'UI', 'API', 'cleanup',
 'UI test creates form via browser, then uses API DELETE to clean up test data. Faster and more reliable than UI cleanup.',
 'Example: UI submits form → Get form_id from success page → Call RequestsLibrary DELETE On Session → Refresh UI → Verify form deleted',
 'DELETE On Session (RequestsLibrary), Aktualizovat Stránku (Browser), Ověřit Že Formulář Byl Smazán',
 'Separates concerns: UI for creation (user flow validation), API for cleanup (speed and reliability). Best practice in modern test automation.'),

(2, 'UI', 'db', 'verification',
 'UI test submits form via browser, then connects to database to verify record was created correctly',
 'Example: UI submits form with email test@example.com → Connect to PostgreSQL → Query SELECT * FROM form_data WHERE email=... → Verify row count = 1 → Verify first_name, last_name match',
 'Connect To Test Database, Query, Check Row Count, Disconnect From Test Database',
 'Ensures end-to-end data flow: UI → Backend API → Database persistence. Validates integration between all layers.'),

(3, 'API', 'db', 'verification',
 'API test creates form via POST request, then queries database to verify DB state matches API response',
 'Example: API POST /form → Get form_id from response → Query DB: SELECT * FROM form_data WHERE id=${form_id} → Compare DB row with API response → Verify all fields match',
 'Same DB keywords as UI-db integration: Connect, Query, Check Row Count, Disconnect',
 'Integration testing: Validates API layer correctness + DB persistence correctness. Catches bugs in API-DB integration.'),

(4, 'UI', 'ImageComparisonLibrary', 'visual_regression',
 'UI test captures screenshot, then compares it with baseline using ImageComparisonLibrary to detect visual regressions',
 'Example: Take Screenshot current.png → Compare Layouts And Generate Diff baseline.png current.png diff/ → If fails: Visual changes detected, see diff image',
 'Compare Layouts And Generate Diff, Check Layouts Are Visually Similar, Take Screenshot',
 'Visual regression testing. Catches CSS changes, layout shifts, rendering bugs that functional tests miss.');

-- ============================================================================
-- 12. RF DEPENDENCIES (Key examples)
-- ============================================================================

INSERT INTO rf_dependencies VALUES
(1, 'API/tests/form_crud_tests.robot', 'API/workflows/form_workflow.resource', 'resource', 0,
 'Tests import workflows - correct Layer 4 → Layer 3 dependency'),
(2, 'API/workflows/form_workflow.resource', 'API/api_actions/form_api.resource', 'resource', 0,
 'Workflows import api_actions - correct Layer 3 → Layer 2 dependency'),
(3, 'API/api_actions/form_api.resource', 'API/endpoints/form_endpoints.resource', 'resource', 0,
 'API actions import endpoints - correct Layer 2 → Layer 1 dependency'),
(4, 'API/common.resource', 'RequestsLibrary', 'library', 0,
 'Common resource imports RequestsLibrary for HTTP operations'),
(5, 'UI/common.resource', 'Browser', 'library', 0,
 'Common resource imports Browser library for Playwright automation'),
(6, 'UI/common.resource', 'db/common.resource', 'resource', 1,
 'Cross-component dependency: UI imports DB keywords for integration testing'),
(7, 'UI/tests/new_form.robot', 'UI/pages/form_page.resource', 'resource', 0,
 'VIOLATION: Test imports pages directly (Layer 4 → Layer 2), should import workflows (Layer 4 → Layer 3)'),
(8, 'UI/common.resource', 'ImageComparisonLibrary', 'library', 0,
 'UI imports custom ImageComparisonLibrary for visual regression testing'),
(9, 'db/common.resource', 'DatabaseLibrary', 'library', 0,
 'DB common imports DatabaseLibrary for SQL operations'),
(10, 'API/workflows/form_workflow.resource', 'FakerLibrary', 'library', 0,
 'Workflows import FakerLibrary for test data generation');

-- ============================================================================
-- 13. RF TEST DATA SOURCES
-- ============================================================================

INSERT INTO rf_test_data_sources VALUES
(1, 'FakerLibrary', 'library', NULL, 'API, UI',
 'random', 'Generate realistic random test data (names, emails, phones) for each test run. Ensures unique data and prevents conflicts.',
 'First Name → "John", Last Name → "Doe", Email → "john.doe.1234@example.com", Phone Number → "+420 123 456 789"',
 'Primary data source for data-driven testing. Based on Python Faker library with localization support.'),

(2, 'dokument.txt', 'file', 'UI/dokument.txt', 'UI',
 'txt', 'Test file upload functionality in form. Plain text file used to validate file attachment feature.',
 '[Plain text file content for testing upload]',
 'Used for testing file attachment feature in form. Tests multipart/form-data upload.'),

(3, 'Hardcoded Easter Egg Names', 'hardcoded', NULL, 'API',
 'hardcoded', 'Special names that trigger easter eggs in backend (e.g., "neo", "trinity", "morpheus" from Matrix)',
 'First name="neo", Last name="anderson" → triggers secret message: "Welcome to the Matrix"',
 'Backend contains hardcoded list of special names for game feature. Tests validate easter egg detection logic.'),

(4, 'instructions.json', 'file', NULL, 'API',
 'json', 'JSON test data for form instructions (metadata)',
 '{"description": "Test instruction", "priority": "high"}',
 'Used in API tests for instructions endpoint (1:1 relationship with FormData)'),

(5, 'Test Data in Variables', 'hardcoded', 'API/variables.resource, UI/variables.resource', 'API, UI',
 'hardcoded', 'Configuration values, URLs, timeouts stored as RF variables',
 '${API_BASE_URL}, ${BROWSER}, ${HEADLESS}, ${TIMEOUT}',
 'Environment-specific configuration. Should be parameterized for different environments (dev/staging/prod).');

-- ============================================================================
-- 14. RF COMMAND REFERENCE
-- ============================================================================

INSERT INTO rf_command_reference VALUES
(1, 'Run API Smoke Tests', 'robot --include smoke RF/API/tests/',
 'Runs only critical API smoke tests (tagged with "smoke")',
 'Before every commit, in CI/CD pipeline for fast feedback (~30 seconds)',
 'API', 'smoke',
 'Fast execution. Tests critical paths: form creation, CRUD lifecycle. Exit code 0 = all passed.',
 'Best for quick validation. Recommended before git push.'),

(2, 'Run All API Tests', 'robot RF/API/tests/',
 'Runs complete API test suite (smoke + regression + extended)',
 'Nightly regression run, before release, after major API changes',
 'API', 'all',
 'Complete API coverage: CRUD, validation, batch operations, easter eggs, edge cases. ~2-3 minutes.',
 'Full regression suite. Use --outputdir results/ to save reports.'),

(3, 'Run UI Tests', 'robot RF/UI/tests/new_form.robot',
 'Runs UI test for form submission (currently only 1 test)',
 'After UI changes, before release, as part of full regression',
 'UI', 'ui',
 'Slower execution (~2-3 min with browser). Includes: UI interaction + API cleanup + DB verification.',
 'End-to-end test. Use --variable HEADLESS:True for CI/CD.'),

(4, 'Run UI Tests Headless', 'robot --variable HEADLESS:True RF/UI/tests/',
 'Runs UI tests in headless mode (no browser GUI)',
 'In CI/CD pipelines where GUI is not available',
 'UI', 'ui',
 'Faster than headed mode. Suitable for Docker containers and CI servers.',
 'Set HEADLESS variable to True. Required for Jenkins/GitLab CI.'),

(5, 'Run DB Verification', 'robot RF/db/tests/verify_email.robot',
 'Verifies specific email exists in database',
 'Standalone DB validation, debugging, data verification',
 'db', 'db',
 'Quick DB check without UI/API overhead. Requires DB connection to 10.8.0.1:5432.',
 'Standalone test. Useful for verifying DB state after manual operations.'),

(6, 'Run Tests by Tag', 'robot --include critical --exclude wip RF/',
 'Runs all tests tagged "critical", excludes "wip" (work-in-progress)',
 'Pre-release validation, critical path testing',
 'All', 'critical, -wip',
 'Selective execution. Only critical tests run, WIP tests skipped.',
 'Combine tags: --include "smoke AND api" for specific subset.'),

(7, 'Generate Test Report', 'robot --outputdir results/ --name "Regression Suite" RF/',
 'Runs all tests and generates reports in results/ directory',
 'Full regression run with organized output',
 'All', 'all',
 'Creates: output.xml, log.html, report.html in results/ directory. Timestamped filenames.',
 'Use --timestampoutputs for unique filenames. Good for archiving results.'),

(8, 'Run Specific Test', 'robot --test "Test Vytvoření Nového Formuláře" RF/API/tests/form_crud_tests.robot',
 'Runs single specific test by name',
 'Debugging, focused testing after bug fix',
 'API', 'specific',
 'Only one test executes. Useful for rapid iteration during development.',
 'Test name must match exactly (case-sensitive). Use --test for precise selection.'),

(9, 'Run with Variable Override', 'robot --variable API_BASE_URL:http://staging.example.com/api/v1/form RF/API/tests/',
 'Runs API tests against staging environment instead of localhost',
 'Testing against different environments (dev/staging/prod)',
 'API', 'all',
 'Overrides ${API_BASE_URL} variable. Enables environment-agnostic tests.',
 'Use --variablefile for multiple variables. Example: --variablefile staging.yaml'),

(10, 'Run with Parallel Execution', 'pabot --processes 4 RF/API/tests/',
 'Runs API tests in parallel using 4 processes (requires pabot)',
 'Faster test execution, especially for large suites',
 'API', 'all',
 'Requires: pip install robotframework-pabot. 4x faster with 4 processes (depends on test independence).',
 'Only works if tests are independent! Not suitable if tests share data.');

-- ============================================================================
-- END OF DATA
-- ============================================================================
