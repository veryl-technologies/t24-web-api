*** Settings ***
Documentation     Basic test case for creating and validating an ACCOUNT
Suite Setup       Register Keyword To Run On Failure    Nothing
Test Teardown     Close Browsers
Library           T24WebDriver.py
Library           Selenium2Library    run_on_failure=Nothing

*** Test Cases ***
Scenario: Run AGENT.STATUS
    @{enquiryConstraints}=    Create List
    @{validationRules}=    Create List    1    2    3    4    5
    ...    6    7
    Execute T24 Enquiry    AGENT.STATUS    ${enquiryConstraints}    Read Data    ${validationRules}
