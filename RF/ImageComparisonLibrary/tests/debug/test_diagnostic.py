"""
Diagnostic script to debug the blue rectangle issue.

Analyzes:
1. How parameters are received by the library
2. What masks are generated
3. What contours are detected
4. What colors are used for drawing
"""

import sys
import numpy as np
import cv2
from pathlib import Path
from PIL import Image

# Add library to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from ImageComparisonLibrary.core import ImageComparisonLibrary

print("=" * 80)
print("DIAGNOSTIC ANALYSIS")
print("=" * 80)

# Initialize library
lib = ImageComparisonLibrary()

# Paths
baseline_path = "/images/baseline/login_page_20251118_174339.png"
screenshot_path = "/images/screenshot/login_page_20251121_084512.png"

print(f"\nLoading images...")
baseline_img = Image.open(baseline_path).convert('RGB')
current_img = Image.open(screenshot_path).convert('RGB')
print(f"  Baseline: {baseline_img.size}")
print(f"  Current:  {current_img.size}")

# Test mask generation
print("\n" + "-" * 80)
print("1. MASK GENERATION TEST")
print("-" * 80)

binary_mask, added_pixels_mask, removed_pixels_mask, color_diff_array, baseline_array, current_array = lib._create_diff_mask(
    baseline_img,
    current_img,
    pixel_tolerance=15
)

binary_count = np.count_nonzero(binary_mask)
added_count = np.count_nonzero(added_pixels_mask)
removed_count = np.count_nonzero(removed_pixels_mask)

print(f"\nMask pixel counts:")
print(f"  Binary (all):     {binary_count:,} pixels")
print(f"  Added (new):      {added_count:,} pixels")
print(f"  Removed (old):    {removed_count:,} pixels")

# Test contour detection
print("\n" + "-" * 80)
print("2. CONTOUR DETECTION TEST")
print("-" * 80)

for mask_name, mask in [("binary", binary_mask), ("added", added_pixels_mask), ("removed", removed_pixels_mask)]:
    contours = lib._find_contours(mask, min_contour_area=50)
    print(f"\n{mask_name.upper()} mask with min_contour_area=50:")
    print(f"  Total contours found: {len(contours)}")
    if contours:
        areas = [int(cv2.contourArea(c)) for c in contours]
        print(f"  Contour areas: {areas}")
        print(f"  Largest: {max(areas)} pixels")
    else:
        print(f"  [WARNING] No contours detected!")

# Test with different thresholds
print("\n" + "-" * 80)
print("3. MIN_CONTOUR_AREA THRESHOLD TEST")
print("-" * 80)

for threshold in [10, 50, 100, 500]:
    contours_added = lib._find_contours(added_pixels_mask, min_contour_area=threshold)
    print(f"  min_contour_area={threshold:4d} -> {len(contours_added)} contours in ADDED mask")

# Test parameter types
print("\n" + "-" * 80)
print("4. PARAMETER TYPE TEST")
print("-" * 80)

severe_colors = [
    (255, 0, 0),          # Python tuple
    "(255, 0, 0)",        # String (как RF может передавать)
    [255, 0, 0],          # List
]

for color in severe_colors:
    print(f"\nTesting severe_color={color} (type: {type(color).__name__})")
    try:
        if isinstance(color, str):
            print(f"  [WARNING] Color is string, not tuple!")
        else:
            print(f"  Type correct: {type(color).__name__}")
            print(f"  RGB values: R={color[0]}, G={color[1]}, B={color[2]}")
    except Exception as e:
        print(f"  [ERROR] {e}")

# Save diagnostic masks
print("\n" + "-" * 80)
print("5. SAVING DIAGNOSTIC MASKS")
print("-" * 80)

output_dir = Path(__file__).parent / "outputs" / "diagnostic"
output_dir.mkdir(parents=True, exist_ok=True)

Image.fromarray(binary_mask).save(output_dir / "mask_binary.png")
Image.fromarray(added_pixels_mask).save(output_dir / "mask_added.png")
Image.fromarray(removed_pixels_mask).save(output_dir / "mask_removed.png")

print(f"\nMasks saved to: {output_dir}")
print("  - mask_binary.png   (all changes)")
print("  - mask_added.png    (new pixels - should show shifted input)")
print("  - mask_removed.png  (old pixels - should show original position)")

print("\n" + "=" * 80)
print("DIAGNOSTIC COMPLETE")
print("=" * 80)
print("\nKEY FINDINGS:")
print(f"  1. Added pixels detected: {added_count > 0}")
print(f"  2. Contours in added mask: {len(lib._find_contours(added_pixels_mask, 50))}")
print(f"  3. Check mask_added.png to see if Email input is visible")
