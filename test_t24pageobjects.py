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
        homePage.enter_t24_command("ENQ %CUSTOMER")
        time.sleep(3)

    def tearDown(self):
        self.loginpage.close()

if __name__ == "__main__":
    unittest.main()
