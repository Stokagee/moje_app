#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test with EXACT user parameters from te.robot"""

import sys
from pathlib import Path

if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except: pass

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from ImageComparisonLibrary import ImageComparisonLibrary

def test_exact_user_params():
    lib = ImageComparisonLibrary()

    baseline = r"C:\Users\stoka\Documents\moje_app\RF\libraries\images\baseline\login_page_20251118_174339.png"
    current = r"C:\Users\stoka\Documents\moje_app\RF\libraries\images\screenshot\login_page_20251121_082406.png"
    output_dir = Path(__file__).parent / "test_outputs" / "user_exact_test"
    output_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 80)
    print("TEST S PŘESNÝMI PARAMETRY Z te.robot (řádek 38)")
    print("=" * 80)
    print(f"\nBaseline: {Path(baseline).name}")
    print(f"Current:  {Path(current).name}")
    print("\nParametry:")
    print("  tolerance=15")
    print("  hash_size=32")
    print("  pixel_tolerance=10      # ← VELMI NÍZKÉ!")
    print("  diff_mode=contours")
    print("  min_contour_area=100")
    print("  contour_thickness=3")

    try:
        distance = lib.compare_layouts_and_generate_diff(
            baseline_image=baseline,
            current_image=current,
            diff_directory=str(output_dir),
            algorithm='phash',
            tolerance=15,
            hash_size=32,
            pixel_tolerance=10,
            diff_mode='contours',
            min_contour_area=100,
            contour_thickness=3,
            add_timestamp=True,
            embed_images_to_log=False,
            log_statistics=True
        )

        print(f"\n✅ TEST PROŠEL!")
        print(f"   Hamming distance: {distance}")
        print(f"   Tolerance: 15")
        print(f"   {distance} <= 15 → PASS")
        print("\n❌ Diff obrázek NEBYL vytvořen (test prošel)")

    except AssertionError as e:
        import re
        match = re.search(r'Hamming distance: (\d+)', str(e))
        distance = int(match.group(1)) if match else "?"

        print(f"\n❌ TEST FAILNUL!")
        print(f"   Hamming distance: {distance}")
        print(f"   Tolerance: 15")
        print(f"   {distance} > 15 → FAIL")
        print(f"\n✅ Diff obrázek BYL vytvořen v: {output_dir}")

        # Find the diff file
        import glob
        diffs = glob.glob(str(output_dir / "*.png"))
        if diffs:
            print(f"   Soubor: {Path(diffs[0]).name}")

    print("\n" + "=" * 80)
    print("ZÁVĚR")
    print("=" * 80)

    # Now test with DIFFERENT parameters to find what works
    print("\n🔬 TEĎ OTESTUJI RŮZNÉ KOMBINACE PARAMETRŮ...")
    print("\nProblem může být v:")
    print("  1. pixel_tolerance=10 je MOC NÍZKÉ")
    print("  2. tolerance=15 je MOC VYSOKÉ")
    print("  3. Obrázky jsou skutečně identické")

    print("\n" + "=" * 80)

if __name__ == "__main__":
    test_exact_user_params()
