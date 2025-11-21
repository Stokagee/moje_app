-- MEMENTO.DB DATA - ImageComparisonLibrary Knowledge Database
-- Created: 2024-11-21
-- Purpose: Data population for memento.db

-- ============================================================================
-- 1. PROJECT_INFO - Basic project metadata
-- ============================================================================

INSERT INTO project_info VALUES (
    1,
    'ImageComparisonLibrary',
    '1.5.0',
    'Dušan Čižmarik',
    'your.email@example.com',
    'Apache License 2.0',
    '3.10',
    'Robot Framework library for image comparison and visual regression testing using perceptual hashing',
    'https://github.com/yourusername/ImageComparisonLibrary',
    'robotframework-imagecomparisonlibrary',
    'GLOBAL',
    '2024-11-21'
);

-- ============================================================================
-- 2. FILES - Project files catalog
-- ============================================================================

INSERT INTO files (file_path, file_name, line_count, responsibility, description) VALUES
('ImageComparisonLibrary/__init__.py', '__init__.py', 7, 'Public API Export', 'Exports ImageComparisonLibrary class and DiffStatistics, defines __all__ for module imports'),
('ImageComparisonLibrary/core.py', 'core.py', 1768, 'Main Implementation', 'Contains all library logic: keywords, private methods, DiffStatistics dataclass'),
('ImageComparisonLibrary/version.py', 'version.py', 4, 'Version Management', 'Stores current version number (__version__ = "1.5.0")'),
('tests/test_core.py', 'test_core.py', NULL, 'Unit Tests', '12 unit tests covering all major functionality'),
('setup.py', 'setup.py', 52, 'Installation Config', 'pip installation configuration with metadata and dependencies'),
('requirements.txt', 'requirements.txt', 6, 'Dependencies', 'Runtime dependencies for the library'),
('README.md', 'README.md', 336, 'User Documentation', 'Main documentation in Czech for end users'),
('CLAUDE.md', 'CLAUDE.md', NULL, 'Developer Guide', 'Guidance for Claude Code when working with the library'),
('IMPORTANT_PLACES.md', 'IMPORTANT_PLACES.md', 607, 'Code Overview', 'Detailed overview of key code locations and responsibilities'),
('CONTRIBUTING.md', 'CONTRIBUTING.md', 474, 'Contributor Guide', 'Guidelines for contributors including coding standards');

-- ============================================================================
-- 3. VERSIONS - Version history
-- ============================================================================

INSERT INTO versions (version_number, release_date, is_current, backward_compatible, summary) VALUES
('1.0.0', '2024-11-01', 0, 1, 'Initial release with two keywords, phash/dhash support, visual diff generation'),
('1.2.0', '2024-11-18', 0, 1, 'Added contours mode, HTML embedding, timestamps, professional diff visualization'),
('1.3.0', '2024-11-19', 0, 1, 'Changed timestamp styling (red, larger, top-right) and HTML layout (3 images)'),
('1.4.0', '2024-11-21', 0, 1, 'Added directional diff detection with diff_base_image and highlight_mode parameters'),
('1.5.0', '2024-11-21', 1, 1, 'Added morphological dilation for element detection (element_fill_expansion parameter), fixed hardcoded color bug in filled mode');

-- ============================================================================
-- 4. VERSION_CHANGES - Detailed changes per version
-- ============================================================================

-- Version 1.5.0 changes
INSERT INTO version_changes (version_id, change_type, category, title, description, related_parameter, impact) VALUES
(5, 'added', 'parameter', 'element_fill_expansion', 'Morphological dilation kernel size for expanding detected edges to fill entire UI elements. Uses cv2.dilate() with elliptical kernel. Default: 15, set to 0 to disable.', 'element_fill_expansion', 'Solves white-on-white element detection - expands contour area by ~238% (165px → 558px in Email input test)'),
(5, 'changed', 'method', '_create_diff_mask() updated', 'Now implements morphological dilation logic with constraining to prevent over-expansion', '_create_diff_mask', 'Better detection of UI elements like input fields and buttons'),
(5, 'fixed', 'bug', 'Hardcoded color in filled mode', 'Line 1574 in core.py now uses severe_color parameter instead of hardcoded (255,0,0)', 'severe_color', 'API consistency - respects user-provided color parameter');

-- Version 1.4.0 changes
INSERT INTO version_changes (version_id, change_type, category, title, description, related_parameter, impact) VALUES
(4, 'added', 'parameter', 'diff_base_image', 'Choose visual base for diff: "baseline" (show where elements WERE) or "current" (where elements ARE)', 'diff_base_image', 'Solves confusion when element moves - can show only new position'),
(4, 'added', 'parameter', 'highlight_mode', 'Which pixels to highlight: "all" (default), "added" (new in current), or "removed" (old from baseline)', 'highlight_mode', 'Directional diff detection - show only added or removed elements'),
(4, 'changed', 'method', '_create_diff_mask() returns 6 values', 'Now returns (binary_mask, added_mask, removed_mask, color_diff, baseline_array, current_array) for directional detection', '_create_diff_mask', 'Enables directional diff visualization');

-- Version 1.3.0 changes
INSERT INTO version_changes (version_id, change_type, category, title, description, related_method, impact) VALUES
(3, 'changed', 'styling', 'Timestamp color changed to red', 'Timestamp on diff images changed from white (255,255,255) to red (255,0,0) for better visibility', '_add_timestamp_to_image', 'Improved visibility against various backgrounds'),
(3, 'changed', 'styling', 'Timestamp font size increased', 'Font size increased from 14 to 16 for better readability', '_add_timestamp_to_image', 'Better readability'),
(3, 'changed', 'styling', 'Timestamp moved to top-right', 'Position changed from bottom-right to top-right corner to avoid blocking important content', '_add_timestamp_to_image', 'Better UX - doesn''t block bottom content'),
(3, 'changed', 'layout', 'HTML embedding now shows 3 images', 'HTML log now displays baseline + diff in top row, current screenshot in bottom row (was 2 images side-by-side)', '_log_images_to_html', 'Complete visual context - users see all 3 images');

-- Version 1.2.0 changes
INSERT INTO version_changes (version_id, change_type, category, title, description, related_parameter, impact) VALUES
(2, 'added', 'feature', 'Contours mode', 'Professional diff visualization with semi-transparent fill and thick outlines', 'diff_mode', 'Much clearer visual representation of changes'),
(2, 'added', 'parameter', 'embed_images_to_log', 'Embed images into Robot Framework log.html as base64 data URIs', 'embed_images_to_log', 'Self-contained reports - no external image files needed'),
(2, 'added', 'parameter', 'add_timestamp', 'Add timestamp overlay to diff images', 'add_timestamp', 'Easy identification when diff was generated'),
(2, 'added', 'parameter', 'min_contour_area', 'Filter contours by minimum area to reduce noise', 'min_contour_area', 'Focus on significant changes, ignore pixel noise');

-- Version 1.0.0 changes
INSERT INTO version_changes (version_id, change_type, category, title, description, impact) VALUES
(1, 'added', 'feature', 'Initial release', 'Two keywords: Compare Layouts And Generate Diff, Check Layouts Are Visually Similar', 'Core functionality established'),
(1, 'added', 'algorithm', 'phash and dhash support', 'Perceptual hashing algorithms for image comparison', 'Flexible comparison strategies'),
(1, 'added', 'feature', 'Visual diff generation', 'Generate red-highlighted diff images on comparison failure', 'Visual debugging aid'),
(1, 'added', 'documentation', 'Dual-language docstrings', 'English and Czech documentation in all public methods', 'Accessible to wider audience');

-- ============================================================================
-- 5. METHODS - All methods in the library
-- ============================================================================

INSERT INTO methods (method_name, method_type, file_name, start_line, end_line, purpose_en, purpose_cz, returns, complexity) VALUES
('compare_layouts_and_generate_diff', 'public', 'core.py', 25, 113, 'Main, strictest keyword for regression testing. Compares images using perceptual hashing and generates visual diff on failure.', 'Hlavní, nejpřísnější keyword pro regresní testování. Porovnává obrázky pomocí perceptual hashingu a generuje vizuální diff při selhání.', 'int (Hamming distance)', 'high'),
('check_layouts_are_visually_similar', 'public', 'core.py', 115, 158, 'Less strict keyword for coarser comparison. Uses higher tolerance by default.', 'Méně přísné keyword pro hrubší porovnání. Používá vyšší toleranci jako výchozí.', 'int (Hamming distance)', 'medium'),
('_load_image', 'private', 'core.py', 878, 917, 'Loads images from str path, pathlib.Path, or PIL.Image.Image. Validates file existence.', 'Načítá obrázky z cesty (str), pathlib.Path nebo PIL.Image.Image. Validuje existenci souboru.', 'PIL.Image.Image', 'low'),
('_calculate_hash', 'private', 'core.py', 919, 965, 'Calculates perceptual hash using imagehash library. Supports phash and dhash algorithms.', 'Vypočítá perceptual hash pomocí knihovny imagehash. Podporuje phash a dhash algoritmy.', 'imagehash.ImageHash', 'low'),
('_generate_visual_diff', 'private', 'core.py', 967, 1103, 'Generates visual diff image with highlighted differences. Supports contours and filled modes.', 'Generuje vizuální diff obrázek se zvýrazněnými rozdíly. Podporuje režimy kontury a vyplnění.', 'Path', 'high'),
('_create_diff_mask', 'private', 'core.py', 327, 379, 'Creates binary mask of differences between images using pixel-by-pixel Manhattan distance comparison. Implements morphological dilation for element fill expansion.', 'Vytváří binární masku rozdílů mezi obrázky pomocí pixel-by-pixel Manhattan distance. Implementuje morfologickou dilataci pro expanzi elementů.', 'tuple (6 values)', 'high'),
('_find_contours', 'private', 'core.py', 465, 514, 'Detects contours in binary mask with minimal preprocessing. Filters by min_contour_area to capture only large changes.', 'Detekuje kontury v binární masce s minimálním preprocessingem. Filtruje podle min_contour_area pro zachycení velkých změn.', 'list of contours', 'medium'),
('_draw_contours_on_diff', 'private', 'core.py', 556, 689, 'Draws contours with semi-transparent fill (30% opacity) and thick outlines (3px). Two-pass rendering.', 'Vykresluje kontury s poloprůhlednou výplní (30% opacity) a silnými obrysy (3px). Dvouprůchodové vykreslování.', 'numpy.ndarray', 'high'),
('_classify_contour_severity', 'private', 'core.py', 423, 459, 'Classifies change severity: minor (≤1.5x tolerance), moderate (≤3.0x tolerance), severe (>3.0x).', 'Klasifikuje závažnost změny: minor (≤1.5x tolerance), moderate (≤3.0x tolerance), severe (>3.0x).', 'str (severity level)', 'low'),
('_add_timestamp_to_image', 'private', 'core.py', 1384, 1454, 'Adds red timestamp overlay to diff image in top-right corner with black shadow for readability.', 'Přidává červený timestamp na diff obrázek v pravém horním rohu s černým stínem pro čitelnost.', 'PIL.Image.Image', 'low'),
('_log_images_to_html', 'private', 'core.py', 1334, 1396, 'Logs 3 images to Robot Framework HTML log: baseline + diff in top row, current in bottom row. Uses base64 data URIs.', 'Loguje 3 obrázky do Robot Framework HTML logu: baseline + diff v horním řádku, current v dolním. Používá base64 data URI.', 'None', 'medium'),
('_encode_image_to_base64', 'private', 'core.py', 1302, 1332, 'Encodes PIL Image or Path to base64 data URI for HTML embedding.', 'Enkóduje PIL Image nebo Path do base64 data URI pro embedování do HTML.', 'str (data URI)', 'low');

-- ============================================================================
-- 6. PARAMETERS - Method parameters
-- ============================================================================

-- Parameters for compare_layouts_and_generate_diff (method_id=1)
INSERT INTO parameters (method_id, param_name, param_type, default_value, description_en, description_cz, min_value, max_value, example_values, added_in_version) VALUES
(1, 'baseline_image', 'Union[str, Path, Image.Image]', NULL, 'Reference/golden standard image', 'Referenční/zlatý standard obrázek', NULL, NULL, 'baseline.png, Path("baseline.png")', '1.0.0'),
(1, 'current_image', 'Union[str, Path, Image.Image]', NULL, 'Current screenshot to verify', 'Aktuální screenshot k ověření', NULL, NULL, 'current.png', '1.0.0'),
(1, 'diff_directory', 'Union[str, Path]', NULL, 'Directory to save diff image on failure', 'Adresář pro uložení diff obrázku při selhání', NULL, NULL, './diffs/', '1.0.0'),
(1, 'algorithm', 'str', 'phash', 'Hashing algorithm: "phash" or "dhash"', 'Hashovací algoritmus: "phash" nebo "dhash"', NULL, NULL, 'phash, dhash', '1.0.0'),
(1, 'tolerance', 'int', '5', 'Maximum allowed Hamming distance', 'Maximální povolená Hammingova vzdálenost', '0', NULL, '5, 10, 15', '1.0.0'),
(1, 'pixel_tolerance', 'int', '60', 'Color difference tolerance (0-255) for diff generation. Higher values ignore semi-transparent overlays.', 'Tolerance barevného rozdílu (0-255) pro generování diffu. Vyšší hodnoty ignorují semi-transparent overlay.', '0', '255', '15, 45, 60', '1.0.0'),
(1, 'hash_size', 'int', '8', 'Hash grid size (affects sensitivity)', 'Velikost hashovací mřížky (ovlivňuje citlivost)', '1', NULL, '8, 16', '1.0.0'),
(1, 'diff_mode', 'str', 'contours', 'Diff visualization mode: "contours" or "filled"', 'Režim vizualizace diffu: "contours" nebo "filled"', NULL, NULL, 'contours, filled', '1.2.0'),
(1, 'min_contour_area', 'int', '5000', 'Minimum contour area to filter noise. Higher = only large changes (loaders, dialogs).', 'Minimální plocha kontury pro filtrování šumu. Vyšší = pouze velké změny (loadery, dialogy).', '0', NULL, '50, 100, 1500, 5000', '1.2.0'),
(1, 'contour_thickness', 'int', '3', 'Thickness of contour outlines in pixels', 'Tloušťka obrysů kontur v pixelech', '1', NULL, '2, 3, 5', '1.2.0'),
(1, 'enable_color_coding', 'bool', 'False', 'Enable color coding by severity (green/yellow/red). Default: only red.', 'Zapnout barevné kódování podle závažnosti (zelená/žlutá/červená). Výchozí: pouze červená.', NULL, NULL, 'True, False', '1.2.0'),
(1, 'add_timestamp', 'bool', 'True', 'Add timestamp overlay to diff image (red, top-right, 16pt)', 'Přidat timestamp overlay na diff obrázek (červený, pravý horní roh, 16pt)', NULL, NULL, 'True, False', '1.2.0'),
(1, 'embed_images_to_log', 'bool', 'True', 'Embed 3 images (baseline, diff, current) into RF log.html as base64', 'Vložit 3 obrázky (baseline, diff, current) do RF log.html jako base64', NULL, NULL, 'True, False', '1.2.0'),
(1, 'diff_base_image', 'str', 'baseline', 'Visual base for diff: "baseline" (where elements WERE) or "current" (where elements ARE)', 'Vizuální základ pro diff: "baseline" (kde elementy BYLY) nebo "current" (kde elementy JSOU)', NULL, NULL, 'baseline, current', '1.4.0'),
(1, 'highlight_mode', 'str', 'all', 'Which pixels to highlight: "all", "added" (new in current), or "removed" (old from baseline)', 'Které pixely zvýraznit: "all", "added" (nové v current), nebo "removed" (staré z baseline)', NULL, NULL, 'all, added, removed', '1.4.0'),
(1, 'element_fill_expansion', 'int', '15', 'Morphological dilation kernel size to fill UI elements. Set to 0 to disable. Expands detected edges ~15px in all directions.', 'Velikost kernelu morfologické dilatace pro vyplnění UI elementů. Nastavit na 0 pro deaktivaci. Rozšíří detekované okraje ~15px všemi směry.', '0', NULL, '0, 7, 15, 30', '1.5.0');

-- Parameters for check_layouts_are_visually_similar (method_id=2)
INSERT INTO parameters (method_id, param_name, param_type, default_value, description_en, description_cz, added_in_version) VALUES
(2, 'baseline_image', 'Union[str, Path, Image.Image]', NULL, 'Reference/golden standard image', 'Referenční/zlatý standard obrázek', '1.0.0'),
(2, 'current_image', 'Union[str, Path, Image.Image]', NULL, 'Current screenshot to verify', 'Aktuální screenshot k ověření', '1.0.0'),
(2, 'diff_directory', 'Union[str, Path]', NULL, 'Directory to save diff image on failure', 'Adresář pro uložení diff obrázku při selhání', '1.0.0'),
(2, 'algorithm', 'str', 'dhash', 'Hashing algorithm (dhash is faster for relaxed comparison)', 'Hashovací algoritmus (dhash je rychlejší pro uvolněné porovnání)', '1.0.0'),
(2, 'tolerance', 'int', '15', 'Higher tolerance for relaxed comparison', 'Vyšší tolerance pro uvolněné porovnání', '1.0.0'),
(2, 'pixel_tolerance', 'int', '10', 'Lower pixel tolerance for filled mode', 'Nižší tolerance pixelů pro filled režim', '1.0.0');

-- ============================================================================
-- 7. DEPENDENCIES - Runtime and dev dependencies
-- ============================================================================

INSERT INTO dependencies (package_name, version_constraint, dependency_type, purpose) VALUES
('robotframework', '>=6.0', 'runtime', 'Robot Framework test automation framework'),
('Pillow', '>=9.0.0', 'runtime', 'Image loading, manipulation, and saving'),
('imagehash', '>=4.3.0', 'runtime', 'Perceptual hashing algorithms (phash, dhash)'),
('opencv-python', '>=4.8.0', 'runtime', 'Contour detection and morphological operations'),
('numpy', '>=1.24.0', 'runtime', 'Array operations for image processing'),
('pytest', NULL, 'dev', 'Testing framework (optional)'),
('pytest-cov', NULL, 'dev', 'Test coverage reporting (optional)'),
('black', NULL, 'dev', 'Code formatter (optional)'),
('flake8', NULL, 'dev', 'Linter (optional)'),
('mypy', NULL, 'dev', 'Type checker (optional)');

-- ============================================================================
-- 8. KEYWORDS - Robot Framework keywords
-- ============================================================================

INSERT INTO keywords (keyword_name, method_id, strictness_level, default_algorithm, default_tolerance, default_pixel_tolerance, typical_use_case, rf_example) VALUES
('Compare Layouts And Generate Diff', 1, 'strict', 'phash', 5, 60, 'Pixel-perfect regression testing of critical pages (login, checkout, forms)',
'Compare Layouts And Generate Diff
    ...    ${BASELINE_DIR}/login.png
    ...    ${RESULTS_DIR}/login.png
    ...    ${DIFF_DIR}
    ...    tolerance=5'),
('Check Layouts Are Visually Similar', 2, 'relaxed', 'dhash', 15, 10, 'Quick visual checks with higher tolerance for dynamic content or smoke tests',
'Check Layouts Are Visually Similar
    ...    ${BASELINE_DIR}/homepage.png
    ...    ${RESULTS_DIR}/homepage.png
    ...    ${DIFF_DIR}
    ...    tolerance=15');

-- ============================================================================
-- 9. ALGORITHMS - Hashing algorithms
-- ============================================================================

INSERT INTO algorithms (algorithm_name, algorithm_type, speed_rating, typical_time_ms, accuracy_rating, use_case, description_en, description_cz, recommended_for) VALUES
('phash', 'Perceptual Hash', 'medium', '50-100', 'high', 'Strict comparison, structural changes', 'Good for detecting structural changes. Resistant to minor color/lighting variations. Based on DCT (Discrete Cosine Transform).', 'Dobrý pro detekci strukturálních změn. Odolný vůči drobným změnám barev a osvětlení. Založen na DCT (Discrete Cosine Transform).', 'Most regression tests, critical pages, default choice'),
('dhash', 'Difference Hash', 'fast', '30-70', 'medium', 'Quick comparison, gradient detection', 'Faster than phash. Focuses on gradients and differences between adjacent pixels. Good for quick smoke tests.', 'Rychlejší než phash. Zaměřuje se na gradienty a rozdíly mezi sousedními pixely. Vhodný pro rychlé smoke testy.', 'Smoke tests, relaxed comparison, dynamic content');

-- ============================================================================
-- 10. USE_CASES - Typical usage scenarios
-- ============================================================================

INSERT INTO use_cases (use_case_name, scenario, recommended_settings, example_code, notes) VALUES
('Semi-transparent overlay detection', 'Detect large UI overlays like loaders, modal dialogs that appear with semi-transparent background', 'pixel_tolerance=60, min_contour_area=5000, element_fill_expansion=15',
'Compare Layouts And Generate Diff
    ...    baseline.png    current.png    diff/
    ...    pixel_tolerance=60
    ...    min_contour_area=5000',
'Default settings - optimized for ignoring semi-transparent changes while capturing large objects'),

('Complete loader circle detection', 'Detect entire loader overlay including light/semi-transparent parts', 'pixel_tolerance=45, min_contour_area=1500, element_fill_expansion=15',
'Compare Layouts And Generate Diff
    ...    baseline.png    current.png    diff/
    ...    pixel_tolerance=45
    ...    min_contour_area=1500',
'Lower thresholds capture more of the loader circle'),

('Pixel-level detailed detection', 'Detect small, subtle changes at pixel level', 'pixel_tolerance=25, min_contour_area=100, element_fill_expansion=15',
'Compare Layouts And Generate Diff
    ...    baseline.png    current.png    diff/
    ...    pixel_tolerance=25
    ...    min_contour_area=100',
'Very sensitive - captures minor changes'),

('White element on white background', 'Detect input fields, buttons, cards with minimal color contrast', 'pixel_tolerance=15, min_contour_area=50, element_fill_expansion=15',
'Compare Layouts And Generate Diff
    ...    baseline.png    current.png    diff/
    ...    pixel_tolerance=15
    ...    min_contour_area=50
    ...    element_fill_expansion=15',
'Morphological dilation fills entire element area (not just edges). Increases contour area by ~238%.'),

('Element position shift only', 'Show only NEW position when element moves (not both old and new)', 'diff_base_image=current, highlight_mode=added, element_fill_expansion=15',
'Compare Layouts And Generate Diff
    ...    baseline.png    current.png    diff/
    ...    diff_base_image=current
    ...    highlight_mode=added
    ...    element_fill_expansion=15',
'Shows only where element IS now, ignoring where it WAS'),

('Cross-browser testing', 'Compare UI rendering across browsers', 'algorithm=phash, tolerance=10',
'Compare Layouts And Generate Diff
    ...    chrome_baseline.png
    ...    firefox_current.png
    ...    diff/
    ...    tolerance=10',
'Slightly higher tolerance for browser rendering differences');

-- ============================================================================
-- 11. TROUBLESHOOTING - Common issues and solutions
-- ============================================================================

INSERT INTO troubleshooting (issue_title, symptoms, cause, solution, related_parameter) VALUES
('Images have different dimensions', 'AssertionError: "Images have different dimensions: baseline (1920x1080) vs current (1366x768)"', 'Baseline and current images must be exactly the same size for comparison', 'Ensure both images are captured at the same resolution. Resize before comparison or capture at consistent resolution.', NULL),

('Unsupported algorithm', 'ValueError: "Unsupported algorithm: ahash. Use ''phash'' or ''dhash''"', 'Only phash and dhash algorithms are currently supported', 'Use algorithm=phash or algorithm=dhash. Check spelling (lowercase).', 'algorithm'),

('Image file not found', 'FileNotFoundError: [Errno 2] No such file or directory: ''/path/to/image.png''', 'Image path is incorrect or file does not exist', 'Verify file path is correct. Use absolute paths or check working directory. Ensure file exists before comparison.', 'baseline_image, current_image'),

('Diff not generated', 'Test passes but no diff image created', 'Diff is only generated on FAILURE (distance > tolerance)', 'This is expected behavior. Diff images are only created when comparison fails. If you want to see diff, lower tolerance or verify images are actually different.', 'tolerance'),

('Small contours not detected', 'Small UI changes (buttons, inputs) not highlighted in diff', 'min_contour_area is too high, filtering out small changes', 'Lower min_contour_area value: try 100 for small elements, 50 for very small. Default 5000 is for large objects like loaders.', 'min_contour_area'),

('White elements not detected', 'Input fields or buttons on white background not highlighted', 'Insufficient element_fill_expansion or pixel_tolerance too high', 'Set element_fill_expansion=15 (default) or higher. Lower pixel_tolerance to 15-25 for better edge detection.', 'element_fill_expansion, pixel_tolerance'),

('Both old and new positions highlighted', 'When element moves, diff shows BOTH original and new positions', 'Default highlight_mode=all shows all changes', 'Use diff_base_image=current and highlight_mode=added to show only new position', 'diff_base_image, highlight_mode');

-- ============================================================================
-- 12. PERFORMANCE_METRICS - Performance characteristics
-- ============================================================================

INSERT INTO performance_metrics (operation, algorithm, image_resolution, typical_time_ms, memory_usage, notes) VALUES
('Hash calculation', 'phash', '1920x1080', '50-100', 'Minimal', 'Perceptual hash - slower but more accurate'),
('Hash calculation', 'dhash', '1920x1080', '30-70', 'Minimal', 'Difference hash - faster for quick checks'),
('Diff generation', NULL, '1920x1080', '200-500', 'One image copy', 'Includes contour detection, drawing, and file save'),
('Contour detection', NULL, '1920x1080', '50-150', 'Minimal', 'OpenCV findContours with minimal preprocessing'),
('Morphological dilation', NULL, '1920x1080', '20-50', 'Minimal', 'cv2.dilate with elliptical kernel (element_fill_expansion)'),
('Image loading', NULL, 'Any', '10-50', 'One image in memory', 'PIL Image.open()'),
('Base64 encoding', NULL, '1920x1080', '100-200', 'Temporary buffer', 'For HTML embedding - increases log.html size');

-- ============================================================================
-- 13. DIFF_MODES - Diff visualization modes
-- ============================================================================

INSERT INTO diff_modes (mode_name, description, visual_style, when_to_use, implementation_method, added_in_version) VALUES
('contours', 'Professional diff visualization with semi-transparent fill and thick outlines', 'Pink semi-transparent fill (30% opacity) + thick red outlines (3px)', 'Default mode. Best for most use cases. Filters noise, highlights significant changes clearly.', '_draw_contours_on_diff() with two-pass rendering: 1) fill contours on overlay, 2) alpha blend 30%+70%, 3) draw thick outlines', '1.2.0'),
('filled', 'Legacy mode - pixel-by-pixel comparison with filled pixels', 'Solid red fill (255,0,0) on all different pixels', 'Backward compatibility. When you need pixel-perfect visualization without contour filtering.', 'Pixel-by-pixel Manhattan distance comparison, mark diff pixels as red', '1.0.0');

-- ============================================================================
-- 14. BEST_PRACTICES - Best practices and recommendations
-- ============================================================================

INSERT INTO best_practices (category, practice_title, description, example_code, do_this, dont_do_this) VALUES
('Testing', 'Aim for 80%+ test coverage', 'Maintain high test coverage to ensure library reliability', 'pytest tests/ --cov=ImageComparisonLibrary --cov-report=html', 'Test edge cases, error scenarios, and all public methods', 'Skip tests or ignore failing tests'),

('Code Style', 'Follow PEP 8 with 100 char line length', 'Maintain consistent code style across the project', NULL, 'Use 4 spaces, max 100 chars per line, meaningful variable names', 'Mix tabs and spaces, exceed line length, use cryptic names'),

('Docstrings', 'Use dual language docstrings (EN + CZ)', 'English description → --- separator → Czech description',
'def compare_images(...):
    """Compare images using perceptual hashing.

    ---

    Porovnej obrázky pomocí perceptual hashování.
    """',
'Include both English and Czech for maximum accessibility', 'Only one language or no docstrings'),

('Type Hints', 'Always use type hints', 'Specify types for all parameters and return values', 'def load_image(path: Union[str, Path]) -> Image.Image:', 'Use Union, Optional, List from typing module', 'Omit type hints or use "Any" everywhere'),

('Baseline Management', 'Update baselines when UI changes are intentional', 'After reviewing diff images and confirming changes are expected', NULL, 'Review diff images first, then update baseline if change is intentional', 'Blindly update baselines without visual review'),

('Tolerance Settings', 'Start with strict tolerance, increase if needed', 'Begin with low tolerance (5-10) for critical pages, higher for dynamic content',
'Compare Layouts And Generate Diff
    ...    tolerance=5    # Critical page

Compare Layouts And Generate Diff
    ...    tolerance=15   # Dynamic content',
'Use strict tolerance (5) for critical pages, relaxed (15) for dynamic content', 'Use same tolerance for all pages without considering their characteristics'),

('Error Messages', 'Always check error messages in log', 'Error messages contain detailed information about failure cause', NULL, 'Read full error message including Hamming distance and paths', 'Ignore error details and just re-run test');
