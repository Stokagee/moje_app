*** Variables ***
${BROWSER}    chromium
${HEADLESS}    ${False}
${TIMEOUT}    10s
${URL}    http://localhost:8081/
${BASE_URL}    http://localhost:8000/api/v1/form
${WIDTH}    900
${HEIGHT}    600
${JSON_PATH}    ${CURDIR}${/}instructions.json
${DOKUMENT_PATH}    ${CURDIR}${/}dokument.txt