"""Visual regression testing library for Robot Framework.

= Introduction =

ImageComparisonLibrary helps you catch unexpected UI changes by comparing
screenshots against baseline images. Perfect for automated regression tests
in CI/CD pipelines.

Uses perceptual hashing (phash/dhash) for fast comparison and OpenCV for
generating visual diff images with highlighted changes.

= Quick Start =

Basic usage in Robot Framework tests:

| Library | ImageComparisonLibrary |
|
| Compare Layouts And Generate Diff | baseline.png | current.png | ./diffs |

For relaxed comparison with higher tolerance:

| Check Layouts Are Visually Similar | baseline.png | current.png | ./diffs |

= When To Use =

*Strict Comparison* (``Compare Layouts And Generate Diff``):
- Login pages, checkout flows, critical UI elements
- Need exact visual match with low tolerance
- Default tolerance: 5, algorithm: phash

*Relaxed Comparison* (``Check Layouts Are Visually Similar``):
- Pages with dynamic content (timestamps, usernames, counters)
- Charts, graphs with changing data
- Default tolerance: 15, algorithm: dhash

= Key Features =

- Fast perceptual hashing (phash, dhash algorithms)
- Visual diff images with highlighted changes
- Semi-transparent overlays and contour outlines
- Automatic embedding of images into RF log.html
- Configurable tolerance and filtering
- Support for PNG, JPG, and other image formats

= Installation =

Install from local directory:

| pip install -e .

Or from requirements.txt:

| pip install -r requirements.txt

= See Also =

- GitHub: https://github.com/yourusername/ImageComparisonLibrary
- Robot Framework: https://robotframework.org
- Documentation: README.md and INSTALL.md

---

= Úvod =

ImageComparisonLibrary vám pomůže zachytit neočekávané změny v UI porovnáním
screenshotů s baseline obrázky. Perfektní pro automatizované regresní testy
v CI/CD pipelines.

Používá perceptual hashing (phash/dhash) pro rychlé porovnání a OpenCV pro
generování vizuálních diff obrázků se zvýrazněnými změnami.

= Rychlý start =

Základní použití v Robot Framework testech:

| Library | ImageComparisonLibrary |
|
| Compare Layouts And Generate Diff | baseline.png | current.png | ./diffs |

Pro uvolněnější porovnání s vyšší tolerancí:

| Check Layouts Are Visually Similar | baseline.png | current.png | ./diffs |

= Kdy použít =

*Přísné porovnání* (``Compare Layouts And Generate Diff``):
- Přihlašovací stránky, checkout, kritické UI elementy
- Potřeba přesné vizuální shody s nízkou tolerancí
- Výchozí tolerance: 5, algoritmus: phash

*Uvolněné porovnání* (``Check Layouts Are Visually Similar``):
- Stránky s dynamickým obsahem (časové značky, uživatelská jména, počítadla)
- Grafy s měnícími se daty
- Výchozí tolerance: 15, algoritmus: dhash

= Klíčové vlastnosti =

- Rychlý perceptual hashing (phash, dhash algoritmy)
- Vizuální diff obrázky se zvýrazněnými změnami
- Poloprůhledné překrytí a obrysy kontur
- Automatické vložení obrázků do RF log.html
- Konfigurovatelná tolerance a filtrování
- Podpora PNG, JPG a dalších obrazových formátů

= Instalace =

Instalace z lokálního adresáře:

| pip install -e .

Nebo z requirements.txt:

| pip install -r requirements.txt

= Viz také =

- GitHub: https://github.com/yourusername/ImageComparisonLibrary
- Robot Framework: https://robotframework.org
- Dokumentace: README.md a INSTALL.md
"""

from .core import ImageComparisonLibrary, DiffStatistics
from .version import __version__

__all__ = ['ImageComparisonLibrary', 'DiffStatistics', '__version__']
