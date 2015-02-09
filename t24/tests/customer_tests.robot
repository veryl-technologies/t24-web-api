*** Settings ***
Documentation     Tests Customers creation
Resource          ../keywords/common_resources.robot
Resource          ../keywords/t24_customer_resources.robot

*** Test Cases ***
Scenario: Create a customer
    Given I log in to T24 as Inputter
    ${customer_id}=    I input a customer with mnemonic (using command line)    XYZ12348
    Then I can see the newly created customer    ${customer_id}
    And I sign off
    And I log in to T24 as Authorizer
    And Authorize a T24 Record    CUSTOMER    ${customer_id}
