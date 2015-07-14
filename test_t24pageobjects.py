from t24pageobjects import T24LoginPage
import os
import unittest
import time


class T24LoginPageTestCase(unittest.TestCase):

    def setUp(self):
        os.environ["PO_BASEURL"] = "http://7.117.75.57:9095"
        os.environ["PO_BROWSER"] = "firefox"
        
        self.loginpage = T24LoginPage()
        self.loginpage.open()
        self.homePage = self.loginpage.enter_T24_credentials("INPUTT", "123456")

    def test_see(self):
        seePage = self.homePage.open_see_page("CUSTOMER", "ABCL")
        print seePage.get_value_of_T24_field("MNEMONIC")
        print seePage.get_value_of_T24_field("SECTOR")
        self.homePage.sign_off()

    def test_full_scenario(self):
        # get an existing customer ID
        enqResultPage = self.homePage.open_t24_enquiry("%CUSTOMER", ["SECTOR NE 1000", "INDUSTRY GT 500"])
        customer_id = enqResultPage.get_first_id_of_enquiry_result()
        print "ID of first found customer is " + customer_id
        enqResultPage.close_window()

        # create an account
        inputPage = self.homePage.open_input_page_new_record("ACCOUNT")
        inputPage.input_text_to_T24_field("CUSTOMER", customer_id)
        inputPage.input_text_to_T24_field("CATEGORY", "1002")
        inputPage.input_text_to_T24_field("CURRENCY", "EUR")
        inputPage.click_commit_button()
        accountId = inputPage.get_id_from_completed_transaction()
        inputPage.close_window()

        # authorize the account
        self.homePage.sign_off()
        self.loginpage.enter_T24_credentials("AUTHOR", "123456")
        authorPage = self.homePage.open_authorize_page("ACCOUNT", accountId)
        authorPage.click_authorize_button()
        authorizedAccountId = inputPage.get_id_from_completed_transaction()
        assert(accountId == authorizedAccountId)
        authorPage.close_window()
        self.homePage.sign_off()

        # homePage._enter_t24_command("CUSTOMER S " + accountId)
        time.sleep(1)

    def tearDown(self):
        self.loginpage.close()

if __name__ == "__main__":
    unittest.main()
