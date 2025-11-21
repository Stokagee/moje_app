# Řešení Pro Detekci Malých Posunů (Input Shift)

## Problém
Test **prochází** i když je input viditelně posunut o 30px. Perceptual hash není dost citlivý.

---

## Řešení 1: Snížit Tolerance ⭐ NEJJEDNODUŠŠÍ

**Změňte v te.robot:**
```robot
Compare Layouts And Generate Diff
    ...    tolerance=2          # ← SNÍŽIT Z 5 NA 2
    ...    pixel_tolerance=45
    ...    hash_size=16
    ...    min_contour_area=500
```

**Výhody:**
- Nejjednodušší změna
- Stačí změnit jedno číslo

**Zkuste postupně:** `tolerance=3`, pak `tolerance=2`, pak `tolerance=1`

---

## Řešení 2: Zvýšit Detaily Hashe

**Změňte v te.robot:**
```robot
Compare Layouts And Generate Diff
    ...    tolerance=5
    ...    pixel_tolerance=45
    ...    hash_size=32         # ← ZVÝŠIT Z 16 NA 32
    ...    min_contour_area=500
```

**Výhody:**
- Více detailů v hashi = citlivější detekce
- hash_size=32 vytvoří 32×32 hash (místo 16×16)

**Zkuste:** `hash_size=24` nebo `hash_size=32`

---

## Řešení 3: Změnit Algoritmus na dhash ⭐ DOPORUČENO

**Změňte v te.robot:**
```robot
Compare Layouts And Generate Diff
    ...    algorithm='dhash'    # ← ZMĚNIT Z 'phash' NA 'dhash'
    ...    tolerance=5
    ...    pixel_tolerance=45
    ...    hash_size=16
    ...    min_contour_area=500
```

**Proč dhash?**
- dhash (Difference Hash) je **citlivější na posuny** než phash
- dhash sleduje gradienty → detekuje změny pozice
- phash sleduje strukturu → ignoruje malé posuny

---

## Řešení 4: Kombinace (NEJCITLIVĚJŠÍ)

```robot
Compare Layouts And Generate Diff
    ...    algorithm='dhash'    # Citlivější algoritmus
    ...    tolerance=3          # Nižší tolerance
    ...    pixel_tolerance=45
    ...    hash_size=24         # Více detailů
    ...    min_contour_area=500
```

---

## Testovací Skript

Vytvořil jsem skript pro otestování různých kombinací:
