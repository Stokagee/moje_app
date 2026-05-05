# Claude Code workspace pro QA testera: kompletní architektonický průvodce 2026

**Claude Code se v roce 2026 stal plnohodnotným AI asistentem pro software testery**, nikoli jen pro vývojáře. Klíčem k efektivnímu využití je správná architektura workspace — hierarchie CLAUDE.md souborů, vlastní skills pro QA workflow, hooks pro automatizaci a MCP servery pro integraci s Jira, databázemi a prohlížečem. Tento průvodce pokrývá všech 10 oblastí nastavení Claude Code workspace specificky pro testera pracujícího s Java/Go/Python stackem, včetně konkrétních konfiguračních příkladů a .robot file generování přes Robot Framework plugin.

---

## 1. Struktura složek a souborů pro QA testera

Tester nepotřebuje stejnou strukturu jako vývojář. Hlavní důraz je na **skills pro opakující se QA workflow**, rules pro testovací konvence a MCP integraci s testovacími nástroji. Doporučená adresářová struktura Claude Code workspace pro QA testera:

```
project-root/
├── CLAUDE.md                          # Hlavní projektové instrukce (sdílené přes Git)
├── CLAUDE.local.md                    # Osobní QA poznámky (v .gitignore)
├── .mcp.json                          # MCP servery pro tým (Jira, GitHub, DB...)
│
├── .claude/
│   ├── settings.json                  # Projektová nastavení + hooks + permissions
│   ├── settings.local.json            # Lokální nastavení (tokeny, gitignored)
│   │
│   ├── skills/                        # QA-specifické skills (doporučený formát)
│   │   ├── bug-report/
│   │   │   ├── SKILL.md              # Instrukce pro generování bug reportu
│   │   │   └── template.md           # Šablona bug reportu
│   │   ├── test-analysis/
│   │   │   └── SKILL.md              # Analýza testovatelnosti
│   │   ├── generate-robot/
│   │   │   ├── SKILL.md              # Generování .robot souborů
│   │   │   └── examples/
│   │   │       └── login-test.robot  # Vzorový .robot soubor
│   │   ├── explore-code/
│   │   │   └── SKILL.md              # Code comprehension pro testera
│   │   └── test-scenarios/
│   │       └── SKILL.md              # Generování test scénářů
│   │
│   ├── agents/                        # Specializovaní subagenti
│   │   ├── test-runner.md            # Agent pro spouštění testů
│   │   └── code-explorer.md          # Agent pro průzkum kódu
│   │
│   ├── rules/                         # Modulární pravidla
│   │   ├── testing-conventions.md    # Testovací konvence projektu
│   │   ├── java-testing.md           # Java-specifická pravidla (paths: src/**/*.java)
│   │   ├── go-testing.md             # Go-specifická pravidla (paths: **/*.go)
│   │   ├── python-testing.md         # Python-specifická pravidla (paths: **/*.py)
│   │   └── robot-framework.md        # RF konvence (paths: **/*.robot)
│   │
│   └── hooks/                         # Skripty pro hooks
│       ├── run-lint-after-edit.sh
│       └── notify-test-complete.sh
│
├── java-service/                      # Java mikroservis
│   └── CLAUDE.md                      # Java-specifické build/test příkazy
├── go-service/                        # Go mikroservis
│   └── CLAUDE.md                      # Go-specifické build/test příkazy
└── python-scripts/                    # Python utility skripty
    └── CLAUDE.md                      # Python-specifické příkazy
```

Pro globální nastavení napříč všemi projekty pak:

```
~/.claude/
├── CLAUDE.md                          # Osobní globální instrukce
├── settings.json                      # Globální nastavení + hooks
├── skills/                            # Osobní skills pro všechny projekty
│   └── quick-bug/
│       └── SKILL.md
└── MEMORY.md                          # Auto-memory (spravuje Claude)
```

Klíčový princip: **path-scoped rules** v `.claude/rules/` se načtou pouze když Claude pracuje se soubory odpovídajícími glob patternu, čímž šetří kontext. Pravidlo `java-testing.md` s frontmatter `paths: ["src/**/*.java"]` se aktivuje jen při práci s Java soubory.

---

## 2. CLAUDE.md hierarchie a best practices pro testera

### Hierarchie načítání (od nejvyšší priority)

| Úroveň | Cesta | Sdílení | Účel |
|---------|-------|---------|------|
| Managed policy | `/etc/claude-code/CLAUDE.md` | Organizace | Firemní standardy |
| Globální osobní | `~/.claude/CLAUDE.md` | Ne | Osobní preference napříč projekty |
| Projektový root | `./CLAUDE.md` | Git | Hlavní projektové instrukce |
| Projektový lokální | `./CLAUDE.local.md` | Ne (.gitignore) | Osobní projektové poznámky |
| Podsložky | `./java-service/CLAUDE.md` | Git | Jazykově specifické instrukce |
| Rules | `.claude/rules/*.md` | Git | Modulární pravidla s path-scoping |

Všechny CLAUDE.md soubory se **načtou na začátku každé konverzace** a **přežijí kompakci** — po `/compact` je Claude znovu přečte z disku. Podsložkové CLAUDE.md se načítají **on-demand** při práci se soubory v dané složce. Soubory `.claude/rules/` se načtou jen když odpovídá `paths` pattern.

### Co patří do CLAUDE.md pro QA testera

**Patří tam** věci, které Claude nemůže odvodit z kódu — build příkazy, testovací konvence, architektonická rozhodnutí a workflow pravidla. **Nepatří tam** to, co je zřejmé z kódu samotného nebo standardní jazykové konvence.

### Konkrétní příklad: projektový CLAUDE.md pro QA

```markdown
# QA Testing Workspace — Project SuperApp

## Architektura projektu
Monorepo se třemi službami:
- `java-service/` — Spring Boot 3.x REST API (Java 21, Gradle)
- `go-service/` — Go 1.22 gRPC mikroservis
- `python-scripts/` — Python 3.12 utility skripty a data generátory

## Build a test příkazy
- Java testy: `cd java-service && ./gradlew test`
- Java single test: `./gradlew test --tests "com.example.MyTest"`
- Go testy: `cd go-service && go test ./...`
- Go single test: `go test -run TestName ./pkg/...`
- Python testy: `cd python-scripts && pytest`
- Robot Framework: `robot --outputdir results tests/`
- Robot single suite: `robot --suite SuiteName tests/`

## Testovací konvence
- DŮLEŽITÉ: Při analýze kódu vždy identifikuj edge cases a boundary values
- Bug reporty piš v češtině s anglickými technickými termíny
- Test scénáře používají BDD formát (Given/When/Then)
- Robot Framework soubory používají keyword-driven přístup
- Názvy test cases: popisné věty, ne technický žargon

## Workflow pravidla
- Před modifikací testů vždy analyzuj, co test skutečně ověřuje
- NIKDY neupravuj aserce testů, aby prošly — oprav implementaci
- Při code comprehension začni od entry pointů (controllers, handlers)
- Při generování .robot souborů vždy použij Page Object pattern
- Snapshot testy: nikdy automaticky neaktualizuj snapshoty

## Git konvence
- Commity: conventional commits (test: , fix: , docs:)
- Branch naming: qa/JIRA-123-popis
- PR popis vždy obsahuje: co bylo testováno, jaké scénáře pokryty

## Kontakt a dokumentace
- API dokumentace: @docs/api-spec.yaml
- Testovací plán: @docs/test-plan.md
```

### Příklad: ~/.claude/CLAUDE.md (globální osobní)

```markdown
# Osobní QA nastavení

## Jazyk a komunikace
- Odpovídej v češtině, technické termíny ponechej anglicky
- Bug reporty formátuj jako Jira tickets
- Výstup test scénářů vždy ve formátu Markdown tabulky

## Preferované nástroje
- Pro Java analýzu preferuj Gradle nad Maven
- Pro Python používej pytest, ne unittest
- Robot Framework verze 7.x syntax

## Workflow
- Při code review vždy hledej: null checks, error handling, race conditions
- Při analýze logů hledej patterns, ne jednotlivé řádky
```

Důležitá pravidla: CLAUDE.md by měl mít **maximálně 200 řádků** — delší soubory spotřebovávají kontext a Claude je méně dodržuje. Pro kritická pravidla použijte důraz: slova **„IMPORTANT"** nebo **„YOU MUST"** zvyšují adherenci. Soubor podporuje `@path/to/import` syntax pro importování dalších souborů (max hloubka 5).

---

## 3. Custom skills (slash commands) pro QA workflow

Skills nahrazují starší commands systém (soubory v `.claude/commands/` stále fungují, ale doporučený formát je `.claude/skills/<name>/SKILL.md`). Každý skill vytvoří slash příkaz dostupný přes `/`.

### Skill: Bug report (`/bug-report`)

```yaml
# .claude/skills/bug-report/SKILL.md
---
name: bug-report
description: Generuje strukturovaný bug report z popisu problému. Použij pro reportování bugů do Jira.
argument-hint: "[popis bugu]"
disable-model-invocation: true
allowed-tools: Read Grep Glob
---

Vytvoř strukturovaný bug report na základě popisu: $ARGUMENTS

Postup:
1. Analyzuj relevantní kód v repozitáři pro kontext bugu
2. Identifikuj affected komponentu a severity
3. Vyplň šablonu z ${CLAUDE_SKILL_DIR}/template.md

Formát severity:
- Critical: data loss, security breach, system crash
- Major: feature nefunkční, workaround existuje
- Minor: kosmetický problém, edge case
- Trivial: překlep, formátování

Výstup v češtině s anglickými technickými termíny.
```

Šablona k tomu:

```markdown
# .claude/skills/bug-report/template.md

## 🐛 Bug Report: [TITLE]

**Severity:** [Critical/Major/Minor/Trivial]
**Komponenta:** [service/module]
**Prostředí:** [dev/staging/prod]

### Popis
[Stručný popis problému]

### Kroky k reprodukci
1. [krok 1]
2. [krok 2]
3. [krok 3]

### Očekávané chování
[Co by se mělo stát]

### Aktuální chování
[Co se skutečně děje]

### Technický kontext
- Affected soubory: [seznam]
- Root cause analýza: [pokud identifikována]
- Related testy: [existující testy pokrývající oblast]

### Přílohy
[Logy, screenshoty, stack traces]
```

### Skill: Test analýza (`/test-analysis`)

```yaml
# .claude/skills/test-analysis/SKILL.md
---
name: test-analysis
description: Analyzuje testovatelnost kódu a identifikuje mezery v pokrytí
argument-hint: "[cesta k souboru nebo modulu]"
disable-model-invocation: true
context: fork
agent: Explore
allowed-tools: Read Grep Glob Bash
---

Proveď hloubkovou test analýzu pro: $ARGUMENTS

## Postup analýzy:
1. **Mapování kódu** — Projdi všechny soubory v zadané oblasti
2. **Identifikace testovatelných bodů:**
   - Public metody a endpointy
   - Boundary values a edge cases
   - Error handling cesty
   - Integration points mezi službami
3. **Existující pokrytí** — Najdi existující testy a co pokrývají
4. **Gap analýza** — Identifikuj nepokryté cesty
5. **Prioritizace** — Seřaď nalezené mezery podle rizika

## Aktuální test příkazy:
- Java: !`cd java-service && ./gradlew test --dry-run 2>&1 | head -20`
- Go: !`cd go-service && go test -list '.*' ./... 2>&1 | head -20`
- Python: !`cd python-scripts && pytest --collect-only 2>&1 | head -20`

## Výstup:
Markdown tabulka s kolonkami: Oblast | Pokrytí | Riziko | Doporučený test typ | Priorita
```

### Skill: Generování Robot Framework souborů (`/generate-robot`)

```yaml
# .claude/skills/generate-robot/SKILL.md
---
name: generate-robot
description: Generuje Robot Framework .robot test soubory z popisu scénáře
argument-hint: "[popis test scénáře]"
disable-model-invocation: true
allowed-tools: Read Write Grep Glob
---

Vygeneruj Robot Framework .robot soubor pro scénář: $ARGUMENTS

## Pravidla pro generování:
1. Použij **keyword-driven** přístup s Page Object patternem
2. Soubor musí obsahovat:
   - *** Settings *** — Library imports, Resource imports
   - *** Variables *** — Konfigurovatelné proměnné (URL, credentials placeholder)
   - *** Test Cases *** — BDD styl (Given/When/Then keywords)
   - *** Keywords *** — Reusable keywords
3. Používej Browser library (Playwright-based), ne SeleniumLibrary
4. Každý test case musí mít [Documentation] a [Tags]
5. Locátory: preferuj data-testid > CSS selektory > XPath
6. Setup/Teardown na úrovni suite i test case
7. Syntax Robot Framework 7.x

## Vzorový výstup viz:
${CLAUDE_SKILL_DIR}/examples/login-test.robot

## Po vygenerování:
- Validuj syntax: `robot --dryrun generated_test.robot`
- Zkontroluj, že nepoužívá hardcoded hodnoty
```

### Skill: Code comprehension (`/explore-code`)

```yaml
# .claude/skills/explore-code/SKILL.md
---
name: explore-code
description: Pomáhá testerovi pochopit neznámý kód — entry pointy, data flow, závislosti
argument-hint: "[oblast kódu nebo otázka]"
context: fork
agent: Explore
allowed-tools: Read Grep Glob Bash
---

Jako QA tester potřebuji pochopit tento kód: $ARGUMENTS

## Postup průzkumu:
1. **Architektura** — Jaký typ aplikace to je? (REST API, gRPC, CLI, web app)
2. **Entry pointy** — Kde začíná zpracování requestu? (controllers, handlers, routes)
3. **Data flow** — Jak data protékají systémem? (input → validace → business logic → persistence → output)
4. **Závislosti** — Na čem závisí? (databáze, externí API, message queue)
5. **Error handling** — Jak se zpracovávají chyby?
6. **Konfigurrace** — Kde je konfigurace a jaké env variables potřebuje?

## Výstup:
- ASCII diagram architektury
- Seznam klíčových souborů s jednořádkovým popisem
- Data flow diagram (text)
- Identifikované rizikové oblasti pro testování
- Navržené test scénáře na základě pochopení kódu
```

### Skill: Test scénáře (`/test-scenarios`)

```yaml
# .claude/skills/test-scenarios/SKILL.md
---
name: test-scenarios
description: Generuje test scénáře v BDD formátu pro zadanou feature
argument-hint: "[feature nebo user story]"
disable-model-invocation: true
allowed-tools: Read Grep Glob
---

Vygeneruj komplexní test scénáře pro: $ARGUMENTS

## Kategorie scénářů (vždy vygeneruj všechny):
1. **Happy path** — Standardní úspěšný průchod
2. **Negative testing** — Nevalidní vstupy, chybové stavy
3. **Boundary values** — Hraniční hodnoty (min, max, empty, null)
4. **Edge cases** — Neobvyklé ale validní kombinace
5. **Security** — Injection, autorizace, autentizace
6. **Performance** — Timeouty, velké objemy dat

## Formát výstupu:
```gherkin
Scenario: [Popisný název]
  Given [předpoklad]
  When [akce]
  Then [očekávaný výsledek]
  And [další ověření]
```

## Po vygenerování:
- Označ prioritu (P0-P3)
- Označ typ (smoke, regression, integration)
- Navrhni, které scénáře automatizovat a které nechat manuální
```

Použití je intuitivní: napíšete `/bug-report Přihlašovací formulář nezobrazuje chybu při špatném hesle` nebo `/generate-robot Login flow s 2FA autentizací` a Claude vykoná celý workflow.

---

## 4. Hooks pro automatizaci QA workflow

Hooks jsou **deterministické triggery** — na rozdíl od instrukcí v CLAUDE.md, které jsou doporučující, hooks **garantují** provedení akce. Konfigurace se ukládá do `.claude/settings.json` (projektový) nebo `~/.claude/settings.json` (globální).

### Hook pro automatické spuštění testů po editaci kódu

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write|MultiEdit",
        "hooks": [
          {
            "type": "command",
            "command": "echo '{\"additionalContext\": \"REMINDER: Soubor byl změněn. Zvař spuštění relevantních testů pro ověření, že změna nic nerozbila.\"}'"
          }
        ]
      }
    ]
  }
}
```

### Hook pro injekci kontextu na začátku session

```json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "startup",
        "hooks": [
          {
            "type": "command",
            "command": "echo '{\"additionalContext\": \"Git branch: '$(git branch --show-current)' | Last commit: '$(git log --oneline -1)' | Failing tests: '$(cd java-service && ./gradlew test 2>&1 | grep -c FAILED || echo 0)'\"}'"
          }
        ]
      }
    ]
  }
}
```

### Hook pro blokování nebezpečných operací (QA tester by neměl mazat produkční data)

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "if": "Bash(rm *)",
            "command": "echo 'BLOCKED: rm commands are not allowed in QA workspace' && exit 2"
          }
        ]
      },
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "if": "Bash(*DROP TABLE*)",
            "command": "echo 'BLOCKED: DROP TABLE is not allowed' && exit 2"
          }
        ]
      }
    ]
  }
}
```

### Hook pro automatickou validaci vygenerovaných .robot souborů

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write",
        "hooks": [
          {
            "type": "command",
            "command": "FILE=$(echo \"$CLAUDE_TOOL_INPUT\" | jq -r '.file_path // empty'); if [ -n \"$FILE\" ] && echo \"$FILE\" | grep -qE '\\.robot$'; then robot --dryrun \"$FILE\" 2>&1 || true; fi"
          }
        ]
      }
    ]
  }
}
```

### Hook pro agent-based ověření po dokončení úlohy

```json
{
  "hooks": {
    "Stop": [
      {
        "hooks": [
          {
            "type": "agent",
            "prompt": "Verify that any generated test files have valid syntax. Check .robot files with 'robot --dryrun', Python tests with 'python -m py_compile', and Java tests with 'javac' dry run. Report any syntax errors found.",
            "timeout": 60
          }
        ]
      }
    ]
  }
}
```

Kompletní přehled dostupných hook eventů zahrnuje **24 eventů** včetně `SessionStart`, `PreToolUse`, `PostToolUse`, `Stop`, `PreCompact`, `PostCompact`, `FileChanged` a dalších. Exit code **0** = pokračuj, **2** = blokuj akci, **jiný** = pokračuj s logováním chyby.

---

## 5. Práce s více jazyky v jednom projektu

Claude Code zvládá polyglotní repozitáře nativně — **automaticky rozpoznává jazyk na základě souborových přípon a kontextu** a přizpůsobuje své odpovědi. Pro tříjazyčný stack Java + Go + Python doporučuji tento přístup:

**Hierarchické CLAUDE.md soubory** jsou klíčovým mechanismem. Root CLAUDE.md popisuje celkovou architekturu a vztahy mezi službami. Každá podsložka služby má vlastní CLAUDE.md s jazykově specifickými příkazy. Claude automaticky načte příslušný podsložkový CLAUDE.md když pracuje se soubory v dané složce.

**Path-scoped rules** v `.claude/rules/` poskytují ještě přesnější kontrolu:

```yaml
# .claude/rules/java-testing.md
---
paths:
  - "java-service/**/*.java"
  - "java-service/**/*.kt"
---
# Java Testing Rules
- Testy používají JUnit 5 + AssertJ
- Mockování přes Mockito
- Integration testy označeny @Tag("integration")
- Testovací data přes @ParameterizedTest kde je to vhodné
- Build: ./gradlew test
- Single test: ./gradlew test --tests "FullyQualifiedTestName"
```

```yaml
# .claude/rules/go-testing.md
---
paths:
  - "go-service/**/*.go"
---
# Go Testing Rules
- Testy v souboru *_test.go vedle testovaného kódu
- Table-driven tests jako výchozí pattern
- Používej testify/assert pro assertions
- go test ./... pro všechny testy
- go test -run TestSpecific ./pkg/ pro konkrétní test
- go test -race ./... pro race condition detekci
```

```yaml
# .claude/rules/python-testing.md
---
paths:
  - "python-scripts/**/*.py"
---
# Python Testing Rules
- pytest jako test runner
- Fixtures v conftest.py
- Parametrize pro data-driven testy
- pytest-cov pro coverage reporting
- pytest -x pro zastavení na prvním failu
```

Kvantitativní benchmarky ukazují, že Claude zvládá staticky typované jazyky (Java, Go) **1.4–2.6× pomaleji** než dynamické (Python), ale výsledky jsou spolehlivé. Na Aider polyglot benchmarku (225 cvičení v C++, Go, Java, JS, Python, Rust) dosáhl Claude **76.4% úspěšnosti**.

---

## 6. CLI mody pro testera

Claude Code nabízí tři hlavní režimy, každý užitečný pro jiný QA scénář:

### Interaktivní režim (výchozí)

```bash
cd project-root
claude                                    # Spustí interaktivní session
claude "explain the auth flow in go-service"  # Jednorázový prompt s počáteční otázkou
claude --continue                         # Pokračuje v poslední konverzaci
claude --resume                           # Výběr z posledních sessions
```

Tohle je hlavní pracovní režim testera — průzkum kódu, kladení otázek, generování testů v dialogu. Užitečné příkazy uvnitř session: `/clear` (nový kontext), `/compact` (komprese kontextu), `/context` (zobrazí využití kontextu), `/memory` (správa paměti).

### Headless / Non-interactive režim (`-p`)

```bash
# Analýza logu
cat error.log | claude -p "Identifikuj root cause těchto chyb a navrhni test scénáře"

# Code review z Git diffu
git diff main | claude -p "Review tento diff z pohledu QA — hledej chybějící validace, edge cases, potenciální bugy"

# Generování test scénářů v batch režimu
claude -p "Vygeneruj test scénáře pro UserService.java" --output-format json

# Strukturovaný JSON výstup
claude -p "Analyzuj tento modul" --output-format json --json-schema '{"type":"object","properties":{"bugs":{"type":"array"},"test_gaps":{"type":"array"}}}'

# Pokračování v předchozí session
claude -p "Teď se zaměř na error handling" --continue
```

Headless mód je ideální pro **skriptování a CI/CD integrace**. Výstupní formáty: `text` (výchozí), `json` (strukturovaný), `stream-json` (real-time streaming). **Pro testera je klíčový pattern pipe:** vezměte výstup libovolného nástroje a pošlete ho Claude k analýze.

### Bare režim (minimální)

```bash
claude --bare -p "Summarize this file" --allowedTools "Read"
```

Přeskočí načítání hooks, skills, plugins, MCP serverů, auto memory a CLAUDE.md. Doporučený pro **CI/CD pipeline skripty** kde chcete maximální rychlost a kontrolu nad kontextem.

### Praktické CLI patterny pro QA testera

```bash
# Denní ranní ritual — zjisti co se změnilo
git log --oneline --since="yesterday" | claude -p "Shrň změny a identifikuj oblasti vyžadující regresní testování"

# Analýza test výsledků
./gradlew test 2>&1 | claude -p "Analyzuj test výsledky, identifikuj patterns ve failech"

# Porovnání API responses
diff <(curl -s api/v1/users) <(curl -s api/v2/users) | claude -p "Analyzuj rozdíly mezi v1 a v2 API responses"

# Batch generování testů pro více souborů
find src -name "*.java" -newer last_test_run | xargs -I {} claude -p "Navrhni test scénáře pro {}"
```

---

## 7. Efektivní správa context window

Kontext je **nejcennější zdroj** v Claude Code — performance degraduje s jeho plněním. S modely Opus 4.6 a Sonnet 4.6 je dostupný **1 milion tokenů** kontextu, ale i tak je správa kritická.

### Co se načte automaticky na začátku session

Na začátku každé session Claude automaticky načte: všechny aplikovatelné **CLAUDE.md** soubory z hierarchie, **auto memory** (prvních 200 řádků nebo 25KB z MEMORY.md), zkrácené **popisy skills** (budget ~1% context window, cca 8000 znaků), názvy **MCP nástrojů** a systémový prompt. Během session se pak přidávají čtené soubory, path-scoped rules a obsah invokovaných skills.

### Co dát explicitně do CLAUDE.md vs. nechat Claude najít

**Do CLAUDE.md explicitně:**
- Build/test příkazy (Claude je nemůže uhodnout)
- Nestandardní konvence (pokud se liší od defaultů)
- Architektonická rozhodnutí a vztahy mezi službami
- Workflow pravidla specifická pro tým
- Kritické varování (`YOU MUST NOT modify production config files`)

**Nechat Claude najít sám:**
- Standardní jazykové konvence (Go formatting, Python PEP8)
- Obsah souborů (Claude si je přečte on-demand)
- Strukturu projektu (Claude použije `list_directory`)
- API detaily (raději linkujte: `@docs/api-spec.yaml`)
- Implementační detaily jednotlivých souborů

### Strategie pro udržení kontextu čistého

Pravidlo `/clear` mezi nesouvisejícími úlohami je nejúčinnější technika. Pokud analyzujete Java service a pak přecházíte na Go service, udělejte `/clear`. Používejte **skills s `context: fork`** pro náročné operace — subagent dostane vlastní kontext. Kompakci říďte přes `/compact Focus on the test analysis results` s instrukcí co zachovat. Po dvou neúspěšných korekcích udělejte `/clear` a začněte s lepším promptem. A nastavte `disable-model-invocation: true` na skills, které chcete volat jen ručně — jejich popisy se pak nenačtou do kontextu automaticky.

---

## 8. MCP servery relevantní pro QA testera

MCP (Model Context Protocol) je od prosince 2025 pod Linux Foundation a stal se **průmyslovým standardem** s 1200+ dostupnými servery. Claude Code funguje jako MCP klient.

### Doporučená konfigurace pro QA tým (`.mcp.json`)

```json
{
  "mcpServers": {
    "github": {
      "type": "http",
      "url": "https://api.githubcopilot.com/mcp",
      "headers": {
        "Authorization": "Bearer $GITHUB_PAT"
      }
    },
    "jira": {
      "command": "uvx",
      "args": ["mcp-atlassian"],
      "env": {
        "JIRA_URL": "https://firma.atlassian.net",
        "JIRA_USERNAME": "$JIRA_USER",
        "JIRA_API_TOKEN": "$JIRA_TOKEN",
        "CONFLUENCE_URL": "https://firma.atlassian.net/wiki",
        "CONFLUENCE_USERNAME": "$JIRA_USER",
        "CONFLUENCE_API_TOKEN": "$JIRA_TOKEN"
      }
    },
    "playwright": {
      "command": "npx",
      "args": ["@playwright/mcp@latest", "--headless"]
    },
    "postgres": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-postgres"],
      "env": {
        "POSTGRES_CONNECTION_STRING": "$DATABASE_URL"
      }
    },
    "sentry": {
      "type": "http",
      "url": "https://mcp.sentry.dev/mcp"
    }
  }
}
```

### Přehled klíčových MCP serverů pro QA

**GitHub MCP** (oficiální, `github/github-mcp-server`) poskytuje správu issues, review PR, code search a správu branches. Přešel na HTTP transport přes `api.githubcopilot.com/mcp`. Pro QA testera klíčový pro vytváření bug issues přímo z Claude Code.

**Jira MCP** — existuje několik variant. Oficiální **Atlassian MCP** (`atlassian/atlassian-mcp-server`) podporuje OAuth 2.1 a pokrývá Jira + Confluence. Komunitní **mcp-atlassian** (`sooperset/mcp-atlassian`) je nejpopulárnější, podporuje Cloud i Server/Data Center a nabízí plnou JQL podporu. Specializovaný **Jira Zephyr MCP** (`leorosignoli/jira-zephyr-mcp`) je určen přímo pro test management — test plány, cykly a executions.

**Playwright MCP** (oficiální Microsoft, `@playwright/mcp`) umožňuje browser automation přes accessibility snapshots bez nutnosti vision modelů. Podporuje Chromium, Firefox a WebKit. Pro QA testera ideální pro exploratorní testování řízené AI. Alternativa **Selenium MCP** (`@angiejones/mcp-selenium`) pro týmy používající Selenium.

**Databázové MCP** — **DBHub** (`bytebase/dbhub`) je multi-database server podporující PostgreSQL, MySQL, SQL Server, MariaDB a SQLite přes jedno rozhraní, ideální pro verifikaci testovacích dat. Alternativně existují jednoúčelové servery pro PostgreSQL a MySQL.

**Sentry MCP** (oficiální, `getsentry/sentry-mcp`) poskytuje přístup k production error monitoring — stack traces, triage issues a identifikace regresí. Pro QA testera klíčový pro korelaci test failures s produkčními chybami. Nejsnazší instalace přes `/install-plugin sentry`.

**Robot Framework MCP** (`robotframework-mcp` na PyPI) nabízí nástroje specificky pro RF automatizaci — generování login testů, page object modelů, data-driven testů a validaci RF syntaxe.

Každý MCP server přidává tokeny do context window. Doporučení: **začněte s 2-3 servery** (GitHub + Jira + DB) a přidávejte postupně. Claude Code varuje, když MCP výstup překročí 10 000 tokenů.

---

## 9. Robot Framework integrace a plugin ekosystém

Pro generování **.robot souborů** existuje v roce 2026 dedikovaný ekosystém. Nejvýznamnějším nástrojem je **robotframework-agentskills** (`manykarim/robotframework-agentskills`) — Claude Code plugin marketplace poskytující **11 specializovaných AI skills** pro Robot Framework:

- **robotframework-browser-skill** — Web testing s Browser/Playwright
- **robotframework-api-skill** — API testing s Requests/RESTinstance
- **robotframework-appium-skill** — Mobile testing s Appium
- **robotframework-results** — Čtení output.xml a produkce JSON souhrnů
- **robotframework-libdoc-search** — Vyhledávání library keywords podle use case
- **robotframework-testcase-builder** — Generování .robot souborů ze strukturovaného JSON
- **robotframework-keyword-explainer** — Vysvětlení keywords a argumentů

Instalace: `claude plugin add github:manykarim/robotframework-agentskills`. Reálný příklad CLAUDE.md z projektu RPA Framework (Robocorp) ukazuje pattern pro monorepo s Python + Robot Framework testy: `invoke code.test-robot` pro RF testy, `invoke code.test-robot -r filename -t "Test Name"` pro konkrétní test.

---

## 10. Git verzování Claude Code konfigurace

### Co commitovat do Git (sdílené s týmem)

```
CLAUDE.md                    # Projektové instrukce
.mcp.json                    # MCP server konfigurace (bez tokenů!)
.claude/settings.json        # Projektová nastavení + hooks
.claude/skills/**/SKILL.md   # Sdílené skills
.claude/agents/*.md          # Sdílení subagenti
.claude/rules/*.md           # Modulární pravidla
.claude/hooks/*.sh           # Hook skripty
```

### Co dát do .gitignore

```gitignore
# Lokální Claude Code soubory
CLAUDE.local.md
.claude/settings.local.json
.claude.json

# Credentials a session data
.claude/.credentials.json
.claude/security_warnings_*.json
.claude/stats-cache.json
.claude/mcp-needs-auth-cache.json

# Session a historie
.claude/history.jsonl
.claude/backups/
.claude/cache/
.claude/debug/
.claude/session-env/
.claude/shell-snapshots/
.claude/file-history/
.claude/paste-cache/

# Agent state
.claude/plans/
.claude/plugins/
.claude/tasks/
.claude/teams/
.claude/todos/

# Telemetrie
.claude/statsig/
.claude/telemetry/
.claude/usage-data/

# IDE integrace
.claude/ide/
```

### Verzování osobní konfigurace (~/.claude)

```bash
cd ~/.claude
git init
git add .gitignore CLAUDE.md settings.json
git add skills/ agents/ commands/ statusline.sh 2>/dev/null
git commit -m "feat: initial QA claude config"
gh repo create claude-config --private --source=. --push
```

Pro osobní konfigurace tester udržuje **privátní Git repo** s `~/.claude/CLAUDE.md`, `settings.json`, a osobními skills. Pro projektovou konfiguraci se CLAUDE.md a `.claude/` commitují přímo do projektového repozitáře — **každý člen týmu tak dostane stejné Claude Code prostředí**. Lokální přepisy přes `CLAUDE.local.md` a `.claude/settings.local.json` zůstávají mimo Git.

---

## Závěr: praktický postup pro nového testera na projektu

Tester přicházející na nový projekt s Java/Go/Python stackem by měl postupovat ve čtyřech fázích. **Fáze 1 (den 1):** Spustit `/init` pro vygenerování základního CLAUDE.md, nastavit MCP servery pro Jira a GitHub, a použít `/explore-code` skill pro pochopení architektury. **Fáze 2 (týden 1):** Vytvořit skills pro opakující se workflow (bug-report, test-scenarios, generate-robot), nastavit path-scoped rules pro každý jazyk a nakonfigurovat hooks pro automatickou validaci. **Fáze 3 (průběžně):** Budovat knihovnu .robot souborů s pomocí generate-robot skill, iterovat na CLAUDE.md na základě zkušeností (přidat co chybí, odebrat co je zbytečné), verzovat vše přes Git. **Fáze 4 (optimalizace):** Sledovat kontext přes `/context`, přesunout doménově specifické znalosti do skills místo CLAUDE.md, a využít headless mód pro CI/CD integraci testovacího pipeline.

Klíčové poučení z komunity v roce 2026: **specializace nad generalizací**. OpenObserve dosáhl 85% redukce flaky testů a 7× zrychlení analýzy features díky 8 specializovaným AI agentům, každý definovaný jako Claude Code skill s přesně vymezenou rolí. Foxbox Digital snížil setup time o 70% díky preciznímu CLAUDE.md. Nejúčinnější investicí QA testera je čas strávený nad kvalitním CLAUDE.md a sadou specializovaných skills — zbytek Claude Code zvládne sám.