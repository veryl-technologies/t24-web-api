from robotpageobjects import Page, robot_alias
from robot.utils import asserts

class T24LoginPage(Page):
    """ Models the T24 login page"""

    # Allows us to call by proper name
    name = "T24Login"

    # This page is found at baseurl
    uri = "/BrowserWeb"

    # Inheritable dictionary mapping human-readable names to Selenium2Library locators. 
    # You can then pass in the keys to Selenium2Library actions instead of the locator strings.
    selectors = {
        "user input": "xpath=.//*[@id='signOnName']",
        "password input": "xpath=.//*[@id='password']",
        "login button": "css=#sign-in",
    }

    # Use robot_alias and the "__name__" token to customize where to insert the optional page object name when calling this keyword. 
    @robot_alias("type_in__name__username_box")
    def _type_username(self, txt):
        self.input_text("user input", txt)

        # We always return something from a page object, even if it's the same page object instance we are currently on.
        return self

    # Use robot_alias and the "__name__" token to customize where to insert the optional page object name when calling this keyword. 
    @robot_alias("type_in__name__password_box")
    def _type_password(self, txt):
        self.input_text("password input", txt)

        # We always return something from a page object, even if it's the same page object instance we are currently on.
        return self

    # Use robot_alias and the "__name__" token to customize where to insert the optional page object name when calling this keyword. 
    @robot_alias("clicks__name__login_button")
    def _click_login(self):
        self.click_element("login button")
        return T24HomePage()

    @robot_alias("enter_T24_credentials")
    def enter_T24_credentials(self, username, password):
        self._type_username(username)
        self._type_password(password)
        return self._click_login()

class T24HomePage(Page):
    """ Models the T24 home page """

    # Allows us to call by proper name
    name = "T24Home"

    # This page is found at baseurl + "/BrowserWeb"
    uri = "/BrowserWeb"

    # Inheritable dictionary mapping human-readable names to Selenium2Library locators.
    # You can then pass in the keys to Selenium2Library actions instead of the locator strings.
    selectors = {
        "banner frame": "xpath=//frame[contains(@id,'banner')]",
        "command line": "css=input[name='commandValue']",
    }

    @robot_alias("sign_off")
    def sign_off(self):
        self.select_frame(self.selectors["banner frame"])
        self.click_link("Sign Off")
        return T24LoginPage()

    # Enter a T24 command and simulate an Enter
    def _enter_t24_command(self, text):
        self.select_window()
        self.select_frame(self.selectors["banner frame"])
        self.wait_until_page_contains_element(self.selectors["command line"])
        self.input_text(self.selectors["command line"], text+"\n")

        # We always return something from a page object,
        # even if it's the same page object instance we are currently on.
        return self

    # Enter a T24 enquiry API command
    @robot_alias("enter_t24_enquiry")
    def open_t24_enquiry(self, enquiry_name, enquiry_filters=[]):

        # prepare the filter text
        if not enquiry_filters:
            enquiry_filters = ["@ID GT 0"]  # This is a workaround only (to jump directly to the results page)
        filter_text = ' '.join([str(f) for f in enquiry_filters])

        self._enter_t24_command("ENQ " + enquiry_name + " " + filter_text)
        return T24EnquiryResultPage()

class T24EnquiryStartPage(Page):
    """ Models the T24 Enquiry Start Page"""

    # Allows us to call by proper name
    name = "T24EnquiryFilters"

    # Probably not necessary
    uri = "/BrowserWeb/servlet/BrowserServlet#1"

    # Inheritable dictionary mapping human-readable names to Selenium2Library locators.
    # You can then pass in the keys to Selenium2Library actions instead of the locator strings.
    selectors = {
        "clear selection link": "xpath=.//a[contains(normalize-space(.), 'Clear Selection')]",
        "find button": "xpath=.//a[@title='Run Selection']",
    }

    # Runs a T24 enquiry
    @robot_alias("run_enquiry_no_filters")
    def run_enquiry_no_filters(self):
        self.wait_until_page_contains_element(self.selectors["clear selection link"])
        self.wait_until_page_contains_element(self.selectors["find button"])

        self.click_element(self.selectors["clear selection link"])
        self.click_element(self.selectors["find button"])

        return T24EnquiryResultPage()

class T24EnquiryResultPage(Page):
    """ Models the T24 Enquiry Result Page"""

    # Allows us to call by proper name
    name = "T24EnquiryResults"

    # Probably not necessary
    uri = "/BrowserWeb/servlet/BrowserServlet#1"

    # Inheritable dictionary mapping human-readable names to Selenium2Library locators.
    # You can then pass in the keys to Selenium2Library actions instead of the locator strings.
    selectors = {
        "refresh button": "xpath=.//img[@alt='Refresh']",
        "first text column in grid": "css=#r1 > td:nth-child(2)",
    }

    # Gets the first ID of an enquiry result
    @robot_alias("get_first_id_of_enquiry_result")
    def get_first_id_of_enquiry_result(self):
        self.select_window("new")
        self.wait_until_page_contains_element(self.selectors["refresh button"])

        #if self._page_contains("No records matched the selection criteria"):
        #    return "" # too slow

        #if not self.wait_until_page_contains_element(self.selectors["first text column in grid"], 5):
        #   return ""  # doesn't work

        res = self._get_text(self.selectors["first text column in grid"])  # TODO error handling (throw better error)
        return res

class T24RecordInputPage(Page):
    """ Models the T24 Record Input Page"""

    # Allows us to call by proper name
    name = "T24RecordInput"

    # Probably not necessary
    uri = "/BrowserWeb/servlet/BrowserServlet#1"

    # Inheritable dictionary mapping human-readable names to Selenium2Library locators.
    # You can then pass in the keys to Selenium2Library actions instead of the locator strings.
    selectors = {
        "transaction complete": "xpath=//tr[contains(td, 'Txn Complete')]",
    }

    # Checks whether the transaction is completed and if yes, extracts the referenced ID
    @robot_alias("get_first_id_of_enquiry_result")
    def get_id_from_completed_transaction(self):
        # self.select_window("new")
        self.wait_until_page_contains("Txn Complete")
        confirmationMsg = self._get_text(self.selectors["transaction complete"])
        transactionId = self._get_id_from_transaction_confirmation_text(confirmationMsg)
        return transactionId

    def _get_id_from_transaction_confirmation_text(self, confirmTransactionText):
        return confirmTransactionText.replace('Txn Complete:', '').strip().split(' ', 1)[0]

    #  Set a value in a text field, by specifying the underlying T24 field name
    def input_text_to_T24_field(self, fieldName, fieldText):
        self.input_text("css=input[name='fieldName:" + fieldName + "}']", fieldText)

    #   Clicks the Commit Button When Dealing with T24 Transactions
    def click_commit_button(self):
        self.click_element("css=img[alt=\"Commit the deal\"]")

    #   Clicks the Authorize Button When Dealing with T24 Transactions
    def click_authorize_button(self):
        self.click_element("css=img[alt=\"Authorises a deal\"]")
