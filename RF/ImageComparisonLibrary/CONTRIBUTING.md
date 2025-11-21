# Přispívání do ImageComparisonLibrary

Děkujeme za váš zájem přispět do ImageComparisonLibrary! Tento dokument poskytuje pokyny pro přispěvatele.

## 📋 Obsah

1. [Jak začít](#jak-začít)
2. [Vývojové prostředí](#vývojové-prostředí)
3. [Coding Standards](#coding-standards)
4. [Testování](#testování)
5. [Proces Pull Request](#proces-pull-request)
6. [Reportování chyb](#reportování-chyb)
7. [Návrhy nových funkcí](#návrhy-nových-funkcí)

## 🚀 Jak začít

### 1. Fork a Clone

```bash
# Fork repozitáře na GitHubu
# Poté naklonujte svůj fork
git clone https://github.com/VASE_JMENO/ImageComparisonLibrary.git
cd ImageComparisonLibrary
```

### 2. Vytvořte novou větev

```bash
git checkout -b feature/moje-nova-funkce
# nebo
git checkout -b fix/oprava-chyby
```

**Konvence názvů větví:**
- `feature/` - pro nové funkce
- `fix/` - pro opravy chyb
- `docs/` - pro úpravy dokumentace
- `refactor/` - pro refactoring kódu
- `test/` - pro přidání/úpravu testů

## 💻 Vývojové prostředí

### Požadavky

- Python 3.10 nebo vyšší
- pip nebo poetry
- Git

### Instalace vývojového prostředí

```bash
# Vytvořte virtuální prostředí
python -m venv venv

# Aktivujte virtuální prostředí
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Nainstalujte závislosti
pip install -r requirements.txt

# Nainstalujte knihovnu v editable módu
pip install -e .

# Nainstalujte vývojové nástroje (volitelné)
pip install pytest pytest-cov black flake8 mypy
```

### Struktura projektu

```
ImageComparisonLibrary/
├── ImageComparisonLibrary/     # Hlavní zdrojový kód
│   ├── __init__.py
│   ├── core.py                # Implementace keywords
│   └── version.py             # Verze
├── tests/                     # Unit testy
│   └── test_core.py
├── README.md                  # Hlavní dokumentace
├── IMPORTANT_PLACES.md        # Přehled důležitých míst v kódu
└── CONTRIBUTING.md            # Tento soubor
```

## 📝 Coding Standards

### Python kód

#### 1. Styl kódu
- Dodržujte **PEP 8** style guide
- Maximální délka řádku: **100 znaků** (místo standardních 79)
- Používejte **4 mezery** pro odsazení (ne taby)

```python
# Správně ✅
def calculate_hash(image: Image.Image, algorithm: str) -> imagehash.ImageHash:
    if algorithm == 'phash':
        return imagehash.phash(image)
    return imagehash.dhash(image)

# Špatně ❌
def calculate_hash(image,algorithm):
  if algorithm=='phash':return imagehash.phash(image)
  return imagehash.dhash(image)
```

#### 2. Type hints
- **Vždy používejte type hints** pro parametry a return hodnoty
- Používejte `Union`, `Optional`, `List`, atd. z `typing`

```python
from typing import Union
from pathlib import Path

def load_image(image: Union[str, Path, Image.Image]) -> Image.Image:
    """Načte obrázek."""
    pass
```

#### 3. Docstringy
- **Všechny public metody musí mít docstring v češtině**
- Používejte Google style docstrings
- Uveďte Args, Returns, Raises a Examples

```python
def compare_images(baseline: str, current: str, tolerance: int = 5) -> int:
    """Porovná dva obrázky pomocí perceptual hashování.

    Args:
        baseline: Cesta k baseline obrázku.
        current: Cesta k aktuálnímu obrázku.
        tolerance: Maximální povolená Hammingova vzdálenost. Výchozí: 5.

    Returns:
        int: Hammingova vzdálenost mezi obrázky.

    Raises:
        FileNotFoundError: Pokud soubor neexistuje.
        ValueError: Pokud je zadán neplatný formát.

    Examples:
        | Compare Images | baseline.png | current.png | tolerance=10 |
    """
    pass
```

#### 4. Komentáře
- Komentáře pište **v češtině**
- Vysvětlujte **PROČ**, ne CO (kód by měl být self-explanatory)
- Používejte komentáře pro komplexní logiku

```python
# Správně ✅
# Konverze do RGB je nutná, protože diff porovnává barevné kanály
if baseline_img.mode != 'RGB':
    baseline_img = baseline_img.convert('RGB')

# Špatně ❌
# Konvertuje obrázek
if baseline_img.mode != 'RGB':
    baseline_img = baseline_img.convert('RGB')
```

#### 5. Pojmenování

**Proměnné a funkce:**
- `snake_case` pro funkce, metody a proměnné
- `PascalCase` pro třídy
- `UPPER_CASE` pro konstanty

```python
# Správně ✅
MAX_TOLERANCE = 100
class ImageComparisonLibrary:
    def calculate_hash(self, image_path: str) -> str:
        hash_value = imagehash.phash(image)
        return hash_value

# Špatně ❌
maxTolerance = 100
class image_comparison_library:
    def CalculateHash(self, ImagePath: str) -> str:
        HashValue = imagehash.phash(image)
        return HashValue
```

### Robot Framework keywords

- Názvy keywords v **Title Case s mezerami**
- Začněte **slovesem** (Compare, Check, Generate, atd.)

```robot
# Správně ✅
Compare Layouts And Generate Diff
Check Layouts Are Visually Similar

# Špatně ❌
compare_layouts_and_generate_diff
Layouts Are Similar Check
```

## 🧪 Testování

### Spuštění testů

```bash
# Spuštění všech testů
python -m unittest discover tests

# Spuštění konkrétního testu
python -m unittest tests.test_core.TestImageComparisonLibrary.test_identical_images_pass

# S pytest (pokud je nainstalován)
pytest tests/ -v

# S coverage reportem
pytest tests/ --cov=ImageComparisonLibrary --cov-report=html
```

### Psaní testů

#### 1. Struktura testů
- Každý test by měl testovat **jednu věc**
- Používejte **popisné názvy testů**
- Dodržujte **AAA pattern**: Arrange, Act, Assert

```python
def test_identical_images_should_pass_comparison(self):
    # Arrange - příprava
    baseline = self.create_test_image(100, 100, 'red')
    current = self.create_test_image(100, 100, 'red')

    # Act - akce
    distance = self.lib.compare_layouts_and_generate_diff(
        baseline, current, self.diff_dir, tolerance=5
    )

    # Assert - ověření
    self.assertEqual(distance, 0)
```

#### 2. Test coverage
- Snažte se o **minimálně 80% coverage**
- Testujte **edge cases** (prázdné vstupy, velké hodnoty, atd.)
- Testujte **error scenarios** (neplatné vstupy, chybějící soubory)

```python
def test_nonexistent_file_should_raise_error(self):
    """Test ověřuje, že neexistující soubor vyvolá FileNotFoundError."""
    with self.assertRaises(FileNotFoundError):
        self.lib._load_image("/nonexistent/path.png")
```

#### 3. Test data
- Používejte **dočasné soubory** pro testy
- **Nesdílejte stav** mezi testy
- Používejte `setUp()` a `tearDown()` pro přípravu a úklid

```python
def setUp(self):
    """Příprava před každým testem."""
    self.temp_dir = tempfile.mkdtemp()
    self.diff_dir = Path(self.temp_dir) / 'diffs'
    self.lib = ImageComparisonLibrary()

def tearDown(self):
    """Úklid po každém testu."""
    shutil.rmtree(self.temp_dir)
```

#### 4. Debug skripty
Pro vývoj a ladění nových funkcí jsou k dispozici debug skripty v `tests/debug/`:

**Dostupné skripty:**
- `test_directional_diff.py` - Kompletní test směrových rozdílů (all/added/removed modes)
- `test_directional_simple.py` - Jednoduchý test s uživatelskými obrázky
- `test_debug_masks.py` - Vizualizace diff masek (binary, added, removed)

**Spuštění:**
```bash
# Z hlavní složky projektu
python tests/debug/test_directional_diff.py
python tests/debug/test_directional_simple.py
python tests/debug/test_debug_masks.py
```

**Výstupy:**
- Debug skripty ukládají výstupy do `tests/debug/outputs/`
- Diff obrázky, masky, a další vizualizace
- Používejte je pro ladění a ověření nových funkcí

**Poznámka:** Debug skripty NEJSOU součástí automatických testů. Jsou určeny pouze pro manuální ladění a vývoj.

### Požadavky na testy před pull requestem

- ✅ Všechny testy musí projít
- ✅ Nové funkce musí mít testy
- ✅ Opravy chyb by měly obsahovat regresní test
- ✅ Nepřidávejte test failures do commitu

## 🔄 Proces Pull Request

### 1. Před vytvořením PR

**Checklist:**
- [ ] Kód dodržuje coding standards
- [ ] Všechny testy procházejí
- [ ] Přidány testy pro novou funkcionalitu
- [ ] Aktualizována dokumentace (README, docstringy)
- [ ] Commit messages jsou jasné a popisné
- [ ] Větev je aktuální s main větví

```bash
# Aktualizujte svou větev
git fetch upstream
git rebase upstream/main
```

### 2. Commit messages

Používejte **jasné a popisné commit messages**:

```bash
# Dobrý commit message ✅
git commit -m "Přidána podpora pro ahash algoritmus

- Implementován average_hash algoritmus
- Přidány testy pro ahash
- Aktualizována dokumentace"

# Špatný commit message ❌
git commit -m "fix"
git commit -m "update"
```

**Formát:**
```
<typ>: <stručný popis>

<detailní popis změn>
<důvod změn>

Fixes #123
```

**Typy commitů:**
- `feat`: Nová funkce
- `fix`: Oprava chyby
- `docs`: Změny v dokumentaci
- `style`: Formátování, chybějící středníky, atd.
- `refactor`: Refaktoring kódu
- `test`: Přidání testů
- `chore`: Údržba

### 3. Vytvoření Pull Requestu

1. Push větve do vašeho forku
```bash
git push origin feature/moje-nova-funkce
```

2. Vytvořte PR na GitHubu

3. **Vyplňte PR template:**
   - Popis změn
   - Related issues (#123)
   - Checklist
   - Screenshots (pokud relevantní)

### 4. Code Review

- Buďte **otevření feedback**
- Odpovídejte na **komentáře** reviewerů
- Provádějte **požadované změny**
- **Neforce-pushujte** po začátku review (pokud není nutné)

## 🐛 Reportování chyb

### Před vytvořením issue

1. **Zkontrolujte existující issues** - možná už někdo reportoval stejnou chybu
2. **Aktualizujte na nejnovější verzi** - chyba už může být opravena

### Vytvoření Bug Reportu

**Uveďte:**
- **Popis chyby** - co se stalo?
- **Kroky k reprodukci** - jak chybu vyvolat?
- **Očekávané chování** - co by se mělo stát?
- **Aktuální chování** - co se skutečně stalo?
- **Prostředí**:
  - Verze Python
  - Verze ImageComparisonLibrary
  - Operační systém
  - Verze Robot Framework
- **Logy/Chybové zprávy** - celá chybová hláška
- **Screenshots** (pokud relevantní)

**Příklad:**
```markdown
### Popis
Diff obrázek se negeneruje při selhání porovnání na Windows.

### Kroky k reprodukci
1. Nainstalovat knihovnu na Windows 11
2. Spustit: `Compare Layouts And Generate Diff | base.png | curr.png | ./diff`
3. Porovnání selže, ale diff se nevytvoří

### Očekávané chování
Diff obrázek by měl být vytvořen v ./diff adresáři

### Aktuální chování
AssertionError se vyvolá, ale diff soubor chybí

### Prostředí
- Python 3.11.5
- ImageComparisonLibrary 1.0.0
- Windows 11
- Robot Framework 6.1.1

### Chybová zpráva
```
AssertionError: Obrázky se liší nad povolenou toleranci!
...
```
```

## 💡 Návrhy nových funkcí

### Feature Request

**Uveďte:**
- **Popis funkce** - co chcete přidat?
- **Use case** - proč je to potřeba?
- **Návrh řešení** - jak by to mohlo fungovat?
- **Alternativy** - zvažovali jste jiná řešení?

**Příklad:**
```markdown
### Popis funkce
Podpora pro SSIM (Structural Similarity Index) metriku.

### Use case
SSIM poskytuje přesnější měření podobnosti obrázků než perceptual hashing
pro případy, kdy potřebujeme detekovat jemné strukturální změny.

### Návrh řešení
Přidat nové keyword:
```robot
Compare Using SSIM | baseline.png | current.png | threshold=0.95
```

### Alternativy
- Rozšířit stávající keyword o nový parametr `algorithm=ssim`
- Vytvořit separátní keyword pouze pro SSIM
```

## 📚 Další zdroje

- [IMPORTANT_PLACES.md](IMPORTANT_PLACES.md) - Přehled důležitých míst v kódu
- [README.md](README.md) - Uživatelská dokumentace
- [Robot Framework Library API](https://robotframework.org/robotframework/latest/RobotFrameworkUserGuide.html#creating-test-libraries)
- [PEP 8](https://pep8.org/) - Python Style Guide
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)

## 🙏 Poděkování

Děkujeme všem, kdo přispívají do ImageComparisonLibrary! Vaše příspěvky pomáhají zlepšovat knihovnu pro celou komunitu.

---

**Máte otázky?** Neváhejte se zeptat v issues nebo discussions!
