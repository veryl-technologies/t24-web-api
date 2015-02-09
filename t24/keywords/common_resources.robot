*** Settings ***
Library           Selenium2Library    timeout=15 s
Library           lib/utils.py

*** Variables ***
${SERVER}         10.10.10.67:9095
${BROWSER}        firefox
${DELAY}          0
${LOGIN URL}      http://${SERVER}/BrowserWeb/
${input_user}     INPUTT
${input_userpass}    1234567
${auth_user}      AUTHOR
${auth_pass}      123456

*** Keywords ***
I go to T24 login page
    Open Browser    ${LOGIN URL}    ${BROWSER}
    Set Selenium Speed    ${DELAY}
    Page Should Contain    T24 Sign in

I log in to T24 as Inputter
    I log in to T24    ${input_user}    ${input_userpass}

I log in to T24 as Authorizer
    I log in to T24    ${auth_user}    ${auth_pass}

I log in to T24
    [Arguments]    ${user}    ${userpass}
    I Go To T24 Login Page
    Input Text    xpath=.//*[@id='signOnName']    ${user}
    Input Text    xpath=.//*[@id='password']    ${userpass}
    Click Element    css=#sign-in

I can see T24 startup page for logged-in users
    Page Should Contain    Sign Off
    Page Should Contain    User Menu
    Page Should Contain    Admin Menu

For future use
    Wait Until Page Contains    xpath=//frame[contains(@id,'menu')]
    Capture Page Screenshot
