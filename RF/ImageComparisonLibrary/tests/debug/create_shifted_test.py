#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Create Synthetic Shifted Screenshot - Manually shift email input to test detection
"""

import sys
from pathlib import Path
from PIL import Image, ImageDraw

# Fix Windows encoding
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except:
        pass

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from ImageComparisonLibrary import ImageComparisonLibrary


def create_shifted_input():
    """Create a synthetic screenshot with Email input shifted 30px right, 15px down."""

    baseline_path = Path(r"C:\Users\stoka\Documents\moje_app\RF\libraries\images\baseline\login_page_20251118_174339.png")
    output_dir = Path(__file__).parent / "test_outputs" / "synthetic"
    output_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 80)
    print("CREATING SYNTHETIC SHIFTED SCREENSHOT")
    print("=" * 80)

    # Load baseline
    baseline = Image.open(baseline_path)
    print(f"\nBaseline loaded: {baseline.size}")

    # Create a copy for manipulation
    shifted = baseline.copy()
    draw = ImageDraw.Draw(shifted)

    # Email input approximate coordinates (measured from screenshot)
    # Box around Email field: x1=640, y1=333, x2=1110, y2=373
    email_region = (640, 333, 1110, 373)
    shift_x = 30
    shift_y = 15

    print(f"\nOriginal Email input region: {email_region}")
    print(f"Shifting by: +{shift_x}px right, +{shift_y}px down")

    # Extract the email input region
    email_crop = baseline.crop(email_region)

    # Clear the original region (fill with white)
    draw.rectangle(email_region, fill=(255, 255, 255))

    # Paste the cropped region at shifted position
    shifted_position = (email_region[0] + shift_x, email_region[1] + shift_y)
    shifted.paste(email_crop, shifted_position)

    # Draw a RED rectangle around the shifted region for visualization
    shifted_box = (
        shifted_position[0],
        shifted_position[1],
        shifted_position[0] + (email_region[2] - email_region[0]),
        shifted_position[1] + (email_region[3] - email_region[1])
    )
    draw.rectangle(shifted_box, outline=(255, 0, 0), width=3)

    # Save synthetic shifted screenshot
    shifted_path = output_dir / "synthetic_shifted_input.png"
    shifted.save(shifted_path)
    print(f"\n✅ Synthetic shifted screenshot saved: {shifted_path}")

    # Also save a visualization showing both
    comparison = Image.new('RGB', (baseline.width * 2, baseline.height))
    comparison.paste(baseline, (0, 0))
    comparison.paste(shifted, (baseline.width, 0))

    comp_draw = ImageDraw.Draw(comparison)
    comp_draw.text((20, 20), "BASELINE (Original)", fill=(0, 0, 0))
    comp_draw.text((baseline.width + 20, 20), "SHIFTED (+30px right, +15px down)", fill=(255, 0, 0))

    comp_path = output_dir / "comparison_baseline_vs_shifted.png"
    comparison.save(comp_path)
    print(f"✅ Comparison image saved: {comp_path}")

    return baseline_path, shifted_path


def test_with_shifted():
    """Test various parameters with synthetic shifted screenshot."""

    baseline_path, shifted_path = create_shifted_input()

    lib = ImageComparisonLibrary()
    output_dir = Path(__file__).parent / "test_outputs" / "synthetic" / "diffs"
    output_dir.mkdir(parents=True, exist_ok=True)

    print("\n" + "=" * 80)
    print("TESTING PARAMETERS WITH SYNTHETIC SHIFTED INPUT")
    print("=" * 80)

    # Test configurations
    tests = [
        ('phash', 5, 16, 500, "Current Settings"),
        ('phash', 5, 24, 500, "hash_size=24"),
        ('phash', 5, 32, 500, "hash_size=32"),
        ('phash', 3, 32, 500, "hash_size=32, tolerance=3"),
        ('dhash', 5, 16, 500, "dhash algorithm"),
        ('dhash', 5, 24, 500, "dhash + hash_size=24"),
    ]

    results = []

    for i, (algo, tol, h_size, min_area, desc) in enumerate(tests, 1):
        print(f"\n{'─' * 80}")
        print(f"Test {i}/{len(tests)}: {desc}")
        print(f"   algorithm={algo}, tolerance={tol}, hash_size={h_size}, min_contour_area={min_area}")

        try:
            distance = lib.compare_layouts_and_generate_diff(
                baseline_image=str(baseline_path),
                current_image=str(shifted_path),
                diff_directory=str(output_dir),
                algorithm=algo,
                tolerance=tol,
                hash_size=h_size,
                pixel_tolerance=45,
                min_contour_area=min_area,
                diff_mode='contours',
                contour_thickness=3,
                add_timestamp=False,
                embed_images_to_log=False,
                log_statistics=True
            )

            results.append((desc, algo, tol, h_size, min_area, distance, "PASS"))
            print(f"   ✅ PASS: distance={distance} <= tolerance={tol}")

        except AssertionError as e:
            import re
            match = re.search(r'Hamming distance: (\d+)', str(e))
            distance = int(match.group(1)) if match else "?"

            results.append((desc, algo, tol, h_size, min_area, distance, "FAIL"))
            print(f"   ❌ FAIL: distance={distance} > tolerance={tol} ⭐ (diff created!)")

    print("\n" + "=" * 80)
    print("RESULTS SUMMARY")
    print("=" * 80)

    print("\n📊 All Tests:")
    for desc, algo, tol, h_size, min_area, dist, status in results:
        icon = "❌" if status == "FAIL" else "✅"
        print(f"   {icon} {desc}: distance={dist}, status={status}")

    # Find tests that failed (detected the shift)
    failed = [r for r in results if r[6] == "FAIL"]

    if failed:
        print("\n🎯 THESE PARAMETERS DETECTED THE SHIFT:")
        for desc, algo, tol, h_size, min_area, dist, status in failed:
            print(f"\n   ⭐ {desc}")
            print(f"      algorithm='{algo}'")
            print(f"      tolerance={tol}")
            print(f"      hash_size={h_size}")
            print(f"      min_contour_area={min_area}")
            print(f"      → Hamming distance: {dist}")

        # Best option (first one that failed)
        best = failed[0]
        print("\n" + "=" * 80)
        print("🏆 RECOMMENDED PARAMETERS FOR te.robot:")
        print("=" * 80)
        print(f"\nCompare Layouts And Generate Diff")
        print(f"    ...    algorithm='{best[1]}'")
        print(f"    ...    tolerance={best[2]}")
        print(f"    ...    hash_size={best[3]}")
        print(f"    ...    pixel_tolerance=45")
        print(f"    ...    min_contour_area={best[4]}")

    else:
        print("\n⚠️  WARNING: Žádný test nezachytil posun!")
        print("   Všechny parametry považují obrázky za identické.")

    print("\n" + "=" * 80)
    print("📂 Files created:")
    print(f"   - Synthetic shifted: test_outputs/synthetic/synthetic_shifted_input.png")
    print(f"   - Comparison view: test_outputs/synthetic/comparison_baseline_vs_shifted.png")
    print(f"   - Diff images: test_outputs/synthetic/diffs/")
    print("=" * 80)


if __name__ == "__main__":
    try:
        test_with_shifted()
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
