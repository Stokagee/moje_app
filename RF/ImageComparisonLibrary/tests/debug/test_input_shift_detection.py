#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Input Shift Detection - Debugging Script for ImageComparisonLibrary
========================================================================

This script tests various parameter combinations to find optimal settings
for detecting small UI changes (like input field shifts).

Author: Claude Code (Debugging Assistant)
Date: 2025-11-20
"""

import sys
import os
from pathlib import Path
from datetime import datetime
import json

# Fix Windows console encoding for Unicode
if sys.platform == 'win32':
    os.system('chcp 65001 > nul')
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

# Add ImageComparisonLibrary to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from ImageComparisonLibrary import ImageComparisonLibrary
from PIL import Image


def run_parameter_tests():
    """Run tests with various parameter combinations."""

    # Initialize library
    lib = ImageComparisonLibrary()

    # Image paths (user's actual test images)
    baseline_path = Path(r"C:\Users\stoka\Documents\moje_app\RF\libraries\images\baseline\login_page_20251118_174339.png")
    current_path = Path(r"C:\Users\stoka\Documents\moje_app\RF\libraries\images\screenshot\login_page_20251120_145142.png")

    # Output directory
    output_dir = Path(__file__).parent / "test_outputs"
    diffs_dir = output_dir / "diffs"
    reports_dir = output_dir / "reports"

    # Verify images exist
    if not baseline_path.exists():
        print(f"❌ ERROR: Baseline image not found: {baseline_path}")
        return
    if not current_path.exists():
        print(f"❌ ERROR: Current image not found: {current_path}")
        return

    print("=" * 80)
    print("🔍 ImageComparisonLibrary Parameter Testing")
    print("=" * 80)
    print(f"\n📸 Baseline: {baseline_path.name}")
    print(f"📸 Current:  {current_path.name}")
    print(f"\n📂 Output directory: {output_dir}")
    print("\n" + "=" * 80)

    # Test parameters to try
    test_configurations = [
        # (min_contour_area, pixel_tolerance, description)
        (1500, 45, "Current Settings (User's Original)"),
        (1000, 45, "Lower Min Area (1000)"),
        (500, 45, "Even Lower Min Area (500)"),
        (100, 45, "Very Low Min Area (100) - Captures Small Changes"),
        (1500, 35, "Lower Pixel Tolerance (35)"),
        (500, 35, "Balanced: Area=500, Tolerance=35"),
        (100, 35, "Sensitive: Area=100, Tolerance=35"),
        (1500, 60, "Higher Pixel Tolerance (60)"),
        (500, 25, "Very Sensitive: Area=500, Tolerance=25"),
    ]

    results = []

    for i, (min_area, pixel_tol, description) in enumerate(test_configurations, 1):
        print(f"\n{'─' * 80}")
        print(f"🧪 Test {i}/{len(test_configurations)}: {description}")
        print(f"   ├─ min_contour_area: {min_area}")
        print(f"   └─ pixel_tolerance: {pixel_tol}")

        # Generate unique diff filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        diff_filename = f"test_{i:02d}_area{min_area}_tol{pixel_tol}_{timestamp}.png"
        diff_path = diffs_dir / diff_filename

        try:
            # Run comparison with specific parameters
            distance = lib.compare_layouts_and_generate_diff(
                baseline_image=str(baseline_path),
                current_image=str(current_path),
                diff_directory=str(diffs_dir),
                algorithm='phash',
                hash_size=16,
                tolerance=5,
                pixel_tolerance=pixel_tol,
                diff_mode='contours',
                contour_thickness=3,
                min_contour_area=min_area,
                enable_color_coding=True,
                minor_color=(0, 255, 0),      # Green
                moderate_color=(0, 255, 255),  # Yellow
                severe_color=(0, 0, 255),      # Blue
                add_timestamp=True,
                embed_images_to_log=False,  # Don't embed during testing
                log_statistics=True
            )

            # Store results
            result = {
                "test_number": i,
                "description": description,
                "min_contour_area": min_area,
                "pixel_tolerance": pixel_tol,
                "hamming_distance": distance,
                "diff_file": diff_filename,
                "status": "PASS" if distance <= 5 else "FAIL",
                "test_passed": distance <= 5
            }
            results.append(result)

            print(f"   ├─ Hamming Distance: {distance}")
            print(f"   ├─ Status: {'✅ PASS' if distance <= 5 else '❌ FAIL'}")
            print(f"   └─ Diff saved: {diff_filename}")

        except Exception as e:
            print(f"   ❌ ERROR: {str(e)}")
            result = {
                "test_number": i,
                "description": description,
                "min_contour_area": min_area,
                "pixel_tolerance": pixel_tol,
                "error": str(e),
                "status": "ERROR"
            }
            results.append(result)

    print("\n" + "=" * 80)
    print("📊 TEST SUMMARY")
    print("=" * 80)

    # Generate summary
    passed = sum(1 for r in results if r.get("test_passed", False))
    failed = sum(1 for r in results if r.get("status") == "FAIL")
    errors = sum(1 for r in results if r.get("status") == "ERROR")

    print(f"\n✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"⚠️  Errors: {errors}")
    print(f"\n📂 All diff images saved to: {diffs_dir}")

    # Save results to JSON
    results_file = reports_dir / f"test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"📄 Results saved to: {results_file}")

    # Generate HTML report
    html_report = generate_html_report(results, baseline_path, current_path, diffs_dir)
    html_file = reports_dir / f"visual_comparison_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(html_report)
    print(f"📊 HTML report generated: {html_file}")

    print("\n" + "=" * 80)
    print("🎯 RECOMMENDATIONS")
    print("=" * 80)

    # Find best configuration
    valid_results = [r for r in results if "hamming_distance" in r]
    if valid_results:
        # Sort by: test passed, then by min_contour_area (lower is more sensitive)
        best = min(valid_results, key=lambda r: (not r.get("test_passed", False), r["min_contour_area"]))

        print(f"\n🏆 Best Configuration for Input Field Detection:")
        print(f"   ├─ min_contour_area: {best['min_contour_area']}")
        print(f"   ├─ pixel_tolerance: {best['pixel_tolerance']}")
        print(f"   ├─ Hamming Distance: {best['hamming_distance']}")
        print(f"   └─ Status: {best['status']}")
        print(f"\n💡 Use this in your Robot Framework test:")
        print(f"   Compare Layouts And Generate Diff")
        print(f"       ...    pixel_tolerance={best['pixel_tolerance']}")
        print(f"       ...    min_contour_area={best['min_contour_area']}")

    print("\n" + "=" * 80)
    print("✨ Testing Complete!")
    print("=" * 80)


def generate_html_report(results, baseline_path, current_path, diffs_dir):
    """Generate HTML report with visual comparison."""

    html = f"""<!DOCTYPE html>
<html lang="cs">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ImageComparisonLibrary - Test Report</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            min-height: 100vh;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        .header p {{
            font-size: 1.1em;
            opacity: 0.9;
        }}
        .content {{
            padding: 40px;
        }}
        .info-box {{
            background: #f8f9fa;
            border-left: 4px solid #667eea;
            padding: 20px;
            margin-bottom: 30px;
            border-radius: 8px;
        }}
        .test-grid {{
            display: grid;
            gap: 30px;
            margin-top: 30px;
        }}
        .test-card {{
            border: 2px solid #e9ecef;
            border-radius: 12px;
            overflow: hidden;
            transition: transform 0.2s, box-shadow 0.2s;
        }}
        .test-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }}
        .test-header {{
            background: #667eea;
            color: white;
            padding: 20px;
        }}
        .test-header h3 {{
            font-size: 1.3em;
            margin-bottom: 10px;
        }}
        .test-params {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 10px;
            margin-top: 10px;
        }}
        .param {{
            background: rgba(255,255,255,0.2);
            padding: 8px 12px;
            border-radius: 6px;
            font-size: 0.9em;
        }}
        .test-body {{
            padding: 20px;
        }}
        .image-comparison {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 20px;
            margin-top: 20px;
        }}
        .image-box {{
            text-align: center;
        }}
        .image-box img {{
            width: 100%;
            height: auto;
            border: 2px solid #dee2e6;
            border-radius: 8px;
            cursor: pointer;
            transition: transform 0.2s;
        }}
        .image-box img:hover {{
            transform: scale(1.05);
        }}
        .image-box h4 {{
            margin-top: 10px;
            color: #495057;
            font-size: 1em;
        }}
        .status-badge {{
            display: inline-block;
            padding: 6px 12px;
            border-radius: 20px;
            font-weight: bold;
            font-size: 0.9em;
        }}
        .status-pass {{
            background: #d4edda;
            color: #155724;
        }}
        .status-fail {{
            background: #f8d7da;
            color: #721c24;
        }}
        .status-error {{
            background: #fff3cd;
            color: #856404;
        }}
        .summary {{
            background: linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%);
            padding: 30px;
            border-radius: 12px;
            margin-bottom: 30px;
        }}
        .summary h2 {{
            color: #333;
            margin-bottom: 20px;
        }}
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 20px;
        }}
        .stat-box {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }}
        .stat-box .number {{
            font-size: 2.5em;
            font-weight: bold;
            color: #667eea;
        }}
        .stat-box .label {{
            color: #6c757d;
            margin-top: 5px;
        }}
        .footer {{
            background: #f8f9fa;
            padding: 20px;
            text-align: center;
            color: #6c757d;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔍 ImageComparisonLibrary Test Report</h1>
            <p>Parameter Optimization for Input Field Detection</p>
            <p style="margin-top: 10px; font-size: 0.9em;">Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>

        <div class="content">
            <div class="info-box">
                <h2>📸 Test Images</h2>
                <p><strong>Baseline:</strong> {baseline_path.name}</p>
                <p><strong>Current:</strong> {current_path.name}</p>
            </div>

            <div class="summary">
                <h2>📊 Test Summary</h2>
                <div class="stats">
                    <div class="stat-box">
                        <div class="number">{len(results)}</div>
                        <div class="label">Total Tests</div>
                    </div>
                    <div class="stat-box">
                        <div class="number">{sum(1 for r in results if r.get("test_passed", False))}</div>
                        <div class="label">Passed</div>
                    </div>
                    <div class="stat-box">
                        <div class="number">{sum(1 for r in results if r.get("status") == "FAIL")}</div>
                        <div class="label">Failed</div>
                    </div>
                    <div class="stat-box">
                        <div class="number">{sum(1 for r in results if r.get("status") == "ERROR")}</div>
                        <div class="label">Errors</div>
                    </div>
                </div>
            </div>

            <h2 style="margin-bottom: 20px;">🧪 Test Results</h2>
            <div class="test-grid">
    """

    # Add each test result
    for result in results:
        status_class = f"status-{result['status'].lower()}"
        status_icon = "✅" if result["status"] == "PASS" else "❌" if result["status"] == "FAIL" else "⚠️"

        html += f"""
                <div class="test-card">
                    <div class="test-header">
                        <h3>{status_icon} Test {result['test_number']}: {result['description']}</h3>
                        <div class="test-params">
                            <div class="param">min_contour_area: {result['min_contour_area']}</div>
                            <div class="param">pixel_tolerance: {result['pixel_tolerance']}</div>
                            {'<div class="param">Hamming Distance: ' + str(result.get('hamming_distance', 'N/A')) + '</div>' if 'hamming_distance' in result else ''}
                        </div>
                    </div>
                    <div class="test-body">
                        <span class="status-badge {status_class}">{result['status']}</span>
        """

        if 'diff_file' in result:
            diff_path_rel = result['diff_file']
            html += f"""
                        <div class="image-comparison">
                            <div class="image-box">
                                <img src="../../libraries/images/baseline/{baseline_path.name}" alt="Baseline">
                                <h4>Baseline</h4>
                            </div>
                            <div class="image-box">
                                <img src="../../libraries/images/screenshot/{current_path.name}" alt="Current">
                                <h4>Current Screenshot</h4>
                            </div>
                            <div class="image-box">
                                <img src="../diffs/{diff_path_rel}" alt="Diff">
                                <h4>Diff (Contours)</h4>
                            </div>
                        </div>
            """
        elif 'error' in result:
            html += f"""
                        <p style="color: #721c24; margin-top: 10px;"><strong>Error:</strong> {result['error']}</p>
            """

        html += """
                    </div>
                </div>
        """

    html += """
            </div>
        </div>

        <div class="footer">
            <p>Generated by ImageComparisonLibrary Test Suite</p>
            <p>Claude Code Debugging Assistant - 2025</p>
        </div>
    </div>
</body>
</html>
    """

    return html


if __name__ == "__main__":
    try:
        run_parameter_tests()
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ FATAL ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
