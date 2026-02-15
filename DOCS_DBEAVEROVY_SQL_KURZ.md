# Kompletní report: Práce s databází v DBeaver - SQL kurz

**Datum:** 16. 1. 2026
**Databáze:** moje_app (PostgreSQL 15)
**Nástroj:** DBeaver
**Úroveň:** Začátečník → Mírně pokročilý

---

## 📋 OBSAH

1. [Architektura projektu](#architektura-projektu)
2. [Připojení k databázi](#připojení-k-databázi)
3. [Struktura databáze](#struktura-databáze)
4. [Probraná témata](#probraná-témata)
5. [SQL příkazy - přehled](#sql-příkazy-přehled)
6. [Klíčové poznatky](#klíčové-poznatky)
7. [DBeaver klávesové zkratky](#dbeaver-klávesové-zkratky)
8. [Vytvořené testovací tabulky](#vytvořené-testovací-tabulky)
9. [Co se dále učit](#co-se-dále-učit)

---

## 🏗️ ARCHITEKTURA PROJEKTU

### Aplikace: moje_app
- **Frontend:** React Native/Expo
- **Backend:** FastAPI (Python)
- **Databáze:** PostgreSQL 15
- **Spuštění:** Docker Compose

### Databázové kontejnery:
- `moje_app_db` - PostgreSQL hlavní DB
- Port mapping: `7432:5432` (host:container)

### Přístupové údaje:
```
Host:     localhost
Port:     7432
Database: moje_app
User:     postgres
Password: postgres
```

---

## 🔌 PŘIPOJENÍ K DATABÁZI

### Postup v DBeaver:

1. **New Database Connection** (ikonka zásuvky ⚡)
2. Vybrat **PostgreSQL**
3. Vyplnit údaje:
   - Host: `localhost`
   - Port: `7432` (pozor, ne 5432!)
   - Database: `moje_app`
   - Username: `postgres`
   - Password: `postgres`
4. **Test Connection** - ověřit
5. **Finish** - uložit

---

## 📊 STRUKTURA DATABÁZE

### Hlavní tabulky (propojené s aplikací):

| Tabulka | Popis | Hlavní sloupce |
|---------|-------|---------------|
| `form_data` | Formuláře | id, first_name, last_name, phone, gender, email |
| `attachments` | Přílohy | id, form_id, filename, content_type, data |
| `instructions` | Instrukce | id, form_id, text, created_at, updated_at |
| `couriers` | Kurýři | id, name, phone, email, lat, lng, status, tags |
| `orders` | Objednávky | id, customer_name, pickup_address, delivery_address, status, is_vip, courier_id |
| `dispatch_logs` | Logy přiřazení | id, order_id, courier_id, action |

### Oddělené tabulky:
| Tabulka | Popis |
|---------|-------|
| `auth_users` | Autentizace (oddělený modul) |

### Relace:
```
form_data (1) ----< (N) attachments
     |
     | (1:1)
     v
instructions (1)

couriers (1) ----< (N) orders
     |
     +----< (N) ----+
dispatch_logs
```

---

## 📚 PROBRANÁ TÉMATA

### ✅ Hotovo (dnešní výuka):

1. **Základy SQL**
   - SELECT - výběr dat
   - WHERE - filtrování
   - ORDER BY - řazení
   - LIMIT - omezení počtu řádků

2. **Modifikace dat**
   - INSERT - vkládání
   - UPDATE - úprava
   - DELETE - mazání

3. **JOIN - spojování tabulek**
   - INNER JOIN - jen shody
   - LEFT JOIN - vše z levé + shody
   - Rozdíl mezi typy JOIN

4. **Pokročilé filtry**
   - LIKE - vzory (%)
   - IN - seznam hodnot
   - BETWEEN - rozsah
   - Kombinace podmínek (AND, OR)

5. **Agregace**
   - COUNT(*) - počítání
   - SUM, AVG, MIN, MAX - statistiky
   - GROUP BY - seskupování
   - HAVING - filtr na agregované výsledky

6. **Práce v DBeaver**
   - Database Navigator
   - SQL Editor
   - Prohlížení dat v GUI
   - Export do CSV

---

## 📝 SQL PŘÍKAZY - PŘEHLED

### 1. SELECT - Základní dotazy

```sql
-- Všechny sloupce, všechny řádky
SELECT * FROM public.form_data;

-- Konkrétní sloupce
SELECT first_name, last_name, email FROM public.form_data;

-- S WHERE (filtrování)
SELECT * FROM public.form_data WHERE id = 1;
SELECT * FROM public.form_data WHERE first_name = 'Jan';
SELECT * FROM public.form_data WHERE gender = 'Žena';

-- S AND/OR (více podmínek)
SELECT * FROM public.form_data
WHERE first_name = 'Jan' AND last_name = 'Novák';

SELECT * FROM public.form_data
WHERE first_name = 'Jan' OR first_name = 'Petr';
```

### 2. ORDER BY - Řazení

```sql
-- Vzestupně (default)
SELECT * FROM public.form_data ORDER BY id ASC;

-- Sestupně
SELECT * FROM public.form_data ORDER BY id DESC;

-- S LIMIT
SELECT * FROM public.form_data ORDER BY id DESC LIMIT 3;

-- Kombinace
SELECT * FROM public.form_data
WHERE gender = 'Muž'
ORDER BY last_name ASC
LIMIT 5;
```

### 3. INSERT - Vkládání

```sql
-- Jedna hodnota
INSERT INTO public.form_data (first_name, last_name, phone, gender, email)
VALUES ('Jan', 'Novák', '+420123456789', 'Muž', 'jan@email.cz');

-- Více hodnot najednou
INSERT INTO public.zakaznici (jmeno, prijmeni, email, mesto, objednavek_cena)
VALUES
    ('Jan', 'Novák', 'jan@email.cz', 'Praha', 1500),
    ('Marie', 'Svobodová', 'marie@email.cz', 'Brno', 2500),
    ('Petr', 'Dvořák', 'petr@email.cz', 'Praha', 800);
```

### 4. UPDATE - Úprava

```sql
-- Změna jednoho řádku (BEZPEČNÉ s ID!)
UPDATE public.form_data
SET phone = '+420777888999'
WHERE id = 2;

-- Změna více sloupců
UPDATE public.form_data
SET phone = '+420777888999', email = 'novy@email.cz'
WHERE id = 2;

-- ⚠️ BEZ WHERE = změní VŠECHNO!
UPDATE public.form_data SET phone = '+420000000000';  -- NEBEZPEČNÉ!
```

### 5. DELETE - Mazání

```sql
-- Bezpečné mazání (podle ID)
DELETE FROM public.form_data WHERE id = 1;

-- Mazání s podmínkou
DELETE FROM public.form_data WHERE email = 'stary@email.cz';

-- ⚠️ BEZ WHERE = SMAZE VŠECHNO!
DELETE FROM public.form_data;  -- NEBEZPEČNÉ!
```

**Bezpečný workflow DELETE:**
```sql
-- 1. NEJDŘÍV SELECT - zkontroluj
SELECT * FROM tabulka WHERE id = 5;

-- 2. DELETE podle ID
DELETE FROM tabulka WHERE id = 5;

-- 3. OVĚŘ smazání
SELECT * FROM tabulka WHERE id = 5;  -- prázdné = smazáno
```

### 6. JOIN - Spojování tabulek

```sql
-- INNER JOIN - jen shody
SELECT
    z.jmeno,
    z.prijmeni,
    o.datum,
    o.castka
FROM public.zakaznici z
INNER JOIN public.objednavky o ON z.id = o.zakaznik_id;

-- LEFT JOIN - vše z levé + shody
SELECT
    z.jmeno,
    z.prijmeni,
    o.datum
FROM public.zakaznici z
LEFT JOIN public.objednavky o ON z.id = o.zakaznik_id;

-- JOIN s WHERE
SELECT
    z.jmeno,
    z.mesto,
    o.datum
FROM public.zakaznici z
LEFT JOIN public.objednavky o ON z.id = o.zakaznik_id
WHERE z.mesto = 'Praha';
```

**Typy JOIN:**
| Typ | Význam |
|-----|---------|
| INNER JOIN | Jen řádky se shodou v OBOU tabulkách |
| LEFT JOIN | Vše z levé tabulky + shody z pravé |
| RIGHT JOIN | Vše z pravé tabulky + shody z levé |
| FULL JOIN | Vše z OBOU tabulek |

### 7. LIKE - Vzory

```sql
-- Začíná na
SELECT * FROM zakaznici WHERE prijmeni LIKE 'N%';

-- Končí na
SELECT * FROM zakaznici WHERE prijmeni LIKE '%ová';

-- Obsahuje
SELECT * FROM zakaznici WHERE prijmeni LIKE '%ov%';
```

### 8. IN - Seznam hodnot

```sql
-- Ekvivalent k: mesto = 'Praha' OR mesto = 'Brno'
SELECT * FROM zakaznici
WHERE mesto IN ('Praha', 'Brno');

-- S jinými podmínkami
SELECT * FROM zakaznici
WHERE jmeno IN ('Jan', 'Petr', 'Marie')
  AND objednavek_cena > 1000;
```

### 9. BETWEEN - Rozsah

```sql
-- Číselný rozsah
SELECT * FROM objednavky
WHERE castka BETWEEN 1000 AND 2000;

-- Datumový rozsah
SELECT * FROM objednavky
WHERE datum BETWEEN '2024-01-01' AND '2024-12-31';
```

### 10. Agregační funkce

```sql
-- COUNT - počítání
SELECT COUNT(*) FROM zakaznici;
SELECT COUNT(*) FROM zakaznici WHERE mesto = 'Praha';

-- SUM - součet
SELECT SUM(castka) FROM objednavky;

-- AVG - průměr
SELECT AVG(castka) FROM objednavky;

-- MIN, MAX - minimum, maximum
SELECT MIN(castka), MAX(castka) FROM objednavky;
```

### 11. GROUP BY - Seskupování

```sql
-- Kolik v každém městě
SELECT mesto, COUNT(*) as pocet
FROM zakaznici
GROUP BY mesto
ORDER BY pocet DESC;

-- SUMA pro každou skupinu
SELECT mesto, SUM(objednavek_cena) as celkem
FROM zakaznici
GROUP BY mesto
ORDER BY celkem DESC;
```

### 12. HAVING - Filtr na seskupená data

```sql
-- Jen města s celkem > 3000
SELECT
    z.mesto,
    SUM(o.castka) as celkem
FROM zakaznici z
JOIN objednavky o ON z.id = o.zakaznik_id
GROUP BY z.mesto
HAVING SUM(o.castka) > 3000
ORDER BY celkem DESC;
```

**Rozdíl WHERE vs HAVING:**
```sql
-- WHERE = filtr PŘED seskupením
WHERE mesto = 'Praha'

-- HAVING = filtr PO seskupení
HAVING SUM(castka) > 3000
```

---

## 🎓 KLÍČOVÉ POZNATKY

### 1. Jak SQL funguje (čtení kódu)

**Fází pořadí (jak to píšete):**
```
SELECT → FROM → JOIN → WHERE → GROUP BY → ORDER BY
```

**Logický pořadí (jak to počítač vykonává):**
```
FROM → JOIN → WHERE → GROUP BY → HAVING → SELECT → ORDER BY
```

**Analogie:** Recept na vaření
1. SELECT = co bude na talíři
2. FROM = suroviny (mám je vzít)
3. JOIN = další suroviny (přidat)
4. WHERE = filtr (jen určitá kvalita)
5. GROUP BY = rozdělení na porce
6. HAVING = vybrat jen určité porce

### 2. Aliasy (zkratky tabulek)

```sql
-- Aliasy si definujete VY
FROM public.zakaznici z           -- "z" = zkratka pro zakaznici
INNER JOIN public.objednavky o    -- "o" = zkratka pro objednavky

-- Můžou být cokoliv
FROM public.zakaznici zakaznik
FROM public.zakaznici z

-- Používají se pro zjednodušení
SELECT z.jmeno           -- místo: zakaznici.jmeno
FROM zakaznici z         -- místo: public.zakaznici
```

### 3. Bezpečnost práce s daty

**✅ BEZPEČNÉ:**
- SELECT - nic nemění, jen čte
- WHERE s ID - přesná identifikace
- Nejdřív SELECT, pak DELETE

**⚠️ POZOR:**
- UPDATE/DELETE bez WHERE - změní/smaže VŠECHNO
- DELETE podle jména - smaže více lidí se stejným jménem

### 4. SELECT vs INSERT/UPDATE/DELETE

| Operace | Co dělá | Ovlivní aplikaci? |
|---------|---------|------------------|
| SELECT | Čte data | ❌ Ne |
| INSERT | Přidá data | ✅ Ano |
| UPDATE | Změní data | ✅ Ano |
| DELETE | Smaže data | ✅ Ano |

---

## ⌨️ DBEAVER KLÁVESOVÉ ZKRATKY

| Zkratka | Akce |
|---------|------|
| `Ctrl+Shift+E` nebo `F3` | Otevřít SQL Editor |
| `Ctrl+Enter` | Spustit SQL dotaz |
| `Alt+X` | Spustit jen vybranou část |
| `Ctrl+Space` | Autocomplete (návrhy) |

### Práce s daty v GUI:
- **Pravé tlačítko na tabulku** → View Data = zobrazit data
- **Záložka Columns** = struktura tabulky (sloupce, typy)
- **Záložka Rows** = samotná data
- **ER Diagram** = grafické zobrazení relací

### Export dat:
1. Spustit SELECT
2. Pravé tlačítko v Result Set
3. Export Result Set → CSV

---

## 🧪 VYTOVOŘENÁ TESTOVACÍ TABULKA

Pro účely výuky byla vytvořena testovací tabulka, která nerozbije aplikaci.

### Tabulka: zakaznici

```sql
CREATE TABLE public.zakaznici (
    id SERIAL PRIMARY KEY,
    jmeno VARCHAR(50),
    prijmeni VARCHAR(50),
    email VARCHAR(100),
    mesto VARCHAR(50),
    objednavek_cena NUMERIC
);
```

### Vložená data:

| ID | Jméno | Příjmení | Email | Město | Cena |
|----|-------|----------|-------|-------|------|
| 1 | Jan | Novák | jan@email.cz | Praha | 1500 |
| 2 | Marie | Svobodová | marie@email.cz | Brno | 2500 |
| 3 | Petr | Dvořák | petr@email.cz | Praha | 800 |
| 4 | Jana | Černá | jana@email.cz | Ostrava | 3200 |
| 5 | Tomáš | Kučera | tomas@email.cz | Brno | 1200 |
| 6 | Karel | Nešpůl | karel@nespul.cz | Plzeň | NULL |

### Tabulka: objednavky

```sql
CREATE TABLE public.objednavky (
    id SERIAL PRIMARY KEY,
    zakaznik_id INTEGER,
    datum DATE,
    castka NUMERIC
);
```

### Relace:
- `objednavky.zakaznik_id` → `zakaznici.id` (Foreign Key)

---

## 📊 PŘÍKLADY Z VÝUKY

### Příklad 1: Najít všechny Pražany

```sql
SELECT * FROM public.zakaznici WHERE mesto = 'Praha';
```
**Výsledek:** Jan Novák, Petr Dvořák (2 řádky)

### Příklad 2: Kolik utratil každý zákazník

```sql
SELECT
    z.jmeno,
    z.prijmeni,
    SUM(o.castka) as celkem_utraceno
FROM public.zakaznici z
JOIN public.objednavky o ON z.id = o.zakaznik_id
GROUP BY z.id, z.jmeno, z.prijmeni
ORDER BY celkem_utraceno DESC;
```

### Příklad 3: Které město utratilo nejvíc

```sql
SELECT
    z.mesto,
    SUM(o.castka) as celkem
FROM public.zakaznici z
JOIN public.objednavky o ON z.id = o.zakaznik_id
GROUP BY z.mesto
ORDER BY celkem DESC;
```

**Výsledek:**
1. Praha - 3500
2. Ostrava - 3200
3. Brno - 2500

---

## 🚀 CO SE DÁLE UČIT

### Pokročilé téma - volitelné:

| Téma | Popis | Obtížnost |
|------|-------|-----------|
| **A** - Poddotazy (Subquery) | Dotaz v dotazu | ⭐⭐⭐ |
| **B** - UNION | Spojení výsledků | ⭐⭐ |
| **C** - CTE (WITH) | Dočasné tabulky | ⭐⭐⭐ |
| **D** - Window Functions | Řadění, čísla řádků | ⭐⭐⭐⭐ |
| **E** - INDEX | Zrychlení dotazů | ⭐⭐⭐ |
| **F** - VIEWS | Uložené pohledy | ⭐⭐ |
| **G** - Transakce | BEGIN/COMMIT/ROLLBACK | ⭐⭐⭐ |

---

## 📌 KONTROLNÍ SEZNAM

Po dnešním kurzu byste měli umět:

- [x] Připojit se k databázi v DBeaver
- [x] Prohlížet strukturu tabulek (Columns, Keys, Indexes)
- [x] Psát základní SELECT dotazy
- [x] Filtrovat s WHERE (=, <>, >, <, AND, OR)
- [x] Řadit s ORDER BY (ASC, DESC)
- [x] Omezovat s LIMIT
- [x] Vkládat data s INSERT
- [x] Upravovat data s UPDATE (bezpečně!)
- [x] Mazat data s DELETE (bezpečně!)
- [x] Spojovat tabulky s JOIN (INNER, LEFT)
- [x] Používat LIKE (vzory)
- [x] Používat IN (seznam)
- [x] Používat BETWEEN (rozsah)
- [x] Groupovat s GROUP BY
- [x] Filtrovat agregace s HAVING
- [x] Exportovat data do CSV

---

## 📚 UŽITEČNÉ ZDROJE

### Dokumentace:
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [DBeaver Documentation](https://dbeaver.com/docs/)

### Online trénink:
- [SQL Fiddle](https://www.sqlfiddle.com/) - trénink online
- [W3Schools SQL](https://www.w3schools.com/sql/) - tutoriály

---

## 🏆 SHRNUTÍ

**Dnešní výuka pokryla:**
- Základy SQL až po středně pokročilé úrovni
- Praktickou práci v DBeaver
- Bezpečnou práci s daty
- JOIN a agregace

**Čas výuky:** ~1-2 hodiny
**Vrstev naučeno:** 12 fází
**SQL příkazů probráno:** 12 hlavních kategorií
**Vytvořeno tabulek:** 2 testovací
**Vloženo řádků:** 11+

---

**Vytvořil:** Claude (AI Assistant)
**Datum:** 16. 1. 2026
**Verze:** 1.0

---

*Tento dokument slouží jako reference pro budoucí práci s databází.*
