*** Settings ***
Documentation    Promenne pro sesuon auth testy

*** Variables ***
#    Base url
${AUTH_BASE_URL}    http://localhost:5101

#    Endpoints
${REGISTER_ENDPOINT}        ${AUTH_BASE_URL}/register
${SESSION_LOGIN_URL}        ${AUTH_BASE_URL}/session/login
${SESSION_ME_URL}           ${AUTH_BASE_URL}/session/me

#    Default credentials
${DEFAULT_USERNAME}        admin
${DEFAULT_PASSWORD}        admin123

#    Session settings
${SESSION_ALIAS}           authsession