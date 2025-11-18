# Instalační Návod - ImageComparisonLibrary

## Rychlá Instalace

### 1. Klonování nebo stažení projektu

```bash
git clone <repository-url>
cd ImageComparisonLibrary
```

### 2. Instalace závislostí

```bash
pip install -r requirements.txt
```

### 3. Instalace knihovny

#### Vývojová instalace (doporučeno pro vývoj)
```bash
pip install -e .
```

#### Produkční instalace
```bash
pip install .
```

## Ověření Instalace

### 1. Spuštění unit testů

```bash
python -m unittest discover tests
```

Všechny testy by měly projít (12 testů).

### 2. Generování Robot Framework dokumentace

```bash
python -m robot.libdoc ImageComparisonLibrary ImageComparisonLibrary.html
```

Otevřete `ImageComparisonLibrary.html` v prohlížeči pro přehled všech klíčových slov.

### 3. Testování v Robot Frameworku

Vytvořte testovací soubor `quick_test.robot`:

```robot
*** Settings ***
Library    ImageComparisonLibrary

*** Test Cases ***
Quick Import Test
    Log    ImageComparisonLibrary successfully imported!
```

Spusťte test:

```bash
robot quick_test.robot
```

## Použití v Robot Frameworku

### Základní použití

```robot
*** Settings ***
Library    ImageComparisonLibrary

*** Variables ***
${BASELINE_DIR}    ./baseline_images
${CURRENT_DIR}     ./current_images
${DIFF_DIR}        ./results/diffs

*** Test Cases ***
Compare Screenshots
    Compare Layouts And Generate Diff
    ...    ${BASELINE_DIR}/homepage.png
    ...    ${CURRENT_DIR}/homepage.png
    ...    ${DIFF_DIR}
```

### Pokročilé použití

```robot
*** Test Cases ***
Compare With Custom Settings
    ${distance}=    Compare Layouts And Generate Diff
    ...    ${BASELINE_DIR}/dashboard.png
    ...    ${CURRENT_DIR}/dashboard.png
    ...    ${DIFF_DIR}
    ...    algorithm=dhash
    ...    tolerance=10
    ...    pixel_tolerance=15
    ...    hash_size=16
    Log    Hamming distance: ${distance}
```

## Integrace s Selenium/Browser Library

```robot
*** Settings ***
Library    SeleniumLibrary
Library    ImageComparisonLibrary

*** Test Cases ***
Visual Regression Test
    Open Browser    https://example.com    chrome
    Maximize Browser Window
    Sleep    2s    # Wait for page load
    
    Capture Page Screenshot    ${CURRENT_DIR}/homepage.png
    
    Compare Layouts And Generate Diff
    ...    ${BASELINE_DIR}/homepage.png
    ...    ${CURRENT_DIR}/homepage.png
    ...    ${DIFF_DIR}
    ...    tolerance=10
    
    Close Browser
```

## Troubleshooting

### Chyba: ModuleNotFoundError

Ujistěte se, že máte nainstalované všechny závislosti:

```bash
pip install robotframework Pillow imagehash
```

### Chyba: Permission denied při ukládání diff

Ujistěte se, že diff adresář existuje a máte práva pro zápis:

```bash
mkdir -p results/diffs
chmod 755 results/diffs
```

### Chyba: Images have different dimensions

Tato chyba znamená, že porovnávané obrázky mají různé rozměry. Ujistěte se, že:
- Screenshoty se pořizují ve stejném rozlišení
- Viewport prohlížeče je stejný
- Obrázky nebyly dodatečně upravovány

## Generování Baseline Obrázků

Při první implementaci testů je potřeba vytvořit baseline obrázky:

```robot
*** Test Cases ***
Generate Baseline Images
    Open Browser    https://example.com    chrome
    Maximize Browser Window
    Sleep    2s
    
    Capture Page Screenshot    ${BASELINE_DIR}/homepage.png
    Capture Page Screenshot    ${BASELINE_DIR}/login.png
    Capture Page Screenshot    ${BASELINE_DIR}/dashboard.png
    
    Close Browser
```

## Continuous Integration

### GitHub Actions

```yaml
name: Visual Regression Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -e .
      - name: Run tests
        run: robot tests/
      - name: Upload diff images
        if: failure()
        uses: actions/upload-artifact@v2
        with:
          name: diff-images
          path: results/diffs/
```

## Doporučení

1. **Stabilní prostředí**: Pro konzistentní výsledky používejte stejný prohlížeč, rozlišení a operační systém
2. **Wait strategie**: Používejte explicitní čekání místo `Sleep` pro lepší stabilitu
3. **Tolerance**: Začněte s nižší tolerancí (5-10) a postupně zvyšujte podle potřeby
4. **Baseline management**: Udržujte baseline obrázky ve verzovacím systému
5. **Diff review**: Pravidelně kontrolujte vygenerované diff obrázky
