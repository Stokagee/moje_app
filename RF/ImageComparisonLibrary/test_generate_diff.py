"""Temporary script to generate new diff with improved visualization."""
import sys
from pathlib import Path

# Add library to path
sys.path.insert(0, str(Path(__file__).parent))

from ImageComparisonLibrary import ImageComparisonLibrary

# Initialize library
lib = ImageComparisonLibrary()

# Paths
baseline = r"C:\Users\stoka\Documents\moje_app\RF\libraries\images\baseline\login_page_20251118_174339.png"
current = r"C:\Users\stoka\Documents\moje_app\RF\libraries\images\screenshot\login_page_20251119_104141.png"
diff_dir = r"C:\Users\stoka\Documents\moje_app\RF\libraries\images\results"

print("Generating diff with improved visualization...")
print(f"Baseline: {baseline}")
print(f"Current: {current}")
print(f"Diff directory: {diff_dir}")
print()

try:
    distance = lib.compare_layouts_and_generate_diff(
        baseline_image=baseline,
        current_image=current,
        diff_directory=diff_dir,
        algorithm='phash',
        tolerance=5,
        # Use new defaults (already set)
        pixel_tolerance=20,
        contour_thickness=3,
        min_contour_area=20,
        log_statistics=True,
        generate_html=False
    )
except AssertionError as e:
    print(f"✅ Comparison failed as expected (images are different)")
    print(f"Error details: {str(e)[:200]}...")
    print()
    print("✅ Diff image generated successfully with improved visualization!")
    print(f"Check the results in: {diff_dir}")
