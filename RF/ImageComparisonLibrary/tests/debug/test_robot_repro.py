"""
Reproduction script for Robot Framework test.

This script EXACTLY replicates the user's te.robot test to debug the blue rectangle issue.
"""

import sys
from pathlib import Path

# Add library to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from ImageComparisonLibrary import ImageComparisonLibrary

print("=" * 80)
print("ROBOT FRAMEWORK TEST REPRODUCTION")
print("=" * 80)

# Initialize library
lib = ImageComparisonLibrary()

# Paths - using Docker mounted volumes
baseline_path = "/images/baseline/login_page_20251118_174339.png"
screenshot_path = "/images/screenshot/login_page_20251121_084512.png"
diff_dir = Path(__file__).parent / "outputs" / "robot_repro"

print(f"\nBaseline:   {baseline_path}")
print(f"Screenshot: {screenshot_path}")
print(f"Diff dir:   {diff_dir}")

# EXACT parameters from te.robot line 38-39
params = {
    'tolerance': 5,
    'hash_size': 32,
    'pixel_tolerance': 15,
    'diff_mode': 'contours',
    'min_contour_area': 50,
    'contour_thickness': 3,
    'severe_color': (255, 0, 0),  # RED - user's specified color
    'diff_base_image': 'current',
    'highlight_mode': 'added'
}

print("\nParameters:")
for key, value in params.items():
    print(f"  {key}: {value} (type: {type(value).__name__})")

print("\n" + "-" * 80)
print("Running comparison...")
print("-" * 80)

try:
    distance = lib.compare_layouts_and_generate_diff(
        baseline_path,
        screenshot_path,
        diff_dir,
        **params
    )
    print(f"\n[UNEXPECTED] Test PASSED with distance={distance}")
    print("ERROR: Test should have FAILED!")

except AssertionError as e:
    print(f"\n[EXPECTED] Test FAILED as expected!")
    print(f"Error message: {str(e)[:200]}...")

    # Check diff image
    diff_files = list(diff_dir.glob("diff_*.png"))
    if diff_files:
        print(f"\n[SUCCESS] Diff image generated: {diff_files[0].name}")
        print("\nEXPECTED RESULT:")
        print("  - Visual base: current screenshot (with shifted input)")
        print("  - Highlight: RED contour around shifted Email input")
        print("  - Should show ENTIRE Email input, not just small piece")
        print("\nACTUAL RESULT:")
        print("  - Check the diff image in outputs/robot_repro/")
        print("  - If you see small BLUE shape -> severe_color not applied")
        print("  - If you see large RED contour -> SUCCESS!")
    else:
        print("\n[ERROR] No diff image found!")

except Exception as e:
    print(f"\n[ERROR] Unexpected exception: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
print("TEST COMPLETE")
print("=" * 80)
