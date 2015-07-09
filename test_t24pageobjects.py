from t24pageobjects import T24LoginPage,T24HomePage
import os
import unittest
import time


class T24LoginPageTestCase(unittest.TestCase):

    def setUp(self):
        os.environ["PO_BASEURL"] = "http://7.117.75.57:9095"
        os.environ["PO_BROWSER"] = "firefox"
        
        self.loginpage = T24LoginPage()
        self.loginpage.open()

    def test_enquiry(self):
        homePage = self.loginpage.enter_T24_credentials("INPUTT","123456")
        enqResultPage = homePage.open_t24_enquiry("%CUSTOMER", ["SECTOR NE 1000", "INDUSTRY GT 500"])
        customer_id = enqResultPage.get_first_id_of_enquiry_result()
        if not customer_id:
            print "No customer found"
            return

        print "ID of first found customer is " + customer_id
        enqResultPage.close_window()
        homePage._enter_t24_command("CUSTOMER S " + customer_id)
        time.sleep(5)

    def tearDown(self):
        self.loginpage.close()

if __name__ == "__main__":
    unittest.main()
