# Docker Testing Environment - ImageComparisonLibrary

This document describes how to use the Docker environment for testing ImageComparisonLibrary in an isolated environment.

## Overview

The Docker setup provides:
- **Isolated testing environment** - No interference with local Python installation
- **Consistent dependencies** - Same Python version and libraries across all machines
- **Access to user's test images** - Mounted from `C:/Users/stoka/Documents/moje_app/RF/libraries/images`
- **Debug script execution** - Run diagnostic and reproduction scripts

## Directory Structure

```
ImageComparisonLibrary/
├── Dockerfile                      # Docker image definition
├── docker-compose.yml              # Service orchestration
├── .dockerignore                   # Files excluded from build
└── tests/debug/
    ├── test_robot_repro.py         # Robot Framework test reproduction
    ├── test_diagnostic.py          # Diagnostic analysis script
    └── outputs/                    # Test outputs (mounted volume)
```

## Prerequisites

- Docker Desktop installed and running
- Access to user's image directory: `C:/Users/stoka/Documents/moje_app/RF/libraries/images`

## Services

### 1. imagelib-test
Runs the Robot Framework test reproduction script.

**Purpose:** Replicates the exact behavior of `te.robot` test to debug blue rectangle issue.

**Command:**
```bash
docker-compose run imagelib-test
```

**Expected Output:**
- Test failure (expected behavior)
- Diff image generated in `tests/debug/outputs/robot_repro/`
- Analysis of whether red contours are drawn correctly

### 2. imagelib-diagnostic
Runs comprehensive diagnostic analysis.

**Purpose:** Analyzes masks, contours, parameter types to identify root cause.

**Command:**
```bash
docker-compose run imagelib-diagnostic
```

**Expected Output:**
- Mask pixel counts (binary, added, removed)
- Contour detection results with different thresholds
- Parameter type analysis (tuple vs string)
- Diagnostic mask images saved to `tests/debug/outputs/diagnostic/`

### 3. imagelib-shell
Interactive shell for manual testing.

**Purpose:** Explore the library and run custom tests.

**Command:**
```bash
docker-compose run imagelib-shell
```

**Usage:**
```bash
# Inside the container
python test_robot_repro.py
python test_diagnostic.py
python -c "from ImageComparisonLibrary import ImageComparisonLibrary; print('OK')"
```

## Quick Start

### 1. Build the Docker Image

```bash
cd C:\Users\stoka\Documents\moje_app\RF\ImageComparisonLibrary
docker-compose build
```

**Expected output:**
- Image built successfully
- Dependencies installed
- Library installed in editable mode

### 2. Run Robot Framework Reproduction Test

```bash
docker-compose run imagelib-test
```

**What to check:**
- Does test fail as expected?
- Is diff image generated?
- What color are the contours? (Should be RED, currently BLUE)
- Is the entire Email input highlighted? (Currently only small area)

### 3. Run Diagnostic Analysis

```bash
docker-compose run imagelib-diagnostic
```

**What to check:**
- Mask pixel counts - are added pixels detected?
- Contour counts - how many contours at different thresholds?
- Parameter types - is severe_color received as tuple or string?
- Visual masks in `outputs/diagnostic/` - does mask_added.png show shifted input?

### 4. Check Output Files

```bash
# Robot repro outputs
dir tests\debug\outputs\robot_repro

# Diagnostic outputs
dir tests\debug\outputs\diagnostic
```

**Expected files:**
- `robot_repro/diff_*.png` - Diff image from test reproduction
- `diagnostic/mask_binary.png` - All changes mask
- `diagnostic/mask_added.png` - Added pixels only (shifted input)
- `diagnostic/mask_removed.png` - Removed pixels only (original position)

## Troubleshooting

### Docker build fails
```bash
# Clean build
docker-compose build --no-cache
```

### Permission denied on outputs folder
```bash
# Create outputs folder manually
mkdir tests\debug\outputs
```

### Image not found error
```bash
# Verify image paths in docker-compose.yml
# Check that C:/Users/stoka/Documents/moje_app/RF/libraries/images exists
dir C:\Users\stoka\Documents\moje_app\RF\libraries\images\baseline
dir C:\Users\stoka\Documents\moje_app\RF\libraries\images\screenshot
```

### Container exits immediately
```bash
# Check logs
docker-compose logs imagelib-test

# Run with interactive shell
docker-compose run imagelib-shell
```

## Current Investigation

**Problem:** Diff shows small BLUE rectangle instead of large RED rectangle around shifted Email input.

**Hypotheses:**
1. **Parameter Type Issue:** Robot Framework may be passing `severe_color=(255, 0, 0)` as string `"(255, 0, 0)"` instead of Python tuple
2. **Contour Fragmentation:** Added pixels may form many small contours, filtered by `min_contour_area=50`
3. **Wrong Mask Selection:** Library might be using wrong mask despite `highlight_mode='added'`

**Diagnostic Steps:**
1. Run `test_diagnostic.py` to check mask generation and parameter types
2. Run `test_robot_repro.py` to reproduce exact issue
3. Compare diagnostic mask images with actual diff output
4. Identify root cause and propose fix

## Notes

- **Read-only volume:** User's images are mounted as read-only (`:ro`) to prevent accidental modifications
- **Output volume:** `tests/debug/outputs/` is writable for saving results
- **No code modifications:** As per user's requirement, NO changes to production code without explicit approval
- **Docker-only testing:** All experiments must be done in Docker environment first

## Next Steps After Testing

1. Analyze outputs from both scripts
2. Compare results with user's actual te.robot outputs
3. Identify root cause of blue rectangle issue
4. Propose fix (with user approval required)
5. Update main library code (only after user approval)

---

**Created:** 2024-11-21
**Purpose:** Isolated testing environment for debugging blue rectangle issue
