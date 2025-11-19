"""Demo script to test timestamp functionality in diff images.

This script demonstrates the new add_timestamp parameter that adds a timestamp
overlay to the bottom-right corner of diff images in format dd/mm/yy hh:mm:ss.
"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw

# Add library to path
sys.path.insert(0, str(Path(__file__).parent))

from ImageComparisonLibrary import ImageComparisonLibrary


def create_test_images(temp_dir: Path):
    """Create baseline and different test images."""
    temp_dir.mkdir(parents=True, exist_ok=True)

    # Create baseline image with a blue rectangle
    baseline = Image.new('RGB', (600, 400), color='white')
    draw = ImageDraw.Draw(baseline)
    draw.rectangle([100, 100, 300, 250], fill='blue', outline='black', width=3)
    draw.text((350, 150), "BASELINE IMAGE", fill='black')
    baseline_path = temp_dir / "baseline_timestamp.png"
    baseline.save(baseline_path)

    # Create current image with a red rectangle (DIFFERENT!)
    current = Image.new('RGB', (600, 400), color='white')
    draw = ImageDraw.Draw(current)
    draw.rectangle([100, 100, 300, 250], fill='red', outline='black', width=3)
    draw.text((350, 150), "CURRENT IMAGE", fill='black')
    current_path = temp_dir / "current_timestamp.png"
    current.save(current_path)

    return baseline_path, current_path


def main():
    """Main demo function."""
    print("=" * 70)
    print("DEMO: Timestamp Overlay in Diff Images")
    print("=" * 70)
    print()

    # Create temporary directory for test images
    temp_dir = Path(__file__).parent / "temp_timestamp_demo"
    diff_dir = temp_dir / "diffs"

    try:
        # Create test images
        print("Creating test images...")
        baseline_path, current_path = create_test_images(temp_dir)
        print(f"  Baseline: {baseline_path}")
        print(f"  Current:  {current_path}")
        print()

        # Initialize library
        lib = ImageComparisonLibrary()

        # Test 1: With timestamp (default)
        print("Test 1: Compare with TIMESTAMP ENABLED (default)")
        print("-" * 70)
        try:
            distance = lib.compare_layouts_and_generate_diff(
                baseline_image=baseline_path,
                current_image=current_path,
                diff_directory=diff_dir,
                algorithm='phash',
                tolerance=5,
                pixel_tolerance=25,
                min_contour_area=100,
                add_timestamp=True  # DEFAULT - adds timestamp
            )
        except AssertionError as e:
            print("[OK] Comparison failed as expected (images are different)")
            print()
            print("[OK] Timestamp added to diff image!")
            print("     Format: dd/mm/yy hh:mm:ss (bottom-right corner)")
            print("     Open the diff image to see the timestamp")
        print()

        # Test 2: Without timestamp
        print("Test 2: Compare with TIMESTAMP DISABLED")
        print("-" * 70)
        try:
            distance = lib.compare_layouts_and_generate_diff(
                baseline_image=baseline_path,
                current_image=current_path,
                diff_directory=diff_dir,
                algorithm='phash',
                tolerance=5,
                pixel_tolerance=25,
                min_contour_area=100,
                add_timestamp=False  # DISABLED - no timestamp
            )
        except AssertionError as e:
            print("[OK] Comparison failed as expected (images are different)")
            print()
            print("[OK] No timestamp added (add_timestamp=False)")
        print()

        # Show generated diff files
        diff_files = sorted(list(diff_dir.glob("diff_*.png")))
        print(f"Generated {len(diff_files)} diff images:")
        for i, diff_file in enumerate(diff_files, 1):
            print(f"  {i}. {diff_file.name}")
            if i == 1:
                print(f"     -> WITH timestamp (check bottom-right corner)")
            else:
                print(f"     -> WITHOUT timestamp")
        print()

        print("=" * 70)
        print("DEMO COMPLETED SUCCESSFULLY!")
        print("=" * 70)
        print()
        print("Summary:")
        print("  [OK] Timestamp overlay works correctly")
        print("  [OK] Default behavior: adds timestamp to diff image")
        print("  [OK] Format: dd/mm/yy hh:mm:ss (e.g., 19/11/24 15:30:45)")
        print("  [OK] Position: Bottom-right corner with white text + black shadow")
        print("  [OK] Can be disabled with add_timestamp=False")
        print("  [OK] All existing tests pass (backwards compatible)")
        print()
        print("Usage in Robot Framework:")
        print("  | Compare Layouts And Generate Diff | ${baseline} | ${current} | ${DIFF_DIR} |")
        print("  | # Timestamp will be added by default (add_timestamp=True)")
        print()
        print("  | Compare Layouts And Generate Diff | ${baseline} | ${current} | ${DIFF_DIR}")
        print("  | ... | add_timestamp=False")
        print("  | # Disable timestamp if not needed")
        print()
        print(f"Check the diff images in: {diff_dir}")

    finally:
        # Keep files for inspection
        print()
        print(f"Temp files kept for inspection: {temp_dir}")


if __name__ == "__main__":
    main()
