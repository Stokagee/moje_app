"""ImageComparisonLibrary - Robot Framework library for image comparison and visual regression testing.

ImageComparisonLibrary - Robot Framework knihovna pro porovnávání obrázků a vizuální regresní testování.
"""

from .core import ImageComparisonLibrary, DiffStatistics
from .version import __version__

__all__ = ['ImageComparisonLibrary', 'DiffStatistics', '__version__']
