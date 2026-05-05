# Robot Framework Agent

Claude Code agent for Robot Framework test automation.

## Installation

1. Place this directory in `.claude/agents/` or use as standalone agent
2. Claude Code will automatically load the configuration

## Usage

### Available Commands

| Command | Description |
|--------|-------|
| `/rf:init` | Map project and suggest structure |
| `/rf:test` | Create new test or extend existing |
| `/rf:keyword` | Create reusable keyword or wrapper |
| `/rf:refactor` | Clean code without changing test meaning |
| `/rf:review` | Code review - find issues, give report |

### Examples

```
# Project initialization
/rf:init

# Create new test
/rf:test
> I want to test endpoint /api/users POST

# Create keyword
/rf:keyword
> I need a keyword to create test user

# Refactoring
/rf:refactor
> Clean file tests/api/users.robot

# Code review
/rf:review
> Check tests/api/orders.robot
```

## Directory Structure

```
rf_agent/
├── CLAUDE.md              # Main file for Claude Code
├── prompts/system/        # System prompts
│   └── rf_agent.md        # Main agent prompt
├── skills/                # Skill definitions
│   ├── rf-init.md
│   ├── rf-test.md
│   ├── rf-keyword.md
│   ├── rf-refactor.md
│   └── rf-review.md
├── templates/             # Templates for .robot/.resource
├── examples/              # Examples of good code
├── config/                # Conventions and configurations
└── docs/                  # Documentation
```

## Conventions

### Variables
- Format: `${<role>_<domain>_<entity>_<purpose>}`
- Example: `${api_create_user_response}`, `${db_user_from_database}`
- FORBIDDEN: `${data}`, `${response}`, `${result}`, `${item}`, `${row}`

### Wrappers
- ALWAYS use `API request` from common_api.resource
- ALWAYS use DB wrappers from common_db.resource
- NEVER call RequestsLibrary/DatabaseLibrary directly in tests

### Documentation
- Every test has `[Documentation]`
- Every keyword has `[Documentation]`
- Code and error messages in English, prompts in Czech
