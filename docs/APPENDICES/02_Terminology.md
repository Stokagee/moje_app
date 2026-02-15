# Terminology and Concepts

## Robot Framework Terms

### Test Case
A single test scenario that verifies specific functionality.

```robotframework
*** Test Cases ***
My Test Case
    [Documentation]    This is a test case
    No Operation
```

### Test Suite
A collection of test cases in one or more files.

### Keyword
Reusable function that can be called from test cases or other keywords.

```robotframework
*** Keywords ***
My Keyword
    [Arguments]    ${param}
    Log    Parameter: ${param}
```

### Resource File
File containing variables, keywords, or settings to be imported.

```robotframework
*** Settings ***
Resource    common.resource
Resource    locators/page.resource
```

### Library
External Python module that extends Robot Framework functionality.

```robotframework
*** Settings ***
Library     Browser
Library     RequestsLibrary
Library     DatabaseLibrary
```

---

## Web Testing Terms

### Selector
Pattern used to find elements on a web page.

**Types:**
- CSS Selector: `.class`, `#id`, `[attr="value"]`
- XPath: `//div[@class="example"]`
- Text: `"Button text"`
- data-testid: `[data-testid="element"]`

### DOM (Document Object Model)
Tree structure of HTML elements that browsers create from HTML.

### Page Object Model (POM)
Design pattern that creates objects for each page, encapsulating element locators and interactions.

### Timeout
Maximum time to wait for an action or condition.

### Explicit Wait
Waiting for a specific condition before proceeding.

### Implicit Wait
Automatic waiting (Browser Library does this automatically).

### Headless Browser
Browser running without visible UI (good for CI/CD).

### Viewport
Visible area of browser window (width x height).

---

## API Testing Terms

### Endpoint
URL path where API receives requests (e.g., `/form/`, `/users/{id}`).

### Method/Verb
HTTP operation type: GET, POST, PUT, PATCH, DELETE.

### Request
Data sent to API (headers, body, parameters).

### Response
Data returned from API (status code, headers, body).

### JSON
JavaScript Object Notation - common data format for APIs.

### REST (Representational State Transfer)
Architectural style for APIs using HTTP methods.

### Status Code
3-digit number indicating request result (200=success, 400=client error, 500=server error).

### Header
Metadata in request/response (Content-Type, Authorization, etc.).

### Payload
Request body containing data.

### Idempotent
Operation that can be applied multiple times with same result (GET, PUT, DELETE).

### Pagination
Splitting large result sets into multiple pages.

---

## Database Terms

### Query
SQL command to retrieve data (SELECT).

### Table
Database structure that stores data in rows and columns.

### Row/Record
Single entry in a table.

### Column/Field
Single attribute in a table.

### Primary Key
Unique identifier for each row (id).

### Foreign Key
Reference to primary key in another table.

### Transaction
Group of database operations treated as single unit.

### Connection
Link between application and database.

### Cursor
Pointer used to traverse query results.

---

## Automation Concepts

### Test Data Management
Strategies for managing data used in tests (Faker, fixtures, factories).

### Test Isolation
Ensuring tests don't depend on each other.

### Cleanup
Removing test data after test execution.

### Flaky Test
Test that passes/fails intermittently without code changes.

### Race Condition
Timing-dependent bug where concurrent operations interfere.

### Stub
Simplified replacement for component during testing.

### Mock
Fake component that simulates real behavior.

### Fixture
Fixed state of environment for testing.

### Setup
Preparation before test execution.

### Teardown
Cleanup after test execution.

### Regression Testing
Testing existing functionality after changes.

### Smoke Testing
Quick basic functionality tests.

### Integration Testing
Testing interaction between components.

### End-to-End (E2E) Testing
Testing complete user workflows.

### Acceptance Testing
Verifying requirements are met.

### Negative Testing
Testing error conditions and invalid inputs.

### Positive Testing
Testing with valid inputs (happy path).

### Edge Case
Extreme values or unusual scenarios.

### Boundary Value
Testing at limits of valid ranges.

---

## Architecture Patterns

### Layered Architecture
Separation into distinct layers (UI, API, DB).

### 4-Layer Architecture (API Tests)
1. **Endpoints**: URL definitions
2. **Actions**: Individual API calls
3. **Workflows**: Business logic
4. **Tests**: Test scenarios

### Page Object Model
Organizing UI code by pages/components.

### Data-Driven Testing
Running same test with different data sets.

### Keyword-Driven Testing
Using keywords to describe test steps in business language.

### Behavior-Driven Development (BDD)
Describing behavior in natural language (Given/When/Then).

### Test Pyramid
Testing strategy: many unit tests, fewer integration tests, fewest E2E tests.

---

## CI/CD Terms

### Continuous Integration
Automatically integrating and testing code changes.

### Continuous Deployment
Automatically deploying code after tests pass.

### Build Process
Compiling and preparing code for deployment.

### Pipeline
Sequence of automated steps (build, test, deploy).

### Artifact
Output of build process (executable, container image).

### Environment
Stage in deployment pipeline (dev, staging, production).

### Branch Protection
Rules for code changes (require tests, reviews).

### Pull Request
Proposed changes to codebase.

### Merge
Combining code changes into main branch.

### Rollback
Reverting to previous version after failure.

---

## Performance Terms

### Response Time
Time taken for system to respond.

### Latency
Delay in data transfer.

### Throughput
Number of requests processed per time unit.

### Load Testing
Testing system under expected load.

### Stress Testing
Testing system beyond expected load.

### Performance Testing
Measuring system speed and stability.

### Benchmark
Standard for measuring performance.

### Optimization
Improving system performance.

---

## Security Terms

### Authentication
Verifying user identity.

### Authorization
Verifying user permissions.

### OAuth
Standard for secure authorization.

### Token
String proving authentication/authorization.

### API Key
Secret key for API access.

### Encryption
Encoding data to prevent unauthorized access.

### SQL Injection
Attacking database via malicious queries.

### XSS (Cross-Site Scripting)
Injecting malicious scripts into web pages.

### CSRF (Cross-Site Request Forgery)
Tricking user into unwanted actions.

---

## Git Terms

### Repository
Storage for project files and history.

### Commit
Save point in project history.

### Branch
Parallel version of code.

### Merge
Combining branches.

### Pull Request
Request to merge branch.

### Conflict
Incompatible changes between branches.

### Clone
Copy repository to local machine.

### Pull
Update local copy with remote changes.

### Push
Send local changes to remote.

### Remote
Repository on server (GitHub, GitLab).

---

## Docker Terms

### Image
Template for creating containers.

### Container
Running instance of an image.

### Volume
Storage for persistent data.

### Network
Communication between containers.

### Compose
Tool for managing multi-container apps.

### Registry
Storage for Docker images.

### Dockerfile
Script to build Docker image.

### Service
Container in compose configuration.

---

## Development Terms

### Debugging
Finding and fixing errors.

### Logging
Recording events during execution.

### Exception
Error that disrupts normal flow.

### Error Handling
Managing errors gracefully.

### Validation
Checking data correctness.

### Refactoring
Improving code structure without changing behavior.

### Technical Debt
Cost of future changes from quick fixes.

### Code Smell
Indicator of potential problems.

### Anti-Pattern
Common but ineffective solution.

### Best Practice
Proven effective approach.

---

## Acronym Decoder

| Acronym | Full Term |
|---------|-----------|
| API | Application Programming Interface |
| BDD | Behavior Driven Development |
| CI/CD | Continuous Integration/Deployment |
| CSS | Cascading Style Sheets |
| DOM | Document Object Model |
| E2E | End to End |
| FAQ | Frequently Asked Questions |
| HTML | HyperText Markup Language |
| HTTP | HyperText Transfer Protocol |
| JSON | JavaScript Object Notation |
| POM | Page Object Model |
| REST | REpresentational State Transfer |
| RF | Robot Framework |
| SDK | Software Development Kit |
| SQL | Structured Query Language |
| UI | User Interface |
| URL | Uniform Resource Locator |
| XML | Extensible Markup Language |
| XSS | Cross-Site Scripting |
| YAML | YAML Ain't Markup Language |
