# ImageComparisonLibrary - Důležitá Místa v Kódu

Tento dokument poskytuje přehled klíčových částí kódu a jejich zodpovědností.

## 📁 Struktura Projektu

```
ImageComparisonLibrary/
├── ImageComparisonLibrary/          # Hlavní balíček
│   ├── __init__.py                 # Export knihovny a veřejné API
│   ├── core.py                     # Hlavní implementace (1,454+ řádků)
│   └── version.py                  # Verze knihovny
├── tests/
│   └── test_core.py                # Jednotkové testy (12 testů)
├── requirements.txt                # Závislosti projektu
├── setup.py                        # Instalační konfigurace
├── README.md                       # Hlavní dokumentace
├── INSTALL.md                      # Instalační návod
├── PROJECT_SUMMARY.md              # Přehled projektu
└── example_test_suite.robot        # Příklady použití v RF
```

## 🆕 Nové Funkce

### Verze 1.3.0 (2024-11-19)

#### Timestamp Styling na Diff Obrázcích - ZMĚNĚNO
- **Barva**: Bílá → **Červená** (255, 0, 0)
- **Velikost**: 14 → **16** (+2 jednotky)
- **Pozice**: Pravý dolní roh → **Pravý horní roh**
- Černý stín pro čitelnost na jakémkoliv pozadí
- Formát: dd/mm/yy hh:mm:ss (např. "19/11/25 18:23:45")

#### HTML Embedding Layout - ZMĚNĚNO
- **Před (v1.2.x)**: 2 obrázky (baseline + diff) vedle sebe
- **Nyní (v1.3.0)**: **3 obrázky**:
  - Horní řádek: Baseline | Diff (vedle sebe)
  - Dolní řádek: Current Screenshot (přes celou šířku)
- Všechny obrázky jako base64 data URI
- Zobrazení přímo v Robot Framework log.html

**Důvod změn:**
- Červený timestamp lépe viditelný proti různým pozadím
- Větší font zlepšuje čitelnost
- Top-right pozice neblokuje důležitý obsah ve spodní části
- 3 obrázky poskytují kompletní přehled (baseline, current, diff)

### Verze 1.1.0-1.2.0

#### Profesionální Diff Vizualizace s Kontúrami
- **Contours mode** (výchozí): Tenké obrysy místo vyplněných oblastí
- **Filled mode**: Zachována zpětná kompatibilita s původním režimem
- **Pouze červená barva** (výchozí): Čistá vizualizace bez barevného kódování
- **Volitelné color coding**: Zelená/žlutá/červená podle závažnosti (enable_color_coding=True)

### DiffStatistics Dataclass
Nová datová struktura pro detailní statistiky porovnání:
- `total_pixels`: Celkový počet pixelů
- `different_pixels`: Počet odlišných pixelů
- `difference_percentage`: Procento rozdílů
- `minor_diff_pixels`: Drobné změny (zelená)
- `moderate_diff_pixels`: Střední změny (žlutá)
- `severe_diff_pixels`: Velké změny (červená)
- `num_contours`: Počet detekovaných kontur
- `largest_contour_area`: Největší kontura
- `average_color_difference`: Průměrný barevný rozdíl

### Nové Závislosti
- **opencv-python >= 4.8.0**: Pro detekci a vykreslování kontur
- **numpy >= 1.24.0**: Pro pole operace s obrázky

## 🎯 Klíčové Soubory a Jejich Zodpovědnosti

### 1. `ImageComparisonLibrary/__init__.py`
**Zodpovědnost:** Export veřejného API knihovny

**Důležité části:**
- **Řádek 6:** Import hlavní třídy `ImageComparisonLibrary` a `DiffStatistics` z `core.py`
- **Řádek 7:** Import verze z `version.py`
- **Řádek 9:** Definice `__all__` - co se exportuje při `from ImageComparisonLibrary import *`

### 2. `ImageComparisonLibrary/core.py`
**Zodpovědnost:** Hlavní implementace knihovny

#### Důležité části:

##### Třída ImageComparisonLibrary (řádky 11-23)
```python
class ImageComparisonLibrary:
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'  # RF konstanta - globální scope
    ROBOT_LIBRARY_VERSION = '1.0.0'  # RF konstanta - verze
```
- **Řádek 18:** `ROBOT_LIBRARY_SCOPE = 'GLOBAL'` - knihovna má globální scope v RF
- **Řádek 19:** `ROBOT_LIBRARY_VERSION` - verze pro Robot Framework

##### Compare Layouts And Generate Diff (řádky 25-113)
**⭐ HLAVNÍ KEYWORD - nejpřísnější porovnání**

**Klíčové sekce:**
- **Řádky 62-64:** Načtení obrázků pomocí `_load_image()`
- **Řádky 67-68:** Výpočet hashů pomocí `_calculate_hash()`
- **Řádek 71:** Výpočet Hammingovy vzdálenosti
- **Řádky 74-78:** ✅ ÚSPĚŠNÝ scénář - vzdálenost ≤ tolerance
- **Řádky 81-85:** ❌ Kontrola rozměrů - fail pokud se liší
- **Řádky 88-93:** ❌ Generování vizuálního diffu
- **Řádky 102-113:** ❌ Vyvolání AssertionError s detailní hláškou

**Pro úpravy:**
- Změna výchozí tolerance: řádek 31 (`tolerance: int = 5`)
- Změna výchozího algoritmu: řádek 30 (`algorithm: str = 'phash'`)

##### Check Layouts Are Visually Similar (řádky 115-158)
**⭐ DRUHÉ KEYWORD - méně přísné porovnání**

- **Řádek 120:** Výchozí algoritmus `dhash` (rychlejší)
- **Řádek 121:** Výchozí tolerance `15` (vyšší než u Compare)
- **Řádky 150-158:** Interně volá `compare_layouts_and_generate_diff()`

##### Private metody:

###### `_create_diff_mask()` (řádky 327-379)
**Zodpovědnost:** Vytvoření binární masky rozdílů mezi obrázky

**Klíčové kroky:**
- Konverze PIL obrázků na numpy pole
- Výpočet barevného rozdílu (Manhattan distance)
- Vytvoření binární masky s prahem `pixel_tolerance`
- Vrací: `(binary_mask, color_diff_array, baseline_array)`

###### `_find_contours()` (řádky 465-514)
**Zodpovědnost:** Detekce kontur v binární masce s minimálním preprocessingem

**Klíčové kroky:**
- **Malý kernel (3,3)** pro MORPH_CLOSE - zavírá malé díry bez agresivního spojování
- **BEZ dilate operací** - nesloučí oddělené oblasti dohromady
- OpenCV `findContours()` s **`RETR_EXTERNAL`** (pouze vnější kontury) a `CHAIN_APPROX_SIMPLE`
- Filtrace podle `min_contour_area` (výchozí **5000 pixelů** - zachytí velké změny jako loader)
- Vrací: seznam filtrovaných kontur

**Účel:** Detekuje JEN velké, významné změny (loader overlay, dialogy), ignoruje malé změny (input pole pod semi-transparent overlay)

###### `_classify_contour_severity()` (řádky 423-459)
**Zodpovědnost:** Klasifikace závažnosti změny v kontuře

**Třída závažnosti:**
- Minor: průměrný rozdíl ≤ pixel_tolerance * 1.5
- Moderate: průměrný rozdíl ≤ pixel_tolerance * 3.0
- Severe: větší rozdíly

###### `_draw_contours_on_diff()` (řádky 556-689)
**Zodpovědnost:** Vykreslení kontur s poloprůhlednou výplní

**Klíčové funkce:**
- **Dvouprůchodové vykreslení:**
  1. **PASS 1:** Vyplnit všechny kontury barvou na overlay
  2. **Alpha blending:** Smíchat overlay s baseline (30% výplň + 70% baseline)
  3. **PASS 2:** Vykreslit silné obrysy (thickness=3) přes smíchaný obrázek
- Volitelné barevné kódování podle závažnosti (výchozí: pouze červená)
- Konverze RGB → BGR pro OpenCV
- `cv2.drawContours()` s anti-aliasing (`cv2.LINE_AA`)
- Vrací: numpy pole s poloprůhlednou výplní + silnými obrysy

**Výsledek:** Změny jsou jasně viditelné díky růžové výplni (30% opacity) + červeným obrysům (3px)

###### `_calculate_statistics()` (řádky 561-649)
**Zodpovědnost:** Výpočet detailních statistik

- Počítá pixely podle závažnosti
- Najde největší konturu
- Vypočítá průměrný barevný rozdíl
- Vrací: `DiffStatistics` objekt

###### `_log_statistics()` (řádky 651-691)
**Zodpovědnost:** Logování statistik do RF logu

###### `_generate_html_report()` (řádky 693-876)
**Zodpovědnost:** Generování HTML reportu s porovnáním

- Side-by-side zobrazení baseline/current/diff
- Vložené obrázky jako base64
- Responzivní design
- Vrací: cestu k HTML souboru

###### `_load_image()` (řádky 878-917)
**Zodpovědnost:** Načítání obrázků z různých zdrojů

**Podporované typy:**
- `PIL.Image.Image` - přímé použití
- `str` nebo `pathlib.Path` - načtení ze souboru
- Kontrola existence souboru - raise `FileNotFoundError`

**Pro rozšíření:** Zde přidat podporu pro další formáty (numpy array, base64, atd.)

###### `_calculate_hash()` (řádky 919-965)
**Zodpovědnost:** Výpočet perceptual hashe

**Podporované algoritmy:**
- `phash` - Perceptual hash (výchozí)
- `dhash` - Difference hash (rychlejší)

**Pro rozšíření:** Zde přidat další algoritmy (ahash, whash)

###### `_generate_visual_diff()` (řádky 967-1103)
**Zodpovědnost:** Generování vizuálního diff obrázku

**Dva režimy:**
1. **'contours' mode** (výchozí): Tenké obrysy pomocí OpenCV
   - Vytvoří binární masku rozdílů
   - Detekuje kontury (filtruje šum)
   - Vykreslí kontury s volitelným barevným kódováním
   - Vypočítá detailní statistiky
   - Volitelně vygeneruje HTML report

2. **'filled' mode**: Původní režim s vyplněnými pixely
   - Pixel-by-pixel porovnání
   - Označení rozdílných pixelů červenou barvou

**Pro úpravy:**
- Změna výchozího režimu: parametr `diff_mode='contours'`
- Změna barvy kontur: parametry `minor_color`, `moderate_color`, `severe_color`
- Změna tloušťky kontur: parametr `contour_thickness`
- Změna filtru šumu: parametr `min_contour_area`

###### `_encode_image_to_base64()` (řádky 1302-1332)
**Zodpovědnost:** Enkódování obrázku do base64 data URI

- Podporuje `PIL.Image.Image` nebo `Path`
- Konverze do PNG formátu
- Vrací: data URI string (`data:image/png;base64,...`)
- Použití: embedování obrázků do HTML logu

###### `_log_images_to_html()` (řádky 1334-1396)
**Zodpovědnost:** Logování obrázků do Robot Framework HTML logu

**ZMĚNĚNO v 1.3.0:**
- **Před**: 2 obrázky (baseline + diff) vedle sebe
- **Nyní**: **3 obrázky** - baseline + diff v horním řádku, current screenshot v dolním řádku

**Parametry:**
- `baseline_img`: Baseline PIL Image
- `current_img`: Current PIL Image (NOVÝ v 1.3.0)
- `diff_path`: Cesta k diff obrázku

**HTML struktura:**
- Tabulka se 2 sloupci
- Řádek 1: Baseline | Diff (vedle sebe)
- Řádek 2: Current Screenshot (přes celou šířku - colspan="2")
- Všechny obrázky jako base64 data URI

###### `_add_timestamp_to_image()` (řádky 1384-1454)
**Zodpovědnost:** Přidání timestamp overlay na diff obrázek

**ZMĚNĚNO v 1.3.0:**

| Aspekt | Před (v1.2.x) | Nyní (v1.3.0) |
|--------|--------------|---------------|
| Barva | Bílá (255,255,255) | **Červená (255,0,0)** |
| Velikost | 14 | **16** |
| Pozice | Pravý dolní roh | **Pravý horní roh** |

**Parametry:**
- `image`: PIL Image pro přidání timestampu
- `timestamp_text`: Řetězec s časem (např. "19/11/25 18:23:45")
- `padding`: Odsazení od okrajů (výchozí: 10px)
- `font_size`: Velikost fontu (výchozí: 16)

**Funkce:**
- Červený text s černým stínem (4 směry) pro čitelnost
- Pokus o načtení Arial fontu, fallback na výchozí
- Pozice: `x = img_width - text_width - padding`, `y = padding`
- Vrací: upravený PIL Image

###### `_get_image_path()` (řádky 1105-1104)
**Zodpovědnost:** Získání cesty k obrázku pro error messages

### 3. `ImageComparisonLibrary/version.py`
**Zodpovědnost:** Správa verze knihovny

```python
__version__ = "1.0.0"
```

**Pro úpravy:** Změnit verzi při release (semantic versioning: MAJOR.MINOR.PATCH)

### 4. `setup.py`
**Zodpovědnost:** Instalační konfigurace pro pip

**Důležité části:**
- **Řádky 7-9:** Načtení verze z `version.py`
- **Řádky 12-13:** Načtení dependencies z `requirements.txt`
- **Řádky 22-51:** Metadata balíčku
  - **Řádek 25-26:** ⚠️ PLACEHOLDER - autor a email
  - **Řádek 30:** ⚠️ PLACEHOLDER - URL repozitáře
  - **Řádky 32-43:** Classifiers pro PyPI
  - **Řádek 45:** Minimální Python verze: 3.10+

### 5. `tests/test_core.py`
**Zodpovědnost:** Unit testy knihovny

**12 testových případů:**
1. `test_identical_images_pass` - identické obrázky projdou
2. `test_different_images_fail` - různé obrázky selžou
3. `test_different_dimensions_fail` - různé rozměry selžou
4. `test_pil_image_input` - podpora PIL.Image
5. `test_pathlib_path_input` - podpora pathlib.Path
6. `test_string_path_input` - podpora str cesty
7. `test_phash_algorithm` - phash algoritmus
8. `test_dhash_algorithm` - dhash algoritmus
9. `test_invalid_algorithm_raises_error` - neplatný algoritmus
10. `test_check_layouts_are_visually_similar` - druhé keyword
11. `test_nonexistent_file_raises_error` - neexistující soubor
12. `test_tolerance_parameter` - tolerance parametr

## 🔧 Běžné Úpravy a Kde Je Provést

### Přidání nového hashovacího algoritmu
**Soubor:** `core.py`
**Místo:** Metoda `_calculate_hash()` (řádky 186-213)

```python
def _calculate_hash(self, image: Image.Image, algorithm: str, hash_size: int):
    if algorithm == 'phash':
        return imagehash.phash(image, hash_size=hash_size)
    elif algorithm == 'dhash':
        return imagehash.dhash(image, hash_size=hash_size)
    elif algorithm == 'ahash':  # ← PŘIDAT NOVÝ
        return imagehash.average_hash(image, hash_size=hash_size)
    else:
        raise ValueError(...)
```

### Změna barvy označení rozdílů v diff obrázku
**Soubor:** `core.py`

**Pro contours mode (výchozí):**
**Místo:** Při volání `compare_layouts_and_generate_diff()`

```python
# Výchozí: pouze červená pro všechny změny
Compare Layouts And Generate Diff
    ...    enable_color_coding=False    severe_color=(255,0,0)

# S barevným kódováním podle závažnosti
Compare Layouts And Generate Diff
    ...    enable_color_coding=True
    ...    minor_color=(0,255,0)        # Zelená
    ...    moderate_color=(255,255,0)   # Žlutá
    ...    severe_color=(255,0,0)       # Červená
```

**Pro filled mode (starý režim):**
**Místo:** Metoda `_generate_visual_diff()` v části filled mode

```python
if color_diff > pixel_tolerance:
    diff_pixels[x, y] = (255, 0, 0)  # Červená
    # Alternativy:
    # diff_pixels[x, y] = (255, 255, 0)  # Žlutá
    # diff_pixels[x, y] = (0, 255, 0)    # Zelená
```

### Změna výchozích hodnot parametrů
**Soubor:** `core.py`
**Místo:** Signatura metody `compare_layouts_and_generate_diff()` (řádky 60-79)

```python
def compare_layouts_and_generate_diff(
    self,
    baseline_image: Union[str, Path, Image.Image],
    current_image: Union[str, Path, Image.Image],
    diff_directory: Union[str, Path],
    algorithm: str = 'phash',         # ← výchozí algoritmus
    tolerance: int = 5,                # ← výchozí tolerance
    pixel_tolerance: int = 60,         # ← tolerance pro diff (optimalizováno pro semi-transparent overlay)
    hash_size: int = 8,                # ← velikost hashe
    diff_mode: str = 'contours',       # ← režim diffu (contours/filled)
    contour_thickness: int = 3,        # ← tloušťka obrysů (nové)
    min_contour_area: int = 5000,      # ← filtrování malých změn (zachytí velké objekty)
    enable_color_coding: bool = False  # ← barevné kódování (výchozí jen červená)
) -> int:
```

**Use cases:**
- `pixel_tolerance=60, min_contour_area=5000`: Výchozí - ignoruje semi-transparent změny, detekuje velké objekty
- `pixel_tolerance=45, min_contour_area=1500`: Pro kompletní loader overlay (včetně světlých částí)
- `pixel_tolerance=25, min_contour_area=100`: Pro detailní pixel-level detekci

### Přidání podpory pro nový formát vstupu
**Soubor:** `core.py`
**Místo:** Metoda `_load_image()` (řádky 160-184)

```python
def _load_image(self, image: Union[str, Path, Image.Image]) -> Image.Image:
    if isinstance(image, Image.Image):
        return image
    elif isinstance(image, (str, Path)):
        # ... načtení ze souboru
    elif isinstance(image, np.ndarray):  # ← PŘIDAT numpy support
        return Image.fromarray(image)
    else:
        raise ValueError(...)
```

### Změna formátu názvu diff souboru
**Soubor:** `core.py`
**Místo:** Metoda `_generate_visual_diff()` (řádky 269-271)

```python
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
diff_filename = f"diff_{timestamp}.png"
# Alternativy:
# diff_filename = f"visual_diff_{timestamp}.png"
# diff_filename = f"{baseline_name}_vs_{current_name}_diff.png"
```

## 🧪 Testování

### Spuštění všech testů
```bash
python -m unittest discover tests
```

### Spuštění konkrétního testu
```bash
python -m unittest tests.test_core.TestImageComparisonLibrary.test_identical_images_pass
```

### Přidání nového testu
**Soubor:** `tests/test_core.py`
**Místo:** Do třídy `TestImageComparisonLibrary`

## 📊 Metriky a Limity

### Aktuální limity:
- **Podporované formáty obrázků:** Vše, co podporuje PIL (PNG, JPEG, BMP, GIF, atd.)
- **Maximální rozlišení:** Limitováno pouze pamětí
- **Podporované Python verze:** 3.10+
- **Podporované algoritmy:** 2 (phash, dhash)

### Performance:
- **phash:** ~50-100ms pro 1920x1080 obrázek
- **dhash:** ~30-70ms pro 1920x1080 obrázek
- **diff generování:** ~200-500ms pro 1920x1080 obrázek

## 🔮 Možná Budoucí Rozšíření

### 1. Podpora více algoritmů
- ahash (Average Hash)
- whash (Wavelet Hash)
- colorhash (Color Hash)

### 2. Pokročilé metriky
- SSIM (Structural Similarity Index)
- MSE (Mean Squared Error)
- PSNR (Peak Signal-to-Noise Ratio)

### 3. ✅ HTML reporty (IMPLEMENTOVÁNO v 1.1.0)
- ✅ Automatické generování HTML reportu s diff obrázky
- ✅ Side-by-side porovnání baseline vs current
- ✅ Responzivní design
- ⏳ Statistiky testů (částečně - statistiky jsou v logu)

### 4. Batch porovnání
- Porovnání více obrázků najednou
- Paralelní zpracování

### 5. Inteligentní ignorování oblastí
- Maskování dynamických oblastí (čas, datum, reklamy)
- Ignorování specifických regionů

### 6. ✅ Profesionální Diff Vizualizace (IMPLEMENTOVÁNO v 1.1.0)
- ✅ Tenké obrysy místo vyplněných oblastí
- ✅ Volitelné barevné kódování podle závažnosti
- ✅ Filtrace šumu (min_contour_area)
- ✅ Detailní statistiky (DiffStatistics)
- ✅ OpenCV integrace pro contour detection

## 📞 Kontaktní Body pro Podporu

### Reportování chyb:
- GitHub Issues (pokud je repozitář veřejný)
- Email autora (z setup.py)

### Přispívání:
- Fork repozitáře
- Vytvořit feature branch
- Otevřít Pull Request

---

**Poslední aktualizace:** 2024-11-19
**Verze knihovny:** 1.3.0 (nové změny: červený timestamp nahoře vpravo, 3-image HTML layout, viz verze historie výše)
