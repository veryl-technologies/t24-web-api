*** Settings ***
Documentation     Test suite that demonstrates the main functionalities of I,A,S,ENQ commands
Test Teardown     Close Browsers
Library           T24WebDriver.py
Library           Selenium2Library    run_on_failure=Nothing

*** Test Cases ***
Scenario: Create and verify a coprorate customer
    [Documentation]    A sample customer test with I,A,S
    [Tags]    tag1    tag2
    T24 Login    INPUTTER
    @{testDataFields}=    Create List    NAME.1:1=JOHN    SHORT.NAME=OLIVER    MNEMONIC=JOL75891    SECTOR=2001    STREET=LAKESHORE STREET
    Create Or Amend T24 Record    CUSTOMER,CORP    \    ${testDataFields}    \    ${EMPTY}
    Authorize T24 Record    CUSTOMER    ${TX_ID}    0
    @{validationRules}=    Create List    CATEGORY :EQ:= 1-002    CURRENCY :EQ:= EUR    ACCOUNT.OFFICER :EQ:= 1
    Check T24 Record    CUSTOMER    ${TX_ID}    ${validationRules}

Scenario: Create and verify an account
    [Documentation]    A sample account test with I,A,S
    [Tags]    tag1    tag2
    T24 Login    INPUTTER
    @{testDataFields}=    Create List    CUSTOMER=ABCL    CATEGORY=1002    CURRENCY=EUR
    Create Or Amend T24 Record    ACCOUNT    \    ${testDataFields}    \    ${EMPTY}
    Authorize T24 Record    ACCOUNT    ${TX_ID}    0
    @{validationRules}=    Create List    ${TX_ID} >> MY_VAR    CATEGORY :EQ:= 1-002    CURRENCY :EQ:= EUR    ACCOUNT.OFFICER :EQ:= 1
    Check T24 Record    ACCOUNT    ${TX_ID}    ${validationRules}

Scenario: Verify %CUSTOMER enquiry
    [Documentation]    A sample test case with enquiry
    [Tags]    tag1    tag3
    @{enquiryConstraints}=    Create List    SECTOR :EQ:= 1000
    @{validationRules}=    Create List    1 :EQ:= 129179    1 >> CUST_ID    2 >> CUST_MNEMONIC
    Execute T24 Enquiry    %CUSTOMER    ${enquiryConstraints}    Check Result    ${validationRules}
    @{validationRules}=    Create List    MNEMONIC :EQ:= ${CUST_MNEMONIC}
    Check T24 Record    CUSTOMER    ${CUST_ID}    ${validationRules}
