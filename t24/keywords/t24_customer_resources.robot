*** Settings ***
Library           Selenium2Library    timeout=15 s
Library           Dialogs
Resource          t24_resources.robot

*** Variables ***
${CUSTOMER_GENDER_RADIOBUTTONS_LOCATOR}    radio:tab1:GENDER

*** Keywords ***
I input a customer with mnemonic (using command line)
    [Arguments]    ${mnemonic}
    Enter T24 Command    CUSTOMER I F3
    ${customer_id}=    Enter Field Values For New Customer And Commit    ${mnemonic}
    [Return]    ${customer_id}

I input a customer with mnemonic (using user menu)
    [Arguments]    ${mnemonic}
    Go To Individual Customer Creation Screen By Menu
    ${customer_id}=    Enter Field Values For New Customer And Commit    ${mnemonic}
    [Return]    ${customer_id}

Enter Field Values For New Customer And Commit
    [Arguments]    ${mnemonic}
    Select Window    CUSTOMER
    Wait Until Page Contains    Mnemonic
    Input Text Value For T24 Field    NAME.1:1    John Smith
    Input Text Value For T24 Field    SHORT.NAME:1    JOHN
    Input Text Value For T24 Field    MNEMONIC    ${mnemonic}
    Input Text Value For T24 Field    SECTOR    1001
    Input Text Value For T24 Field    LANGUAGE    2
    Select Radio Button    ${CUSTOMER_GENDER_RADIOBUTTONS_LOCATOR}    MALE
    Click Commit Button
    Accept Overrides
    ${customer_id}=    Get Id From Completed Transaction
    Log    Created customer with ID = ${customer_id}
    Close Window
    Select Window
    [Return]    ${customer_id}

I can see the newly created customer
    [Arguments]    ${customer_id}
    Open a T24 Record For Viewing    CUSTOMER    ${customer_id}
    Select Window    CUSTOMER
    Wait Until Page Contains    John Smith
    Close Window
    Select Window

Go To Individual Customer Creation Screen By Menu
    Expand T24 Menu    User Menu
    Expand T24 Menu    Customer
    Click Link    Individual Customer
