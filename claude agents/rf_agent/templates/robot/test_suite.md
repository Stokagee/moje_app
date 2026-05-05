# Test Suite Template

Basic template for new Robot Framework test suite.

```robot
*** Settings ***
Documentation     <BRIEF_DESCRIPTION> - Test suite for <feature>
Resource          ../../common/common_api.resource
Resource          ../../common/common_db.resource
Resource          ../<feature>.resource
Suite Setup       Prepare <Feature> Test Environment
Suite Teardown    Cleanup <Feature> Test Data
Test Setup        <Optional: Per-test setup>
Test Teardown     <Optional: Per-test teardown>

*** Variables ***
# Endpoint configuration
${api_<feature>_endpoint}          /api/v1/<endpoint>
${api_<feature>_timeout}           30s

# Test data defaults
${test_<entity>_default_name}      Test User
${test_<entity>_default_email}     test@example.com

*** Test Cases ***
<Feature> - <Scenario> - <Expected Outcome>
    [Documentation]    <What this test verifies in detail>
    [Tags]             <tag1>    <tag2>
    # Given
    ${api_<action>_<entity>_request_payload}=    Create <Entity> Request Payload
    # When
    ${api_<action>_<entity>_response}=    API request
    ...    method=POST
    ...    url=${api_<feature>_endpoint}
    ...    body=${api_<action>_<entity>_request_payload}
    ...    expected_status=anything
    ...    context_name=<Action> <entity>
    # Then
    ${api_<action>_<entity>_response_status_code}=    Set Variable    ${api_<action>_<entity>_response.status_code}
    Should Be Equal As Integers    ${api_<action>_<entity>_response_status_code}    201
    # And DB verification
    ${db_<entity>_expected_row_count}=    Set Variable    ${1}
    Verify Row Count In Database
    ...    query=SELECT * FROM <table> WHERE <column>='${api_<action>_<entity>_request_payload}[<field>]'
    ...    expected_count=${db_<entity>_expected_row_count}
    ...    operator===
    ...    context_name=Verify <entity> exists in database

<Feature> - <Another Scenario> - <Expected Outcome>
    [Documentation]    <What this test verifies>
    [Tags]             <tag1>    <tag2>
    # Test steps...

*** Keywords ***
Prepare <Feature> Test Environment
    [Documentation]    Sets up test environment and creates necessary test data.
    ${context_name}=    Set Variable    Prepare <feature> test environment
    TRY
        Connect To Test Database
        # Create any necessary prerequisites
    EXCEPT    AS    ${error_message}
        Fail    ${context_name}: Failed to prepare environment. Error: ${error_message}
    END

Cleanup <Feature> Test Data
    [Documentation]    Removes all test data created during test execution.
    ${context_name}=    Set Variable    Cleanup <feature> test data
    TRY
        Delete All Test Data    <table_name>
        Disconnect From Test Database
    EXCEPT    AS    ${error_message}
        Log    ${context_name}: Warning - Cleanup failed: ${error_message}    level=WARN
    END

Create <Entity> Request Payload
    [Documentation]    Creates a valid request payload for <entity> creation.
    ...                Uses FakerLibrary for dynamic data generation.
    ${test_<entity>_name}=    FakerLibrary.Name
    ${test_<entity>_email}=    FakerLibrary.Email
    ${api_create_<entity>_request_payload}=    Create Dictionary
    ...    name=${test_<entity>_name}
    ...    email=${test_<entity>_email}
    RETURN    ${api_create_<entity>_request_payload}
```

## Rules

1. **Test name**: `<Feature> - <Scenario> - <Expected Outcome>`
2. **Variables**: Always `${api_<action>_<entity>_<type>}` or `${db_<entity>_<purpose>}`
3. **API calls**: Always via `API request` wrapper
4. **DB verification**: Always via DB wrappers
5. **Error handling**: TRY/EXCEPT with `${context_name}`
