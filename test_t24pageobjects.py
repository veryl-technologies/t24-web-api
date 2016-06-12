from t24pageobjects import T24LoginPage
import os
import unittest
import time


class T24WebDriverTestCase(unittest.TestCase):

    def setUp(self):
        os.environ["PO_BASEURL"] = "http://192.168.1.120:9095/"   # "http://192.168.1.120:9095"
        os.environ["PO_BROWSER"] = "firefox"   # phantomjs

        self.loginpage = T24LoginPage()
        self.loginpage.open()
        self.homePage = self.loginpage.enter_T24_credentials("INPUTT", "123456")





    def test_input_customer_input(self):
        inputPage = self.homePage.open_input_page_new_record("CUSTOMER,INPUT")

        inputPage.set_T24_field_value("TITLE", "?SELECT-FIRST")
        inputPage.set_T24_field_value("ACCOUNT.OFFICER", "1")
        inputPage.set_T24_field_value("GENDER", "?SELECT-FIRST")

        inputPage.set_T24_field_value("CUSTOMER.STATUS", "2")
        inputPage.set_T24_field_value("FAMILY.NAME", "SMITH")
        inputPage.set_T24_field_value("GIVEN.NAMES", "JOHN")
        inputPage.set_T24_field_value("INDUSTRY", "1000")
        inputPage.set_T24_field_value("LANGUAGE", "2")
        inputPage.set_T24_field_value("NAME.1:1", "?AUTO-VALUE")
        inputPage.set_T24_field_value("SHORT.NAME:1", "?AUTO-VALUE")
        inputPage.set_T24_field_value("MNEMONIC", "?AUTO-VALUE")
        inputPage.set_T24_field_value("SECTOR", "1001")
        inputPage.set_T24_field_value("TARGET", "2")
        inputPage.set_T24_field_value("MARITAL.STATUS", "DIVORCED")

        inputPage.click_commit_button()
        inputPage.click_accept_overrides()
        inputPage.receive_documents()
        inputPage.click_commit_button()
        new_id = inputPage.get_id_from_completed_transaction()
        print "ID of created CUSTOMER record is " + new_id
        inputPage.close_window()
        self.homePage.sign_off()   # sometimes this blows up
"""

    def test_menu_command(self):
        inputPage = self.homePage.run_t24_menu_command("User Menu > Customer >Corporate Customer")

    def test_see(self):
        # seePage = self.homePage.open_see_page("CUSTOMER", "? 'AB' + 'CL'")
        seePage = self.homePage.open_see_page("FT", "? 'FT' + '141124JS4S'")
        print seePage.get_T24_field_value("@ID")
        print seePage.get_T24_field_value("MNEMONIC")
        print seePage.get_T24_field_value("SECTOR")
        self.homePage.sign_off()

    def test_input_customer_complex(self):
        inputPage = self.homePage.open_input_page_new_record("CUSTOMER,CORP")
        inputPage.set_T24_field_value("TITLE", "Dr")
        inputPage.set_T24_field_value("MNEMONIC", "?AUTO-MNEMONIC")
        inputPage.set_T24_field_value("NAME.1:1", "DUP")
        inputPage.set_T24_field_value("SHORT.NAME:1", "OLIVER")
        inputPage.set_T24_field_value("SECTOR", "2001")
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

    def test_teller(self):
        inputPage = self.homePage.open_input_page_new_record("FUNDS.TRANSFER,ACTR.FTHP")

        inputPage.set_T24_field_value("DEBIT.ACCT.NO", "51116")
        inputPage.set_T24_field_value("DEBIT.CURRENCY", "USD")
        inputPage.set_T24_field_value("DEBIT.AMOUNT", "1000")
        inputPage.set_T24_field_value("CREDIT.ACCT.NO", "51128")
        inputPage.set_T24_field_value("CREDIT.CURRENCY", "EUR")

        inputPage.click_commit_button()
        self.homePage.sign_off()
        self.homePage.close()  # TODO - Find out how to close the popup with print dialog


    def test_ft(self):
        inputPage = self.homePage.open_input_page_new_record("FUNDS.TRANSFER")
        inputPage.set_T24_field_value("TRANSACTION.TYPE", "AC")
        inputPage.set_T24_field_value("DEBIT.ACCT.NO", "50733")
        inputPage.set_T24_field_value("DEBIT.CURRENCY", "USD")
        inputPage.set_T24_field_value("CREDIT.ACCT.NO", "50741")
        inputPage.set_T24_field_value("DEBIT.AMOUNT", "10")

        inputPage.click_commit_button()
        inputPage.click_accept_overrides()
        inputPage.click_commit_button()
        new_id = inputPage.get_id_from_completed_transaction()
        print "ID of created FT record is " + new_id
        inputPage.close_window()
        self.homePage.sign_off()   # sometimes this blows up

    def test_input_customer(self):
        inputPage = self.homePage.open_input_page_new_record("CUSTOMER")
        inputPage.set_T24_field_value("MNEMONIC", "?AUTO")
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
"""

#    def tearDown(self):
#        self.loginpage.close()

if __name__ == "__main__":
    unittest.main()
