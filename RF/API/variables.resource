*** Comments ***
# API Test Variables
#
# Globální proměnné pro API testing


*** Variables ***
# API Configuration
${API_BASE_URL}         http://localhost:20300
${API_TIMEOUT}          30s
${API_VERIFY_SSL}       ${False}

# Default Session
${DEFAULT_SESSION}      mysession

${LOG_TO_CONSOLE}    ${False}