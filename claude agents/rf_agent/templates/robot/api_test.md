# API Test Template

Template specifically for API tests.

```robot
*** Settings ***
Documentation     API tests for <endpoint> endpoint.
Resource          ../../common/common_api.resource
Resource          ../../common/common_db.resource
Resource          ../<feature>_api.resource
Suite Setup       Create API Session    api    ${BASE_URL}
Suite Teardown    Disconnect From Test Database

*** Variables ***
${api_<feature>_base_path}         /api/v1/<feature>
${api_<feature>_timeout}           30s

*** Test Cases ***
<Feature> - Create - Success 201
    [Documentation]    Verify that creating a new <entity> returns 201 with valid response body.
    [Tags]             api    <feature>    create    positive
    # Given
    ${api_create_<entity>_request_payload}=    Create Valid <Entity> Payload
    # When
    ${api_create_<entity>_response}=    API request
    ...    method=POST
    ...    url=${api_<feature>_base_path}
    ...    body=${api_create_<entity>_request_payload}
    ...    expected_status=anything
    ...    context_name=Create <entity> via API
    # Then
    ${api_create_<entity>_response_status}=    Set Variable    ${api_create_<entity>_response.status_code}
    Should Be Equal As Integers    ${api_create_<entity>_response_status}    201
    Dictionary Should Contain Key    ${api_create_<entity>_response.json()}    id

<Feature> - Create - Validation Error 400
    [Documentation]    Verify that creating <entity> with invalid payload returns 400.
    [Tags]             api    <feature>    create    negative
    # Given
    ${api_create_<entity>_invalid_payload}=    Create Dictionary    email=invalid-email
    # When
    ${api_create_<entity>_response}=    API request
    ...    method=POST
    ...    url=${api_<feature>_base_path}
    ...    body=${api_create_<entity>_invalid_payload}
    ...    expected_status=anything
    ...    context_name=Create <entity> with invalid payload
    # Then
    ${api_create_<entity>_response_status}=    Set Variable    ${api_create_<entity>_response.status_code}
    Should Be Equal As Integers    ${api_create_<entity>_response_status}    400

<Feature> - Get By ID - Success 200
    [Documentation]    Verify that fetching <entity> by ID returns 200 with correct data.
    [Tags]             api    <feature>    read    positive
    # Given
    ${api_create_<entity>_response_body}=    Create <Entity> Via API
    ${test_<entity>_id}=    Set Variable    ${api_create_<entity>_response_body}[id]
    # When
    ${api_get_<entity>_response}=    API request
    ...    method=GET
    ...    url=${api_<feature>_base_path}/${test_<entity>_id}
    ...    expected_status=anything
    ...    context_name=Get <entity> by ID
    # Then
    ${api_get_<entity>_response_status}=    Set Variable    ${api_get_<entity>_response.status_code}
    Should Be Equal As Integers    ${api_get_<entity>_response_status}    200

<Feature> - Delete - Success 204
    [Documentation]    Verify that deleting <entity> returns 204 and removes from database.
    [Tags]             api    <feature>    delete    positive
    # Given
    ${api_create_<entity>_response_body}=    Create <Entity> Via API
    ${test_<entity>_id}=    Set Variable    ${api_create_<entity>_response_body}[id]
    # When
    ${api_delete_<entity>_response}=    API request
    ...    method=DELETE
    ...    url=${api_<feature>_base_path}/${test_<entity>_id}
    ...    expected_status=anything
    ...    context_name=Delete <entity> by ID
    # Then
    ${api_delete_<entity>_response_status}=    Set Variable    ${api_delete_<entity>_response.status_code}
    Should Be Equal As Integers    ${api_delete_<entity>_response_status}    204
    # And verify deleted from DB
    Verify Row Count In Database
    ...    query=SELECT * FROM <table> WHERE id='${test_<entity>_id}'
    ...    expected_count=0
    ...    operator===
    ...    context_name=Verify <entity> deleted from database
```

## Notes

- Always use `expected_status=anything` and validate status manually
- For creation tests always verify response contains ID
- For delete tests always verify record was removed from DB
