*** Comments ***
# API Test Variables
#
# Globální proměnné pro API testing


*** Variables ***
# API Configuration
${API_BASE_URL}         http://localhost:8000/api/v1/form
${API_TIMEOUT}          30s
${API_VERIFY_SSL}       ${False}

# Default Session
${DEFAULT_SESSION}      mysession

# Test Data
${DEFAULT_GENDER}       male
${TEST_EMAIL_PREFIX}    test_rf

# Easter Egg Test Data
${POSITIVE_EGG_TEXT}    neo
${NEGATIVE_EGG_TEXT}    random_text_123

# Timeouts
${SHORT_TIMEOUT}        5s
${MEDIUM_TIMEOUT}       15s
${LONG_TIMEOUT}         30s

# Expected Messages
${DELETE_SUCCESS_MSG}   smazán
${EASTER_EGG_MSG}       Tajemství odhaleno
