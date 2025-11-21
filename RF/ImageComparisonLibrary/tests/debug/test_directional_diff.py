"""Test script for directional diff feature with user's actual images."""

import sys
from pathlib import Path

# Add library to path (go up two levels: debug/ -> tests/ -> ImageComparisonLibrary/)
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from ImageComparisonLibrary import ImageComparisonLibrary

# Configure UTF-8 output for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

def test_directional_diff():
    """Test the new directional diff feature."""

    # Initialize library
    lib = ImageComparisonLibrary()

    # Paths to user's images
    baseline_path = r"C:\Users\stoka\Documents\moje_app\RF\libraries\images\baseline\login_page_20251118_174339.png"
    screenshot_path = r"C:\Users\stoka\Documents\moje_app\RF\libraries\images\screenshot\login_page_20251121_084512.png"
    diff_dir = Path(__file__).parent / "outputs" / "directional_diff"

    print("=" * 80)
    print("TESTING DIRECTIONAL DIFF FEATURE")
    print("=" * 80)

    # Test 1: Original behavior (baseline as base, all changes)
    print("\n[TEST 1] Original behavior: diff_base_image='baseline', highlight_mode='all'")
    print("-" * 80)
    try:
        distance = lib.compare_layouts_and_generate_diff(
            baseline_path,
            screenshot_path,
            diff_dir,
            tolerance=5,
            pixel_tolerance=15,
            min_contour_area=50,
            severe_color=(255, 0, 0),
            diff_base_image='baseline',
            highlight_mode='all'
        )
    except AssertionError as e:
        print(f"✓ Test failed as expected (distance > tolerance)")
        print(f"  Generated diff with baseline as base, showing ALL changes")

    # Test 2: NEW BEHAVIOR - Show only shifted input (current as base, added pixels)
    print("\n[TEST 2] NEW BEHAVIOR: diff_base_image='current', highlight_mode='added'")
    print("-" * 80)
    try:
        distance = lib.compare_layouts_and_generate_diff(
            baseline_path,
            screenshot_path,
            diff_dir,
            tolerance=5,
            pixel_tolerance=15,
            min_contour_area=50,
            severe_color=(255, 0, 0),
            diff_base_image='current',
            highlight_mode='added'
        )
    except AssertionError as e:
        print(f"✓ Test failed as expected (distance > tolerance)")
        print(f"  Generated diff with CURRENT as base, showing only ADDED pixels")
        print(f"  This should highlight the NEW (shifted) input position!")

    # Test 3: Show only original position (baseline as base, removed pixels)
    print("\n[TEST 3] Alternative: diff_base_image='baseline', highlight_mode='removed'")
    print("-" * 80)
    try:
        distance = lib.compare_layouts_and_generate_diff(
            baseline_path,
            screenshot_path,
            diff_dir,
            tolerance=5,
            pixel_tolerance=15,
            min_contour_area=50,
            severe_color=(255, 0, 0),
            diff_base_image='baseline',
            highlight_mode='removed'
        )
    except AssertionError as e:
        print(f"✓ Test failed as expected (distance > tolerance)")
        print(f"  Generated diff with baseline as base, showing only REMOVED pixels")

    print("\n" + "=" * 80)
    print("TESTING COMPLETE!")
    print("=" * 80)
    print(f"\nCheck the diff images in: {diff_dir}")
    print("\nExpected results:")
    print("  TEST 1: Shows BOTH old and new positions (large rectangle + small edge)")
    print("  TEST 2: Shows ONLY NEW position (shifted input) ← THIS IS WHAT YOU WANT!")
    print("  TEST 3: Shows ONLY OLD position (original input)")

if __name__ == "__main__":
    test_directional_diff()
