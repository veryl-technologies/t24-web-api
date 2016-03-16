from t24pageobjects import T24LoginPage
import os
import unittest
import time


class T24WebDriverTestCase(unittest.TestCase):

    def setUp(self):
        os.environ["PO_BASEURL"] = "http://192.168.1.120:9095" # "http://7.117.75.57:9095/"   # 192.168.1.120
        os.environ["PO_BROWSER"] = "firefox"   # phantomjs
        
        self.loginpage = T24LoginPage()
        self.loginpage.open()
        self.homePage = self.loginpage.enter_T24_credentials("INPUTT", "123456")

    def test_input_customer_complex(self):
        inputPage = self.homePage.open_input_page_new_record("CUSTOMER,CORP")
        inputPage.set_T24_field_value("MNEMONIC", "#AUTO-MNEMONIC")
        inputPage.set_T24_field_value("NAME.1:1", "DUP")
        inputPage.set_T24_field_value("SHORT.NAME:1", "OLIVER")
        inputPage.set_T24_field_value("SECTOR", "2001")  # TODO hot fields currently need to be at the end of the test
        inputPage.set_T24_field_value("NATIONALITY", "GR")
        inputPage.set_T24_field_value("RESIDENCE", "GR")
        inputPage.set_T24_field_value("LANGUAGE", "1")
        inputPage.set_T24_field_value("STREET:1", "SESAME STR")

        inputPage.click_commit_button()
        inputPage.click_accept_overrides()
        inputPage.receive_documents()
        inputPage.click_commit_button()
        new_id = inputPage.get_id_from_completed_transaction()
        print "ID of created CUSTOMER record is " + new_id
        inputPage.close_window()
        self.homePage.sign_off()   # sometimes this blows up

    def test_input_customer(self):
        inputPage = self.homePage.open_input_page_new_record("CUSTOMER")
        inputPage.set_T24_field_value("MNEMONIC", "#AUTO")
        inputPage.set_T24_field_value("NAME.1:1", "ALABALA")
        inputPage.set_T24_field_value("SHORT.NAME:1", "SOMETHING")
        inputPage.set_T24_field_value("STREET:1", "SESAME STR")
        inputPage.set_T24_field_value("NATIONALITY", "GR")
        inputPage.set_T24_field_value("RESIDENCE", "GR")
        inputPage.set_T24_field_value("LANGUAGE", "1")
        inputPage.set_T24_field_value("SECTOR", "2001")
        inputPage.click_commit_button()
        inputPage.click_accept_overrides()
        inputPage.click_commit_button()
        # id = inputPage.get_id_from_completed_transaction()
        # print "ID of created CUSTOMER record is " + id
        inputPage.close_window()
        self.homePage.sign_off()

    def test_enquiry(self):
        enqResultPage = self.homePage.open_t24_enquiry("AGENT.STATUS")
        id = enqResultPage.get_first_id_of_enquiry_result()
        print "ID of first found record is " + id
        self.homePage.sign_off()

    def test_see(self):
        seePage = self.homePage.open_see_page("CUSTOMER", "ABCL")
        print seePage.get_T24_field_value("MNEMONIC")
        print seePage.get_T24_field_value("SECTOR")
        self.homePage.sign_off()

    def test_enq_ia(self):
        # get an existing customer ID
        enqResultPage = self.homePage.open_t24_enquiry("%CUSTOMER", ["SECTOR NE 1000", "INDUSTRY GT 500"])
        customer_id = enqResultPage.get_first_id_of_enquiry_result()
        print "ID of first found customer is " + customer_id

        # create an account
        inputPage = self.homePage.open_input_page_new_record("ACCOUNT")
        inputPage.set_T24_field_value("CUSTOMER", customer_id)
        inputPage.set_T24_field_value("CATEGORY", "1002")
        inputPage.set_T24_field_value("CURRENCY", "EUR")
        inputPage.click_commit_button()
        accountId = inputPage.get_id_from_completed_transaction()

        # authorize the account
        self.homePage.sign_off()
        self.loginpage.enter_T24_credentials("AUTHOR", "123456")
        authorPage = self.homePage.open_authorize_page("ACCOUNT", accountId)
        authorPage.click_authorize_button()
        authorizedAccountId = inputPage.get_id_from_completed_transaction()
        assert(accountId == authorizedAccountId)
        self.homePage.sign_off()

        # homePage._enter_t24_command("CUSTOMER S " + accountId)
        time.sleep(1)
    
#    def tearDown(self):
#        self.loginpage.close()

if __name__ == "__main__":
    unittest.main()
