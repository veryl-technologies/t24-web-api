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

        # We always return something from a page object, even if it's the same page object instance we are currently on.
        return T24HomePage()

    @robot_alias("enter_T24_credentials")
    def enter_T24_credentials(self, username, password):
        self._type_username (username)
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

    # Enter a T24 command
    @robot_alias("enter_t24_command")
    def enter_t24_command(self, text):
        self.select_frame(self.selectors["banner frame"])
        self.wait_until_page_contains_element(self.selectors["command line"])
        self.input_text(self.selectors["command line"], text+"\n")

        # We always return something from a page object,
        # even if it's the same page object instance we are currently on.
        return self

    # Enter a T24 enquiry API command
    @robot_alias("enter_t24_enquiry")
    def open_t24_enquiry(self, text):
        self.enter_t24_command(text)

        return T24EnquiryStartPage()

class T24EnquiryStartPage(Page):
    """ Models the T24 Enquiry Start Page"""

    # Allows us to call by proper name
    name = "T24Enquiry"

    # Probably not necessary
    uri = "/BrowserWeb/servlet/BrowserServlet#1"

    # Inheritable dictionary mapping human-readable names to Selenium2Library locators.
    # You can then pass in the keys to Selenium2Library actions instead of the locator strings.
    selectors = {
        "clear selection link": "xpath=.//a[contains(normalize-space(.), 'Clear Selection')]",
        "find button": "xpath=.//a[@title='Run Selection']",
    }

    # Runs a T24 enquiry
    @robot_alias("run_enquiry")
    def run_enquiry(self, fieldName, fieldValue):
        self.wait_until_page_contains_element(self.selectors["clear selection link"])
        self.wait_until_page_contains_element(self.selectors["find button"])

        self.click_element(self.selectors["clear selection link"])
        self.click_element(self.selectors["find button"])

        # We always return something from a page object,
        # even if it's the same page object instance we are
        # currently on.
        return self

