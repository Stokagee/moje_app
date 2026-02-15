# Installation & Setup

## Learning Objectives
- [ ] Install Python and pip
- [ ] Set up Robot Framework
- [ ] Install required libraries (Browser, Requests, Database, Appium)
- [ ] Verify installation

## Prerequisites
- Windows, macOS, or Linux operating system
- Administrator/sudo access for installation
- Basic command line knowledge

---

## 1. Install Python

**Windows:**
1. Download from [python.org](https://www.python.org/downloads/)
2. Run installer - **Check "Add Python to PATH"**
3. Verify: `python --version`

**macOS:**
```bash
brew install python3
```

**Linux:**
```bash
sudo apt-get install python3 python3-pip
```

---

## 2. Create Project Virtual Environment

```bash
# Navigate to your project
cd moje_app/RF

# Create virtual environment
python -m venv .venv

# Activate (Windows)
.venv\Scripts\activate

# Activate (macOS/Linux)
source .venv/bin/activate
```

**Tip:** You should see `(.venv)` in your terminal prompt.

---

## 3. Install Robot Framework

```bash
pip install --upgrade pip
pip install robotframework
```

Verify:
```bash
robot --version
# Output: Robot Framework 7.2.2
```

---

## 4. Install Testing Libraries

```bash
# Browser Library (UI testing with Playwright)
pip install robotframework-browser

# Requests Library (API testing)
pip install robotframework-requests

# Database Library (PostgreSQL, MySQL, etc.)
pip install robotframework-databaselibrary

# Appium (Mobile testing)
pip install robotframework-appiumlibrary

# Supporting libraries
pip install robotframework-faker
pip install robotframework-jsonlibrary
pip install robotframework-debuglibrary
```

---

## 5. Install Browser Dependencies

Browser Library requires Playwright browsers:

```bash
# Install Playwright browsers
playwright install chromium
```

**Optional:** Install other browsers
```bash
playwright install firefox
playwright install webkit
```

---

## 6. Database Driver (PostgreSQL)

For this application's PostgreSQL database:

```bash
pip install psycopg2-binary
```

**For other databases:**
- MySQL: `pip install pymysql`
- Oracle: `pip install cx_Oracle`
- MSSQL: `pip install pymssql`

---

## 7. Verify Installation

Create test file `verify_installation.robot`:

```robotframework
*** Settings ***
Library    Browser
Library    RequestsLibrary
Library    DatabaseLibrary

*** Test Cases ***
Verify Libraries Are Available
    Log    Robot Framework Version: ${ROBOT_VERSION}
    Log    Browser Library: ${BROWSER_VERSION}
    Log    Installation successful!    level=INFO
```

Run:
```bash
robot verify_installation.robot
```

Expected output:
```
==============================================================================
Verify Installation
==============================================================================
Verify Libraries Are Available                                             | PASS |
------------------------------------------------------------------------------
Verify Installation                                                       | PASS |
1 test, 1 passed, 0 failed
==============================================================================
```

---

## 8. Application Setup (Optional)

If you want to test against the real application:

### Backend (FastAPI)
```bash
cd be
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Backend runs at: `http://localhost:8000`

### Frontend (React Native/Expo Web)
```bash
cd fe/mojeApp
npm install
npm run web
```

Frontend runs at: `http://localhost:8081`

### Database (PostgreSQL with Docker)
```bash
docker compose up -d db
```

Or use local PostgreSQL:
- Database: `moje_app`
- User: `postgres`
- Password: `postgres`
- Port: `5432`

---

## Common Pitfalls

| Pitfall | Why It Happens | How to Avoid |
|---------|---------------|--------------|
| `robot` command not found | Python not in PATH | Reinstall Python with "Add to PATH" checked |
| Import errors | Wrong virtual environment | Ensure `(.venv)` is active in terminal |
| Browser library fails | Playwright not installed | Run `playwright install chromium` |
| DB connection fails | Missing driver | Install `psycopg2-binary` for PostgreSQL |

---

## Self-Check Questions

1. What command activates the virtual environment on Windows?
2. Which library is used for UI automation with Robot Framework?
3. What is the purpose of `playwright install chromium`?
4. How do you verify Robot Framework is installed correctly?

---

## References

- [Robot Framework Official Guide](https://robotframework.org/robotframework/latest/RobotFrameworkUserGuide.html)
- [Browser Library Docs](https://marketsquare.github.io/robotframework-browser/Browser.html)
- [Requests Library Docs](https://github.com/arketii/robotframework-requests)
- [Database Library Docs](https://github.com/frank-rouvy/RobotFramework-Database-Library)
- Project: `/RF/requirements.txt`
