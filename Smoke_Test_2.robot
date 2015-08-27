*** Settings ***
Documentation     Basic test case for creating and validating an ACCOUNT
Suite Setup       Register Keyword To Run On Failure    Nothing
Test Teardown     Close Browsers
Library           T24WebDriver.py
Library           Selenium2Library    run_on_failure=Nothing
Library           Dialogs

*** Test Cases ***
Scenario: Run AGENT.STATUS
    @{enquiryConstraints}=    Create List
    @{validationRules}=    Create List    1    2    3    4    5
    ...    6
    Execute T24 Enquiry    AGENT.STATUS    ${enquiryConstraints}    Read Data    ${validationRules}
    Dialogs.Pause Execution    Let' test pausing
    @{enquiryConstraints}=    Create List    df
    @{validationRules}=    Create List    fdgdf
    Execute T24 Enquiry    \    ${enquiryConstraints}    \    ${validationRules}

Manual COB
    [Tags]    manual
    Dialogs.Execute Manual Step    Please Run COB
    Dialogs.Get Selection From User    For which T24 company    AAA    BB    CC    DD
    Dialogs.Pause Execution    Let' test pausing
    Dialogs.Get Value From User    Any problems during COB?
