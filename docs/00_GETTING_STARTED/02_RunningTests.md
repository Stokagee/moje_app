# Running and Organizing Tests

## Learning Objectives
- [ ] Run tests with different options
- [ ] Organize tests into suites
- [ ] Use tags for selective execution
- [ ] Interpret test reports

## Prerequisites
- Completed first test
- Have at least 2 test files

---

## Running Single Test Files

### Basic Command

```bash
robot my_test.robot
```

### With Options

```bash
# Specify output directory
robot --outputdir results my_test.robot

# Change log level (TRACE, DEBUG, INFO, WARN, ERROR)
robot --loglevel DEBUG my_test.robot

# Don't create log/report files
robot --log NONE --report NONE my_test.robot

# Run with variables
robot --variable URL:http://localhost:3000 my_test.robot
```

---

## Running Test Suites

### Directory Structure

```
tests/
├── ui/
│   ├── form_tests.robot
│   └── list_tests.robot
└── api/
    ├── form_api_tests.robot
    └── order_api_tests.robot
```

### Run All Tests in Directory

```bash
robot tests/
```

This runs all `.robot` files recursively.

### Run Specific Subdirectory

```bash
robot tests/ui/
robot tests/api/
```

### Run Specific Files

```bash
robot tests/ui/form_tests.robot
robot tests/api/form_api_tests.robot
```

---

## Using Tags for Selective Execution

### Defining Tags

```robotframework
*** Test Cases ***
Create Form Successfully
    [Documentation]    Test happy path form creation
    [Tags]    smoke    happy-path    form    critical

    # ... test steps ...

Delete Form
    [Documentation]    Test form deletion
    [Tags]    regression    form    delete

    # ... test steps ...

Invalid Email Should Fail
    [Documentation]    Test email validation
    [Tags]    regression    form    validation    negative

    # ... test steps ...
```

### Running by Tags

```bash
# Run only smoke tests
robot --include smoke tests/

# Run only form tests
robot --include form tests/

# Run only critical tests
robot --include critical tests/

# Exclude negative tests
robot --exclude negative tests/

# Combine: smoke but not slow
robot --include smoke --exclude slow tests/

# Multiple includes
robot --include smoke --include critical tests/
```

### Suite Tags

Set default tags for all tests in suite:

```robotframework
*** Settings ***
Force Tags      regression    api
Default Tags    sanity
```

| Tag Type | Purpose |
|----------|---------|
| `Force Tags` | Applied to ALL tests, cannot be excluded |
| `Default Tags` | Applied if test has no tags, can be excluded |

---

## Test Suites and Setup/Teardown

### Suite Setup/Teardown

Runs once before/after ALL tests in suite:

```robotframework
*** Settings ***
Suite Setup     Log    Starting test suite
Suite Teardown  Log    Cleaning up after suite

*** Test Cases ***
Test One
    Log    Running test one

Test Two
    Log    Running test two
```

### Test Setup/Teardown

Runs before/after EACH test:

```robotframework
*** Settings ***
Test Setup      Log    Before each test
Test Teardown   Log    After each test

*** Test Cases ***
Test One
    Log    Running test one
```

### Combined Example

```robotframework
*** Settings ***
Suite Setup     Connect To Database
Suite Teardown  Disconnect From Database
Test Setup      Create API Session
Test Teardown   Delete All Sessions

*** Test Cases ***
Create And Verify Form
    # Uses DB connection + API session
    # ...
```

---

## Parallel Execution with Pabot

For faster test execution, run tests in parallel:

```bash
# Install pabot
pip install robotframework-pabot

# Run with 4 parallel processes
pabot --processes 4 tests/

# Run with test-level parallelization (splits suites)
pabot --testlevelsplit tests/
```

---

## Interpreting Results

### Report.html

**Summary view showing:**
- Overall pass/fail statistics
- Execution time
- Test sorted by status (failed first)
- Tags summary

### Log.html

**Detailed view showing:**
- Each test step with timing
- Keyword expansions
- Screenshot links
- Error messages and stack traces
- Log messages

### Status Indicators

| Symbol | Meaning |
|--------|---------|
| 🟢 PASS | Test passed successfully |
| 🔴 FAIL | Test failed - assertion or error |
| ⚠️ SKIP | Test was skipped (e.g., wrong tags) |

---

## Variable Files and Configurations

### Variable File

Create `variables.py`:

```python
# variables.py
URL = "http://localhost:8081"
API_BASE = "http://localhost:8000/api/v1"
BROWSER = "chromium"
HEADLESS = True
```

Use in test:

```robotframework
*** Settings ***
Variables    variables.py

*** Test Cases ***
Use Variables From File
    New Page    ${URL}
    Log    Using browser: ${BROWSER}
```

### Command Line Variables

```bash
# Override single variable
robot --variable URL:http://staging.example.com tests/

# Override multiple variables
robot --variable URL:http://staging.example.com --variable HEADLESS:True tests/

# Variable file
robot --variablefile prod_variables.py tests/
```

---

## Output Formats

### Default Outputs

```
my_test.robot
├── output.xml       # Machine-readable XML
├── log.html         # Detailed log
└── report.html      # Summary report
```

### Alternative Formats

```bash
# No HTML outputs
robot --log NONE --report NONE --outputdir results my_test.robot

# Custom output names
robot --output my_output.xml --log my_log.html --report my_report.html my_test.robot

# Output directory
robot --outputdir test_results/ tests/
```

---

## Common Command Patterns

### Development Phase
```bash
# Fast feedback - single test, detailed output
robot --test "Specific Test" --loglevel DEBUG my_test.robot
```

### Regression Testing
```bash
# All tests, organized output
robot --outputdir regression_results/ tests/
```

### Quick Smoke Test
```bash
# Only smoke tests, minimal output
robot --include smoke --log NONE --report NONE tests/
```

### Debugging
```bash
# Single test, full tracing
robot --test "Failing Test" --loglevel TRACE --dryrun my_test.robot
```

### CI/CD Pipeline
```bash
# Parallel execution, xUnit output for CI
pabot --processes 4 --outputdir ci_results/ --xunit ci_results.xml tests/
```

---

## Self-Check Questions

1. What command runs only tests tagged "smoke"?
2. How do you run tests in parallel?
3. What's the difference between Suite Setup and Test Setup?
4. What files are created by default when running tests?

---

## Best Practices

1. **Organize tests by feature:**
   ```
   tests/
   ├── form/
   ├── orders/
   └── dispatch/
   ```

2. **Use meaningful tags:**
   - `smoke` - Quick sanity checks
   - `regression` - Full test coverage
   - `critical` - Core functionality
   - `api` / `ui` / `db` - Layer designation

3. **Use setup/teardown for cleanup:**
   ```robotframework
   [Teardown]    Delete Test Data    ${created_id}
   ```

4. **Configure output directory per environment:**
   ```bash
   robot --outputdir results/prod/ tests/
   ```

---

## References

- [Robot Framework Command Line Options](https://robotframework.org/robotframework/latest/RobotFrameworkUserGuide.html#running-tests)
- [Pabot Documentation](https://github.com/mkorpela/pabot)
- Project structure: `/RF/` directory
