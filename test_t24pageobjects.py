from t24pageobjects import T24LoginPage,T24HomePage
import os
import unittest


class T24LoginPageTestCase(unittest.TestCase):

    def setUp(self):
        os.environ["PO_BASEURL"] = "http://192.168.131.132:9095"
        os.environ["PO_BROWSER"] = "firefox"
        
        self.loginpage = T24LoginPage()
        self.loginpage.open()

    def test_login(self):
        page = self.loginpage.enter_T24_credentials("INPUTT","123456")
        page.enter_t24_command("CUSTOMER I F3")

    def tearDown(self):
        self.loginpage.close()

if __name__ == "__main__":
    unittest.main()