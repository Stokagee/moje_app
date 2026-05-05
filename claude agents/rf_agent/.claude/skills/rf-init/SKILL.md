# rf-init — Project Initialization and Mapping

## When to Use This Skill

Use whenever:
- User enters `/rf:init`
- You need to map repository structure
- Looking for existing tests, resources, wrappers
- Starting on a new project and need context
- User says "explore", "check project", "what do we have"

## Purpose

Map repository, understand structure, find all key files and prepare context for further work. If structure is missing or incomplete — suggest and create it.

## Workflow

### 1. Repository Exploration

Explore repository systematically. Look for:

```bash
# Top-level structure
ls -la
find . -name "*.robot" -o -name "*.resource" -o -name "*.py" | head -50

# Robot Framework files
find . -name "*.robot" | sort
find . -name "*.resource" | sort
find . -name "*.py" -path "*/libraries/*" -o -name "*.py" -path "*/lib/*" | sort

# BE code (for verifying endpoints and models)
find . -name "*.py" -path "*/routes/*" -o -name "*.py" -path "*/models/*" | head -30
find . -name "*.py" -path "*/migrations/*" | head -20

# Configuration
find . -name "*.yaml" -o -name "*.yml" -o -name "*.cfg" -o -name "*.ini" | head -20
```

### 2. Analysis of Found Files

For each category find out:

**Tests (.robot):**
- How many tests exist
- How they are organized (per feature? per endpoint? per module?)
- What tags are used
- Suite setup/teardown patterns

**Resources (.resource):**
- Which common wrappers exist (look for `common_api.resource`, `common_db.resource`)
- What page objects / endpoint resources exist
- How they are imported (relative vs. absolute paths)

**Libraries (.py):**
- Custom Python libraries
- What dependencies they have

**BE code:**
- API structure (routes, controllers)
- Data models
- DB migrations and schemas

### 3. Output — Project Map

Create structured overview:

```
## Project Map

### Folder Structure
<tree of main folders>

### Tests
- Count: X
- Organization: <per feature / per endpoint / other>
- Tags: <found tags>

### Resources
- Common wrappers: <list>
- Endpoint resources: <list>
- Page objects: <list>

### Libraries
- Custom: <list>
- External dependencies: <requirements.txt content>

### BE Context
- API framework: <Flask / FastAPI / Django / other>
- DB: <PostgreSQL / other>
- Key models: <list>

### Configuration
- Test execution: <command>
- Environment variables: <what's needed>

### Issues and Recommendations
- <what's missing, what's poorly named, what's inconsistent>
```

### 4. Scaffolding — If Needed

If structure is missing or incomplete, suggest recommended structure:

```
tests/
├── api/
│   ├── users/
│   │   ├── users_crud.robot
│   │   └── users_crud.resource
│   ├── orders/
│   │   ├── orders_crud.robot
│   │   └── orders_crud.resource
│   └── auth/
│       ├── auth_login.robot
│       └── auth_login.resource
├── db/
│   └── <db-only validation tests>
├── e2e/
│   └── <end-to-end scenarios>
└── common/
    ├── common_api.resource
    ├── common_db.resource
    └── common_setup.resource
```

**Scaffolding rules:**
- Suggest, DON'T CREATE automatically — show user and wait for approval
- If project already has partial structure — adapt suggestion to what exists
- New feature = new folder + .robot + .resource file
- Name folders after business domains, not technical layers

### 5. Context Storage

At the end summarize findings in a short block:

```
## Project Context
- Structure: <description>
- Common wrappers: common_api.resource (Create API Session, API request), common_db.resource (Connect To Test Database, ...)
- Execution: <command>
- BE: <framework>, DB: <type>
- Conventions: <what you discovered>
```

## What NOT To Do

- Don't create files without user approval
- Don't change existing structure
- Don't guess names — if something is unclear, write TODO and ask
- Don't ignore BE code — always explore it, it's the source of truth for endpoints and models
