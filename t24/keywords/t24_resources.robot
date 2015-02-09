*** Settings ***
Library           Selenium2Library    timeout=15 s
Library           String
Library           lib/utils.py
Resource          common_resources.robot

*** Variables ***
${BANNER_FRAME_LOCATOR}    xpath=//frame[contains(@id,'banner')]
${COMMAND_LINE_LOCATOR}    css=input[name='commandValue']
${ACCEPT_OVERRIDES_LOCATOR}    xpath=//a[contains(@onclick, 'javascript:commitOverrides')]
${TXN_COMPLETED_LOCATOR}    xpath=//tr[contains(td, 'Txn Complete')]

*** Keywords ***
I sign off
    Select Frame    ${BANNER_FRAME_LOCATOR}
    Click Link    Sign Off

Enter T24 Command
    [Arguments]    ${command}
    [Documentation]    Inputting a T24 command in the main T24 page
    Select Frame    ${BANNER_FRAME_LOCATOR}
    Wait Until Page Contains Element    ${COMMAND_LINE_LOCATOR}
    Input Text    ${COMMAND_LINE_LOCATOR}    ${command}\n

Input Text Value For T24 Field
    [Arguments]    ${fieldName}    ${fieldText}
    [Documentation]    Set a value in a text field, by specifying the underlying T24 field name
    Input Text    css=input[name='fieldName:${fieldName}']    ${fieldText}

Click Commit Button
    [Documentation]    Clicks the Commit Button When Dealing with T24 Transactions
    Click Element    css=img[alt="Commit the deal"]

Click Authorize Deal Button
    [Documentation]    Clicks the Commit Button When Dealing with T24 Transactions
    Click Element    css=img[alt="Authorises a deal"]

Accept Overrides
    [Documentation]    Clicks the Accept Overrides Links (When Dealing with T24 Transactions)
    Wait Until Page Contains Element    ${ACCEPT_OVERRIDES_LOCATOR}
    Click Element    ${ACCEPT_OVERRIDES_LOCATOR}

Get Id From Completed Transaction
    [Documentation]    Checks whether the transaction is completed and if yes, extracts the referenced ID
    Wait Until Page Contains    Txn Complete
    ${confirmationMsg}=    Get Text    ${TXN_COMPLETED_LOCATOR}
    ${transactionId}=    Get Id From Transaction Confirmation Text    ${confirmationMsg}
    [Return]    ${transactionId}

Expand T24 Menu
    [Arguments]    ${menuText}
    [Documentation]    Expands a T24 menu (NOT READY)
    Click Element    css=img[alt="${menuText}")]

Open a T24 Record For Viewing
    [Arguments]    ${application}    ${recordId}
    Enter T24 Command    ${application} S ${recordId}

Open a T24 Record For Authorization
    [Arguments]    ${application}    ${recordId}
    Enter T24 Command    ${application} A ${recordId}

Authorize a T24 Record
    [Arguments]    ${application}    ${recordId}
    Open a T24 Record For Authorization    ${application}    ${recordId}
    Select Window    ${application}
    Click Authorize Deal Button
    ${transactionId}=    Get Id From Completed Transaction
    Should Be Equal    ${transactionId}    ${recordId}
    Close Window
