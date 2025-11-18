"""Core implementation of ImageComparisonLibrary for Robot Framework."""

from pathlib import Path
from typing import Union
from datetime import datetime
import imagehash
from PIL import Image
from robot.api import logger


class ImageComparisonLibrary:
    """Robot Framework library for image comparison and visual regression testing.
    
    This library provides keywords for comparing images using perceptual hashing
    and generating visual diff images when comparisons fail.
    """
    
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'
    ROBOT_LIBRARY_VERSION = '1.0.0'
    
    def __init__(self):
        """Initialize the ImageComparisonLibrary."""
        pass
    
    def compare_layouts_and_generate_diff(
        self,
        baseline_image: Union[str, Path, Image.Image],
        current_image: Union[str, Path, Image.Image],
        diff_directory: Union[str, Path],
        algorithm: str = 'phash',
        tolerance: int = 5,
        pixel_tolerance: int = 10,
        hash_size: int = 8
    ) -> int:
        """Compare two images using perceptual hashing and generate diff on failure.
        
        This is the main, strictest keyword for regression testing. It compares
        the baseline image against the current image using the specified hashing
        algorithm. If the comparison fails (distance > tolerance), it generates
        a visual diff image highlighting the differences.
        
        Args:
            baseline_image: Reference image. Accepts str (path), pathlib.Path, or PIL.Image.Image.
            current_image: Current image to verify. Accepts str (path), pathlib.Path, or PIL.Image.Image.
            diff_directory: Directory path to save diff image on failure. Accepts str or pathlib.Path.
            algorithm: Hashing algorithm to use. Options: 'phash', 'dhash'. Default: 'phash'.
            tolerance: Maximum allowed Hamming distance. Default: 5.
            pixel_tolerance: Color difference tolerance (0-255) for visual diff generation. Default: 10.
            hash_size: Hash grid size. Default: 8.
            
        Returns:
            int: The Hamming distance between the two images.
            
        Raises:
            AssertionError: If images differ beyond the allowed tolerance or have different dimensions.
            ValueError: If invalid algorithm is specified.
            
        Examples:
            | Compare Layouts And Generate Diff | baseline.png | current.png | ${DIFF_DIR} |
            | Compare Layouts And Generate Diff | baseline.png | current.png | ${DIFF_DIR} | algorithm=dhash | tolerance=10 |
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
                f"Layouty jsou si podobné. Vzdálenost: {distance} (práh: {tolerance})."
            )
            return distance
        
        # Failure scenario - check dimensions first
        if baseline_img.size != current_img.size:
            raise AssertionError(
                f"Obrázky mají různé rozměry. "
                f"Baseline: {baseline_img.size}, Current: {current_img.size}"
            )
        
        # Generate visual diff
        diff_path = self._generate_visual_diff(
            baseline_img,
            current_img,
            diff_directory,
            pixel_tolerance
        )
        
        logger.info(f"Vizuální rozdíly byly uloženy do: {diff_path}")
        
        # Get paths for error message
        baseline_path = self._get_image_path(baseline_image)
        current_path = self._get_image_path(current_image)
        
        # Raise detailed error
        error_message = (
            f"Obrázky se liší nad povolenou toleranci!\n\n"
            f"Detaily porovnání:\n"
            f"  - Baseline obrázek: {baseline_path}\n"
            f"  - Aktuální obrázek: {current_path}\n"
            f"  - Použitý algoritmus: {algorithm} (hash_size={hash_size})\n"
            f"  - Hammingova vzdálenost: {distance}\n"
            f"  - Nastavená tolerance: {tolerance}\n\n"
            f"Vizuální rozdíly byly uloženy do: {diff_path}"
        )
        
        raise AssertionError(error_message)
    
    def check_layouts_are_visually_similar(
        self,
        baseline_image: Union[str, Path, Image.Image],
        current_image: Union[str, Path, Image.Image],
        diff_directory: Union[str, Path],
        algorithm: str = 'dhash',
        tolerance: int = 15,
        pixel_tolerance: int = 10,
        hash_size: int = 8
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
            pixel_tolerance: Color difference tolerance (0-255) for visual diff generation. Default: 10.
            hash_size: Hash grid size. Default: 8.
            
        Returns:
            int: The Hamming distance between the two images.
            
        Raises:
            AssertionError: If images differ beyond the allowed tolerance or have different dimensions.
            
        Examples:
            | Check Layouts Are Visually Similar | baseline.png | current.png | ${DIFF_DIR} |
            | Check Layouts Are Visually Similar | baseline.png | current.png | ${DIFF_DIR} | tolerance=20 |
        """
        return self.compare_layouts_and_generate_diff(
            baseline_image=baseline_image,
            current_image=current_image,
            diff_directory=diff_directory,
            algorithm=algorithm,
            tolerance=tolerance,
            pixel_tolerance=pixel_tolerance,
            hash_size=hash_size
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
    
    def _generate_visual_diff(
        self,
        baseline_img: Image.Image,
        current_img: Image.Image,
        diff_directory: Union[str, Path],
        pixel_tolerance: int
    ) -> Path:
        """Generate a visual diff image highlighting differences.
        
        Args:
            baseline_img: Baseline PIL Image.
            current_img: Current PIL Image.
            diff_directory: Directory to save the diff image.
            pixel_tolerance: Color difference tolerance (0-255).
            
        Returns:
            Path: Path to the saved diff image.
        """
        # Ensure diff directory exists
        diff_dir = Path(diff_directory)
        diff_dir.mkdir(parents=True, exist_ok=True)
        
        # Create diff image as copy of baseline
        diff_img = baseline_img.copy()
        diff_pixels = diff_img.load()
        
        # Convert images to RGB if needed
        if baseline_img.mode != 'RGB':
            baseline_img = baseline_img.convert('RGB')
        if current_img.mode != 'RGB':
            current_img = current_img.convert('RGB')
        
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
        
        # Generate unique filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        diff_filename = f"diff_{timestamp}.png"
        diff_path = diff_dir / diff_filename
        
        # Save diff image
        diff_img.save(diff_path)
        
        return diff_path
    
    def _get_image_path(self, image: Union[str, Path, Image.Image]) -> str:
        """Get string representation of image path for error messages.
        
        Args:
            image: Image as str path, pathlib.Path, or PIL.Image.Image.
            
        Returns:
            str: String representation of the image path.
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
