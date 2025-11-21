#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test with FIXED pixel_tolerance to show difference"""

import sys
from pathlib import Path

if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except: pass

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from ImageComparisonLibrary import ImageComparisonLibrary

def test_pixel_tolerance_comparison():
    lib = ImageComparisonLibrary()

    baseline = r"C:\Users\stoka\Documents\moje_app\RF\libraries\images\baseline\login_page_20251118_174339.png"
    current = r"C:\Users\stoka\Documents\moje_app\RF\libraries\images\screenshot\login_page_20251121_082406.png"
    output_dir = Path(__file__).parent / "test_outputs" / "pixel_tolerance_fix"
    output_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 80)
    print("SROVNÁNÍ: pixel_tolerance=10 VS pixel_tolerance=45")
    print("=" * 80)

    tests = [
        (10, "ŠPATNĚ (současný stav)"),
        (45, "SPRÁVNĚ (opravené)"),
    ]

    for pixel_tol, desc in tests:
        print(f"\n{'─' * 80}")
        print(f"Test: pixel_tolerance={pixel_tol} ({desc})")
        print(f"{'─' * 80}")

        try:
            distance = lib.compare_layouts_and_generate_diff(
                baseline_image=baseline,
                current_image=current,
                diff_directory=str(output_dir),
                algorithm='phash',
                tolerance=5,  # SNÍŽENO z 15 na 5
                hash_size=32,
                pixel_tolerance=pixel_tol,
                diff_mode='contours',
                min_contour_area=100,
                contour_thickness=3,
                add_timestamp=False,
                embed_images_to_log=False,
                log_statistics=True,
                enable_color_coding=False,
                severe_color=(255, 0, 0)  # Červená
            )

            print(f"   Hamming distance: {distance}")
            print(f"   Status: PROŠEL (distance {distance} <= tolerance 5)")

        except AssertionError as e:
            import re
            match = re.search(r'Hamming distance: (\d+)', str(e))
            distance = int(match.group(1)) if match else "?"

            print(f"   Hamming distance: {distance}")
            print(f"   Status: FAILNUL (distance {distance} > tolerance 5) ✅")

            # Find diff file
            import glob
            import time
            time.sleep(0.5)  # Wait for file to be written
            diffs = sorted(glob.glob(str(output_dir / "*.png")), key=lambda x: Path(x).stat().st_mtime)
            if diffs:
                latest_diff = diffs[-1]
                print(f"   Diff vytvořen: {Path(latest_diff).name}")
                print(f"   S pixel_tolerance={pixel_tol}:")
                if pixel_tol == 10:
                    print(f"      ❌ Diff bude PRÁZDNÝ (žádné kontury)")
                else:
                    print(f"      ✅ Diff bude VYKRESLENÝ (s konturami)")

    print("\n" + "=" * 80)
    print("ZÁVĚR")
    print("=" * 80)
    print("\n❌ pixel_tolerance=10:")
    print("   - Téměř žádné pixely nejsou označeny jako 'změněné'")
    print("   - Diff mask je prázdná")
    print("   - Žádné kontury se nenajdou")
    print("   - Diff obrázek je ČISTÝ (bez kontur)")
    print("\n✅ pixel_tolerance=45:")
    print("   - Pixely s rozdílem >45 jsou označeny jako 'změněné'")
    print("   - Diff mask obsahuje změny")
    print("   - Kontury se najdou a vykreslí")
    print("   - Diff obrázek UKAZUJE změny (červené kontury)")

    print(f"\n📂 Oba diff obrázky jsou v: {output_dir}")
    print("   Porovnejte je vizuálně!")
    print("=" * 80)

if __name__ == "__main__":
    test_pixel_tolerance_comparison()
