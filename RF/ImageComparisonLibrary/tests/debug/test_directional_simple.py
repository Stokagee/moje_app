"""Simple direct test of directional diff."""

import sys
from pathlib import Path

# Add library to path (go up two levels: debug/ -> tests/ -> ImageComparisonLibrary/)
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from ImageComparisonLibrary.core import ImageComparisonLibrary

# Configure UTF-8 output for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Initialize library
lib = ImageComparisonLibrary()

# Paths
baseline_path = r"C:\Users\stoka\Documents\moje_app\RF\libraries\images\baseline\login_page_20251118_174339.png"
screenshot_path = r"C:\Users\stoka\Documents\moje_app\RF\libraries\images\screenshot\login_page_20251121_084512.png"
diff_dir = Path(__file__).parent / "outputs" / "directional_simple"

print("Testing directional diff...")
print(f"Baseline: {baseline_path}")
print(f"Screenshot: {screenshot_path}")
print(f"Diff dir: {diff_dir}")

try:
    distance = lib.compare_layouts_and_generate_diff(
        baseline_path,
        screenshot_path,
        diff_dir,
        tolerance=5,
        hash_size=32,
        pixel_tolerance=15,
        min_contour_area=50,
        severe_color=(255, 0, 0),
        diff_base_image='current',
        highlight_mode='added'
    )
    print(f"UNEXPECTED: Test passed with distance={distance}")
except AssertionError as e:
    print(f"SUCCESS: Test failed as expected!")
    print(f"Error message: {str(e)[:200]}...")
except Exception as e:
    print(f"ERROR: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()

print("\nDone!")
