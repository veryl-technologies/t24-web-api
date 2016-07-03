import time

from selenium.common import exceptions

from pageObjects import Page, robot_alias
from robot.libraries.BuiltIn import BuiltIn
from selenium.webdriver.common.keys import Keys

from T24OperationType import T24OperationType
from T24ExecutionContext import T24ExecutionContext
import BuiltinFunctions
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

    def evaluate_value(self, fieldText):
        fieldText = str(fieldText)
        if fieldText.upper().startswith("?AUTO"):
            fieldText = BuiltinFunctions.get_unique_new_customer_mnemonic()
        elif fieldText.startswith("?"):
            fieldText = self._evaluate_expression(fieldText[1:])

        return fieldText

    def _evaluate_expression(self, expr):
        # NOTE For a safer alternative to eval() see ast.literal_eval()
        # http://stackoverflow.com/questions/15197673/using-pythons-eval-vs-ast-literal-eval
        expr = expr.replace('$', "__import__('BuiltinFunctions').")  # TODO support escaping (via $$)
        self.log("Evaluating expression '" + expr + "' ...", "INFO", False)
        res = str(eval(expr))
        self.log("The result of expression evaluation is '" + res + "'", "INFO", False)
        return res

    def _get_authorize_locator(self):
        return "css=img[alt=\"Authorises a deal\"]"

    def _get_commit_locator(self):
        return "css=img[alt=\"Commit the deal\"]"


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
        "menu frame": "xpath=//frame[contains(@id,'menu') or contains(@id,'USER')]",
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

    def _find_or_open_app_window(self, version, command, id):
        if self._find_and_select_suitable_opened_window(version, command, id):
            return

        self._enter_t24_command(version + " " + command + " " + id)

    def _find_or_open_enq_window(self, enquiry_name, filter_text):
        if self._find_and_select_suitable_opened_window(enquiry_name, "ENQ", None):
            return

        command = "ENQ " + enquiry_name
        if filter_text:
            command += " " + filter_text
        self._enter_t24_command("ENQ " + enquiry_name + " " + id)

    def _find_and_select_suitable_opened_window(self, version, command, id):
        return False
        """NOT IMPLEMENTED

        windowNames = self.get_window_names()

        while len(windowNames) > 1:    # while there are other windows apart from the main
            self.select_window(windowNames[len(windowNames) - 1])
            if self._is_current_window_suitable_for_command(version, command, id):
                return True

            self._get_current_page().close_window()
            windowNames = self.get_window_names()

        self._set_current_page(T24HomePage())
        self.select_window()
        return False
        """

    def _is_current_window_suitable_for_command(self, version, command, id):
        info = self._get_current_window_info()

        if info['isCommited']:
            return False

        if info is not None and info['command'] == command and info['version'] == version:
            if command == "I" or command == "A" or command == "S":
                if id is not None and len(id) > 0 and id != "F3":
                    # transaction ID must match
                    if info['transactionId'] != id:
                        return False

            return True

        return False

    def _get_current_window_info(self):
        try:
            form = self.find_element("xpath=.//form[@id='appreq']", False, 0)
            version = form.find_element_by_xpath("input[@id='version']").get_attribute("value")
            application = form.find_element_by_xpath("input[@id='application']").get_attribute("value")

            if T24RecordInputPage().is_txn_complete_displayed_no_wait():
                id = T24RecordInputPage().get_id_from_completed_transaction()
                return dict(command = "", version = application + version, transactionId = id, isCommited = True)

            id = T24TransactionPage().get_transaction_id()

            if T24TransactionPage().commit_btn_enabled():
                return dict(command = "I", version = application + version, transactionId = id, isCommited = False)
            elif T24TransactionPage.autorize_btn_enabled():
                return dict(command = "A", version = application + version, transactionId = id, isCommited = False)
            else:
                return dict(command = "S", version = application + version, transactionId = id, isCommited = False)
        except:
            try:
                form = self.find_element("xpath=.//form[@id='enqsel']", False, 0) # enquiry form don't exists when on selection
                enqname = form.find_element_by_xpath("input[@id='enqname']").get_attribute("value")
                return dict(command = "ENQ", version = enqname, isSelection = True, transactionId = '', isCommited = False)
            except:
                try:
                    form = self.find_element("xpath=.//form[@id='enquiry']", False, 0)
                    version = form.find_element_by_xpath("input[@id='version']").get_attribute("value")
                    return dict(command = "ENQ", version = version, isSelection = False, transactionId = '', isCommited = False)
                except:
                    pass

        return None

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
            self._find_or_open_enq_window(enquiry_name, None)
            enq_start_page = T24EnquiryStartPage()
            self._set_current_page(enq_start_page)
            return enq_start_page.run_enquiry_no_filters()
        else:
            filter_text = ' '.join([str(f) for f in enquiry_filters])
            self._find_or_open_enq_window(enquiry_name, filter_text)
            self._set_current_page(T24EnquiryResultPage())
            return self._get_current_page()

    # Executed T24 menu command
    @robot_alias("run_t24_menu_command")
    def run_t24_menu_command(self, menu_items):
        self._make_sure_home_page_is_active()

        self.log("Executing menu command '" + menu_items + "' ...", "INFO", False)

        self.select_window()

        self.select_frame(self.selectors["menu frame"])

        items = [item.strip() for item in menu_items.split('>')]

        xpath = self._build_menu_command_xpath_full(items)
        elements = self.find_elements(xpath)
        if len(elements) == 0:
            raise exceptions.NoSuchElementException("Unable to find menu path '" + menu_items + "'")
        elif len(elements) > 1:
            raise exceptions.NoSuchElementException("More than one menu items with given path found: '" + menu_items + "'")

        menu_element = elements[0]

        # go and find all of the parent nodes
        parent = menu_element.find_element_by_xpath("..")
        parents = []
        while True:
            parent = parent.find_element_by_xpath("../..")
            if parent.tag_name != u'li':
                break;
            parents.insert(0, parent)

        # expand all of the parent nodes
        for p in parents:
            e = p.find_element_by_xpath("span[@onclick='ProcessMouseClick(event)']/img")
            e.click()

        # click on the end element
        menu_element.click()

        # todo - set curret page should be done here or sth else?
        # todo - we can check the menu_element for type of the page opened (I, A, S, COS ... ) to determine what current page we should set

        self._take_page_screenshot("VERBOSE")

        self._set_current_page(T24Page())
        return self._get_current_page()

    def _build_menu_command_xpath_full(self, items):
        # "xpath=.//li[@class='clsHasKids']/span[text()='Customer']/following-sibling::ul[1]/li/a[contains(@onclick, 'Individual Customer')]"
        result = "xpath=./"
        i = 0
        for item in items:
            i += 1
            if i == len(items): # last item
                result += "/li/a[contains(@onclick, '" + item + "')]"
            else:
                result += "/li[@class='clsHasKids']/span[text()='" + item + "']/following-sibling::ul[1]"

        return result

    # Opens a T24 input page
    @robot_alias("open_input_page_new_record")
    def open_input_page_new_record(self, version):
        self._add_operation(T24OperationType.StartInputNewRecord)
        self._find_or_open_app_window(version, "I", "F3")

        self._set_current_page(T24RecordInputPage())
        return self._get_current_page()

    @robot_alias("open_edit_page")
    def open_edit_page(self, version, record_id):
        self._add_operation(T24OperationType.StertEditExitingRecord)

        record_id = self.evaluate_value(record_id)
        self._find_or_open_app_window(version, "I", record_id)

        self._set_current_page(T24RecordInputPage())
        return self._get_current_page()

    @robot_alias("open_authorize_page")
    def open_authorize_page(self, version, record_id):
        self._add_operation(T24OperationType.StartAuthorizingRecord)

        record_id = self.evaluate_value(record_id)
        self._find_or_open_app_window(version, "A", record_id)

        self._set_current_page(T24RecordInputPage())
        return self._get_current_page()

    @robot_alias("open_see_page")
    def open_see_page(self, version, record_id):
        self._add_operation(T24OperationType.SeeRecord)

        record_id = self.evaluate_value(record_id)
        self._find_or_open_app_window(version, "S", record_id)

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


class T24TransactionPage(T24Page):
    def get_transaction_id(self):
        try:
            return self.get_text("xpath=.//span[contains(@class, 'iddisplay')]")
        except:
            return ""

    def commit_btn_enabled(self):
        try:
            btn = self.find_element("xpath=.//img[@title='Commit the deal']")
            return "_dis.gif" not in btn.get_attribute("src")
        except:
            return False

    def autorize_btn_enabled(self):
        try:
            btn = self.find_element("xpath=.//img[@title='Authorises a deal']")
            return "_dis.gif" not in btn.get_attribute("src")
        except:
            return False


class T24RecordSeePage(T24TransactionPage):
    """ Models the T24 Record See Page"""

    # Allows us to call by proper name
    name = "T24 Record Page"

    # Probably not necessary
    uri = "/BrowserWeb/servlet/BrowserServlet#1"

    # Gets a text value from the underlying T24 field name
    @robot_alias("get_T24_field_value")
    def get_T24_field_value(self, fieldName):
        if fieldName == "ID" or fieldName == "@ID":
            fieldValue = self._get_value("xpath=.//input[@id='transactionId' and preceding-sibling::span]")
        elif Config.get_t24_version() >= 14:
            fieldValue = self._get_text("xpath=.//*[@id='fieldCaption:" + fieldName + "']/../../..//*[3]//*")
        else:
            fieldValue = self._get_text("xpath=.//*[@id='fieldCaption:" + fieldName + "']/../..//*[3]//*")
        self.log("Retrieved value for field '" + fieldName + "' is '" + fieldValue + "'", "INFO", False)
        return fieldValue


class T24RecordInputPage(T24TransactionPage):
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

    def is_txn_complete_displayed(self):
        return self._page_contains("Txn Complete")

    def is_txn_complete_displayed_no_wait(self):
        try:
            if self.find_element("xpath=.//*[contains(text(),'Txn Complete')]", False, 0) is not None:
                return True
            return False
        except:
            return False

    def _get_id_from_transaction_confirmation_text(self, confirmTransactionText):
        return confirmTransactionText.replace('Txn Complete:', '').strip().split(' ', 1)[0]

    # Set a value in a text field, by specifying the underlying T24 field name
    @robot_alias("set_T24_field_value")
    def set_T24_field_value(self, fieldName, fieldText):

        fieldCtrl = self._get_field_ctrl(fieldName)
        if not fieldCtrl:
            raise exceptions.NoSuchElementException("Unable to find control for '" + fieldName + "' field name")

        self.log("Checking if the field is in another tab...", "DEBUG", False)
        self._select_field_tab(fieldCtrl)

        if fieldText.upper().startswith("?SELECT-FIRST"):
            fieldText = fieldCtrl.get_first_value()
        else:
            fieldText = self.evaluate_value(fieldText)

        self.log("Setting value '" + fieldText + "' to field '" + fieldName + "'", "INFO", False)

        fieldCtrl.set_text(fieldText)

        return self

    def _get_field_ctrl(self, fieldName):
        waitTimeBetweenRetries = 1
        maxRetries = 10

        while maxRetries > 0:
            maxRetries -= 1
            hiddenFieldTabName = None
            try:
                element = self.find_elements(T24InputFieldCtrl.get_locator(fieldName), False, 0)[0]
                if element and element.get_attribute("type") != u'hidden':
                    return T24InputFieldCtrl(self, fieldName, element)
                elif element.get_attribute("type") == u'hidden':
                    hiddenFieldTabName = element.get_attribute("tabname")
            except:
                pass

            try:
                element = self.find_elements(T24SelectFieldCtrl.get_locator(fieldName), False, 0)[0]
                if element:
                    return T24SelectFieldCtrl(self, fieldName, element)
            except:
                pass

            try:
                elements = self.find_elements(T24RadioFieldCtrl.get_locator(fieldName, hiddenFieldTabName), False, waitTimeBetweenRetries)
                if elements:
                    return T24RadioFieldCtrl(self, fieldName, elements, hiddenFieldTabName)
            except:
                pass

        return None

    def _select_field_tab(self, fieldCtrl):
        try:
            tabName = fieldCtrl.element.get_attribute("tabname")
            if tabName and tabName != "mainTab" and tabName != 'tab1':
                onclickVal = "javascript:changetab('" + tabName + "')"
                tabElement = self.find_element('xpath=.//a[@onclick="' + onclickVal + '"]')
                if tabElement.get_attribute("class") == "nonactive-tab":
                    self.log("Activating tab " + tabName, "DEBUG", False)
                    tabElement.click()
        except:
            pass    # not essential action

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

    def is_receive_documents_pending(self):
        try:
            self.wait_until_page_contains_element("xpath=//select[starts-with(@id,'warningChooser:Have you received')]", 3)
            return True
        except:  # catch *all* exceptions
            return False

    # Receive documents (if available) when dealing with T24 transactions
    def receive_documents(self):
        try:
            self._take_page_screenshot("VERBOSE")
            for elementOption in self.find_elements("xpath=//select[starts-with(@id,'warningChooser:Have you received')]/option[@value='RECEIVED']"):
                elementOption.click()

        except: # catch *all* exceptions
            pass

        return self

    # Clicks the Authorize Button When Dealing with T24 Transactions
    def click_authorize_button(self):
        self.click_element(self._get_authorize_locator())
        return self


class T24FieldCtrl:
    def __init__(self, page, fieldName, element):
        self.page = page
        self.fieldName = fieldName
        self.element = element

    def set_text(self, fieldText):
        self.page.log("Checking if the field is a hot field...", "DEBUG", False)
        isHotField = self._is_hot_field()

        self.page.log("Checking if the field auto-launches an enquiry...", "DEBUG", False)
        isAutoLaunchEnquiry = not isHotField and self._is_auto_launch_enquiry()

        self.set_control_text(fieldText)

        if isHotField:
            self._leave_focus()
            time.sleep(1)
            # wait for a reload (necessary after setting hot fields), but maybe do it only if the field is hot [hot="Y"]
            self.page.wait_until_page_contains_element(self.page._get_commit_locator())
        elif isAutoLaunchEnquiry:
            windowsCount = len(self.page.get_window_names())
            self._leave_focus()
            time.sleep(1)

            newWindowNames = self.page.get_window_names()

            while len(newWindowNames) > windowsCount:
                self.page.select_window(newWindowNames[len(newWindowNames) - 1])
                self.page.close_window()

                newWindowNames = self.page.get_window_names()

            self.page.select_window(newWindowNames[len(newWindowNames) - 1])

        return self

    def _is_hot_field(self):
        return self.element and self.element.get_attribute('hot') == 'Y'

    def _is_auto_launch_enquiry(self):
        return self.element and self.element.get_attribute('autoenqname') and len(self.element.get_attribute('autoenqname')) > 1

    def _leave_focus(self):
        if self.element:
            self.element.send_keys(Keys.TAB);


class T24InputFieldCtrl(T24FieldCtrl):
    def __init__(self, page, fieldName, element):
        T24FieldCtrl.__init__(self, page, fieldName, element)

    @staticmethod
    def get_locator(fieldName):
        return "css=input[name='fieldName:" + fieldName + "']"

    def set_control_text(self, fieldText):
        self.page.log("Setting a value to a text field...", "DEBUG", False)
        self.page.input_text(self.get_locator(self.fieldName), fieldText)

    def get_first_value(self):
        return ''  # TODO maybe it's good to return the text of the input field, although it would be empty


class T24SelectFieldCtrl(T24FieldCtrl):
    def __init__(self, page, fieldName, element):
        T24FieldCtrl.__init__(self, page, fieldName, element)

    @staticmethod
    def get_locator(fieldName):
        return "css=select[name='fieldName:" + fieldName + "']"

    def set_control_text(self, fieldText):
        self.page.log("Selecting a value from a list...", "DEBUG", False)
        self.page.select_from_list(self.get_locator(self.fieldName), fieldText)

    def get_first_value(self):
        locator = self.get_locator(self.fieldName) + " option"
        elements = self.page.find_elements(locator)
        if len(elements) > 0 and len(elements[0].get_attribute('value')):
            return elements[0].get_attribute('value')
        elif len(elements) > 1:
            return elements[1].get_attribute('value')

        return ''


class T24RadioFieldCtrl(T24FieldCtrl):
    def __init__(self, page, fieldName, elements, tabName):
        T24FieldCtrl.__init__(self, page, fieldName, elements[0])
        self.elements = elements
        self.tabName = tabName

    @staticmethod
    def get_locator(fieldName, tabName):
        return "css=input[name='radio:" + tabName + ":" + fieldName + "']"

    def set_control_text(self, fieldText):
        self.page.log("Choosing a value via a radio button...", "DEBUG", False)
        for elem in self.elements:
            val = elem.get_attribute("value")
            if val == fieldText or self._get_radio_button_text(val) == fieldText:
                elem.click()

    def _get_radio_button_text(self, radioInputValue):
        try:
            locator = "css=input[name='radio:" + self.tabName + ":" + self.fieldName + "'][value='" + radioInputValue + "'] + span"
            elem = self.page.find_element(locator)
            return elem.get_attribute("innerText")
        except:
            return ""

    def get_first_value(self):
        return self.elements[0].get_attribute("value")
