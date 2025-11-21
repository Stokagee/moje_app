# ImageComparisonLibrary - Debugging Report
**Datum:** 2025-11-20
**Problém:** Test failnul, ale diff obrázek nevykreslil viditelné změny
**Analyzováno:** Claude Code Debugging Assistant

---

## 🔍 IDENTIFIKOVANÝ PROBLÉM

### Původní Parametry (te.robot:36-38)
```robot
Compare Layouts And Generate Diff
    ${BASELINE_IMAGE_PATH}login_page_20251118_174339.png
    ${image_for_test}
    ${diff_image_path}
    ...    pixel_tolerance=45
    ...    hash_size=16
    ...    diff_mode=contours
    ...    contour_thickness=3
    ...    min_contour_area=1500     # ← PROBLÉM JE TADY!
    ...    minor_color=(0, 255, 0)
    ...    moderate_color=(0, 255, 255)
    ...    severe_color=(0, 0, 255)
```

### Co Bylo Špatně?

**`min_contour_area=1500` je příliš vysoké!**

- Tento parametr filtruje kontury menší než 1500 pixelů
- Posun input fieldu vytváří **malé kontury** (několik set pixelů)
- Všechny malé kontury byly **odfiltrovány**
- Diff obrázek byl vytvořen, ale **bez viditelných kontur**

---

## 📸 SROVNÁNÍ TESTŮ

### Test 1: `min_contour_area=1500` (PŮVODNÍ)
**Výsledek:** ❌ ŠPATNĚ
- Diff obrázek: Žádné kontury kolem textu
- Zachycuje jen tablet (velká kontura > 1500 px)
- **Nezachytí změny v input fields, textu, tlačítkách**

### Test 3: `min_contour_area=500` ⭐ DOPORUČENO
**Výsledek:** ✅ SKVĚLÉ
- Diff obrázek: Všechny změny viditelné!
- Červené kontury: Hlavní změny (nadpisy, tlačítka, odkazy)
- Žluté kontury: Menší změny (části textu)
- Růžové kontury: Velké změny (tablet)
- **Zachytí VŠE, co se změnilo**

### Test 4: `min_contour_area=100`
**Výsledek:** ✅ IDENTICKÉ JAKO TEST 3
- Velmi citlivé nastavení
- Zachycuje i nejmenší změny
- Pro většinu případů je `500` lepší (méně šumu)

---

## 🎯 DOPORUČENÉ PARAMETRY

### Pro Detekci Malých Změn (Input Shifts, Text Changes)

```robot
Compare Layouts And Generate Diff
    ${BASELINE_IMAGE_PATH}login_page.png
    ${CURRENT_IMAGE_PATH}
    ${DIFF_IMAGE_PATH}
    ...    pixel_tolerance=45           # ← OK, ponechat
    ...    hash_size=16                 # ← OK, ponechat
    ...    diff_mode=contours           # ← OK, ponechat
    ...    contour_thickness=3          # ← OK, ponechat
    ...    min_contour_area=500         # ← ZMĚNIT Z 1500 NA 500! ⭐
    ...    minor_color=(0, 255, 0)      # ← Zelená pro malé změny
    ...    moderate_color=(0, 255, 255) # ← Žlutá pro střední změny
    ...    severe_color=(0, 0, 255)     # ← Modrá pro velké změny
```

### Alternativní Nastavení Pro Různé Scénáře

#### 1. Ultra Citlivé (Zachytí VŠE)
```robot
min_contour_area=100
pixel_tolerance=35
```
**Použití:** Když potřebujete zachytit i nejmenší pixelové změny

#### 2. Vyvážené (DOPORUČENO) ⭐
```robot
min_contour_area=500
pixel_tolerance=45
```
**Použití:** Ideální pro většinu UI testů, zachytí změny v inputech, textu, tlačítkách

#### 3. Pouze Velké Změny
```robot
min_contour_area=1500
pixel_tolerance=60
```
**Použití:** Když chcete ignorovat malé změny a sledovat jen velké sekce (loadery, dialogy)

---

## 📊 VÝSLEDKY TESTOVÁNÍ

| Test | min_contour_area | pixel_tolerance | Hamming Distance | Zachytí Input Shift? |
|------|-----------------|-----------------|------------------|---------------------|
| 1    | 1500 (původní)  | 45              | 12               | ❌ NE               |
| 2    | 1000            | 45              | 12               | ⚠️  ČÁSTEČNĚ        |
| **3**| **500** ⭐      | 45              | 12               | ✅ **ANO**          |
| 4    | 100             | 45              | 12               | ✅ ANO              |
| 5    | 1500            | 35              | 12               | ❌ NE               |
| 6    | 500             | 35              | 12               | ✅ ANO              |
| 7    | 100             | 35              | 12               | ✅ ANO              |
| 8    | 1500            | 60              | 12               | ❌ NE               |
| 9    | 500             | 25              | 12               | ✅ ANO              |

**Závěr:**
- `min_contour_area <= 500` → Zachytí změny ✅
- `min_contour_area >= 1000` → Nezachytí malé změny ❌

---

## 🔧 JAK TO OPRAVIT

### Krok 1: Upravte te.robot

**Najděte řádek 37 v te.robot:**
```robot
...    min_contour_area=1500
```

**Změňte na:**
```robot
...    min_contour_area=500
```

### Krok 2: Spusťte Test Znovu

```bash
robot C:\Users\stoka\Documents\moje_app\RF\te.robot
```

### Krok 3: Zkontrolujte Diff Obrázek

- Diff obrázek bude mít **červené, žluté a růžové kontury**
- Kontury budou obklopovat **všechny změny**, včetně posunu inputu
- Otevřete diff soubor v `${RESULTS_IMAGE_PATH}`

---

## 📝 VYSVĚTLENÍ PARAMETRŮ

### `min_contour_area` (Minimální Velikost Kontury)
- **Účel:** Filtruje malé šumové kontury
- **Hodnota:** Plocha v pixelech (např. 500 = kontura musí mít alespoň 500 px²)
- **Dopad:**
  - Nízká hodnota (100) = Citlivé, zachytí všechny změny
  - Střední hodnota (500) = Vyvážené, ignoruje šum ⭐
  - Vysoká hodnota (1500) = Zachytí jen velké objekty

### `pixel_tolerance` (Tolerance Barevného Rozdílu)
- **Účel:** Určuje, jaký barevný rozdíl se považuje za "změnu"
- **Hodnota:** 0-255 (Manhattan distance v RGB prostoru)
- **Dopad:**
  - Nízká hodnota (25) = Velmi citlivé na barvy
  - Střední hodnota (45) = Vyvážené ⭐
  - Vysoká hodnota (60) = Ignoruje drobné barevné rozdíly

### `contour_thickness` (Tloušťka Obrysu)
- **Účel:** Tloušťka čáry obrysu kontury
- **Hodnota:** Pixely (např. 3)
- **Dopad:** Vyšší hodnota = viditelnější kontury

---

## 🎨 BAREVNÉ KÓDOVÁNÍ

Knihovna podporuje barevné kódování závažnosti změn:

- **Zelená (minor_color):** Malé změny (pixel_tolerance × 1.5)
- **Žlutá (moderate_color):** Střední změny (pixel_tolerance × 3.0)
- **Modrá/Červená (severe_color):** Velké změny (> pixel_tolerance × 3.0)

V testech jsme použili:
```robot
minor_color=(0, 255, 0)      # Zelená
moderate_color=(0, 255, 255) # Žlutá (cyan)
severe_color=(0, 0, 255)     # Modrá
```

---

## 📂 TESTOVACÍ SOUBORY

Všechny testovací výstupy jsou uloženy v:
```
C:\Users\stoka\Documents\moje_app\RF\ImageComparisonLibrary\test_outputs\
├── baseline/          (prázdné - používáme původní baseline)
├── current/           (prázdné - používáme původní screenshot)
├── diffs/             9 diff obrázků s různými parametry
│   ├── diff_20251120_150652_572496.png  (Test 1: area=1500)
│   ├── diff_20251120_150652_698314.png  (Test 2: area=1000)
│   ├── diff_20251120_150652_828273.png  (Test 3: area=500) ⭐
│   ├── diff_20251120_150652_964735.png  (Test 4: area=100)
│   └── ...
└── reports/
    ├── test_results_20251120_150653.json
    └── visual_comparison_20251120_150653.html
```

### Vizuální Report

Otevřete HTML report pro interaktivní porovnání:
```
C:\Users\stoka\Documents\moje_app\RF\ImageComparisonLibrary\test_outputs\reports\visual_comparison_20251120_150653.html
```

---

## 🧪 TESTOVACÍ SKRIPT

Byl vytvořen Python skript pro automatické testování parametrů:
```
C:\Users\stoka\Documents\moje_app\RF\ImageComparisonLibrary\test_input_shift_detection.py
```

**Použití:**
```bash
cd C:\Users\stoka\Documents\moje_app\RF\ImageComparisonLibrary
python test_input_shift_detection.py
```

Skript automaticky:
1. Načte vaše baseline a current obrázky
2. Otestuje 9 kombinací parametrů
3. Vygeneruje diff obrázky pro každou kombinaci
4. Vytvoří JSON report a HTML vizualizaci
5. Doporučí nejlepší nastavení

---

## ✅ KONTROLNÍ SEZNAM

- [x] **Identifikován problém:** `min_contour_area=1500` příliš vysoké
- [x] **Otestováno 9 kombinací** parametrů
- [x] **Nalezeno optimální nastavení:** `min_contour_area=500`
- [x] **Vytvořen testovací skript** pro budoucí ladění
- [x] **Vygenerován HTML report** s vizuálním porovnáním
- [ ] **Uživatel upraví te.robot** s novými parametry
- [ ] **Uživatel spustí test** a ověří, že diff se vykresluje správně

---

## 🚀 DALŠÍ KROKY

1. **Upravte `te.robot`:** Změňte `min_contour_area` z 1500 na 500
2. **Spusťte test:** Ověřte, že diff obrázky zobrazují všechny změny
3. **Archivujte test_outputs/:** Všechny soubory můžete ponechat pro referenci
4. **Upravte baseline:** Pokud je změna jazyka (EN→CZ) zamýšlená, vytvořte nový baseline

---

## 📞 POZNÁMKY

### Proč Test Failnul i s Optimálními Parametry?

**Hamming distance: 12 > tolerance: 5**

Test failnul správně, protože:
- **Baseline:** Anglická verze ("Sign in", "Email", "Password", "Log In")
- **Current:** Česká verze ("Přihlásit se", "E-mail", "Heslo", "Přihlásit se")
- **Změny:** Obrovské rozdíly v textu → vysoký Hamming distance (12)

To je **správné chování** knihovny - test MUSÍ failnout při takto velkých změnách!

### Pokud Je Česká Verze Zamýšlená

Pokud jste záměrně změnil jazyk stránky na češtinu:
1. Vytvořte nový baseline screenshot v češtině
2. Použijte tento baseline pro budoucí testy
3. Test pak projde (distance bude ~0)

### Pokud Chcete Testovat Jen Posun Input Fieldu

Pro izolovaný test posunu inputu:
1. Použijte baseline a current **ve stejném jazyce**
2. Aplikujte `transform: translate(30px, 15px)` na input
3. S parametry `min_contour_area=500` se posun zobrazí

---

**Report vygenerován:** 2025-11-20 15:06:53
**Analyzováno pomocí:** ImageComparisonLibrary v1.0.0 + Claude Code
**Testovací skript:** test_input_shift_detection.py
