*** Settings ***
Documentation     Just a test
Library           t24pageobjects.T24LoginPage
Library           t24pageobjects.T24HomePage
Library           t24pageobjects.T24EnquiryStartPage
Library           t24pageobjects.T24EnquiryResultPage
Library           t24pageobjects.T24RecordSeePage
Library           t24pageobjects.T24RecordInputPage

*** Test Cases ***
Scenario: Create a customer
    Open T24Login
    Enter T24 Credentials    INPUTT    123456
    Open See Page    CUSTOMER    ABCL
    Close
