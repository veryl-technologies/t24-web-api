*** Settings ***
Documentation     Basic test case for creating and validating an ACCOUNT
Suite Setup       Register Keyword To Run On Failure    Nothing
Test Teardown     Close Browsers
Library           T24WebDriver.py
Library           Selenium2Library    run_on_failure=Nothing
Library           Dialogs

*** Test Cases ***
Scenario: Run AGENT.STATUS
    [Documentation]    Run one enquiry twice with a manual pause between
    @{enquiryConstraints}=    Create List
    @{validationRules}=    Create List    1 >> AGENT.ID    2 >> T24.SESSION.NO    3 >> SERVER.NAME    4 >> AGENT.STATUS    5 >> PROCESS.ID
    Execute T24 Enquiry    AGENT.STATUS    ${enquiryConstraints}    Check Result    ${validationRules}
    Dialogs.Pause Execution    Let' test pausing
    @{enquiryConstraints}=    Create List
    @{validationRules}=    Create List    1 >> AGENT.ID    2 >> T24.SESSION.NO
    Execute T24 Enquiry    AGENT.STATUS    ${enquiryConstraints}    \    ${validationRules}

Manual COB
    [Documentation]    Showcase all options for manual actions
    [Tags]    manual
    Dialogs.Execute Manual Step    Please Run COB
    Dialogs.Get Selection From User    For which T24 company    AAA    BB    CC    DD
    Dialogs.Pause Execution    Let' test pausing
    Dialogs.Get Value From User    Any problems during COB?
