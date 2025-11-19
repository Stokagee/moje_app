"""Unit tests for ImageComparisonLibrary core functionality."""

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from PIL import Image
import sys
import os

# Add parent directory to path to import the library
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from ImageComparisonLibrary.core import ImageComparisonLibrary


class TestImageComparisonLibrary(unittest.TestCase):
    """Test cases for ImageComparisonLibrary."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.lib = ImageComparisonLibrary()
        self.temp_dir = TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)
        
        # Create test images with patterns (not solid colors)
        self.baseline_img = Image.new('RGB', (100, 100), color='white')
        pixels = self.baseline_img.load()
        # Add a checkerboard pattern
        for y in range(100):
            for x in range(100):
                if (x // 10 + y // 10) % 2 == 0:
                    pixels[x, y] = (200, 50, 50)  # Red
                    
        self.identical_img = self.baseline_img.copy()
        
        # Create truly different image with different pattern
        self.different_img = Image.new('RGB', (100, 100), color='white')
        diff_pixels = self.different_img.load()
        # Add a different pattern - stripes instead of checkerboard
        for y in range(100):
            for x in range(100):
                if x % 20 < 10:
                    diff_pixels[x, y] = (50, 50, 200)  # Blue
                    
        self.different_size_img = Image.new('RGB', (200, 200), color='white')
        size_pixels = self.different_size_img.load()
        # Add completely different pattern to ensure hash difference
        for y in range(200):
            for x in range(200):
                if (x + y) % 30 < 15:
                    size_pixels[x, y] = (100, 200, 50)  # Green pattern
        
        # Save test images
        self.baseline_path = self.temp_path / "baseline.png"
        self.identical_path = self.temp_path / "identical.png"
        self.different_path = self.temp_path / "different.png"
        self.different_size_path = self.temp_path / "different_size.png"
        
        self.baseline_img.save(self.baseline_path)
        self.identical_img.save(self.identical_path)
        self.different_img.save(self.different_path)
        self.different_size_img.save(self.different_size_path)
        
        # Create diff directory
        self.diff_dir = self.temp_path / "diffs"
        self.diff_dir.mkdir(exist_ok=True)
    
    def tearDown(self):
        """Clean up test fixtures."""
        self.temp_dir.cleanup()
    
    def test_identical_images_pass(self):
        """Test that identical images pass comparison."""
        distance = self.lib.compare_layouts_and_generate_diff(
            self.baseline_path,
            self.identical_path,
            self.diff_dir
        )
        self.assertEqual(distance, 0)
        
        # Verify no diff file was created
        diff_files = list(self.diff_dir.glob("*.png"))
        self.assertEqual(len(diff_files), 0)
    
    def test_different_images_fail(self):
        """Test that different images fail comparison."""
        with self.assertRaises(AssertionError) as context:
            self.lib.compare_layouts_and_generate_diff(
                self.baseline_path,
                self.different_path,
                self.diff_dir,
                tolerance=5
            )
        
        error_message = str(context.exception)
        self.assertIn("Images differ beyond allowed tolerance", error_message)
        self.assertIn("Hamming distance:", error_message)
        
        # Verify diff file was created
        diff_files = list(self.diff_dir.glob("diff_*.png"))
        self.assertEqual(len(diff_files), 1)
    
    def test_different_dimensions_fail(self):
        """Test that images with different dimensions fail immediately."""
        with self.assertRaises(AssertionError) as context:
            self.lib.compare_layouts_and_generate_diff(
                self.baseline_path,
                self.different_size_path,
                self.diff_dir
            )
        
        error_message = str(context.exception)
        self.assertIn("different dimensions", error_message)
    
    def test_pil_image_input(self):
        """Test that PIL Image objects can be used as input."""
        distance = self.lib.compare_layouts_and_generate_diff(
            self.baseline_img,
            self.identical_img,
            self.diff_dir
        )
        self.assertEqual(distance, 0)
    
    def test_pathlib_path_input(self):
        """Test that pathlib.Path objects can be used as input."""
        distance = self.lib.compare_layouts_and_generate_diff(
            Path(self.baseline_path),
            Path(self.identical_path),
            Path(self.diff_dir)
        )
        self.assertEqual(distance, 0)
    
    def test_string_path_input(self):
        """Test that string paths can be used as input."""
        distance = self.lib.compare_layouts_and_generate_diff(
            str(self.baseline_path),
            str(self.identical_path),
            str(self.diff_dir)
        )
        self.assertEqual(distance, 0)
    
    def test_phash_algorithm(self):
        """Test that phash algorithm works."""
        distance = self.lib.compare_layouts_and_generate_diff(
            self.baseline_path,
            self.identical_path,
            self.diff_dir,
            algorithm='phash'
        )
        self.assertEqual(distance, 0)
    
    def test_dhash_algorithm(self):
        """Test that dhash algorithm works."""
        distance = self.lib.compare_layouts_and_generate_diff(
            self.baseline_path,
            self.identical_path,
            self.diff_dir,
            algorithm='dhash'
        )
        self.assertEqual(distance, 0)
    
    def test_invalid_algorithm_raises_error(self):
        """Test that invalid algorithm raises ValueError."""
        with self.assertRaises(ValueError) as context:
            self.lib.compare_layouts_and_generate_diff(
                self.baseline_path,
                self.identical_path,
                self.diff_dir,
                algorithm='invalid'
            )
        
        error_message = str(context.exception)
        self.assertIn("Unsupported algorithm", error_message)
    
    def test_check_layouts_are_visually_similar(self):
        """Test the relaxed comparison keyword."""
        distance = self.lib.check_layouts_are_visually_similar(
            self.baseline_path,
            self.identical_path,
            self.diff_dir
        )
        self.assertEqual(distance, 0)
    
    def test_nonexistent_file_raises_error(self):
        """Test that nonexistent file raises FileNotFoundError."""
        with self.assertRaises(FileNotFoundError):
            self.lib.compare_layouts_and_generate_diff(
                "nonexistent.png",
                self.identical_path,
                self.diff_dir
            )
    
    def test_tolerance_parameter(self):
        """Test that tolerance parameter works correctly."""
        # Create slightly different image with more significant changes
        slightly_different = self.baseline_img.copy()
        pixels = slightly_different.load()
        # Change a larger area to ensure hash difference
        for y in range(20, 40):
            for x in range(20, 40):
                pixels[x, y] = (50, 200, 200)  # Cyan block
        
        slightly_different_path = self.temp_path / "slightly_different.png"
        slightly_different.save(slightly_different_path)
        
        # With low tolerance, should fail
        with self.assertRaises(AssertionError):
            self.lib.compare_layouts_and_generate_diff(
                self.baseline_path,
                slightly_different_path,
                self.diff_dir,
                tolerance=1
            )
        
        # With high tolerance, should pass
        distance = self.lib.compare_layouts_and_generate_diff(
            self.baseline_path,
            slightly_different_path,
            self.diff_dir,
            tolerance=100
        )
        self.assertIsInstance(distance, int)
        self.assertGreaterEqual(distance, 0)


if __name__ == '__main__':
    unittest.main()
