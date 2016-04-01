import time

from robotpageobjects import Page, robot_alias
from robot.libraries.BuiltIn import BuiltIn
from selenium.webdriver.common.keys import Keys

from T24OperationType import T24OperationType
from T24ExecutionContext import T24ExecutionContext
from utils import BuiltinFunctions
from utils import Config
from datetime import datetime
import time
import sys


class T24Page(Page):
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'
    __version__ = '0.1'

    def _get_current_page(self):
        return T24ExecutionContext.Instance().get_current_page()

    def _set_current_page(self, page):
        self.log("The current page is changing to " + page.name, "DEBUG", False)
        return T24ExecutionContext.Instance().set_current_page(page)

    def _add_operation(self, operation):
        self.log("Executing operation '" + operation + "' ...", "DEBUG", False)
        T24ExecutionContext.Instance().add_operation(operation)

    @staticmethod
    def _get_screenshot_level(level):
        if not level:
            return 0

        level = level.upper()
        if level == "INFO":
            return 1
        if level == "VERBOSE":
            return 2
        return 0

    def _get_current_screenshot_level(self):
        try:
            level = BuiltIn().get_variable_value("${SCREENSHOTS}")
            return self._get_screenshot_level(level)
        except:
            return 0

    def _take_page_screenshot(self, level="INFO"):
        if self._get_screenshot_level(level) > self._get_current_screenshot_level():
            return

        try:
            fileName = T24ExecutionContext.Instance().get_next_screenshot_filename()
            self.capture_page_screenshot(fileName)
        except:
            pass

class T24LoginPage(T24Page):
    """ Models the T24 login page"""

    # Allows us to call by proper name
    name = "T24 Login Page"

    # This page is found at baseurl
    uri = "/BrowserWeb"

    # Inheritable dictionary mapping human-readable names to Selenium2Library locators. 
    # You can then pass in the keys to Selenium2Library actions instead of the locator strings.
    selectors = {
        "user input": "xpath=.//*[@id='signOnName']",
        "password input": "xpath=.//*[@id='password']",
        "login button": "css=#sign-in",
    }

    # Use robot_alias and the "__name__" token to customize where to insert the optional page object name.
    @robot_alias("type_in__name__username_box")
    def _type_username(self, txt):
        self.input_text("user input", txt)

        # We always return something from a page object, even if it's the same page object instance we are currently on.
        return self

    # Use robot_alias and the "__name__" token to customize where to insert the optional page object name.
    @robot_alias("type_in__name__password_box")
    def _type_password(self, txt):
        self.input_text("password input", txt)

        # We always return something from a page object, even if it's the same page object instance we are currently on.
        return self

    # Use robot_alias and the "__name__" token to customize where to insert the optional page object name.
    @robot_alias("clicks__name__login_button")
    def _click_login(self):
        self.click_element("login button")
        self._set_current_page(T24HomePage())
        return self._get_current_page()

    @robot_alias("enter_T24_credentials")
    def enter_T24_credentials(self, username, password):
        self._add_operation(T24OperationType.Login)
        self._type_username(username)
        self._type_password(password)

        self._take_page_screenshot("VERBOSE")

        return self._click_login()

class T24HomePage(T24Page):
    """ Models the T24 home page """

    # Allows us to call by proper name
    name = "T24 Home Page"

    # This page is found at baseurl + "/BrowserWeb"
    uri = "/BrowserWeb"

    # Inheritable dictionary mapping human-readable names to Selenium2Library locators.
    # You can then pass in the keys to Selenium2Library actions instead of the locator strings.
    selectors = {
        "banner frame": "xpath=//frame[contains(@id,'banner') or contains(@id,'USER')]",
        "banner frame user": "xpath=//frame[contains(@id,'USER')]",
        "command line": "css=input[name='commandValue']",
        "frame tab": "xpath=//frame[contains(@id,'FRAMETAB')]",
    }

    @robot_alias("sign_off")
    def sign_off(self):
        self._add_operation(T24OperationType.SignOff)
        self._make_sure_home_page_is_active()

        self.select_window()
        self.select_frame(self.selectors["banner frame"])
        self.click_link("Sign Off")

        self._set_current_page(T24LoginPage())
        return self._get_current_page()

    # Enter a T24 command and simulate an Enter
    def _enter_t24_command(self, text):

        self._make_sure_home_page_is_active()

        self.log("Executing command '" + text.strip() + "' ...", "INFO", False)

        self.select_window()

        isCos = self._is_cos()

        self.select_frame(self.selectors["banner frame"])

        self.wait_until_page_contains_element(self.selectors["command line"])
        self.input_text(self.selectors["command line"], text + "\n")
        self._take_page_screenshot("VERBOSE")

        if isCos:
            self.unselect_frame()
            self.select_frame(self.selectors["frame tab"])
        else:
            self.select_window("new")

        self._take_page_screenshot("VERBOSE")

        # We always return something from a page object, even if it's the same page object instance we are currently on.
        return self

    def _is_cos(self):
        try:
            return self.find_element(self.selectors["banner frame user"], False, 0) != None
        except:
            return False

    def _make_sure_home_page_is_active(self):
        if not isinstance(self._get_current_page(), T24HomePage):
            self.log("Automatically closing " + self._get_current_page().name + "...", "INFO", False)
            self._get_current_page().close_window()
            self._set_current_page(self)  # don't create new object for home page (reuse the current one)

    # Enter a T24 enquiry API command
    @robot_alias("run_t24_enquiry")
    def open_t24_enquiry(self, enquiry_name, enquiry_filters=[]):
        self._add_operation(T24OperationType.Enquiry)
        # prepare the filter text
        if not enquiry_filters:
            self._enter_t24_command("ENQ " + enquiry_name)
            enq_start_page = T24EnquiryStartPage()
            self._set_current_page(enq_start_page)
            return enq_start_page.run_enquiry_no_filters()
        else:
            filter_text = ' '.join([str(f) for f in enquiry_filters])
            self._enter_t24_command("ENQ " + enquiry_name + " " + filter_text)
            self._set_current_page(T24EnquiryResultPage())
            return self._get_current_page()

    # Opens a T24 input page
    @robot_alias("open_input_page_new_record")
    def open_input_page_new_record(self, version):
        self._add_operation(T24OperationType.StartInputNewRecord)
        self._enter_t24_command(version + " I F3")

        self._set_current_page(T24RecordInputPage())
        return self._get_current_page()

    @robot_alias("open_edit_page")
    def open_edit_page(self, version, record_id):
        self._add_operation(T24OperationType.StertEditExitingRecord)
        self._enter_t24_command(version + " I " + record_id)

        self._set_current_page(T24RecordInputPage())
        return self._get_current_page()

    @robot_alias("open_authorize_page")
    def open_authorize_page(self, version, record_id):
        self._add_operation(T24OperationType.StartAuthorizingRecord)
        self._enter_t24_command(version + " A " + record_id)

        self._set_current_page(T24RecordInputPage())
        return self._get_current_page()

    @robot_alias("open_see_page")
    def open_see_page(self, version, record_id):
        self._add_operation(T24OperationType.SeeRecord)
        self._enter_t24_command(version + " S " + record_id)

        self._set_current_page(T24RecordSeePage())
        return self._get_current_page()

class T24EnquiryStartPage(T24Page):
    """ Models the T24 Enquiry Start Page"""

    # Allows us to call by proper name
    name = "T24 Enquiry Filters Page"

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

        self._take_page_screenshot("VERBOSE")

        self._set_current_page(T24EnquiryResultPage())
        return self._get_current_page()

class T24EnquiryResultPage(T24Page):
    """ Models the T24 Enquiry Result Page"""

    # Allows us to call by proper name
    name = "T24 Enquiry Results Page"

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
        self.select_window("self")
        self.wait_until_page_contains_element(self.selectors["refresh button"])

        #if self._page_contains("No records matched the selection criteria"):
        #    return "" # too slow

        #if not self.wait_until_page_contains_element(self.selectors["first text column in grid"], 5):
        #   return ""  # doesn't work

        res = self._get_text(self.selectors["first text column in grid"])  # TODO error handling (throw better error)
        return res

    # Gets the first ID of an enquiry result
    @robot_alias("get_values_from_enquiry_result")
    def get_values_from_enquiry_result(self, column_indexes):
        self.select_window("self")
        self.wait_until_page_contains_element(self.selectors["refresh button"])

        #if self._page_contains("No records matched the selection criteria"):
        #    return "" # too slow

        #if not self.wait_until_page_contains_element(self.selectors["first text column in grid"], 5):
        #   return ""  # doesn't work

        res = []
        for c in column_indexes:
            index = int(c) + 1
            val = self._get_text("css=#r1 > td:nth-child(" + str(index) + ")")  # TODO error handling (throw better error)
            res.append(val)

        return res

class T24RecordSeePage(T24Page):
    """ Models the T24 Record See Page"""

    # Allows us to call by proper name
    name = "T24 Record Page"

    # Probably not necessary
    uri = "/BrowserWeb/servlet/BrowserServlet#1"

    # Gets a text value from the underlying T24 field name
    @robot_alias("get_T24_field_value")
    def get_T24_field_value(self, fieldName):
        if fieldName == "ID" or fieldName == "@ID":
            fieldValue = self._get_text("xpath=.//*[@id='transactionId']")
        elif Config.get_t24_version() >= 14:
            fieldValue = self._get_text("xpath=.//*[@id='fieldCaption:" + fieldName + "']/../../..//*[3]//*")
        else:
            fieldValue = self._get_text("xpath=.//*[@id='fieldCaption:" + fieldName + "']/../..//*[3]//*")
        self.log("Retrieved value for field '" + fieldName + "' is '" + fieldValue + "'", "INFO", False)
        return fieldValue

class T24RecordInputPage(T24Page):
    """ Models the T24 Record Input Page"""

    # Allows us to call by proper name
    name = "T24 Record Edit Page"

    # Probably not necessary
    uri = "/BrowserWeb/servlet/BrowserServlet#1"

    # Inheritable dictionary mapping human-readable names to Selenium2Library locators.
    # You can then pass in the keys to Selenium2Library actions instead of the locator strings.
    selectors = {
        "transaction complete": "xpath=//tr[contains(td, 'Txn Complete')]",
    }

    # Checks whether the transaction is completed and if yes, extracts the referenced ID
    @robot_alias("get_id_from_completed_transaction")
    def get_id_from_completed_transaction(self):
        self.wait_until_page_contains("Txn Complete")  # Put a timeout or wait for error, too

        self._take_page_screenshot("VERBOSE")

        confirmationMsg = self._get_text(self.selectors["transaction complete"])
        transactionId = self._get_id_from_transaction_confirmation_text(confirmationMsg)
        return transactionId

    def is_txt_complete_displayed(self):
        return self._page_contains("Txn Complete")

    def _get_id_from_transaction_confirmation_text(self, confirmTransactionText):
        return confirmTransactionText.replace('Txn Complete:', '').strip().split(' ', 1)[0]

    # Set a value in a text field, by specifying the underlying T24 field name
    @robot_alias("set_T24_field_value")
    def set_T24_field_value(self, fieldName, fieldText):

        # TODO here we would support more field
        if fieldText.upper().startswith("#AUTO"):
            fieldText = BuiltinFunctions().get_unique_new_customer_mnemonic()

        # if fieldName == "GENDER"

        isHotField = self._is_hot_field(fieldName)

        self.log("Setting value '" + fieldText + "' to field '" + fieldName + "'", "INFO", False)
        self.input_text(self._get_field_locator(fieldName), fieldText)

        if isHotField:
            self._leave_focus(fieldName)
            time.sleep(1)
            # wait for a reload (necessary after setting hot fields), but maybe do it only if the field is hot [hot="Y"]
            self.wait_until_page_contains_element(self._get_commit_locator())

        return self

    def _is_hot_field(self, fieldName):
        element = self.find_element(self._get_field_locator(fieldName))
        return element and element.get_attribute('hot') == 'Y'

    def _leave_focus(self, fieldName):
        element = self.find_element(self._get_field_locator(fieldName))
        if element:
            element.send_keys(Keys.TAB);

    def _get_field_locator(self, fieldName):
        return "css=input[name='fieldName:" + fieldName + "']"

    def _get_commit_locator(self):
        return "css=img[alt=\"Commit the deal\"]"

    # Clicks the Commit Button when dealing with T24 transactions
    def click_commit_button(self):
        self._take_page_screenshot("VERBOSE")

        self.wait_until_page_contains_element(self._get_commit_locator(), 3)

        self.click_element(self._get_commit_locator())
        return self

    def is_accept_overrides_displayed(self):
        try:
            self.wait_until_page_contains_element("link=Accept Overrides", 3)
            return True
        except: # catch *all* exceptions
            return False

    # Clicks the Accept Overrides link (if available) when dealing with T24 transactions
    def click_accept_overrides(self):
        try:
            start = datetime.now()
            self.log("Waiting for Accept Overrides link to appear... ")
            self.wait_until_page_contains_element("link=Accept Overrides", 10)
            self.log("Accept Overrides link found in " + str(int((datetime.now() - start).total_seconds())) + " seconds")

            self._take_page_screenshot("VERBOSE")

            self.click_link("link=Accept Overrides")

            # The fastest way to search for completing of operation is just to look in the page source
            # We could also use self.wait_until_page_does_not_contain or wait_until_page_does_not_contain_element,
            # but need to temporarily reduce 'selenium_implicit_wait' from 10 to something quite smaller (e.g. 0.1)
            start = datetime.now()
            self.log("Waiting for completion of accepting overrides...")
            err = self._wait_until_page_source_does_not_contain("Accept Overrides", 10)
            if err is None:
                self.log("Completed processing of 'Accept Overrides' in " +
                     str(int((datetime.now() - start).total_seconds())) + " seconds")
            else:
                self.log(err)
        except:  # catch *all* exceptions
            e = sys.exc_info()[0]
            self.log("Warning: " + str(e))
            pass

        return self

    def _wait_until_page_source_does_not_contain(self, text, timeout=None, error=None):
        def check_present_src():
            present = self.get_source().find(text) > -1
            if not present:
                return
            else:
                return error or "Text '%s' not found in %s" % (text, self._format_timeout(timeout))
        self._wait_until_no_error(timeout, check_present_src)

    # Receive documents (if available) when dealing with T24 transactions
    def receive_documents(self):
        try:
            self.wait_until_page_contains_element("xpath=//select[starts-with(@id,'warningChooser:Have you received')]", 3)
            self._take_page_screenshot("VERBOSE")

            for elementOption in self.find_elements("xpath=//select[starts-with(@id,'warningChooser:Have you received')]/option[@value='RECEIVED']"):
                elementOption.click()

        except: # catch *all* exceptions
            pass

        return self

    # Clicks the Authorize Button When Dealing with T24 Transactions
    def click_authorize_button(self):
        self.click_element("css=img[alt=\"Authorises a deal\"]")
        return self
