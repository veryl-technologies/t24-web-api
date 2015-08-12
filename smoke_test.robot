*** Settings ***
Documentation     Just a test
Library           T24WebDriver.py

*** Test Cases ***
Scenario: Create and verify an account
    T24 Login    INPUTTER
    @{testDataFields1}=    Create List    CUSTOMER=ABCL    CATEGORY=1002    CURRENCY=EUR
    Create Or Amend T24 Record    ACCOUNT    \    ${testDataFields1}    \    ${EMPTY}
    Authorize T24 Record    ACCOUNT    ${TX_ID}    0
    @{validationRules1}=    Create List    CUSTOMER EQ ABCL    CATEGORY EQ 1002    CURRENCY EQ EUR
    Check T24 Record Exists    ACCOUNT    ${TX_ID}    ${validationRules1}
