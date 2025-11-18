"""Setup script for ImageComparisonLibrary."""

from setuptools import setup, find_packages
from pathlib import Path

# Read version from version.py
version = {}
with open("ImageComparisonLibrary/version.py") as f:
    exec(f.read(), version)

# Read requirements
with open("requirements.txt") as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]

# Read README if it exists
readme_path = Path("README.md")
long_description = ""
if readme_path.exists():
    with open(readme_path, encoding="utf-8") as f:
        long_description = f.read()

setup(
    name="robotframework-imagecomparisonlibrary",
    version=version["__version__"],
    author="Your Name",
    author_email="your.email@example.com",
    description="Robot Framework library for image comparison and visual regression testing",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/ImageComparisonLibrary",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Testing",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Framework :: Robot Framework",
        "Framework :: Robot Framework :: Library",
    ],
    keywords="robotframework testing test automation image comparison visual regression",
    python_requires=">=3.10",
    install_requires=requirements,
    project_urls={
        "Bug Reports": "https://github.com/yourusername/ImageComparisonLibrary/issues",
        "Source": "https://github.com/yourusername/ImageComparisonLibrary",
    },
)
