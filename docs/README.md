# Robot Framework Learning Documentation

Complete learning materials for Robot Framework testing over a real full-stack application.

**Application:** React Native/Expo frontend + FastAPI backend + PostgreSQL database

**Libraries Covered:** Browser, Requests, Database, Appium

---

## 📚 Documentation Structure

```
docs/
├── README.md (this file)
│
├── 00_GETTING_STARTED/           # Start here!
│   ├── 00_Installation.md         # Setup guide
│   ├── 01_FirstTest.md            # Your first test
│   └── 02_RunningTests.md         # How to run tests
│
├── 01_BROWSER_LIBRARY/           # UI Testing with Playwright
│   ├── BEGINNER/
│   │   ├── 00_BrowserBasics.md     # Browser setup, navigation
│   │   ├── 01_ElementInteractions.md  # Click, type, forms
│   │   ├── 02_Navigation.md        # Page navigation
│   │   └── 03_WaitingStrategies.md # Waiting techniques
│   ├── INTERMEDIATE/
│   │   ├── 00_PageObjectModel.md   # POM pattern
│   │   ├── 01_Locators.md          # Selector strategies
│   │   ├── 02_ErrorHandling.md     # TRY-EXCEPT, debugging
│   │   └── 03_Screenshots.md        # (planned)
│   ├── ADVANCED/
│   │   ├── 00_Workflows.md          # Complex scenarios
│   │   ├── 01_TestDataManagement.md # Data-driven testing
│   │   └── 02_NetworkInterception.md # API mocking
│   └── REFERENCE/
│       └── BrowserKeywords.md      # Quick reference
│
├── 02_REQUESTS_LIBRARY/          # API Testing
│   ├── BEGINNER/
│   │   ├── 00_APIBasics.md         # HTTP methods, REST
│   │   ├── 01_GETRequests.md       # GET, pagination
│   │   ├── 02_POSTRequests.md      # POST, validation
│   │   └── 03_ResponseValidation.md # Assert responses
│   ├── INTERMEDIATE/
│   │   ├── 00_APIStructure.md      # Architecture patterns
│   │   ├── 01_EndpointsLayer.md    # URL management
│   │   ├── 02_APIActionsLayer.md  # API call keywords
│   │   └── 03_WorkflowsLayer.md    # Business logic
│   ├── ADVANCED/
│   │   ├── 00_CRUDOperations.md    # Full CRUD patterns
│   │   ├── 01_ErrorScenarios.md     # Negative testing
│   │   └── 02_APIUIIntegration.md  # Hybrid testing
│   └── REFERENCE/
│       └── RequestsKeywords.md    # Quick reference
│
├── 03_DATABASE_LIBRARY/          # Database Testing
│   ├── BEGINNER/
│   │   ├── 00_DBBasics.md          # PostgreSQL, connections, queries
│   │   ├── 01_BestPractices.md     # Clean code patterns, TRY/FINALLY
│   │   └── 02_AntiPatterns.md      # Common mistakes to avoid
│   ├── INTERMEDIATE/
│   │   ├── 00_ConnectionManagement.md  # Connection pooling, retry logic
│   │   └── 01_CleanupStrategies.md     # Guaranteed cleanup patterns
│   ├── ADVANCED/
│   │   ├── 00_PerformancePatterns.md  # Query optimization
│   │   └── 01_ComplexQueries.md       # JOINs, CTEs, window functions
│   └── REFERENCE/
│       └── DatabaseKeywords.md    # Complete keyword reference
│
├── 04_APPIUM_LIBRARY/            # Mobile Testing
│   ├── BEGINNER/
│   │   ├── 00_MobileBasics.md      # Appium setup, devices
│   │   ├── 01_AppiumSetup.md       # Configuration
│   │   └── 02_MobileInteractions.md # Gestures, locators
│   └── REFERENCE/
│       └── AppiumKeywords.md      # Quick reference
│
├── 05_INTEGRATION_PATTERNS/      # Multi-Layer Testing
│   ├── 00_FullStackTests.md       # UI+API+DB together
│   ├── 01_APIUIIntegration.md    # Hybrid patterns
│   └── 02_APIDBIntegration.md    # Backend verification
│
├── 06_ADVANCED_TOPICS/          # Specialized Topics
│   ├── 00_DataDrivenTesting.md   # DDT, templates
│   ├── 01_CustomLibraries.md    # Python libraries
│   └── 02_VisualRegression.md   # Image comparison
│
└── APPENDICES/                   # Reference Materials
    ├── 00_QuickReference.md     # Command & syntax ref
    ├── 01_ApplicationContext.md # API/DB schema
    ├── 02_Terminology.md         # Glossary of terms
    └── 03_Troubleshooting.md     # Debugging guide
```

---

## 🚀 Quick Start

### 1. **Beginner Path** (4-6 weeks)

```
Week 1: Setup & Basics
├── 00_Installation.md
├── 01_FirstTest.md
└── 02_RunningTests.md

Week 2-3: Browser Library (UI Testing)
├── 00_BrowserBasics.md
├── 01_ElementInteractions.md
├── 02_Navigation.md
└── 03_WaitingStrategies.md

Week 4: Requests Library (API Testing)
├── 00_APIBasics.md
├── 01_GETRequests.md
└── 02_POSTRequests.md

Week 5: Database Library
├── 00_DBBasics.md
└── 01_ConnectionSetup.md
```

### 2. **Intermediate Path** (4-6 weeks)

```
Browser Library:
├── 00_PageObjectModel.md
├── 01_Locators.md
└── 02_ErrorHandling.md

Requests Library:
├── 00_APIStructure.md
├── 01_EndpointsLayer.md
└── 03_WorkflowsLayer.md

Integration:
└── 00_FullStackTests.md
```

### 3. **Advanced Path** (4-6 weeks)

```
Advanced Topics:
├── 00_DataDrivenTesting.md
├── 01_CustomLibraries.md
└── 02_VisualRegression.md

Integration Patterns:
├── 00_FullStackTests.md
├── 01_APIUIIntegration.md
└── 02_APIDBIntegration.md
```

---

## 📖 Learning Paths by Library

### Browser Library (UI Testing)

**Goal:** Master web UI automation

1. **Beginner** → Learn basics of browser automation
   - Browser setup and navigation
   - Element interactions (click, type)
   - Waiting strategies

2. **Intermediate** → Build maintainable test suites
   - Page Object Model
   - Advanced selectors
   - Error handling

3. **Advanced** → Complex workflows
   - Multi-page scenarios
   - Data-driven testing
   - Network interception

**Key Files:**
- `/RF/UI/locators/` - Selector examples
- `/RF/UI/pages/` - Page keyword examples
- `/RF/UI/tests/` - Complete test examples

---

### Requests Library (API Testing)

**Goal:** Master REST API testing

1. **Beginner** → Learn HTTP and REST
   - GET/POST requests
   - JSON handling
   - Status codes

2. **Intermediate** → Build maintainable API tests
   - 4-layer architecture
   - Session management
   - Response validation

3. **Advanced** → Complex API scenarios
   - Full CRUD operations
   - Error scenarios
   - API + DB verification

**Key Files:**
- `/RF/API/endpoints/` - Endpoint definitions
- `/RF/API/api_actions/` - API call examples
- `/RF/API/workflows/` - Workflow examples
- `/RF/API/tests/` - Complete test examples

---

### Database Library

**Goal:** Master database testing and verification

1. **Beginner** → Learn SQL basics and best practices
   - Connection setup and teardown
   - Simple queries (SELECT, COUNT)
   - Data verification
   - **NEW:** Best practices (TRY/FINALLY, SUITE scope)
   - **NEW:** Anti-patterns (what NOT to do)

2. **Intermediate** → Advanced connection and cleanup
   - **NEW:** Connection management (retry logic, health checks)
   - **NEW:** Cleanup strategies (FINALLY, Teardown, transaction rollback)
   - Connection pooling
   - Error handling

3. **Advanced** → Performance and complex queries
   - **NEW:** Performance patterns (query optimization, batch operations)
   - **NEW:** Complex queries (JOINs, CTEs, window functions, JSON)
   - API + DB verification
   - Data integrity checks

**Key Files:**
- `/RF/db/tests/` - DB test examples
- `/RF/db/common.resource` - DB utilities
- `/be/app/models/` - Database schema

**Learning Path:**
```
BEGINNER:
├── 00_DBBasics.md           # Start here - setup and basic queries
├── 01_BestPractices.md      # TRY/FINALLY, SUITE scope, clean code
└── 02_AntiPatterns.md       # Common mistakes and how to avoid them

INTERMEDIATE:
├── 00_ConnectionManagement.md  # Connection pooling, retry logic, health checks
└── 01_CleanupStrategies.md     # Guaranteed cleanup patterns

ADVANCED:
├── 00_PerformancePatterns.md  # Query optimization, batch operations
└── 01_ComplexQueries.md       # JOINs, CTEs, window functions, JSON handling

REFERENCE:
└── DatabaseKeywords.md       # Complete keyword reference with examples
```

---

## 🎯 How to Use This Documentation

### For Self-Learning

1. **Start with GETTING_STARTED** - Set up your environment
2. **Choose a library path** (Browser → Requests → Database)
3. **Work through BEGINNER files** - Learn fundamentals
4. **Progress to INTERMEDIATE** - Build maintainable tests
5. **Explore ADVANCED topics** - Master complex scenarios

### For AI-Assisted Learning

Use these prompts with your AI assistant:

```
# Start learning
"I want to learn Robot Framework Browser Library. Start with 00_BROWSER_LIBRARY/BEGINNER/00_BrowserBasics.md"

# Get exercises
"Give me an exercise from Browser Library BEGINNER level"

# Get hints
"I'm stuck on exercise ex01_fill_form. Give me a hint"

# Progressive help
"Give me hint 2 for exercise ex01_fill_form"
"Show me the solution for ex01_fill_form"

# Move to next topic
"I've mastered Browser Basics. What's next?"

# Focus on specific skill
"I want to practice error handling in Browser tests. What exercises do you have?"
```

### For Reference

- **Quick Reference** (`APPENDICES/00_QuickReference.md`)
  - Command syntax
  - Common patterns
  - Status codes

- **Troubleshooting** (`APPENDICES/03_Troubleshooting.md`)
  - Common errors
  - Debugging tips
  - Solutions

- **Application Context** (`APPENDICES/01_ApplicationContext.md`)
  - API endpoints
  - Database schema
  - UI selectors

---

## 📁 Project File References

All documentation references actual project files:

### Frontend (React Native/Expo)
- **Location:** `/fe/mojeApp/src/component/pages/`
- **Use:** UI testing examples, test IDs
- **Key Files:**
  - `FormPage.js` - Form with test IDs
  - `Page2.js` - List view
  - `Page3.js` - Orders
  - `Page4.js` - Dispatch

### Backend (FastAPI)
- **Location:** `/be/app/api/endpoints/`
- **Use:** API testing examples
- **Key Files:**
  - `form_data.py` - Form CRUD
  - `couriers.py` - Courier management
  - `orders.py` - Order lifecycle
  - `dispatch.py` - Auto-assignment

### Database Models
- **Location:** `/be/app/models/`
- **Use:** Database testing schema reference
- **Key Files:**
  - `form_data.py` - Form table
  - `courier.py` - Courier table
  - `order.py` - Order table

### Robot Framework Tests
- **Location:** `/RF/`
- **Use:** Real test examples
- **Key Files:**
  - `/RF/UI/` - UI test examples
  - `/RF/API/` - API test examples
  - `/RF/db/` - DB test examples

---

## 🎓 Learning Strategies

### Strategy 1: Sequential Learning

1. Complete GETTING_STARTED
2. Work through Browser Library BEGINNER
3. Work through Requests Library BEGINNER
4. Work through Database Library BEGINNER
5. Return to Browser/Requests INTERMEDIATE

### Strategy 2: Skill-Focused

1. **UI Testing:** Browser Library (all levels)
2. **API Testing:** Requests Library (all levels)
3. **Data Verification:** Database Library
4. **Integration:** Integration Patterns
5. **Advanced:** Custom Libraries, DDT

### Strategy 3: Project-Based

1. **Goal:** "I want to test form submission"
2. Learn: Browser interactions (submit form)
3. Learn: API verification (check API)
4. Learn: DB verification (check database)
5. Practice: Integration Patterns

---

## 💡 Tips for Success

1. **Practice with Real Application**
   - All examples use the actual app
   - Run tests against running instance
   - Modify and experiment

2. **Do Exercises, Don't Just Read**
   - Each file has exercises
   - Progressive hints available
   - Full solutions provided

3. **Build on Previous Knowledge**
   - Master BEGINNER before INTERMEDIATE
   - Each level builds on earlier concepts

4. **Use the References**
   - Check Quick Reference when stuck
   - Review Troubleshooting for errors
   - Consult Application Context for API/DB details

5. **Ask AI for Help**
   - Can provide hints for exercises
   - Can explain concepts differently
   - Can generate additional examples

---

## 🔧 Environment Setup

### Prerequisites

```bash
# Python 3.8+
python --version

# Virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # macOS/Linux

# Install RF and libraries
pip install robotframework
pip install robotframework-browser
pip install robotframework-requests
pip install robotframework-databaselibrary
pip install robotframework-faker
```

### Application Setup

```bash
# Backend
cd be && uvicorn app.main:app --reload

# Frontend
cd fe/mojeApp && npm run web

# Database (Docker)
docker compose up -d db
```

---

## 📊 Progress Tracking

Track your learning progress:

### Beginner Level
- [ ] Completed installation
- [ ] Can write basic Browser tests
- [ ] Can write basic API tests
- [ ] Can write basic DB queries

### Intermediate Level
- [ ] Using Page Object Model
- [ ] Using 4-layer API architecture
- [ ] Writing reusable keywords
- [ ] Handling errors properly

### Advanced Level
- [ ] Data-driven testing
- [ ] Custom library development
- [ ] Full-stack integration tests
- [ ] Performance testing

---

## 🤝 Contributing

Want to improve the documentation?

1. Fix typos or errors
2. Add more examples
3. Create additional exercises
4. Improve explanations

All documentation files are Markdown and easy to edit!

---

## 📞 Support

### Getting Stuck?

1. **Check Troubleshooting Guide** (`APPENDICES/03_Troubleshooting.md`)
2. **Review Quick Reference** (`APPENDICES/00_QuickReference.md`)
3. **Check Project Examples** - Real code in `/RF/` folders
4. **Ask AI Assistant** - Use prompts above

### Common Issues

| Issue | Solution |
|-------|----------|
| Port 8081 occupied | Change `FRONTEND_PORT` in `.env` |
| Backend won't start | Check Python dependencies |
| Tests fail randomly | Add explicit waits |
| Database errors | Verify PostgreSQL running |

---

## 📈 Learning Roadmap

### Phase 1: Foundation (Weeks 1-4)
**Outcome:** Can write simple tests for all layers

- Setup & Installation
- Browser Library basics
- Requests Library basics
- Database Library basics

### Phase 2: Structure (Weeks 5-8)
**Outcome:** Can design maintainable test suites

- Page Object Model
- 4-layer API architecture
- Error handling
- Test organization

### Phase 3: Integration (Weeks 9-12)
**Outcome:** Can test complex scenarios

- Integration patterns
- Data-driven testing
- Custom libraries
- Full-stack testing

---

## 🎉 Ready to Start!

Begin with: **00_GETTING_STARTED/00_Installation.md**

Good luck with your Robot Framework learning journey! 🚀
