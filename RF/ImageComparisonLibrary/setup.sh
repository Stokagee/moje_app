#!/bin/bash
# Quick setup script for ImageComparisonLibrary

echo "======================================"
echo "ImageComparisonLibrary - Quick Setup"
echo "======================================"
echo ""

# Check Python version
echo "1. Checking Python version..."
python_version=$(python --version 2>&1 | awk '{print $2}')
echo "   Python version: $python_version"

# Check if Python 3.10+
if python -c "import sys; exit(0 if sys.version_info >= (3, 10) else 1)" 2>/dev/null; then
    echo "   ✓ Python version is 3.10 or higher"
else
    echo "   ✗ Warning: Python 3.10+ is recommended"
fi
echo ""

# Install dependencies
echo "2. Installing dependencies..."
pip install -q robotframework Pillow imagehash
if [ $? -eq 0 ]; then
    echo "   ✓ Dependencies installed successfully"
else
    echo "   ✗ Error installing dependencies"
    exit 1
fi
echo ""

# Install library in development mode
echo "3. Installing ImageComparisonLibrary..."
pip install -q -e .
if [ $? -eq 0 ]; then
    echo "   ✓ Library installed successfully"
else
    echo "   ✗ Error installing library"
    exit 1
fi
echo ""

# Run unit tests
echo "4. Running unit tests..."
python -m unittest discover tests -v
if [ $? -eq 0 ]; then
    echo ""
    echo "   ✓ All tests passed!"
else
    echo ""
    echo "   ✗ Some tests failed"
    exit 1
fi
echo ""

# Generate documentation
echo "5. Generating Robot Framework documentation..."
python -m robot.libdoc ImageComparisonLibrary ImageComparisonLibrary.html
if [ $? -eq 0 ]; then
    echo "   ✓ Documentation generated: ImageComparisonLibrary.html"
else
    echo "   ⚠ Warning: Could not generate documentation"
fi
echo ""

echo "======================================"
echo "✓ Setup completed successfully!"
echo "======================================"
echo ""
echo "Next steps:"
echo "  1. Check PROJECT_SUMMARY.md for overview"
echo "  2. Read INSTALL.md for usage instructions"
echo "  3. See example_test_suite.robot for examples"
echo "  4. Open ImageComparisonLibrary.html for keyword documentation"
echo ""
echo "Quick test:"
echo "  python -c 'from ImageComparisonLibrary import ImageComparisonLibrary; print(\"✓ Import successful!\")'"
echo ""
