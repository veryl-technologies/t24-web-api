*** Settings ***
Documentation     Tests the Login to T24 web application
Resource          ../keywords/common_resources.robot

*** Test Cases ***
Scenario: Login as a valid user to T24 web
    Given I log in to T24 as Inputter
    Then I can see T24 startup page for logged-in users
