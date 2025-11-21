"""Debug script to check the masks being generated."""

import sys
import numpy as np
from pathlib import Path
from PIL import Image

# Add library to path (go up two levels: debug/ -> tests/ -> ImageComparisonLibrary/)
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from ImageComparisonLibrary.core import ImageComparisonLibrary

# Configure UTF-8 output for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Paths
baseline_path = r"C:\Users\stoka\Documents\moje_app\RF\libraries\images\baseline\login_page_20251118_174339.png"
screenshot_path = r"C:\Users\stoka\Documents\moje_app\RF\libraries\images\screenshot\login_page_20251121_084512.png"

# Load images
baseline_img = Image.open(baseline_path).convert('RGB')
current_img = Image.open(screenshot_path).convert('RGB')

# Create library instance
lib = ImageComparisonLibrary()

# Call _create_diff_mask to get all masks
binary_mask, added_pixels_mask, removed_pixels_mask, color_diff_array, baseline_array, current_array = lib._create_diff_mask(
    baseline_img,
    current_img,
    pixel_tolerance=15
)

# Count non-zero pixels in each mask
binary_count = np.count_nonzero(binary_mask)
added_count = np.count_nonzero(added_pixels_mask)
removed_count = np.count_nonzero(removed_pixels_mask)

print("Mask Statistics:")
print(f"  Binary mask (all changes): {binary_count} pixels")
print(f"  Added mask (new pixels):   {added_count} pixels")
print(f"  Removed mask (old pixels): {removed_count} pixels")

# Save masks as images for visual inspection
output_dir = Path(__file__).parent / "outputs" / "debug_masks"
output_dir.mkdir(parents=True, exist_ok=True)

Image.fromarray(binary_mask).save(output_dir / "binary_mask.png")
Image.fromarray(added_pixels_mask).save(output_dir / "added_pixels_mask.png")
Image.fromarray(removed_pixels_mask).save(output_dir / "removed_pixels_mask.png")

print(f"\nMask images saved to: {output_dir}")
print("\nCheck the mask images to see which pixels are being detected!")
