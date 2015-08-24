*** Settings ***
Documentation     Basic test case for creating and validating an ACCOUNT
Suite Setup       Register Keyword To Run On Failure    Nothing
Test Teardown     Close Browsers
Library           T24WebDriver.py
Library           Selenium2Library    run_on_failure=Nothing

*** Test Cases ***
Scenario: Create and verify an account
    [Documentation]    A sample test with I,A,S
    [Tags]    tag1    tag2
    T24 Login    INPUTTER
    @{testDataFields}=    Create List    CUSTOMER=ABCL    CATEGORY=1002    CURRENCY=EUR
    Create Or Amend T24 Record    ACCOUNT    \    ${testDataFields}    \    ${EMPTY}
    Authorize T24 Record    ACCOUNT    ${TX_ID}    0
    @{validationRules}=    Create List    CATEGORY :EQ:= 1-002    CURRENCY :EQ:= EUR    ACCOUNT.OFFICER :EQ:= 1
    Check T24 Record Exists    ACCOUNT    ${TX_ID}    ${validationRules}

Scenario: Verify %CUSTOMER enquiry
    [Documentation]    A sample test with enquiry
    [Tags]    tag1    tag3
    @{enquiryConstraints}=    Create List    SECTOR :EQ:= 1000
    @{validationRules}=    Create List    1 :EQ:= 129179    2 :EQ:= ABC000604
    Execute T24 Enquiry    %CUSTOMER    ${enquiryConstraints}    Check Result    ${validationRules}
    @{validationRules}=    Create List    MNEMONIC :EQ:= ABC000604
    Check T24 Record Exists    CUSTOMER    ${ENQ_RES_1}    ${validationRules}
