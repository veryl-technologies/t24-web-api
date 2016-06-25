*** Settings ***
Documentation     Show casing manual keywords
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
    Dialogs.Pause Execution    Take a pause
    @{enquiryConstraints}=    Create List
    @{validationRules}=    Create List    1 >> AGENT.ID    2 >> T24.SESSION.NO
    Execute T24 Enquiry    AGENT.STATUS    ${enquiryConstraints}    \    ${validationRules}

Scenario: Manual COB
    [Documentation]    Showcase all built-in options for manual actions
    [Tags]    manual
    Dialogs.Get Selection From User    For which T24 company    GB00001    US00002
    Pause Step    Please start the COB process manually and wait for it to complete.
    Dialogs.Get Value From User    How many minutes did the operation take?.
    Manual Step    Did the COB test case pass successfully?
