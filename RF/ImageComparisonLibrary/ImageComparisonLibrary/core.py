"""Core implementation of ImageComparisonLibrary for Robot Framework.

Hlavní implementace ImageComparisonLibrary pro Robot Framework.
"""

from pathlib import Path
from typing import Union, Dict, Tuple, Optional, Literal
from datetime import datetime
from dataclasses import dataclass
import imagehash
from PIL import Image, ImageDraw, ImageFont
from robot.api import logger
import cv2
import numpy as np


@dataclass
class DiffStatistics:
    """Statistics from image comparison.

    ---

    Statistiky z porovnání obrázků.
    """
    total_pixels: int
    different_pixels: int
    difference_percentage: float
    minor_diff_pixels: int  # green
    moderate_diff_pixels: int  # yellow
    severe_diff_pixels: int  # red
    num_contours: int
    largest_contour_area: int
    average_color_difference: float


class ImageComparisonLibrary:
    """Visual regression testing library for catching unexpected UI changes.

    = Overview =

    ImageComparisonLibrary provides two main keywords for automated UI testing:

    1. ``Compare Layouts And Generate Diff`` - Strict pixel-perfect verification
    2. ``Check Layouts Are Visually Similar`` - Relaxed comparison for dynamic content

    Both keywords use perceptual hashing for fast comparison and generate visual
    diff images with highlighted changes when tests fail.

    = Typical Workflow =

    1. Capture baseline screenshots of your UI (one-time setup)
    2. Run tests that capture current screenshots
    3. Compare current vs baseline using library keywords
    4. Review diff images in Robot Framework log.html if tests fail
    5. Update baselines when UI changes are intentional

    = Use Cases =

    *Regression Testing:*
    - Catch unintended UI changes after code updates
    - Verify critical pages (login, checkout, forms)
    - Automated smoke tests in CI/CD pipelines

    *Cross-Browser Testing:*
    - Compare UI rendering across different browsers
    - Detect browser-specific layout issues

    *Responsive Design:*
    - Verify UI at different screen resolutions
    - Compare mobile vs desktop layouts

    = Algorithm Choice =

    *phash (Perceptual Hash):*
    - Default for strict comparison
    - Good for structural changes
    - Resistant to minor color/lighting variations
    - Recommended for most tests

    *dhash (Difference Hash):*
    - Default for relaxed comparison
    - Faster than phash
    - Focuses on gradients
    - Good for quick smoke tests

    = See Also =

    - GitHub: https://github.com/yourusername/ImageComparisonLibrary
    - README.md for installation and examples
    - IMPORTANT_PLACES.md for code structure

    ---

    = Přehled =

    ImageComparisonLibrary poskytuje dvě hlavní klíčová slova pro automatizované UI testování:

    1. ``Compare Layouts And Generate Diff`` - Přísné pixel-perfect ověření
    2. ``Check Layouts Are Visually Similar`` - Uvolněné porovnání pro dynamický obsah

    Obě klíčová slova používají perceptual hashing pro rychlé porovnání a generují
    vizuální diff obrázky se zvýrazněnými změnami, když testy selžou.

    = Typický workflow =

    1. Zachyťte baseline screenshoty vašeho UI (jednorázové nastavení)
    2. Spusťte testy, které zachytí aktuální screenshoty
    3. Porovnejte aktuální vs baseline pomocí klíčových slov knihovny
    4. Zkontrolujte diff obrázky v Robot Framework log.html, pokud testy selžou
    5. Aktualizujte baselines, když jsou UI změny záměrné

    = Případy použití =

    *Regresní testování:*
    - Zachycení nezáměrných UI změn po aktualizacích kódu
    - Ověření kritických stránek (přihlášení, checkout, formuláře)
    - Automatizované smoke testy v CI/CD pipelines

    *Cross-Browser testování:*
    - Porovnání vykreslování UI napříč různými prohlížeči
    - Detekce problémů s layoutem specifických pro prohlížeč

    *Responzivní design:*
    - Ověření UI při různých rozlišeních obrazovky
    - Porovnání mobilních vs desktopových layoutů

    = Volba algoritmu =

    *phash (Perceptual Hash):*
    - Výchozí pro přísné porovnání
    - Dobré pro strukturální změny
    - Odolné vůči menším barevným/světelným variacím
    - Doporučené pro většinu testů

    *dhash (Difference Hash):*
    - Výchozí pro uvolněné porovnání
    - Rychlejší než phash
    - Zaměřuje se na gradienty
    - Dobré pro rychlé smoke testy

    = Viz také =

    - GitHub: https://github.com/yourusername/ImageComparisonLibrary
    - README.md pro instalaci a příklady
    - IMPORTANT_PLACES.md pro strukturu kódu
    """
    
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'
    ROBOT_LIBRARY_VERSION = '1.0.0'
    
    def __init__(self):
        """Initialize the ImageComparisonLibrary.

        Inicializuje ImageComparisonLibrary.
        """
        pass
    
    def compare_layouts_and_generate_diff(
        self,
        baseline_image: Union[str, Path, Image.Image],
        current_image: Union[str, Path, Image.Image],
        diff_directory: Union[str, Path],
        algorithm: str = 'phash',
        tolerance: int = 5,
        pixel_tolerance: int = 60,
        hash_size: int = 8,
        # NEW PARAMETERS for enhanced diff visualization
        diff_mode: Literal['filled', 'contours'] = 'contours',
        contour_thickness: int = 3,
        min_contour_area: int = 5000,
        minor_color: Tuple[int, int, int] = (0, 255, 0),
        moderate_color: Tuple[int, int, int] = (0, 255, 255),
        severe_color: Tuple[int, int, int] = (0, 0, 255),
        enable_color_coding: bool = False,
        log_statistics: bool = True,
        generate_html: bool = False,
        embed_images_to_log: bool = True,
        add_timestamp: bool = True,
        # NEW PARAMETERS for directional diff support
        diff_base_image: Literal['baseline', 'current'] = 'baseline',
        highlight_mode: Literal['all', 'added', 'removed'] = 'all',
        element_fill_expansion: int = 15
    ) -> int:
        """Verify that UI layout matches baseline screenshot (strict pixel-perfect mode).

        = When To Use =

        Use this keyword for:
        - *Critical UI elements:* Login pages, checkout flows, payment forms
        - *Regression testing:* Catch unintended UI changes after code updates
        - *CI/CD pipelines:* Automated smoke tests with binary pass/fail results
        - *Pixel-perfect verification:* When exact visual match is required

        This is the main, strictest keyword with low tolerance (default: 5).
        For pages with dynamic content, use ``Check Layouts Are Visually Similar`` instead.

        = What This Does =

        1. Calculates perceptual hash of both images (phash or dhash algorithm)
        2. Compares hashes using Hamming distance
        3. If similar (distance ≤ tolerance): Test PASSES ✓
        4. If different (distance > tolerance): Test FAILS and generates diff image
        5. Diff image shows highlighted changes with semi-transparent overlays
        6. Embeds baseline, current, and diff images into Robot Framework log.html

        = Common Usage Patterns =

        *Basic regression test:*

        | Compare Layouts And Generate Diff | baseline.png | current.png | ${DIFF_DIR} |

        *Ignore semi-transparent overlays (loaders, dialogs):*

        | Compare Layouts And Generate Diff | baseline.png | current.png | ${DIFF_DIR}
        | ...    pixel_tolerance=60    min_contour_area=5000

        *Capture only major layout changes:*

        | Compare Layouts And Generate Diff | baseline.png | current.png | ${DIFF_DIR}
        | ...    tolerance=10    min_contour_area=10000

        *Use faster algorithm for quick tests:*

        | Compare Layouts And Generate Diff | baseline.png | current.png | ${DIFF_DIR}
        | ...    algorithm=dhash

        *Disable auto-embedding to log (reduce log.html size):*

        | Compare Layouts And Generate Diff | baseline.png | current.png | ${DIFF_DIR}
        | ...    embed_images_to_log=False

        = Understanding The Output =

        *When test PASSES:*
        - Log message: "Layouts are similar. Distance: X (threshold: Y)"
        - No diff image generated
        - Returns Hamming distance (integer)

        *When test FAILS:*
        - AssertionError with detailed message
        - Visual diff image saved to diff_directory
        - Baseline, current, and diff images embedded in log.html
        - Statistics logged (pixels changed, contours detected, etc.)

        Args:
            baseline_image: Reference image. Accepts str (path), pathlib.Path, or PIL.Image.Image.
            current_image: Current image to verify. Accepts str (path), pathlib.Path, or PIL.Image.Image.
            diff_directory: Directory path to save diff image on failure. Accepts str or pathlib.Path.
            algorithm: Hashing algorithm to use. Options: 'phash', 'dhash'. Default: 'phash'.
            tolerance: Maximum allowed Hamming distance. Default: 5.
            pixel_tolerance: Color difference tolerance (0-255) for visual diff generation. Default: 60.
            hash_size: Hash grid size. Default: 8.
            diff_mode: Diff visualization mode: 'contours' (new, default) or 'filled' (legacy). Default: 'contours'.
            contour_thickness: Thickness of contour lines in pixels (for contours mode). Default: 3.
            min_contour_area: Minimum contour area to keep, filters small changes. Default: 5000.
            minor_color: RGB tuple for minor differences (green). Default: (0, 255, 0).
            moderate_color: RGB tuple for moderate differences (yellow). Default: (0, 255, 255).
            severe_color: RGB tuple for severe differences (red). Default: (0, 0, 255).
            enable_color_coding: If False, use only severe_color for all changes. Default: False.
            log_statistics: If True, log detailed statistics to RF logger. Default: True.
            generate_html: If True, generate HTML report with side-by-side comparison. Default: False.
            embed_images_to_log: If True, embed baseline and diff images to RF log.html as base64. Default: True.
            add_timestamp: If True, add timestamp to diff image (bottom-right corner, format: dd/mm/yy hh:mm:ss). Default: True.
            diff_base_image: Which image to use as visual base for diff. Options: 'baseline' (show where elements were), 'current' (show where elements are). Default: 'baseline'.
            highlight_mode: Which pixels to highlight. Options: 'all' (all changes), 'added' (new pixels in current), 'removed' (old pixels from baseline). Default: 'all'.

        Returns:
            int: The Hamming distance between the two images.

        Raises:
            AssertionError: If images differ beyond the allowed tolerance or have different dimensions.
            ValueError: If invalid algorithm or diff_mode is specified.

        ---

        = Kdy použít =

        Použijte toto klíčové slovo pro:
        - *Kritické UI elementy:* Přihlašovací stránky, checkout, platební formuláře
        - *Regresní testování:* Zachycení nezáměrných UI změn po aktualizacích kódu
        - *CI/CD pipelines:* Automatizované smoke testy s binárním pass/fail výsledkem
        - *Pixel-perfect ověření:* Když je vyžadována přesná vizuální shoda

        Toto je hlavní, nejpřísnější klíčové slovo s nízkou tolerancí (výchozí: 5).
        Pro stránky s dynamickým obsahem použijte ``Check Layouts Are Visually Similar``.

        = Co to dělá =

        1. Vypočítá perceptual hash obou obrázků (phash nebo dhash algoritmus)
        2. Porovná hashe pomocí Hammingovy vzdálenosti
        3. Pokud jsou podobné (distance ≤ tolerance): Test PROJDE ✓
        4. Pokud jsou odlišné (distance > tolerance): Test SELŽE a vygeneruje diff obrázek
        5. Diff obrázek zobrazuje zvýrazněné změny s poloprůhledným překrytím
        6. Vloží baseline, aktuální a diff obrázky do Robot Framework log.html

        = Běžné vzory použití =

        *Základní regresní test:*

        | Compare Layouts And Generate Diff | baseline.png | current.png | ${DIFF_DIR} |

        *Ignorovat poloprůhledné překrytí (loadery, dialogy):*

        | Compare Layouts And Generate Diff | baseline.png | current.png | ${DIFF_DIR}
        | ...    pixel_tolerance=60    min_contour_area=5000

        *Zachytit pouze významné změny layoutu:*

        | Compare Layouts And Generate Diff | baseline.png | current.png | ${DIFF_DIR}
        | ...    tolerance=10    min_contour_area=10000

        *Použít rychlejší algoritmus pro rychlé testy:*

        | Compare Layouts And Generate Diff | baseline.png | current.png | ${DIFF_DIR}
        | ...    algorithm=dhash

        *Vypnout automatické vkládání do logu (zmenšit velikost log.html):*

        | Compare Layouts And Generate Diff | baseline.png | current.png | ${DIFF_DIR}
        | ...    embed_images_to_log=False

        = Pochopení výstupu =

        *Když test PROJDE:*
        - Log zpráva: "Layouts are similar. Distance: X (threshold: Y)"
        - Žádný diff obrázek není vygenerován
        - Vrací Hammingovu vzdálenost (integer)

        *Když test SELŽE:*
        - AssertionError s detailní zprávou
        - Vizuální diff obrázek uložen do diff_directory
        - Baseline, aktuální a diff obrázky vloženy do log.html
        - Statistiky zalogované (změněné pixely, detekované kontury, atd.)

        Args:
            baseline_image: Referenční obrázek. Akceptuje str (cestu), pathlib.Path, nebo PIL.Image.Image.
            current_image: Aktuální obrázek k ověření. Akceptuje str (cestu), pathlib.Path, nebo PIL.Image.Image.
            diff_directory: Cesta k adresáři pro uložení diff obrázku při selhání. Akceptuje str nebo pathlib.Path.
            algorithm: Hashovací algoritmus k použití. Možnosti: 'phash', 'dhash'. Výchozí: 'phash'.
            tolerance: Maximální povolená Hammingova vzdálenost. Výchozí: 5.
            pixel_tolerance: Tolerance barevného rozdílu (0-255) pro generování vizuálního diffu. Výchozí: 60.
            hash_size: Velikost hashovací mřížky. Výchozí: 8.
            diff_mode: Režim vizualizace: 'contours' (nový, výchozí) nebo 'filled' (legacy). Výchozí: 'contours'.
            contour_thickness: Tloušťka linií kontur v pixelech (pro contours režim). Výchozí: 3.
            min_contour_area: Minimální plocha kontury, filtruje malé změny. Výchozí: 5000.
            minor_color: RGB tuple pro menší rozdíly (zelená). Výchozí: (0, 255, 0).
            moderate_color: RGB tuple pro střední rozdíly (žlutá). Výchozí: (0, 255, 255).
            severe_color: RGB tuple pro velké rozdíly (červená). Výchozí: (0, 0, 255).
            enable_color_coding: Pokud False, použije se pouze severe_color. Výchozí: False.
            log_statistics: Pokud True, zaloguje detailní statistiky do RF loggeru. Výchozí: True.
            generate_html: Pokud True, vygeneruje HTML report s porovnáním. Výchozí: False.
            embed_images_to_log: Pokud True, embeduje baseline a diff obrázky do RF log.html jako base64. Výchozí: True.
            add_timestamp: Pokud True, přidá timestamp do diff obrázku (pravý dolní roh, formát: dd/mm/yy hh:mm:ss). Výchozí: True.
            diff_base_image: Který obrázek použít jako vizuální základ pro diff. Možnosti: 'baseline' (ukáže kde elementy byly), 'current' (ukáže kde elementy jsou). Výchozí: 'baseline'.
            highlight_mode: Které pixely zvýraznit. Možnosti: 'all' (všechny změny), 'added' (nové pixely v current), 'removed' (staré pixely z baseline). Výchozí: 'all'.

        Returns:
            int: Hammingova vzdálenost mezi dvěma obrázky.

        Raises:
            AssertionError: Pokud se obrázky liší nad povolenou toleranci nebo mají různé rozměry.
            ValueError: Pokud je zadán neplatný algoritmus nebo diff_mode.

        Examples:
            | Compare Layouts And Generate Diff | baseline.png | current.png | ${DIFF_DIR} |
            | Compare Layouts And Generate Diff | baseline.png | current.png | ${DIFF_DIR} | algorithm=dhash | tolerance=10 |
            | Compare Layouts And Generate Diff | baseline.png | current.png | ${DIFF_DIR} | generate_html=True |
            | Compare Layouts And Generate Diff | baseline.png | current.png | ${DIFF_DIR} | diff_mode=filled |
        """
        # Load images
        baseline_img = self._load_image(baseline_image)
        current_img = self._load_image(current_image)
        
        # Calculate hashes
        baseline_hash = self._calculate_hash(baseline_img, algorithm, hash_size)
        current_hash = self._calculate_hash(current_img, algorithm, hash_size)
        
        # Calculate Hamming distance
        distance = int(baseline_hash - current_hash)
        
        # Success scenario
        if distance <= tolerance:
            logger.info(
                f"Layouts are similar. Distance: {distance} (threshold: {tolerance})."
            )
            return distance
        
        # Failure scenario - check dimensions first
        if baseline_img.size != current_img.size:
            raise AssertionError(
                f"Images have different dimensions. "
                f"Baseline: {baseline_img.size}, Current: {current_img.size}"
            )
        
        # Get paths for HTML report
        baseline_path_str = self._get_image_path(baseline_image)
        current_path_str = self._get_image_path(current_image)

        # Generate visual diff with enhanced options
        diff_path, stats = self._generate_visual_diff(
            baseline_img,
            current_img,
            diff_directory,
            pixel_tolerance,
            diff_mode=diff_mode,
            contour_thickness=contour_thickness,
            min_contour_area=min_contour_area,
            minor_color=minor_color,
            moderate_color=moderate_color,
            severe_color=severe_color,
            enable_color_coding=enable_color_coding,
            log_statistics=log_statistics,
            generate_html=generate_html,
            embed_images_to_log=embed_images_to_log,
            add_timestamp=add_timestamp,
            diff_base_image=diff_base_image,
            highlight_mode=highlight_mode,
            element_fill_expansion=element_fill_expansion,
            baseline_path_for_html=baseline_path_str,
            current_path_for_html=current_path_str,
            hash_distance_for_html=distance,
            tolerance_for_html=tolerance,
            algorithm_for_html=algorithm
        )

        logger.info(f"Visual differences saved to: {diff_path}")
        # Statistics already logged by _generate_visual_diff if log_statistics=True

        # Raise detailed error
        error_message = (
            f"Images differ beyond allowed tolerance!\n\n"
            f"Comparison details:\n"
            f"  - Baseline image: {baseline_path_str}\n"
            f"  - Current image: {current_path_str}\n"
            f"  - Algorithm used: {algorithm} (hash_size={hash_size})\n"
            f"  - Hamming distance: {distance}\n"
            f"  - Tolerance threshold: {tolerance}\n\n"
            f"Visual differences saved to: {diff_path}"
        )
        
        raise AssertionError(error_message)
    
    def check_layouts_are_visually_similar(
        self,
        baseline_image: Union[str, Path, Image.Image],
        current_image: Union[str, Path, Image.Image],
        diff_directory: Union[str, Path],
        algorithm: str = 'dhash',
        tolerance: int = 15,
        pixel_tolerance: int = 60,
        hash_size: int = 8,
        # NEW PARAMETERS for enhanced diff visualization (same as compare_layouts_and_generate_diff)
        diff_mode: Literal['filled', 'contours'] = 'contours',
        contour_thickness: int = 3,
        min_contour_area: int = 5000,
        minor_color: Tuple[int, int, int] = (0, 255, 0),
        moderate_color: Tuple[int, int, int] = (0, 255, 255),
        severe_color: Tuple[int, int, int] = (0, 0, 255),
        enable_color_coding: bool = False,
        log_statistics: bool = True,
        generate_html: bool = False,
        embed_images_to_log: bool = True,
        add_timestamp: bool = True,
        element_fill_expansion: int = 15
    ) -> int:
        """Verify UI layout with relaxed tolerance for pages with dynamic content.

        = When To Use =

        Use this keyword for:
        - *Dynamic content:* Pages with timestamps, usernames, counters, session IDs
        - *Data-driven pages:* Dashboards, charts, graphs with changing data
        - *Quick smoke tests:* Fast comparison without pixel-perfect requirements
        - *A/B testing:* When minor visual differences are acceptable

        This keyword uses relaxed tolerance (default: 15) and faster dhash algorithm.
        For pixel-perfect verification, use ``Compare Layouts And Generate Diff`` instead.

        = What This Does =

        Same as ``Compare Layouts And Generate Diff``, but with relaxed settings:
        1. Uses dhash algorithm (faster) instead of phash
        2. Higher tolerance (15 instead of 5) - allows more variation
        3. Same visual diff generation if test fails
        4. Same embedding into Robot Framework log.html

        = Common Usage Patterns =

        *Basic relaxed comparison:*

        | Check Layouts Are Visually Similar | baseline.png | current.png | ${DIFF_DIR} |

        *Even more relaxed (ignore minor changes):*

        | Check Layouts Are Visually Similar | baseline.png | current.png | ${DIFF_DIR}
        | ...    tolerance=20

        *Dashboard with changing data:*

        | Check Layouts Are Visually Similar | dashboard_baseline.png | dashboard_current.png | ${DIFF_DIR}
        | ...    tolerance=15    pixel_tolerance=80

        *Quick smoke test across multiple pages:*

        | FOR    ${page}    IN    @{PAGES}
        |     Check Layouts Are Visually Similar    ${page}_baseline.png    ${page}_current.png    ${DIFF_DIR}
        | END

        = Comparison: Strict vs Relaxed =

        *Compare Layouts And Generate Diff (STRICT):*
        - Tolerance: 5 (low)
        - Algorithm: phash (precise)
        - Use for: Critical UI, pixel-perfect tests

        *Check Layouts Are Visually Similar (RELAXED):*
        - Tolerance: 15 (high)
        - Algorithm: dhash (fast)
        - Use for: Dynamic content, quick tests

        Args:
            baseline_image: Reference image. Accepts str (path), pathlib.Path, or PIL.Image.Image.
            current_image: Current image to verify. Accepts str (path), pathlib.Path, or PIL.Image.Image.
            diff_directory: Directory path to save diff image on failure. Accepts str or pathlib.Path.
            algorithm: Hashing algorithm to use. Default: 'dhash'.
            tolerance: Maximum allowed Hamming distance. Default: 15.
            pixel_tolerance: Color difference tolerance (0-255) for visual diff generation. Default: 60.
            hash_size: Hash grid size. Default: 8.
            diff_mode: Diff visualization mode: 'contours' (new, default) or 'filled' (legacy). Default: 'contours'.
            contour_thickness: Thickness of contour lines in pixels (for contours mode). Default: 3.
            min_contour_area: Minimum contour area to keep, filters small changes. Default: 5000.
            minor_color: RGB tuple for minor differences (green). Default: (0, 255, 0).
            moderate_color: RGB tuple for moderate differences (yellow). Default: (0, 255, 255).
            severe_color: RGB tuple for severe differences (red). Default: (0, 0, 255).
            enable_color_coding: If False, use only severe_color for all changes. Default: False.
            log_statistics: If True, log detailed statistics to RF logger. Default: True.
            generate_html: If True, generate HTML report with side-by-side comparison. Default: False.
            embed_images_to_log: If True, embed baseline and diff images to RF log.html as base64. Default: True.
            add_timestamp: If True, add timestamp to diff image (bottom-right corner, format: dd/mm/yy hh:mm:ss). Default: True.

        Returns:
            int: The Hamming distance between the two images.

        Raises:
            AssertionError: If images differ beyond the allowed tolerance or have different dimensions.

        ---

        = Kdy použít =

        Použijte toto klíčové slovo pro:
        - *Dynamický obsah:* Stránky s časovými značkami, uživatelskými jmény, počítadly, session ID
        - *Data-driven stránky:* Dashboardy, grafy s měnícími se daty
        - *Rychlé smoke testy:* Rychlé porovnání bez pixel-perfect požadavků
        - *A/B testování:* Když jsou menší vizuální rozdíly přijatelné

        Toto klíčové slovo používá uvolněnou toleranci (výchozí: 15) a rychlejší dhash algoritmus.
        Pro pixel-perfect ověření použijte ``Compare Layouts And Generate Diff``.

        = Co to dělá =

        Stejné jako ``Compare Layouts And Generate Diff``, ale s uvolněným nastavením:
        1. Používá dhash algoritmus (rychlejší) místo phash
        2. Vyšší tolerance (15 místo 5) - povoluje více variací
        3. Stejné generování vizuálního diffu, pokud test selže
        4. Stejné vkládání do Robot Framework log.html

        = Běžné vzory použití =

        *Základní uvolněné porovnání:*

        | Check Layouts Are Visually Similar | baseline.png | current.png | ${DIFF_DIR} |

        *Ještě více uvolněné (ignorovat menší změny):*

        | Check Layouts Are Visually Similar | baseline.png | current.png | ${DIFF_DIR}
        | ...    tolerance=20

        *Dashboard s měnícími se daty:*

        | Check Layouts Are Visually Similar | dashboard_baseline.png | dashboard_current.png | ${DIFF_DIR}
        | ...    tolerance=15    pixel_tolerance=80

        *Rychlý smoke test napříč více stránkami:*

        | FOR    ${page}    IN    @{PAGES}
        |     Check Layouts Are Visually Similar    ${page}_baseline.png    ${page}_current.png    ${DIFF_DIR}
        | END

        = Porovnání: Přísné vs Uvolněné =

        *Compare Layouts And Generate Diff (PŘÍSNÉ):*
        - Tolerance: 5 (nízká)
        - Algoritmus: phash (přesný)
        - Použití: Kritické UI, pixel-perfect testy

        *Check Layouts Are Visually Similar (UVOLNĚNÉ):*
        - Tolerance: 15 (vysoká)
        - Algoritmus: dhash (rychlý)
        - Použití: Dynamický obsah, rychlé testy

        Args:
            baseline_image: Referenční obrázek. Akceptuje str (cestu), pathlib.Path, nebo PIL.Image.Image.
            current_image: Aktuální obrázek k ověření. Akceptuje str (cestu), pathlib.Path, nebo PIL.Image.Image.
            diff_directory: Cesta k adresáři pro uložení diff obrázku při selhání. Akceptuje str nebo pathlib.Path.
            algorithm: Hashovací algoritmus k použití. Výchozí: 'dhash'.
            tolerance: Maximální povolená Hammingova vzdálenost. Výchozí: 15.
            pixel_tolerance: Tolerance barevného rozdílu (0-255) pro generování vizuálního diffu. Výchozí: 60.
            hash_size: Velikost hashovací mřížky. Výchozí: 8.
            diff_mode: Režim vizualizace: 'contours' (nový, výchozí) nebo 'filled' (legacy). Výchozí: 'contours'.
            contour_thickness: Tloušťka linií kontur v pixelech (pro contours režim). Výchozí: 3.
            min_contour_area: Minimální plocha kontury, filtruje malé změny. Výchozí: 5000.
            minor_color: RGB tuple pro menší rozdíly (zelená). Výchozí: (0, 255, 0).
            moderate_color: RGB tuple pro střední rozdíly (žlutá). Výchozí: (0, 255, 255).
            severe_color: RGB tuple pro velké rozdíly (červená). Výchozí: (0, 0, 255).
            enable_color_coding: Pokud False, použije se pouze severe_color. Výchozí: False.
            log_statistics: Pokud True, zaloguje detailní statistiky do RF loggeru. Výchozí: True.
            generate_html: Pokud True, vygeneruje HTML report s porovnáním. Výchozí: False.
            embed_images_to_log: Pokud True, embeduje baseline a diff obrázky do RF log.html jako base64. Výchozí: True.
            add_timestamp: Pokud True, přidá timestamp do diff obrázku (pravý dolní roh, formát: dd/mm/yy hh:mm:ss). Výchozí: True.

        Returns:
            int: Hammingova vzdálenost mezi dvěma obrázky.

        Raises:
            AssertionError: Pokud se obrázky liší nad povolenou toleranci nebo mají různé rozměry.

        Examples:
            | Check Layouts Are Visually Similar |   baseline.png |     current.png |   ${DIFF_DIR} |
            | Check Layouts Are Visually Similar |   baseline.png |     current.png |   ${DIFF_DIR} |   tolerance=20 |
            | Check Layouts Are Visually Similar |   baseline.png |     current.png |   ${DIFF_DIR} |   generate_html=True |
        """
        return self.compare_layouts_and_generate_diff(
            baseline_image=baseline_image,
            current_image=current_image,
            diff_directory=diff_directory,
            algorithm=algorithm,
            tolerance=tolerance,
            pixel_tolerance=pixel_tolerance,
            hash_size=hash_size,
            diff_mode=diff_mode,
            contour_thickness=contour_thickness,
            min_contour_area=min_contour_area,
            minor_color=minor_color,
            moderate_color=moderate_color,
            severe_color=severe_color,
            enable_color_coding=enable_color_coding,
            log_statistics=log_statistics,
            generate_html=generate_html,
            embed_images_to_log=embed_images_to_log,
            add_timestamp=add_timestamp,
            element_fill_expansion=element_fill_expansion
        )
    
    def _load_image(self, image: Union[str, Path, Image.Image]) -> Image.Image:
        """Load an image from various input types.

        Args:
            image: Image as str path, pathlib.Path, or PIL.Image.Image.

        Returns:
            PIL.Image.Image: Loaded image.

        Raises:
            ValueError: If image type is not supported.
            FileNotFoundError: If image file doesn't exist.

        ---

        Načte obrázek z různých typů vstupů.

        Args:
            image: Obrázek jako str cesta, pathlib.Path, nebo PIL.Image.Image.

        Returns:
            PIL.Image.Image: Načtený obrázek.

        Raises:
            ValueError: Pokud typ obrázku není podporován.
            FileNotFoundError: Pokud soubor obrázku neexistuje.
        """
        if isinstance(image, Image.Image):
            return image
        elif isinstance(image, (str, Path)):
            image_path = Path(image)
            if not image_path.exists():
                raise FileNotFoundError(f"Image file not found: {image_path}")
            return Image.open(image_path)
        else:
            raise ValueError(
                f"Unsupported image type: {type(image)}. "
                f"Expected str, pathlib.Path, or PIL.Image.Image."
            )
    
    def _calculate_hash(
        self,
        image: Image.Image,
        algorithm: str,
        hash_size: int
    ) -> imagehash.ImageHash:
        """Calculate perceptual hash of an image.

        Args:
            image: PIL Image object.
            algorithm: Hashing algorithm ('phash' or 'dhash').
            hash_size: Size of the hash grid.

        Returns:
            imagehash.ImageHash: Calculated hash.

        Raises:
            ValueError: If algorithm is not supported.

        ---

        Vypočítá perceptual hash obrázku.

        Args:
            image: PIL Image objekt.
            algorithm: Hashovací algoritmus ('phash' nebo 'dhash').
            hash_size: Velikost hashovací mřížky.

        Returns:
            imagehash.ImageHash: Vypočítaný hash.

        Raises:
            ValueError: Pokud algoritmus není podporován.
        """
        if algorithm == 'phash':
            return imagehash.phash(image, hash_size=hash_size)
        elif algorithm == 'dhash':
            return imagehash.dhash(image, hash_size=hash_size)
        else:
            raise ValueError(
                f"Unsupported algorithm: {algorithm}. "
                f"Supported algorithms: 'phash', 'dhash'."
            )

    def _create_diff_mask(
        self,
        baseline_img: Image.Image,
        current_img: Image.Image,
        pixel_tolerance: int,
        element_fill_expansion: int = 15
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """Create binary masks and color difference arrays for directional diff detection.

        Args:
            baseline_img: Baseline PIL Image (RGB).
            current_img: Current PIL Image (RGB).
            pixel_tolerance: Threshold for marking pixel as different.
            element_fill_expansion: Kernel size for morphological dilation to fill element interiors.
                                    Set to 0 to disable. Default: 15.

        Returns:
            Tuple of (binary_mask, added_pixels_mask, removed_pixels_mask, color_diff_array, baseline_array, current_array)
            - binary_mask: uint8 array, 255=different, 0=same (all changes)
            - added_pixels_mask: uint8 array, 255=new pixels in current, 0=not new
            - removed_pixels_mask: uint8 array, 255=old pixels from baseline, 0=not old
            - color_diff_array: float array of per-pixel color differences
            - baseline_array: numpy array of baseline image
            - current_array: numpy array of current image

        ---

        Vytvoří binární masky a pole barevných rozdílů pro směrovou detekci změn.

        Args:
            baseline_img: Baseline PIL Image (RGB).
            current_img: Aktuální PIL Image (RGB).
            pixel_tolerance: Práh pro označení pixelu jako odlišný.
            element_fill_expansion: Velikost kernelu pro morfologickou dilataci k vyplnění vnitřků elementů.
                                    Nastavte na 0 pro deaktivaci. Výchozí: 15.

        Returns:
            Tuple (binary_mask, added_pixels_mask, removed_pixels_mask, color_diff_array, baseline_array, current_array)
            - binary_mask: uint8 pole, 255=odlišný, 0=stejný (všechny změny)
            - added_pixels_mask: uint8 pole, 255=nové pixely v current, 0=ne nové
            - removed_pixels_mask: uint8 pole, 255=staré pixely z baseline, 0=ne staré
            - color_diff_array: float pole barevných rozdílů pro každý pixel
            - baseline_array: numpy pole baseline obrázku
            - current_array: numpy pole current obrázku
        """
        # Convert PIL images to numpy arrays (RGB)
        baseline_array = np.array(baseline_img)
        current_array = np.array(current_img)

        # Calculate per-pixel color difference (Manhattan distance in RGB space)
        # Shape: (height, width, 3) -> (height, width)
        color_diff_array = np.sum(
            np.abs(baseline_array.astype(np.float32) - current_array.astype(np.float32)),
            axis=2
        ) / 3.0  # Average across RGB channels

        # Create binary mask: 255 where difference > tolerance, 0 otherwise
        binary_mask = np.where(
            color_diff_array > pixel_tolerance,
            255,
            0
        ).astype(np.uint8)

        # Calculate pixel intensity (sum of RGB channels) to detect directionality
        # Higher intensity = darker/more colorful pixels (e.g., element borders)
        # Lower intensity = lighter/less colorful pixels (e.g., white background)
        baseline_intensity = np.sum(baseline_array.astype(np.float32), axis=2)
        current_intensity = np.sum(current_array.astype(np.float32), axis=2)

        # Added pixels: pixels that became darker/more intense in current
        # (e.g., new element borders appeared where there was background)
        added_edges_mask = np.where(
            (color_diff_array > pixel_tolerance) & (current_intensity < baseline_intensity),
            255,
            0
        ).astype(np.uint8)

        # Removed pixels: pixels that became lighter/less intense in current
        # (e.g., old element borders disappeared and became background)
        removed_edges_mask = np.where(
            (color_diff_array > pixel_tolerance) & (baseline_intensity < current_intensity),
            255,
            0
        ).astype(np.uint8)

        # Apply morphological dilation to fill element interiors (if enabled)
        if element_fill_expansion > 0:
            # Create elliptical kernel for dilation
            dilation_kernel = cv2.getStructuringElement(
                cv2.MORPH_ELLIPSE,
                (element_fill_expansion, element_fill_expansion)
            )

            # Dilate added edges to fill element interiors
            added_pixels_mask = cv2.dilate(added_edges_mask, dilation_kernel, iterations=1)

            # Constrain to pixels where there's at least some color change
            # This prevents over-expansion into completely unchanged areas
            added_pixels_mask = np.where(
                (added_pixels_mask == 255) & (color_diff_array > pixel_tolerance * 0.5),
                255,
                0
            ).astype(np.uint8)

            # Dilate removed edges similarly
            removed_pixels_mask = cv2.dilate(removed_edges_mask, dilation_kernel, iterations=1)
            removed_pixels_mask = np.where(
                (removed_pixels_mask == 255) & (color_diff_array > pixel_tolerance * 0.5),
                255,
                0
            ).astype(np.uint8)
        else:
            # No dilation - use edge masks as-is
            added_pixels_mask = added_edges_mask
            removed_pixels_mask = removed_edges_mask

        return binary_mask, added_pixels_mask, removed_pixels_mask, color_diff_array, baseline_array, current_array

    def _find_contours(
        self,
        diff_mask: np.ndarray,
        min_contour_area: int = 5000
    ) -> list:
        """Find contours in difference mask using OpenCV with minimal preprocessing.

        Args:
            diff_mask: Binary mask (uint8, 255=diff, 0=same).
            min_contour_area: Minimum contour area to keep (filters small changes). Default: 5000.

        Returns:
            List of contours (OpenCV format).

        ---

        Najde kontury v masce rozdílů pomocí OpenCV s minimálním preprocessingem.

        Args:
            diff_mask: Binární maska (uint8, 255=rozdíl, 0=stejné).
            min_contour_area: Minimální plocha kontury (filtruje malé změny). Výchozí: 5000.

        Returns:
            Seznam kontur (OpenCV formát).
        """
        # Preprocessing: Apply minimal morphological operations
        # Small kernel to fill tiny holes without aggressive expansion
        kernel_close = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))

        # Close small holes in the mask
        mask_processed = cv2.morphologyEx(diff_mask, cv2.MORPH_CLOSE, kernel_close)

        # NO dilate - we don't want to expand contours and merge separate regions

        # Find contours in the processed binary mask
        # RETR_EXTERNAL = retrieve only outermost contours (ignore nested)
        # CHAIN_APPROX_SIMPLE = compress contours (store only corners)
        contours, _ = cv2.findContours(
            mask_processed,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )

        # Filter out small contours (e.g., input fields with slightly changed colors)
        filtered_contours = [
            contour for contour in contours
            if cv2.contourArea(contour) >= min_contour_area
        ]

        return filtered_contours

    def _classify_diff_severity(
        self,
        color_diff: float,
        pixel_tolerance: int,
        minor_threshold_multiplier: float = 1.5,
        moderate_threshold_multiplier: float = 3.0
    ) -> Literal['minor', 'moderate', 'severe']:
        """Classify difference severity based on color difference.

        Args:
            color_diff: Color difference value (0-765 range).
            pixel_tolerance: Base tolerance threshold.
            minor_threshold_multiplier: Multiplier for minor/moderate boundary.
            moderate_threshold_multiplier: Multiplier for moderate/severe boundary.

        Returns:
            Severity level: 'minor', 'moderate', or 'severe'.

        ---

        Klasifikuje závažnost rozdílu pro barevné kódování.

        Args:
            color_diff: Hodnota barevného rozdílu (rozsah 0-765).
            pixel_tolerance: Základní práh tolerance.
            minor_threshold_multiplier: Násobitel pro hranici minor/moderate.
            moderate_threshold_multiplier: Násobitel pro hranici moderate/severe.

        Returns:
            Úroveň závažnosti: 'minor', 'moderate', nebo 'severe'.
        """
        if color_diff <= pixel_tolerance * minor_threshold_multiplier:
            return 'minor'  # green
        elif color_diff <= pixel_tolerance * moderate_threshold_multiplier:
            return 'moderate'  # yellow
        else:
            return 'severe'  # red

    def _draw_contours_on_diff(
        self,
        baseline_array: np.ndarray,
        current_array: np.ndarray,
        contours: list,
        color_diff_array: np.ndarray,
        pixel_tolerance: int,
        diff_mask: np.ndarray,
        contour_thickness: int = 3,
        minor_color: Tuple[int, int, int] = (0, 255, 0),
        moderate_color: Tuple[int, int, int] = (0, 255, 255),
        severe_color: Tuple[int, int, int] = (0, 0, 255),
        enable_color_coding: bool = True,
        diff_base_image: Literal['baseline', 'current'] = 'baseline'
    ) -> np.ndarray:
        """Draw contours on chosen base image (baseline or current) with semi-transparent fill and outlines.

        Args:
            baseline_array: Numpy array of baseline image (RGB).
            current_array: Numpy array of current image (RGB).
            contours: List of contours from cv2.findContours().
            color_diff_array: Array of per-pixel color differences.
            pixel_tolerance: Base tolerance for severity classification.
            diff_mask: Binary mask of differences.
            contour_thickness: Thickness of contour lines in pixels. Default: 3.
            minor_color: RGB color for minor differences (default: green).
            moderate_color: RGB color for moderate differences (default: yellow).
            severe_color: RGB color for severe differences (default: red).
            enable_color_coding: If False, use only severe_color for all contours.
            diff_base_image: Which image to use as visual base. 'baseline' or 'current'. Default: 'baseline'.

        Returns:
            Numpy array of diff image with filled contours and outlines (RGB).

        ---

        Vykreslí kontury na zvoleném základním obrázku (baseline nebo current) s poloprůhlednou výplní a obrysem.

        Args:
            baseline_array: Numpy pole baseline obrázku (RGB).
            current_array: Numpy pole current obrázku (RGB).
            contours: Seznam kontur z cv2.findContours().
            color_diff_array: Pole barevných rozdílů pro každý pixel.
            pixel_tolerance: Základní tolerance pro klasifikaci závažnosti.
            diff_mask: Binární maska rozdílů.
            contour_thickness: Tloušťka linií kontury v pixelech. Výchozí: 3.
            minor_color: RGB barva pro menší rozdíly (výchozí: zelená).
            moderate_color: RGB barva pro střední rozdíly (výchozí: žlutá).
            severe_color: RGB barva pro velké rozdíly (výchozí: červená).
            enable_color_coding: Pokud False, použije se pouze severe_color pro všechny kontury.
            diff_base_image: Který obrázek použít jako vizuální základ. 'baseline' nebo 'current'. Výchozí: 'baseline'.

        Returns:
            Numpy pole diff obrázku s vyplněnými konturami a obrysem (RGB).
        """
        # Choose which image to use as visual base for diff
        base_image_array = current_array if diff_base_image == 'current' else baseline_array

        # Create copy of chosen base for diff image
        diff_image = base_image_array.copy()

        # Create overlay for semi-transparent fill
        overlay = base_image_array.copy()

        # Color mapping for severity levels
        color_map = {
            'minor': minor_color,
            'moderate': moderate_color,
            'severe': severe_color
        }

        # PASS 1: Draw filled contours on overlay
        for contour in contours:
            if enable_color_coding:
                # Calculate average color difference within this contour
                # Create mask for this specific contour
                contour_mask = np.zeros(diff_mask.shape, dtype=np.uint8)
                cv2.drawContours(contour_mask, [contour], 0, 255, -1)  # Fill the contour

                # Get pixels within this contour
                contour_pixels_mask = (contour_mask == 255) & (diff_mask == 255)

                if np.any(contour_pixels_mask):
                    # Calculate average color difference for pixels in this contour
                    avg_color_diff = np.mean(color_diff_array[contour_pixels_mask])

                    # Classify severity
                    severity = self._classify_diff_severity(avg_color_diff, pixel_tolerance)
                    color = color_map[severity]
                else:
                    # Fallback if no pixels found (shouldn't happen)
                    color = severe_color
            else:
                # Single color mode (typically red)
                color = severe_color

            # OpenCV uses BGR, but we work in RGB
            # Convert RGB to BGR for OpenCV drawing
            bgr_color = (color[2], color[1], color[0])

            # Draw filled contour on overlay
            cv2.drawContours(
                overlay,
                [contour],
                -1,
                bgr_color,
                -1  # -1 = fill the contour
            )

        # Blend overlay with baseline image (30% filled areas, 70% baseline)
        alpha = 0.3
        diff_image = cv2.addWeighted(overlay, alpha, diff_image, 1 - alpha, 0)

        # PASS 2: Draw contour outlines on top for clear boundaries
        for contour in contours:
            if enable_color_coding:
                # Recalculate color for this contour
                contour_mask = np.zeros(diff_mask.shape, dtype=np.uint8)
                cv2.drawContours(contour_mask, [contour], 0, 255, -1)
                contour_pixels_mask = (contour_mask == 255) & (diff_mask == 255)

                if np.any(contour_pixels_mask):
                    avg_color_diff = np.mean(color_diff_array[contour_pixels_mask])
                    severity = self._classify_diff_severity(avg_color_diff, pixel_tolerance)
                    color = color_map[severity]
                else:
                    color = severe_color
            else:
                color = severe_color

            bgr_color = (color[2], color[1], color[0])

            # Draw contour outline with anti-aliasing
            cv2.drawContours(
                diff_image,
                [contour],
                -1,
                bgr_color,
                contour_thickness,
                cv2.LINE_AA  # Anti-aliased lines for smooth appearance
            )

        return diff_image

    def _calculate_statistics(
        self,
        diff_mask: np.ndarray,
        color_diff_array: np.ndarray,
        contours: list,
        pixel_tolerance: int
    ) -> DiffStatistics:
        """Calculate comprehensive statistics from diff analysis.

        Args:
            diff_mask: Binary mask of differences.
            color_diff_array: Array of per-pixel color differences.
            contours: List of detected contours.
            pixel_tolerance: Tolerance threshold.

        Returns:
            DiffStatistics object with comprehensive metrics.

        ---

        Vypočítá komplexní statistiky z diff analýzy.

        Args:
            diff_mask: Binární maska rozdílů.
            color_diff_array: Pole barevných rozdílů pro každý pixel.
            contours: Seznam detekovaných kontur.
            pixel_tolerance: Práh tolerance.

        Returns:
            DiffStatistics objekt s komplexními metrikami.
        """
        # Total pixels in image
        total_pixels = diff_mask.size

        # Count different pixels
        different_pixels = int(np.count_nonzero(diff_mask))

        # Calculate percentage
        difference_percentage = (different_pixels / total_pixels * 100.0) if total_pixels > 0 else 0.0

        # Count severity levels
        minor_count = 0
        moderate_count = 0
        severe_count = 0

        if different_pixels > 0:
            # Get only the different pixels' color differences
            diff_pixels_mask = diff_mask == 255
            diff_color_values = color_diff_array[diff_pixels_mask]

            # Classify each different pixel
            for color_diff in diff_color_values:
                severity = self._classify_diff_severity(color_diff, pixel_tolerance)
                if severity == 'minor':
                    minor_count += 1
                elif severity == 'moderate':
                    moderate_count += 1
                else:  # severe
                    severe_count += 1

            # Calculate average color difference
            average_color_difference = float(np.mean(diff_color_values))
        else:
            average_color_difference = 0.0

        # Count contours
        num_contours = len(contours)

        # Find largest contour area
        if num_contours > 0:
            largest_contour_area = int(max(cv2.contourArea(c) for c in contours))
        else:
            largest_contour_area = 0

        return DiffStatistics(
            total_pixels=total_pixels,
            different_pixels=different_pixels,
            difference_percentage=difference_percentage,
            minor_diff_pixels=minor_count,
            moderate_diff_pixels=moderate_count,
            severe_diff_pixels=severe_count,
            num_contours=num_contours,
            largest_contour_area=largest_contour_area,
            average_color_difference=average_color_difference
        )

    def _log_statistics(self, stats: DiffStatistics) -> None:
        """Log diff statistics to Robot Framework logger.

        Args:
            stats: DiffStatistics object.

        ---

        Zaloguje statistiky diffu do Robot Framework loggeru.

        Args:
            stats: DiffStatistics objekt.
        """
        logger.info("=== Image Comparison Statistics ===")
        logger.info(f"Total pixels: {stats.total_pixels:,}")
        logger.info(f"Different pixels: {stats.different_pixels:,} ({stats.difference_percentage:.2f}%)")
        logger.info(f"  - Minor differences (green): {stats.minor_diff_pixels:,}")
        logger.info(f"  - Moderate differences (yellow): {stats.moderate_diff_pixels:,}")
        logger.info(f"  - Severe differences (red): {stats.severe_diff_pixels:,}")
        logger.info(f"Number of contours detected: {stats.num_contours}")
        if stats.num_contours > 0:
            logger.info(f"Largest contour area: {stats.largest_contour_area:,} pixels")
        logger.info(f"Average color difference: {stats.average_color_difference:.2f}")

    def _generate_html_report(
        self,
        baseline_path: str,
        current_path: str,
        diff_path: Path,
        stats: DiffStatistics,
        distance: int,
        tolerance: int,
        algorithm: str
    ) -> Path:
        """Generate HTML report with side-by-side comparison.

        Args:
            baseline_path: Path to baseline image.
            current_path: Path to current image.
            diff_path: Path to saved diff image.
            stats: DiffStatistics object.
            distance: Hamming distance.
            tolerance: Tolerance threshold.
            algorithm: Hash algorithm used.

        Returns:
            Path to HTML report.

        ---

        Vygeneruje HTML report s porovnáním vedle sebe.

        Args:
            baseline_path: Cesta k baseline obrázku.
            current_path: Cesta k aktuálnímu obrázku.
            diff_path: Cesta k uloženému diff obrázku.
            stats: DiffStatistics objekt.
            distance: Hammingova vzdálenost.
            tolerance: Práh tolerance.
            algorithm: Použitý hashovací algoritmus.

        Returns:
            Cesta k HTML reportu.
        """
        # Generate HTML report filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        html_filename = f"comparison_report_{timestamp}.html"
        html_path = diff_path.parent / html_filename

        # Get relative paths for embedding in HTML
        baseline_rel = Path(baseline_path).name
        current_rel = Path(current_path).name
        diff_rel = diff_path.name

        # Create HTML content
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Image Comparison Report - {timestamp}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #333;
            border-bottom: 3px solid #4CAF50;
            padding-bottom: 10px;
        }}
        .image-grid {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 20px;
            margin: 20px 0;
        }}
        .image-panel {{
            text-align: center;
        }}
        .image-panel img {{
            max-width: 100%;
            border: 1px solid #ddd;
            border-radius: 4px;
        }}
        .image-panel h3 {{
            margin-top: 10px;
            color: #555;
        }}
        .stats-table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        .stats-table th, .stats-table td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        .stats-table th {{
            background-color: #4CAF50;
            color: white;
        }}
        .stats-table tr:hover {{
            background-color: #f5f5f5;
        }}
        .legend {{
            display: flex;
            justify-content: center;
            gap: 30px;
            margin: 20px 0;
            padding: 15px;
            background-color: #f9f9f9;
            border-radius: 4px;
        }}
        .legend-item {{
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        .legend-color {{
            width: 30px;
            height: 30px;
            border: 1px solid #333;
            border-radius: 4px;
        }}
        .timestamp {{
            text-align: right;
            color: #888;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Image Comparison Report</h1>
        <p class="timestamp">Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>

        <div class="image-grid">
            <div class="image-panel">
                <h3>Baseline Image</h3>
                <img src="{baseline_path}" alt="Baseline">
                <p><small>{baseline_rel}</small></p>
            </div>
            <div class="image-panel">
                <h3>Current Image</h3>
                <img src="{current_path}" alt="Current">
                <p><small>{current_rel}</small></p>
            </div>
            <div class="image-panel">
                <h3>Diff Image</h3>
                <img src="{diff_rel}" alt="Diff">
                <p><small>{diff_rel}</small></p>
            </div>
        </div>

        <div class="legend">
            <div class="legend-item">
                <div class="legend-color" style="background-color: rgb(0, 255, 0);"></div>
                <span>Minor Differences</span>
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background-color: rgb(0, 255, 255);"></div>
                <span>Moderate Differences</span>
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background-color: rgb(0, 0, 255);"></div>
                <span>Severe Differences</span>
            </div>
        </div>

        <h2>Hash Comparison</h2>
        <table class="stats-table">
            <tr>
                <th>Metric</th>
                <th>Value</th>
            </tr>
            <tr>
                <td>Algorithm</td>
                <td>{algorithm}</td>
            </tr>
            <tr>
                <td>Hamming Distance</td>
                <td>{distance}</td>
            </tr>
            <tr>
                <td>Tolerance Threshold</td>
                <td>{tolerance}</td>
            </tr>
            <tr>
                <td>Result</td>
                <td>{'<span style="color: red; font-weight: bold;">FAILED</span>' if distance > tolerance else '<span style="color: green; font-weight: bold;">PASSED</span>'}</td>
            </tr>
        </table>

        <h2>Pixel-Level Statistics</h2>
        <table class="stats-table">
            <tr>
                <th>Metric</th>
                <th>Value</th>
            </tr>
            <tr>
                <td>Total Pixels</td>
                <td>{stats.total_pixels:,}</td>
            </tr>
            <tr>
                <td>Different Pixels</td>
                <td>{stats.different_pixels:,} ({stats.difference_percentage:.2f}%)</td>
            </tr>
            <tr>
                <td>Minor Differences (Green)</td>
                <td>{stats.minor_diff_pixels:,}</td>
            </tr>
            <tr>
                <td>Moderate Differences (Yellow)</td>
                <td>{stats.moderate_diff_pixels:,}</td>
            </tr>
            <tr>
                <td>Severe Differences (Red)</td>
                <td>{stats.severe_diff_pixels:,}</td>
            </tr>
            <tr>
                <td>Number of Contours</td>
                <td>{stats.num_contours}</td>
            </tr>
            <tr>
                <td>Largest Contour Area</td>
                <td>{stats.largest_contour_area:,} pixels</td>
            </tr>
            <tr>
                <td>Average Color Difference</td>
                <td>{stats.average_color_difference:.2f}</td>
            </tr>
        </table>
    </div>
</body>
</html>"""

        # Write HTML file
        html_path.write_text(html_content, encoding='utf-8')

        return html_path

    def _generate_visual_diff(
        self,
        baseline_img: Image.Image,
        current_img: Image.Image,
        diff_directory: Union[str, Path],
        pixel_tolerance: int,
        # NEW PARAMETERS with defaults for backwards compatibility
        diff_mode: Literal['filled', 'contours'] = 'contours',
        contour_thickness: int = 2,
        min_contour_area: int = 100,
        minor_color: Tuple[int, int, int] = (0, 255, 0),
        moderate_color: Tuple[int, int, int] = (0, 255, 255),
        severe_color: Tuple[int, int, int] = (0, 0, 255),
        enable_color_coding: bool = False,
        log_statistics: bool = True,
        generate_html: bool = False,
        embed_images_to_log: bool = True,
        add_timestamp: bool = True,
        diff_base_image: Literal['baseline', 'current'] = 'baseline',
        highlight_mode: Literal['all', 'added', 'removed'] = 'all',
        element_fill_expansion: int = 15,
        baseline_path_for_html: Optional[str] = None,
        current_path_for_html: Optional[str] = None,
        hash_distance_for_html: Optional[int] = None,
        tolerance_for_html: Optional[int] = None,
        algorithm_for_html: Optional[str] = None
    ) -> Tuple[Path, DiffStatistics]:
        """Generate a visual diff image highlighting differences.

        Args:
            baseline_img: Baseline PIL Image.
            current_img: Current PIL Image.
            diff_directory: Directory to save the diff image.
            pixel_tolerance: Color difference tolerance (0-255).
            diff_mode: Diff visualization mode: 'filled' (old) or 'contours' (new).
            contour_thickness: Thickness of contour lines in pixels (for contours mode).
            min_contour_area: Minimum contour area to keep (filters noise).
            minor_color: RGB color for minor differences (default: green).
            moderate_color: RGB color for moderate differences (default: yellow).
            severe_color: RGB color for severe differences (default: red).
            enable_color_coding: If False, use only severe_color for all changes.
            log_statistics: If True, log statistics to Robot Framework logger.
            generate_html: If True, generate HTML report.
            embed_images_to_log: If True, embed baseline and diff images to RF log.html as base64.
            add_timestamp: If True, add timestamp to diff image (bottom-right corner). Default: True.
            baseline_path_for_html: Baseline image path for HTML report.
            current_path_for_html: Current image path for HTML report.
            hash_distance_for_html: Hash distance for HTML report.
            tolerance_for_html: Tolerance threshold for HTML report.
            algorithm_for_html: Algorithm name for HTML report.

        Returns:
            Tuple[Path, DiffStatistics]: Path to saved diff image and statistics object.

        ---

        Vygeneruje vizuální diff obrázek zvýrazňující rozdíly.

        Args:
            baseline_img: Baseline PIL Image.
            current_img: Aktuální PIL Image.
            diff_directory: Adresář pro uložení diff obrázku.
            pixel_tolerance: Tolerance barevného rozdílu (0-255).
            diff_mode: Režim vizualizace: 'filled' (starý) nebo 'contours' (nový).
            contour_thickness: Tloušťka linií kontur v pixelech (pro contours režim).
            min_contour_area: Minimální plocha kontury (filtruje šum).
            minor_color: RGB barva pro menší rozdíly (výchozí: zelená).
            moderate_color: RGB barva pro střední rozdíly (výchozí: žlutá).
            severe_color: RGB barva pro velké rozdíly (výchozí: červená).
            enable_color_coding: Pokud False, použije se pouze severe_color.
            log_statistics: Pokud True, zaloguje statistiky do RF loggeru.
            generate_html: Pokud True, vygeneruje HTML report.
            embed_images_to_log: Pokud True, embeduje baseline a diff obrázky do RF log.html jako base64.
            add_timestamp: Pokud True, přidá timestamp do diff obrázku (pravý dolní roh). Výchozí: True.
            baseline_path_for_html: Cesta k baseline obrázku pro HTML report.
            current_path_for_html: Cesta k aktuálnímu obrázku pro HTML report.
            hash_distance_for_html: Hash vzdálenost pro HTML report.
            tolerance_for_html: Práh tolerance pro HTML report.
            algorithm_for_html: Název algoritmu pro HTML report.

        Returns:
            Tuple[Path, DiffStatistics]: Cesta k diff obrázku a statistiky.
        """
        # Ensure diff directory exists
        diff_dir = Path(diff_directory)
        diff_dir.mkdir(parents=True, exist_ok=True)

        # Convert images to RGB if needed (required for consistent pixel comparison)
        if baseline_img.mode != 'RGB':
            baseline_img = baseline_img.convert('RGB')
        if current_img.mode != 'RGB':
            current_img = current_img.convert('RGB')

        # Create diff masks and calculate pixel differences
        binary_mask, added_pixels_mask, removed_pixels_mask, color_diff_array, baseline_array, current_array = self._create_diff_mask(
            baseline_img,
            current_img,
            pixel_tolerance,
            element_fill_expansion
        )

        # Select appropriate mask based on highlight_mode
        if highlight_mode == 'added':
            diff_mask = added_pixels_mask
        elif highlight_mode == 'removed':
            diff_mask = removed_pixels_mask
        else:  # 'all'
            diff_mask = binary_mask

        # Find contours (for both modes, needed for statistics)
        contours = self._find_contours(diff_mask, min_contour_area)

        # Calculate statistics
        stats = self._calculate_statistics(
            diff_mask,
            color_diff_array,
            contours,
            pixel_tolerance
        )

        # Log statistics if requested
        if log_statistics:
            self._log_statistics(stats)

        # Generate diff visualization based on mode
        if diff_mode == 'filled':
            # OLD MODE: Filled red pixels (backwards compatibility)
            diff_img = baseline_img.copy()
            diff_pixels = diff_img.load()

            baseline_pixels = baseline_img.load()
            current_pixels = current_img.load()

            width, height = baseline_img.size

            # Compare pixels and mark differences in red
            for y in range(height):
                for x in range(width):
                    baseline_pixel = baseline_pixels[x, y]
                    current_pixel = current_pixels[x, y]

                    # Calculate color difference (simple Manhattan distance)
                    color_diff = sum(
                        abs(baseline_pixel[i] - current_pixel[i])
                        for i in range(3)
                    ) / 3

                    # Mark pixel as different if it exceeds tolerance
                    if color_diff > pixel_tolerance:
                        diff_pixels[x, y] = severe_color  # Use parameter color

        elif diff_mode == 'contours':
            # NEW MODE: Contour outlines with optional color coding
            diff_array = self._draw_contours_on_diff(
                baseline_array,
                current_array,
                contours,
                color_diff_array,
                pixel_tolerance,
                diff_mask,
                contour_thickness,
                minor_color,
                moderate_color,
                severe_color,
                enable_color_coding,
                diff_base_image
            )

            # Convert numpy array back to PIL Image
            diff_img = Image.fromarray(diff_array.astype(np.uint8))

        else:
            raise ValueError(
                f"Unsupported diff_mode: {diff_mode}. "
                f"Supported modes: 'filled', 'contours'."
            )

        # Generate unique filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        diff_filename = f"diff_{timestamp}.png"
        diff_path = diff_dir / diff_filename

        # Add timestamp overlay to diff image if requested
        if add_timestamp:
            timestamp_str = datetime.now().strftime("%d/%m/%y %H:%M:%S")
            diff_img = self._add_timestamp_to_image(diff_img, timestamp_str)

        # Save diff image
        diff_img.save(diff_path)

        # Embed images to Robot Framework log if requested
        if embed_images_to_log:
            self._log_images_to_html(baseline_img, current_img, diff_path)

        # Generate HTML report if requested
        if generate_html and all([
            baseline_path_for_html,
            current_path_for_html,
            hash_distance_for_html is not None,
            tolerance_for_html is not None,
            algorithm_for_html
        ]):
            html_path = self._generate_html_report(
                baseline_path_for_html,
                current_path_for_html,
                diff_path,
                stats,
                hash_distance_for_html,
                tolerance_for_html,
                algorithm_for_html
            )
            logger.info(f"HTML report generated: {html_path}")

        return diff_path, stats
    
    def _get_image_path(self, image: Union[str, Path, Image.Image]) -> str:
        """Get string representation of image path for error messages.

        Args:
            image: Image as str path, pathlib.Path, or PIL.Image.Image.

        Returns:
            str: String representation of the image path.

        ---

        Získá řetězcovou reprezentaci cesty k obrázku pro chybové zprávy.

        Args:
            image: Obrázek jako str cesta, pathlib.Path, nebo PIL.Image.Image.

        Returns:
            str: Řetězcová reprezentace cesty k obrázku.
        """
        if isinstance(image, (str, Path)):
            return str(Path(image).resolve())
        elif isinstance(image, Image.Image):
            # If it's a PIL Image, check if it has a filename attribute
            if hasattr(image, 'filename') and image.filename:
                return str(Path(image.filename).resolve())
            else:
                return "<PIL Image object in memory>"
        else:
            return str(image)

    def _encode_image_to_base64(self, image: Union[Path, Image.Image]) -> str:
        """Encode image to base64 data URI for HTML embedding.

        Args:
            image: Image as Path or PIL.Image.Image.

        Returns:
            str: Data URI string (data:image/png;base64,...)

        ---

        Enkóduje obrázek do base64 data URI pro HTML embedding.

        Args:
            image: Obrázek jako Path nebo PIL.Image.Image.

        Returns:
            str: Data URI řetězec (data:image/png;base64,...)
        """
        import base64
        from io import BytesIO

        # Load image if it's a Path
        if isinstance(image, Path):
            img = Image.open(image)
        else:
            img = image

        # Convert to RGB if needed
        if img.mode not in ('RGB', 'RGBA'):
            img = img.convert('RGB')

        # Encode to base64
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        img_bytes = buffer.getvalue()
        img_base64 = base64.b64encode(img_bytes).decode('utf-8')

        return f"data:image/png;base64,{img_base64}"

    def _log_images_to_html(
        self,
        baseline_img: Image.Image,
        current_img: Image.Image,
        diff_path: Path
    ) -> None:
        """Log baseline, current, and diff images as HTML table to Robot Framework log.

        Creates an HTML table with baseline and diff images side-by-side on top row,
        and current screenshot on bottom row. All images are embedded as base64 data URIs
        for direct viewing in log.html.

        Args:
            baseline_img: Baseline PIL Image.
            current_img: Current PIL Image.
            diff_path: Path to saved diff image.

        ---

        Zaloguje baseline, aktuální a diff obrázky jako HTML tabulku do Robot Framework logu.

        Vytvoří HTML tabulku s baseline a diff obrázky vedle sebe v horním řádku,
        a aktuálním screenshotem v dolním řádku. Všechny obrázky jsou enkódovány
        jako base64 data URI pro přímé zobrazení v log.html.

        Args:
            baseline_img: Baseline PIL Image.
            current_img: Aktuální PIL Image.
            diff_path: Cesta k uloženému diff obrázku.
        """
        # Encode images to base64
        baseline_base64 = self._encode_image_to_base64(baseline_img)
        current_base64 = self._encode_image_to_base64(current_img)
        diff_base64 = self._encode_image_to_base64(diff_path)

        # Create HTML table with baseline and diff on top, current screenshot on bottom
        html_content = f"""
<table style="width:100%; border-collapse: collapse; margin-top: 10px;">
  <tr>
    <th style="text-align:center; padding:10px; background-color:#f0f0f0; border:1px solid #ddd;">Baseline Image</th>
    <th style="text-align:center; padding:10px; background-color:#f0f0f0; border:1px solid #ddd;">Diff Image</th>
  </tr>
  <tr>
    <td style="padding:5px; text-align:center; border:1px solid #ddd;">
      <img src="{baseline_base64}" style="max-width:100%; height:auto; display:block; margin:auto;">
    </td>
    <td style="padding:5px; text-align:center; border:1px solid #ddd;">
      <img src="{diff_base64}" style="max-width:100%; height:auto; display:block; margin:auto;">
    </td>
  </tr>
  <tr>
    <th colspan="2" style="text-align:center; padding:10px; background-color:#f0f0f0; border:1px solid #ddd;">Current Screenshot</th>
  </tr>
  <tr>
    <td colspan="2" style="padding:5px; text-align:center; border:1px solid #ddd;">
      <img src="{current_base64}" style="max-width:100%; height:auto; display:block; margin:auto;">
    </td>
  </tr>
</table>
"""

        # Log HTML to Robot Framework log
        logger.info(html_content, html=True)

    def _add_timestamp_to_image(
        self,
        image: Image.Image,
        timestamp_text: str,
        padding: int = 10,
        font_size: int = 16
    ) -> Image.Image:
        """Add timestamp overlay to image (top-right corner).

        Adds timestamp text to the top-right corner of the image with
        red text and black shadow for readability on any background.

        Args:
            image: PIL Image to add timestamp to.
            timestamp_text: Timestamp string to display (e.g., "19/11/24 14:35:22").
            padding: Padding from image edges in pixels. Default: 10.
            font_size: Font size for timestamp text. Default: 16.

        Returns:
            PIL.Image.Image: Image with timestamp overlay.

        ---

        Přidá timestamp overlay do obrázku (pravý horní roh).

        Přidá timestamp text do pravého horního rohu obrázku s červeným textem
        a černým stínem pro čitelnost na jakémkoliv pozadí.

        Args:
            image: PIL Image pro přidání timestampu.
            timestamp_text: Timestamp řetězec k zobrazení (např. "19/11/24 14:35:22").
            padding: Odsazení od okrajů obrázku v pixelech. Výchozí: 10.
            font_size: Velikost fontu pro timestamp text. Výchozí: 16.

        Returns:
            PIL.Image.Image: Obrázek s timestamp overlay.
        """
        # Create drawing context
        draw = ImageDraw.Draw(image)

        # Try to load TrueType font, fallback to default
        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except (OSError, IOError):
            # Fallback to default font if Arial not available
            font = ImageFont.load_default()

        # Calculate text bounding box
        bbox = draw.textbbox((0, 0), timestamp_text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        # Position: top-right corner with padding
        img_width, img_height = image.size
        x = img_width - text_width - padding
        y = padding

        # Draw black shadow (4-direction offset for better contrast)
        shadow_offsets = [(1, 1), (-1, -1), (1, -1), (-1, 1)]
        for offset_x, offset_y in shadow_offsets:
            draw.text(
                (x + offset_x, y + offset_y),
                timestamp_text,
                font=font,
                fill=(0, 0, 0)  # Black shadow
            )

        # Draw red text on top
        draw.text((x, y), timestamp_text, font=font, fill=(255, 0, 0))

        return image
