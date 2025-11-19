"""Core implementation of ImageComparisonLibrary for Robot Framework.

Hlavní implementace ImageComparisonLibrary pro Robot Framework.
"""

from pathlib import Path
from typing import Union, Dict, Tuple, Optional, Literal
from datetime import datetime
from dataclasses import dataclass
import imagehash
from PIL import Image
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
    """Robot Framework library for image comparison and visual regression testing.

    This library provides keywords for comparing images using perceptual hashing
    and generating visual diff images when comparisons fail.

    ---

    Robot Framework knihovna pro porovnávání obrázků a vizuální regresní testování.

    Tato knihovna poskytuje klíčová slova pro porovnávání obrázků pomocí perceptual
    hashování a generování vizuálních diff obrázků při selhání porovnání.
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
        pixel_tolerance: int = 25,
        hash_size: int = 8,
        # NEW PARAMETERS for enhanced diff visualization
        diff_mode: Literal['filled', 'contours'] = 'contours',
        contour_thickness: int = 2,
        min_contour_area: int = 100,
        minor_color: Tuple[int, int, int] = (0, 255, 0),
        moderate_color: Tuple[int, int, int] = (0, 255, 255),
        severe_color: Tuple[int, int, int] = (0, 0, 255),
        enable_color_coding: bool = False,
        log_statistics: bool = True,
        generate_html: bool = False
    ) -> int:
        """Compare two images using perceptual hashing and generate diff on failure.

        This is the main, strictest keyword for regression testing. It compares
        the baseline image against the current image using the specified hashing
        algorithm. If the comparison fails (distance > tolerance), it generates
        a visual diff image highlighting the differences with contour outlines
        and optional color coding.

        Args:
            baseline_image: Reference image. Accepts str (path), pathlib.Path, or PIL.Image.Image.
            current_image: Current image to verify. Accepts str (path), pathlib.Path, or PIL.Image.Image.
            diff_directory: Directory path to save diff image on failure. Accepts str or pathlib.Path.
            algorithm: Hashing algorithm to use. Options: 'phash', 'dhash'. Default: 'phash'.
            tolerance: Maximum allowed Hamming distance. Default: 5.
            pixel_tolerance: Color difference tolerance (0-255) for visual diff generation. Default: 25.
            hash_size: Hash grid size. Default: 8.
            diff_mode: Diff visualization mode: 'contours' (new, default) or 'filled' (legacy). Default: 'contours'.
            contour_thickness: Thickness of contour lines in pixels (for contours mode). Default: 2.
            min_contour_area: Minimum contour area to keep, filters noise. Default: 100.
            minor_color: RGB tuple for minor differences (green). Default: (0, 255, 0).
            moderate_color: RGB tuple for moderate differences (yellow). Default: (0, 255, 255).
            severe_color: RGB tuple for severe differences (red). Default: (0, 0, 255).
            enable_color_coding: If False, use only severe_color for all changes. Default: False.
            log_statistics: If True, log detailed statistics to RF logger. Default: True.
            generate_html: If True, generate HTML report with side-by-side comparison. Default: False.

        Returns:
            int: The Hamming distance between the two images.

        Raises:
            AssertionError: If images differ beyond the allowed tolerance or have different dimensions.
            ValueError: If invalid algorithm or diff_mode is specified.

        ---

        Porovná dva obrázky pomocí perceptual hashování a vygeneruje diff při selhání.

        Toto je hlavní, nejpřísnější klíčové slovo pro regresní testování. Porovnává
        baseline obrázek s aktuálním obrázkem pomocí zadaného hashovacího algoritmu.
        Pokud porovnání selže (distance > tolerance), vygeneruje vizuální diff obrázek
        s obrysovými konturami a volitelným barevným kódováním.

        Args:
            baseline_image: Referenční obrázek. Akceptuje str (cestu), pathlib.Path, nebo PIL.Image.Image.
            current_image: Aktuální obrázek k ověření. Akceptuje str (cestu), pathlib.Path, nebo PIL.Image.Image.
            diff_directory: Cesta k adresáři pro uložení diff obrázku při selhání. Akceptuje str nebo pathlib.Path.
            algorithm: Hashovací algoritmus k použití. Možnosti: 'phash', 'dhash'. Výchozí: 'phash'.
            tolerance: Maximální povolená Hammingova vzdálenost. Výchozí: 5.
            pixel_tolerance: Tolerance barevného rozdílu (0-255) pro generování vizuálního diffu. Výchozí: 25.
            hash_size: Velikost hashovací mřížky. Výchozí: 8.
            diff_mode: Režim vizualizace: 'contours' (nový, výchozí) nebo 'filled' (legacy). Výchozí: 'contours'.
            contour_thickness: Tloušťka linií kontur v pixelech (pro contours režim). Výchozí: 2.
            min_contour_area: Minimální plocha kontury, filtruje šum. Výchozí: 100.
            minor_color: RGB tuple pro menší rozdíly (zelená). Výchozí: (0, 255, 0).
            moderate_color: RGB tuple pro střední rozdíly (žlutá). Výchozí: (0, 255, 255).
            severe_color: RGB tuple pro velké rozdíly (červená). Výchozí: (0, 0, 255).
            enable_color_coding: Pokud False, použije se pouze severe_color. Výchozí: False.
            log_statistics: Pokud True, zaloguje detailní statistiky do RF loggeru. Výchozí: True.
            generate_html: Pokud True, vygeneruje HTML report s porovnáním. Výchozí: False.

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
        pixel_tolerance: int = 25,
        hash_size: int = 8,
        # NEW PARAMETERS for enhanced diff visualization (same as compare_layouts_and_generate_diff)
        diff_mode: Literal['filled', 'contours'] = 'contours',
        contour_thickness: int = 2,
        min_contour_area: int = 100,
        minor_color: Tuple[int, int, int] = (0, 255, 0),
        moderate_color: Tuple[int, int, int] = (0, 255, 255),
        severe_color: Tuple[int, int, int] = (0, 0, 255),
        enable_color_coding: bool = False,
        log_statistics: bool = True,
        generate_html: bool = False
    ) -> int:
        """Check if two images are visually similar with relaxed tolerance.

        This is a less strict keyword for faster, coarser comparison. It internally
        calls compare_layouts_and_generate_diff with different default values
        (tolerance=15, algorithm='dhash').

        Args:
            baseline_image: Reference image. Accepts str (path), pathlib.Path, or PIL.Image.Image.
            current_image: Current image to verify. Accepts str (path), pathlib.Path, or PIL.Image.Image.
            diff_directory: Directory path to save diff image on failure. Accepts str or pathlib.Path.
            algorithm: Hashing algorithm to use. Default: 'dhash'.
            tolerance: Maximum allowed Hamming distance. Default: 15.
            pixel_tolerance: Color difference tolerance (0-255) for visual diff generation. Default: 25.
            hash_size: Hash grid size. Default: 8.
            diff_mode: Diff visualization mode: 'contours' (new, default) or 'filled' (legacy). Default: 'contours'.
            contour_thickness: Thickness of contour lines in pixels (for contours mode). Default: 2.
            min_contour_area: Minimum contour area to keep, filters noise. Default: 100.
            minor_color: RGB tuple for minor differences (green). Default: (0, 255, 0).
            moderate_color: RGB tuple for moderate differences (yellow). Default: (0, 255, 255).
            severe_color: RGB tuple for severe differences (red). Default: (0, 0, 255).
            enable_color_coding: If False, use only severe_color for all changes. Default: False.
            log_statistics: If True, log detailed statistics to RF logger. Default: True.
            generate_html: If True, generate HTML report with side-by-side comparison. Default: False.

        Returns:
            int: The Hamming distance between the two images.

        Raises:
            AssertionError: If images differ beyond the allowed tolerance or have different dimensions.

        ---

        Zkontroluje, zda jsou dva obrázky vizuálně podobné s uvolněnou tolerancí.

        Toto je méně přísné klíčové slovo pro rychlejší, hrubší porovnání. Interně
        volá compare_layouts_and_generate_diff s odlišnými výchozími hodnotami
        (tolerance=15, algorithm='dhash').

        Args:
            baseline_image: Referenční obrázek. Akceptuje str (cestu), pathlib.Path, nebo PIL.Image.Image.
            current_image: Aktuální obrázek k ověření. Akceptuje str (cestu), pathlib.Path, nebo PIL.Image.Image.
            diff_directory: Cesta k adresáři pro uložení diff obrázku při selhání. Akceptuje str nebo pathlib.Path.
            algorithm: Hashovací algoritmus k použití. Výchozí: 'dhash'.
            tolerance: Maximální povolená Hammingova vzdálenost. Výchozí: 15.
            pixel_tolerance: Tolerance barevného rozdílu (0-255) pro generování vizuálního diffu. Výchozí: 25.
            hash_size: Velikost hashovací mřížky. Výchozí: 8.
            diff_mode: Režim vizualizace: 'contours' (nový, výchozí) nebo 'filled' (legacy). Výchozí: 'contours'.
            contour_thickness: Tloušťka linií kontur v pixelech (pro contours režim). Výchozí: 2.
            min_contour_area: Minimální plocha kontury, filtruje šum. Výchozí: 100.
            minor_color: RGB tuple pro menší rozdíly (zelená). Výchozí: (0, 255, 0).
            moderate_color: RGB tuple pro střední rozdíly (žlutá). Výchozí: (0, 255, 255).
            severe_color: RGB tuple pro velké rozdíly (červená). Výchozí: (0, 0, 255).
            enable_color_coding: Pokud False, použije se pouze severe_color. Výchozí: False.
            log_statistics: Pokud True, zaloguje detailní statistiky do RF loggeru. Výchozí: True.
            generate_html: Pokud True, vygeneruje HTML report s porovnáním. Výchozí: False.

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
            generate_html=generate_html
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
        pixel_tolerance: int
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Create binary mask and color difference arrays.

        Args:
            baseline_img: Baseline PIL Image (RGB).
            current_img: Current PIL Image (RGB).
            pixel_tolerance: Threshold for marking pixel as different.

        Returns:
            Tuple of (binary_mask, color_diff_array, baseline_array)
            - binary_mask: uint8 array, 255=different, 0=same
            - color_diff_array: float array of per-pixel color differences
            - baseline_array: numpy array of baseline image

        ---

        Vytvoří binární masku rozdílů.

        Args:
            baseline_img: Baseline PIL Image (RGB).
            current_img: Aktuální PIL Image (RGB).
            pixel_tolerance: Práh pro označení pixelu jako odlišný.

        Returns:
            Tuple (binary_mask, color_diff_array, baseline_array)
            - binary_mask: uint8 pole, 255=odlišný, 0=stejný
            - color_diff_array: float pole barevných rozdílů pro každý pixel
            - baseline_array: numpy pole baseline obrázku
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

        return binary_mask, color_diff_array, baseline_array

    def _find_contours(
        self,
        diff_mask: np.ndarray,
        min_contour_area: int = 10
    ) -> list:
        """Find contours in difference mask using OpenCV.

        Args:
            diff_mask: Binary mask (uint8, 255=diff, 0=same).
            min_contour_area: Minimum contour area to keep (filters noise).

        Returns:
            List of contours (OpenCV format).

        ---

        Najde kontury v masce rozdílů pomocí OpenCV.

        Args:
            diff_mask: Binární maska (uint8, 255=rozdíl, 0=stejné).
            min_contour_area: Minimální plocha kontury (filtruje šum).

        Returns:
            Seznam kontur (OpenCV formát).
        """
        # Find contours in the binary mask
        # RETR_EXTERNAL = retrieve only outer contours
        # CHAIN_APPROX_SIMPLE = compress contours (store only corners)
        contours, _ = cv2.findContours(
            diff_mask,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )

        # Filter out small contours (noise)
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
        contours: list,
        color_diff_array: np.ndarray,
        pixel_tolerance: int,
        diff_mask: np.ndarray,
        contour_thickness: int = 2,
        minor_color: Tuple[int, int, int] = (0, 255, 0),
        moderate_color: Tuple[int, int, int] = (0, 255, 255),
        severe_color: Tuple[int, int, int] = (0, 0, 255),
        enable_color_coding: bool = True
    ) -> np.ndarray:
        """Draw contours on baseline image with severity-based coloring.

        Args:
            baseline_array: Numpy array of baseline image (RGB).
            contours: List of contours from cv2.findContours().
            color_diff_array: Array of per-pixel color differences.
            pixel_tolerance: Base tolerance for severity classification.
            diff_mask: Binary mask of differences.
            contour_thickness: Thickness of contour lines in pixels.
            minor_color: RGB color for minor differences (default: green).
            moderate_color: RGB color for moderate differences (default: yellow).
            severe_color: RGB color for severe differences (default: red).
            enable_color_coding: If False, use only severe_color for all contours.

        Returns:
            Numpy array of diff image with contours drawn (RGB).

        ---

        Vykreslí kontury na diff obrázek s barevným kódováním podle závažnosti.

        Args:
            baseline_array: Numpy pole baseline obrázku (RGB).
            contours: Seznam kontur z cv2.findContours().
            color_diff_array: Pole barevných rozdílů pro každý pixel.
            pixel_tolerance: Základní tolerance pro klasifikaci závažnosti.
            diff_mask: Binární maska rozdílů.
            contour_thickness: Tloušťka linií kontury v pixelech.
            minor_color: RGB barva pro menší rozdíly (výchozí: zelená).
            moderate_color: RGB barva pro střední rozdíly (výchozí: žlutá).
            severe_color: RGB barva pro velké rozdíly (výchozí: červená).
            enable_color_coding: Pokud False, použije se pouze severe_color pro všechny kontury.

        Returns:
            Numpy pole diff obrázku s nakreslenými konturami (RGB).
        """
        # Create copy of baseline for diff image
        diff_image = baseline_array.copy()

        # Color mapping for severity levels
        color_map = {
            'minor': minor_color,
            'moderate': moderate_color,
            'severe': severe_color
        }

        # Draw each contour with appropriate color
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

            # Draw contour outline
            cv2.drawContours(
                diff_image,
                [contour],
                -1,  # Draw all contours (we're passing one at a time)
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

        # Create diff mask and calculate pixel differences
        diff_mask, color_diff_array, baseline_array = self._create_diff_mask(
            baseline_img,
            current_img,
            pixel_tolerance
        )

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
                        diff_pixels[x, y] = (255, 0, 0)  # Red for differences

        elif diff_mode == 'contours':
            # NEW MODE: Contour outlines with optional color coding
            diff_array = self._draw_contours_on_diff(
                baseline_array,
                contours,
                color_diff_array,
                pixel_tolerance,
                diff_mask,
                contour_thickness,
                minor_color,
                moderate_color,
                severe_color,
                enable_color_coding
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

        # Save diff image
        diff_img.save(diff_path)

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
