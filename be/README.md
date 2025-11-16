
# Frontend
- React Native
- Expo
- React Navigation
- React Native Picker

# Backend
- FastAPI
- PostgreSQL
- SQLAlchemy
- Pydantic

# Instalace a spuštění
- Frontend, nainstalujte závislosti:
- npm install

# Spusťte aplikaci:
- npx expo start
- Naskenujte QR kód v Expo Go aplikaci na telefonu

# Backend
Nainstalujte závislosti:
- pip install -r requirements.txt

# Vytvořte soubor .env s proměnnými prostředí:
- env
- DATABASE_URL=postgresql://username:password@localhost:5432/your_database_name
- LOG_LEVEL=INFO
- LOG_FILE=app.log

# Spusťte server:
- uvicorn app.main:app --reload

# Databázová struktura
- Aplikace ukládá data do PostgreSQL s následující strukturou:
Column	Type	Constraints
id	Integer	Primary Key, Index
first_name	String	Not Null, Index
last_name	String	Not Null, Index
phone	String	Not Null, Index
gender	String	Not Null, Index
email	String	Not Null, Unique, Index

# API Endpointy
POST /api/v1/form/ - Odeslání formulářových dat
GET /api/v1/form/ - Získání všech záznamů
GET /api/v1/form/{id} - Získání konkrétního záznamu
POST /api/v1/form/evaluate-name - Vyhodnocení textu/jména (mini hra)

# Struktura projektu
Frontend
/mojeApp
/src
  /common
    Button.js
    Input.js
  /layout
    Container.js
  /pages
    FormPage.js
    Page2.js
    Page3.js
    Page4.js
  AppNavigator.js
Backend
  /app
    /api
      /endpoints
        form_data.py
    /core
      config.py
      logging.py
    /crud
      form_data.py
    /models
      form_data.py
    /schemas
      form_data.py
    database.py
    main.py
  requirements.txt
  .env

# Testování
- Aplikace obsahuje testovací identifikátory (testID) pro automatizované testování:
- firstNameInput - Vstup pro jméno
- lastNameInput - Vstup pro příjmení
- phoneInput - Vstup pro telefon
- emailInput - Vstup pro email
- genderPicker - Výběr pohlaví
- submitButton - Tlačítko pro odeslání

# Použití
- Spusťte backend server
- Spusťte frontend aplikaci
- Vyplňte formulářová pole
- Ověřte, že jsou všechna pole vyplněna
- Klikněte na tlačítko "Odeslat"
- Data se odešlou na server a uloží do databáze
- Aplikace vás přesměruje na další stránku
 - Pokud křestní jméno nebo příjmení odpovídá tajným jménům, odpověď obsahuje:
   - easter_egg: true
   - secret_message: string s hláškou pro zobrazení na FE

## Mini hra – API kontrakt

- Rozšířená odpověď POST /api/v1/form/:
  {
    id, first_name, last_name, phone, gender, email,
    easter_egg: boolean,
    secret_message: string | null
  }

- Samostatný endpoint:
  POST /api/v1/form/evaluate-name
  Body: { "text": "libovolný vstup" }
  Response: { "matched": boolean, "message": string | null }

# Řešení problémů
- Ujistěte se, že je PostgreSQL server spuštěn
- Zkontrolujte připojení k databázi v souboru .env
- Pro frontend použijte Node.js verzi kompatibilní s Expo

