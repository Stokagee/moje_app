# ImageComparisonLibrary

Robustní Python knihovna pro Robot Framework určená k regresnímu testování UI pomocí porovnávání obrázků.

## Popis

ImageComparisonLibrary poskytuje klíčová slova pro porovnání aktuálního screenshotu proti "zlatému standardu" (baseline). Využívá perceptual hashing pro rychlou detekci změn a Pillow pro generování vizuálních diff obrázků.

## Instalace

### Z lokálního adresáře

```bash
pip install -e .
```

### Z requirements.txt

```bash
pip install -r requirements.txt
```

## Požadavky

- Python 3.10+
- Robot Framework 6.0+
- Pillow 9.0.0+
- imagehash 4.3.0+

## Klíčová slova

### Compare Layouts And Generate Diff

Hlavní, nejpřísnější klíčové slovo pro regresní testy.

**Signatura:**
```robot
Compare Layouts And Generate Diff
    [Arguments]    ${baseline_image}    ${current_image}    ${diff_directory}
    ...           algorithm=phash    tolerance=5    pixel_tolerance=10    hash_size=8
```

**Parametry:**
- `baseline_image` (povinný): Referenční obrázek (cesta, pathlib.Path, nebo PIL.Image)
- `current_image` (povinný): Aktuální obrázek k ověření
- `diff_directory` (povinný): Adresář pro uložení diff obrázku při selhání
- `algorithm` (volitelný, výchozí 'phash'): Hashovací algoritmus ('phash' nebo 'dhash')
- `tolerance` (volitelný, výchozí 5): Maximální povolená Hammingova vzdálenost
- `pixel_tolerance` (volitelný, výchozí 10): Tolerance barevného rozdílu (0-255)
- `hash_size` (volitelný, výchozí 8): Velikost hashovací mřížky

**Příklady:**
```robot
*** Settings ***
Library    ImageComparisonLibrary

*** Variables ***
${BASELINE_DIR}    ${CURDIR}/baseline_images
${RESULTS_DIR}     ${CURDIR}/results
${DIFF_DIR}        ${RESULTS_DIR}/diffs

*** Test Cases ***
Verify Login Page Layout
    [Documentation]    Ověří, že layout přihlašovací stránky odpovídá baseline
    Capture Page Screenshot    ${RESULTS_DIR}/login_page.png
    Compare Layouts And Generate Diff
    ...    ${BASELINE_DIR}/login_page.png
    ...    ${RESULTS_DIR}/login_page.png
    ...    ${DIFF_DIR}

Verify Dashboard With Custom Tolerance
    [Documentation]    Ověří dashboard s vyšší tolerancí
    Capture Page Screenshot    ${RESULTS_DIR}/dashboard.png
    Compare Layouts And Generate Diff
    ...    ${BASELINE_DIR}/dashboard.png
    ...    ${RESULTS_DIR}/dashboard.png
    ...    ${DIFF_DIR}
    ...    algorithm=dhash
    ...    tolerance=10
```

### Check Layouts Are Visually Similar

Méně přísné klíčové slovo pro rychlejší, hrubší srovnání.

**Signatura:**
```robot
Check Layouts Are Visually Similar
    [Arguments]    ${baseline_image}    ${current_image}    ${diff_directory}
    ...           algorithm=dhash    tolerance=15    pixel_tolerance=10    hash_size=8
```

**Parametry:** Stejné jako u `Compare Layouts And Generate Diff`, ale s odlišnými výchozími hodnotami (tolerance=15, algorithm=dhash).

**Příklady:**
```robot
*** Test Cases ***
Quick Visual Check
    [Documentation]    Rychlé vizuální ověření s vyšší tolerancí
    Capture Page Screenshot    ${RESULTS_DIR}/homepage.png
    Check Layouts Are Visually Similar
    ...    ${BASELINE_DIR}/homepage.png
    ...    ${RESULTS_DIR}/homepage.png
    ...    ${DIFF_DIR}
```

## Chování knihovny

### Úspěšný scénář
Pokud je Hammingova vzdálenost ≤ tolerance:
- Vypočítá se vzdálenost
- Zapíše se INFO log: "Layouty jsou si podobné. Vzdálenost: X (práh: Y)."
- Vrátí se hodnota vzdálenosti (int)
- Negeneruje se žádný diff obrázek

### Neúspěšný scénář
Pokud je Hammingova vzdálenost > tolerance:
- Vypočítá se vzdálenost
- Ověří se, že oba obrázky mají stejné rozměry
- Vygeneruje se vizuální diff obrázek:
  - Pixely lišící se více než `pixel_tolerance` se přebarví na červenou
- Diff se uloží do `diff_directory` s unikátním názvem
- Vyvolá se `AssertionError` s detailní chybovou hláškou

## Příklad chybové hlášky

```
AssertionError: Obrázky se liší nad povolenou toleranci!

Detaily porovnání:
  - Baseline obrázek: /path/to/baseline.png
  - Aktuální obrázek: /path/to/current.png
  - Použitý algoritmus: phash (hash_size=8)
  - Hammingova vzdálenost: 18
  - Nastavená tolerance: 5

Vizuální rozdíly byly uloženy do: /path/to/results/diffs/diff_20241118_143022_123456.png
```

## Hashovací algoritmy

### phash (Perceptual Hash)
- Výchozí algoritmus
- Dobře rozpoznává strukturální změny
- Odolný vůči drobným změnám barev a světelným podmínkám

### dhash (Difference Hash)
- Rychlejší než phash
- Zaměřuje se na gradienty a rozdíly mezi sousedními pixely
- Vhodný pro rychlé, méně přísné srovnání

## Struktura projektu

```
ImageComparisonLibrary/
├── ImageComparisonLibrary/
│   ├── __init__.py
│   ├── core.py           # Hlavní implementace
│   └── version.py        # Verze knihovny
├── tests/
│   └── test_core.py      # Jednotkové testy
├── requirements.txt      # Závislosti
├── setup.py             # Instalační skript
└── README.md            # Dokumentace
```

## Testování

Spuštění jednotkových testů:

```bash
python -m pytest tests/
```

Nebo pomocí unittest:

```bash
python -m unittest discover tests
```

## Licence

Apache License 2.0

## Podpora

Pro hlášení chyb nebo feature requesty použijte GitHub Issues.
