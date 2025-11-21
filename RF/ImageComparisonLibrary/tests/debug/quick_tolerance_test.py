#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quick Tolerance Test - Find optimal parameters for input shift detection
"""

import sys
import os
from pathlib import Path

# Fix Windows console encoding
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except:
        pass

# Add library to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from ImageComparisonLibrary import ImageComparisonLibrary

def test_parameters():
    """Test various parameter combinations to find what makes test fail."""

    lib = ImageComparisonLibrary()

    # Your images
    baseline = r"C:\Users\stoka\Documents\moje_app\RF\libraries\images\baseline\login_page_20251118_174339.png"
    current = r"C:\Users\stoka\Documents\moje_app\RF\libraries\images\screenshot\login_page_20251120_152201.png"
    output_dir = Path(__file__).parent / "test_outputs" / "quick_tests"
    output_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 80)
    print("QUICK TOLERANCE TEST")
    print("=" * 80)
    print(f"\nBaseline: {Path(baseline).name}")
    print(f"Current:  {Path(current).name}")
    print("\n" + "=" * 80)

    # Test configurations: (algorithm, tolerance, hash_size, description)
    tests = [
        ('phash', 5, 16, "Current Settings"),
        ('phash', 3, 16, "Lower Tolerance (3)"),
        ('phash', 2, 16, "Even Lower Tolerance (2)"),
        ('phash', 1, 16, "Strictest Tolerance (1)"),
        ('phash', 5, 24, "Higher Hash Size (24)"),
        ('phash', 5, 32, "Highest Hash Size (32)"),
        ('dhash', 5, 16, "dhash Algorithm"),
        ('dhash', 3, 16, "dhash + Lower Tolerance"),
        ('dhash', 2, 24, "dhash + Tolerance 2 + Hash 24"),
    ]

    results = []

    for i, (algo, tol, h_size, desc) in enumerate(tests, 1):
        print(f"\n{'─' * 80}")
        print(f"Test {i}/{len(tests)}: {desc}")
        print(f"   algorithm={algo}, tolerance={tol}, hash_size={h_size}")

        try:
            distance = lib.compare_layouts_and_generate_diff(
                baseline_image=baseline,
                current_image=current,
                diff_directory=str(output_dir),
                algorithm=algo,
                tolerance=tol,
                hash_size=h_size,
                pixel_tolerance=45,
                min_contour_area=500,
                diff_mode='contours',
                contour_thickness=3,
                add_timestamp=False,
                embed_images_to_log=False,
                log_statistics=False
            )

            # If we get here, test PASSED (distance <= tolerance)
            status = "PASS (no diff)"
            results.append((desc, algo, tol, h_size, distance, "PASS"))
            print(f"   Distance: {distance} <= {tol}")
            print(f"   Status: ✅ PASS (test prošel - diff nebyl vytvořen)")

        except AssertionError as e:
            # Test FAILED (distance > tolerance) - THIS IS WHAT WE WANT!
            # Extract distance from error message
            try:
                import re
                match = re.search(r'Hamming distance: (\d+)', str(e))
                distance = int(match.group(1)) if match else "?"
            except:
                distance = "?"

            results.append((desc, algo, tol, h_size, distance, "FAIL"))
            print(f"   Distance: {distance} > {tol}")
            print(f"   Status: ❌ FAIL (test failnul - diff byl vytvořen) ⭐ THIS IS GOOD!")

    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)

    print("\n✅ Tests that PASSED (not what we want):")
    for desc, algo, tol, h_size, dist, status in results:
        if status == "PASS":
            print(f"   - {desc}: distance={dist} <= tolerance={tol}")

    print("\n❌ Tests that FAILED (this is what we want!):")
    failed = [r for r in results if r[5] == "FAIL"]
    if failed:
        for desc, algo, tol, h_size, dist, status in failed:
            print(f"   - {desc}: distance={dist} > tolerance={tol} ⭐")

        print("\n" + "=" * 80)
        print("🎯 RECOMMENDATION")
        print("=" * 80)

        # Pick the first failing test with most lenient settings
        best = failed[0]
        print(f"\nUse these parameters in te.robot:")
        print(f"   algorithm='{best[1]}'")
        print(f"   tolerance={best[2]}")
        print(f"   hash_size={best[3]}")
        print(f"   pixel_tolerance=45")
        print(f"   min_contour_area=500")
    else:
        print("   (NONE - všechny testy prošly!)")
        print("\n⚠️  WARNING: Žádný test nefailnul!")
        print("   To znamená, že baseline a current screenshot jsou IDENTICKÉ")
        print("   nebo transform se neaplikuje správně.")
        print("\n   Zkontrolujte:")
        print("   1. Aplikuje se Add Style Tag před Take Screenshot?")
        print("   2. Je Sleep 2s dostatečný?")
        print("   3. Je selector správný? ${LOGIN_EMAIL_INPUT}")

    print("\n" + "=" * 80)
    print(f"Diff images saved to: {output_dir}")
    print("=" * 80)


if __name__ == "__main__":
    try:
        test_parameters()
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
