# Robot Framework Tests

## Instalace

### 1. Aktivuj virtual environment
```powershell
# PowerShell
.\.venv\Scripts\Activate.ps1

# CMD
.venv\Scripts\activate.bat

# Git Bash
source .venv/Scripts/activate
```

### 2. Nainstaluj Robot Framework dependencies
```bash
cd RF
pip install -r requirements.txt
```

### 3. Inicializuj Browser library (Playwright browsers)
```bash
rfbrowser init
```

## Spuštění testů

### API testy
```bash
cd RF/API
robot tests/create_form.robot
robot tests/form_crud_tests.robot
robot tests/easter_egg_tests.robot
```

### UI testy
```bash
cd RF/UI
robot tests/new_form.robot
```

## Ověření instalace
```bash
# Zkontroluj Robot Framework verzi
robot --version

# Zkontroluj Browser library
rfbrowser --version

# Zobraz nainstalované RF knihovny
pip list | grep robot
```

## Troubleshooting

### "rfbrowser: command not found"
Ujisti se, že jsi aktivoval venv a nainstaloval requirements.txt

### Browser library nefunguje
Spusť: `rfbrowser init` pro stažení Playwright browsers

### VS Code nevidí RF keywords
1. Nainstaluj extension: "Robot Framework Language Server"
2. Nastav Python interpreter na venv: Ctrl+Shift+P → "Python: Select Interpreter"
