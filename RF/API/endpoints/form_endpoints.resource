*** Comments ***
# LAYER 1: API Endpoints
# Tento soubor obsahuje POUZE API endpoint URLs a query parameters.
# Žádná logika, žádné API calls - pouze konstanty.


*** Variables ***
# Base URLs
${BASE_API_URL}             http://localhost:8000/api/v1
${FORM_BASE_ENDPOINT}       ${BASE_API_URL}/form

# Form CRUD endpoints
${FORM_LIST_ENDPOINT}                   ${FORM_BASE_ENDPOINT}/
${FORM_CREATE_ENDPOINT}                 ${FORM_BASE_ENDPOINT}/
${FORM_GET_BY_ID_ENDPOINT}              ${FORM_BASE_ENDPOINT}/{id}
${FORM_DELETE_ENDPOINT}                 ${FORM_BASE_ENDPOINT}/{id}

# Game/Easter egg endpoints
${FORM_EVALUATE_NAME_ENDPOINT}          ${FORM_BASE_ENDPOINT}/evaluate-name

# Attachment endpoints
${FORM_ATTACHMENT_CREATE_ENDPOINT}      ${FORM_BASE_ENDPOINT}/{id}/attachment
${FORM_ATTACHMENT_LIST_ENDPOINT}        ${FORM_BASE_ENDPOINT}/{id}/attachments

# Instruction endpoints
${FORM_INSTRUCTION_CREATE_ENDPOINT}     ${FORM_BASE_ENDPOINT}/{id}/instructions
${FORM_INSTRUCTION_GET_ENDPOINT}        ${FORM_BASE_ENDPOINT}/{id}/instructions

# Query parameters (pokud by byly potřeba)
# ${QUERY_SKIP}    skip
# ${QUERY_LIMIT}   limit
