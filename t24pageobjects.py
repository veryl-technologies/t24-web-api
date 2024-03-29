import time

from selenium.common import exceptions

from pageObjects import Page, robot_alias
from robot.libraries.BuiltIn import BuiltIn
from selenium.webdriver.common.keys import Keys

from T24OperationType import T24OperationType
from T24ExecutionContext import T24ExecutionContext
from T24CosObjects import *
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

    def _get_validate_locator(self):
        return "css=img[alt=\"Validate a deal\"]"

    def _split_enquiry_filter(self, filter):
        operators = ["EQ", "LK", "UL", "NE", "GT", "GE", "LT", "LE", "RG", "NR", "CT", "NC", "BW", "EW", "DNBW", "DNEW", "SAID"]

        for op in operators:
            try:
                idx = filter.index(" " + op + " ")
                return filter[:idx], op, filter[idx + len(" " + op + " "):]
            except:
                pass

        raise Exception("Invalid enquiry filter: '" + filter + "'")

    def _evaluate_comparison(self, value, oper, testValue):
        if oper == "EQ":
            return value == testValue

        raise NotImplementedError("'_evaluate_comparison' is not implemented of operator: '" + oper + "'")

    def _enumerate_all_frames(self, frame_name_hint=None):
        frames = []
        self._enumerate_frames_recursively(frames, [], [])

        # performance optimization - we don't need frames that contain children
        frames = [f for f in frames if (len(f.children) == 0)]

        if frame_name_hint:
            # performance optimization - it's more likely to find the item in main frames
            main_frames = [f for f in frames if frame_name_hint in f.name]
            other_frames = [f for f in frames if frame_name_hint not in f.name]
            frames = main_frames + other_frames

        return frames

    def _enumerate_frames_recursively(self, all_frames_found, parent_frames, currently_selected_frames):
        frame_elements = self.find_elements("xpath=.//frame", False, 0)
        child_frames = [CosFrame(f, parent_frames) for f in frame_elements]

        all_frames_found.extend(child_frames)

        for frame in child_frames:
            if self._cos_frame_can_have_children(frame):
                parents_ids = parent_frames[:]
                parents_ids.append(frame.id)

                self._select_frames_by_ids(parents_ids, currently_selected_frames)

                # NOTE: For now we don't use CosDivPane's therefore we will not extract them to improve the performance a bit
                # But if in future they would be needed please uncomment the line bellow:
                #
                #all_frames_found.extend([CosDivPane(p, parents) for p in self.find_elements("xpath=.//div[starts-with(@id,'pane_')]", False, 0)])
                #

                children = self._enumerate_frames_recursively(all_frames_found, parents_ids, currently_selected_frames)
                frame.children = children

        return child_frames

    def _select_frames_by_ids(self, frames, currently_selected_frames):
        try:
            # this logic is to reuse already selected frames, in case of exception - the normal logic would be executed
            remaining_frames = frames[:]
            if len(currently_selected_frames) > 0 and len(currently_selected_frames) <= len(remaining_frames):
                for selected_frame in currently_selected_frames:
                    if selected_frame == remaining_frames[0]:
                        remaining_frames = remaining_frames[1:]
                    else:
                        raise Exception

            else:
                raise Exception

            for f in remaining_frames:
                self.select_frame(f)
        except:
            # the normal logic - deselecting all frames and then selecting the given ones
            # NOTE: only these 3 lines below are enough, but for performance reasons, try to reuse already selected frames
            self.unselect_frame()
            for f in frames:
                self.select_frame(f)

        # set the list with currently selected frames
        if currently_selected_frames is not None:
            del currently_selected_frames[:]
            currently_selected_frames.extend(frames)

    def _cos_frame_can_have_children(self, cos_frame):
        # todo - may be other types also cannot have children. That's a quick performance optimization
        return cos_frame.get_type() != "tab" and cos_frame.get_type() != "menu" and cos_frame.get_type() != "end"

    def _select_cos_frame(self, cos_frame):
        self.unselect_frame()

        for parent in cos_frame.parent_frames:
            self.select_frame(parent)

        self.select_frame(cos_frame.id)

    def _wait_until_page_contains_any_element(self, *selectors):
        waitTimeBetweenRetries = 1
        maxRetries = 10

        while maxRetries > 0:
            maxRetries -= 1
            isLastTry = maxRetries == 0

            for s in selectors:
                isLastSelector = s == selectors[len(selectors) - 1]
                try:
                    waitTime = 0
                    if isLastSelector:
                        waitTime = waitTimeBetweenRetries
                    if self.find_element(s, False, waitTime) is not None:
                        return
                except:
                    if isLastTry and isLastSelector:
                        raise
                    else:
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

    def _find_or_open_app_window(self, version, command, record_id):
        if self._find_and_select_suitable_opened_window(version, command, record_id):
            return

        self._enter_t24_command(version + " " + command + " " + record_id)

    def _find_or_open_enq_window(self, enquiry_name, enquiry_filters):
        if self._find_and_select_suitable_opened_window(enquiry_name, "ENQ", None):
            info = self._get_current_window_info()
            if info["isSelection"]:
                T24EnquiryStartPage().run_enquiry(enquiry_filters)
            return

        self._enter_t24_command("ENQ " + enquiry_name)

        if enquiry_filters:
            T24EnquiryStartPage().run_enquiry(enquiry_filters)

    def _find_tab(self, tab_label):
        xpath = "xpath=.//a[contains(@class,'active-tab')]/span[text()='" + tab_label + "']"  # handles both "active-tab" or "nonactive-tab"

        if self._find_and_select_suitable_opened_window(None, "TAB", xpath):
            return self.find_element(xpath, False, 0)

        return None

    def _find_or_open_menu_window(self, items):
        xpath = self._build_menu_command_xpath_full(items)

        if self._find_and_select_suitable_opened_window(None, "MENU", xpath):
            elements = self.find_elements(xpath, False, 0)
            return elements

        self._make_sure_home_page_is_active()

        self.select_window()

        self.select_frame(self.selectors["menu frame"])

        elements = self.find_elements(xpath, False, 0)
        return elements;

    def _find_and_select_suitable_opened_window(self, version, command, record_id):
        try:
            windowNames = self.get_window_names()

            while len(windowNames) > 1:  # while there are other windows apart from the main
                window_name = windowNames[len(windowNames) - 1]
                self.log("Analyzing if window '" + window_name + "' is suitable for " + command + " command...", "INFO", False)

                self.select_window(window_name)

                if command == "TAB" and self.find_elements(record_id, False, 0):
                    return True

                frame_name_hint = None
                if command == "TAB":
                    frame_name_hint = "main"
                elif command == "ENQ":
                    frame_name_hint = "workarea"

                frames = self._enumerate_all_frames(frame_name_hint)

                if frames:
                    self.log("Analyzing " + str(len(frames)) + " frames ...", "INFO", False)

                    for f in frames:
                        if isinstance(f, CosDivPane):
                            continue

                        self.log("Analyzing if '" + f.name + "' is suitable for " + command + " command...", "INFO", False)

                        self._select_cos_frame(f)

                        self.log("Processing COS frame '" + f.get_type() + "'...", "DEBUG", False)

                        if command == "MENU" and f.get_type() == "menu":
                            if len(self.find_elements(record_id, False, 0)) > 0:
                                return True
                        elif command == "TAB" and f.get_type() == "tab":
                            if len(self.find_elements(record_id, False, 0)) > 0:
                                return True
                        elif self._is_current_window_suitable_for_command(version, command, record_id):
                            return True
                elif self._is_current_window_suitable_for_command(version, command, record_id):
                    return True

                self._get_current_page().close_window()
                windowNames = self.get_window_names()

            self._set_current_page(T24HomePage())
            self.select_window()
            return False

        except:
            e = sys.exc_info()[1]
            self.log("Error finding suitable window: " + str(e), "WARN")
            return False

    def _is_current_window_suitable_for_command(self, version, command, record_id):
        info = self._get_current_window_info()

        if not info:
            return False

        if info['isCommited']:
            return False

        if info is not None and info['command'] == command and info['version'] == version:
            if command == "I" or command == "A" or command == "S":
                if record_id is not None and len(record_id) > 0 and record_id != "F3":
                    # transaction ID must match
                    if info['transactionId'] != record_id:
                        return False

            return True

        return False

    def _get_current_window_info(self):
        try:
            form = self.find_element("xpath=.//form[@id='appreq' or starts-with(@id,'appreq_')]", False, 0)
            version = form.find_element_by_xpath("input[@id='version']").get_attribute("value")
            application = form.find_element_by_xpath("input[@id='application']").get_attribute("value")

            if T24RecordInputPage().is_txn_complete_displayed_no_wait():
                id = T24RecordInputPage().get_id_from_completed_transaction()
                return dict(command = "", version = application + version, transactionId = id, isCommited = True)

            id = T24TransactionPage().get_transaction_id()

            if T24TransactionPage().commit_btn_enabled():
                return dict(command = "I", version = application + version, transactionId = id, isCommited = False)
            elif T24TransactionPage().autorize_btn_enabled():
                return dict(command = "A", version = application + version, transactionId = id, isCommited = False)
            elif T24TransactionPage().validate_btn_enabled():
                return dict(command = "I", version = application + version, transactionId = id, isCommited = False)
            else:
                return dict(command = "S", version = application + version, transactionId = id, isCommited = False)
        except:
            try:
                self.find_element("xpath=.//form[starts-with(@id,'enquiryData')]", False, 0)
                form = self.find_element("xpath=.//form[@id='enquiry' or starts-with(@id,'enquiry_')]", False, 0)
                version = form.find_element_by_xpath("input[@name='version']").get_attribute("value")
                return dict(command = "ENQ", version = version, isSelection = False, transactionId = '', isCommited = False)
            except:
                try:
                    form = self.find_element("xpath=.//form[@id='enqsel']", False, 0)
                    enqname = form.find_element_by_xpath("input[@id='enqname']").get_attribute("value")
                    return dict(command = "ENQ", version = enqname, isSelection = True, transactionId = '', isCommited = False)
                except:
                    pass

        return None

    # Input a T24 command and simulate pressing Enter
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
            self._find_or_open_enq_window(enquiry_name, enquiry_filters)
            self._set_current_page(T24EnquiryResultPage())
            return self._get_current_page()

    # Executed T24 tab command
    @robot_alias("run_t24_tab_command")
    def run_t24_tab_command(self, tab_items):
        self._add_operation(T24OperationType.Tab)

        self.log("Executing tab command '" + tab_items + "' ...", "INFO", False)

        items = [item.strip() for item in tab_items.split('>')]

        for item in items:
            element = self._find_tab(item)
            if element is None:
                raise exceptions.NoSuchElementException("Unable to find tab '" + item + "'")

            element = element.find_element_by_xpath("..")  # we need parent 'a' element
            if element.get_attribute("class") != "active-tab":  # else "nonactive-tab"
                element.click()

        self._take_page_screenshot("VERBOSE")

        self._set_current_page(T24Page())
        return self._get_current_page()


    # Executed T24 menu command
    @robot_alias("run_t24_menu_command")
    def run_t24_menu_command(self, menu_items):
        self._add_operation(T24OperationType.Menu)

        self.log("Executing menu command '" + menu_items + "' ...", "INFO", False)

        items = [item.strip() for item in menu_items.split('>')]

        elements = self._find_or_open_menu_window(items)

        if len(elements) == 0:
            raise exceptions.NoSuchElementException("Unable to find menu path '" + menu_items + "'")
        elif len(elements) > 1:
            # raise exceptions.NoSuchElementException("More than one menu items with given path found: '" + menu_items + "'")
            # for now we will result the first match
            pass

        menu_element = elements[0]

        # find all of the parent nodes
        parent = menu_element.find_element_by_xpath("..")
        parents = []
        while True:
            parent = parent.find_element_by_xpath("../..")
            if parent.tag_name != u'li':
                break
            parents.insert(0, parent)

        # expand all of the parent nodes
        for p in parents:
            e = p.find_element_by_xpath("span[@onclick='ProcessMouseClick(event)']/img")
            if e.get_attribute("src").find("menu_down") > 0:
                e.click()

        # click on the end element
        menu_element.click()

        # todo - set current page should be done here or sth else?
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
            if i == len(items):  # last item
                result += "/li/a[contains(@onclick, '" + item + "')]"
            else:
                result += "/li[@class='clsHasKids']/span[text()='" + item + "']/following-sibling::ul[1]"

        return result

    # Opens a T24 input page
    @robot_alias("open_input_page_new_record")
    def open_input_page_new_record(self, version):
        self._add_operation(T24OperationType.StartInputNewRecord)
        self._find_or_open_app_window(version, "I", "F3")

        self._set_current_page(T24RecordInputPage(version))
        return self._get_current_page()

    @robot_alias("open_edit_page")
    def open_edit_page(self, version, record_id):
        self._add_operation(T24OperationType.StertEditExitingRecord)

        record_id = self.evaluate_value(record_id)
        self._find_or_open_app_window(version, "I", record_id)

        self._set_current_page(T24RecordInputPage(version, record_id))
        return self._get_current_page()

    @robot_alias("open_authorize_page")
    def open_authorize_page(self, version, record_id):
        self._add_operation(T24OperationType.StartAuthorizingRecord)

        record_id = self.evaluate_value(record_id)
        self._find_or_open_app_window(version, "A", record_id)

        self._set_current_page(T24RecordInputPage(version, record_id))
        return self._get_current_page()

    @robot_alias("open_see_page")
    def open_see_page(self, version, record_id):
        self._add_operation(T24OperationType.SeeRecord)

        record_id = self.evaluate_value(record_id)

        self._find_or_open_app_window(version, "S", record_id)

        self._set_current_page(T24RecordSeePage(version, record_id))
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
        return self.run_enquiry(None)

    def run_enquiry(self, enquiry_filters):
        self.wait_until_page_contains_element(self.selectors["clear selection link"])
        self.wait_until_page_contains_element(self.selectors["find button"])

        self.click_element(self.selectors["clear selection link"])

        if enquiry_filters is not None:
            self._set_filters(enquiry_filters)

        self.click_element(self.selectors["find button"])

        self._take_page_screenshot("VERBOSE")

        self._set_current_page(T24EnquiryResultPage())
        return self._get_current_page()

    def _set_filters(self, filters):
        for f in filters:
            field, oper, value = self._split_enquiry_filter(f)

            try:
                element = self.find_element('xpath=.//input[@type="hidden" and @value="' + field + '"]', False, 0)
                id = element.get_attribute("id")
            except:
                # if field name not found, probably this would be used as post filter
                continue

            indexes = id[id.index(":"):]

            if not self.find_elements("xpath=//input[@type='hidden' and @name='operand" + indexes + "' and @value='" + oper + "']", False, 0):
                element_ops = self.find_elements("xpath=//select[@name='operand" + indexes + "']/option[@value='" + oper + "']", False, 0)
                if element_ops:
                    element_ops[0].click()

            element_val = self.find_element("xpath=//input[@type='text' and @id='value" + indexes + "']")
            element_val.send_keys(value)

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
        "enquiry data table": "xpath=.//table[@id='enquiryResponseData']"
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
    def get_values_from_enquiry_result(self, column_indexes, enquiry_constraints):
        self.select_window("self")
        self.wait_until_page_contains_element(self.selectors["refresh button"])

        #if self._page_contains("No records matched the selection criteria"):
        #    return "" # too slow

        #if not self.wait_until_page_contains_element(self.selectors["first text column in grid"], 5):
        #   return ""  # doesn't work

        row_id = self._find_first_matching_enquiry_row_id(enquiry_constraints)
        if row_id is None:
            return []

        res = []
        for c in column_indexes:
            index = int(c) + 1
            val = self._get_text("css=#" + row_id + " > td:nth-child(" + str(index) + ")")  # TODO error handling (throw better error)
            res.append(val)

        return res

    # Executes enquiry action on first matching row
    @robot_alias("execute_enquiry_action")
    def execute_enquiry_action(self, enquiry_constraints, action):
        self.select_window("self")
        self._wait_until_page_contains_any_element(self.selectors["refresh button"], self.selectors["enquiry data table"])

        self._take_page_screenshot("INFO")

        row_id = self._find_first_matching_enquiry_row_id(enquiry_constraints)
        if row_id is None:
            return False, "No matching enquiry rows found"

        try:
            if unicode(str(action), 'utf-8').isnumeric():
                element = self.find_element("css=#" + row_id + " > td:nth-child(" + str(action) + ") > a", False, 0)
            else:
                element = self.find_element("xpath=.//tr[@id='" + row_id + "']/td/a[@title='" + action + "']", False, 0)
            element.click()
            time.sleep(2)  # TODO why sleep? N.Z. There are re-loads of frames, but not quite sure whether this is needed at all
        except:
            return False, "Unable to find action element '" + action + "' on enquiry result row: " + row_id

        return True, ""

    def _find_first_matching_enquiry_row_id(self, enquiry_constraints):
        if enquiry_constraints is None:
            return self._find_enq_row_id_by_index(1)

        enquiry_constraints_by_idx = []

        header = self._enumerate_enquiry_header()
        for filter in enquiry_constraints:
            field, oper, value = self._split_enquiry_filter(filter)
            header_item = [tup for tup in header if tup[1] == field]
            if len(header_item) > 0:
                idx = header_item[0][0]
                enquiry_constraints_by_idx.append( (idx, oper, value) )

        # todo if there are pages and we are not able to find the row we have to move to the next page - all logic bellow should be moved to method and from here we have to switch pages until match

        # expand expandable rows that might match the constraints
        has_expandable_rows = False
        for e in self.find_elements("xpath=.//tr/td[1]/a[starts-with(@onclick,'javascript:expandrow(')]", False, 0):
            # expandable row id's
            row_id = e.find_element_by_xpath("../..").get_attribute("id");

            for c in enquiry_constraints_by_idx:
                val = self._get_text("css=#" + row_id + " > td:nth-child(" + str(c[0]) + ")")
                if self._evaluate_comparison(val, c[1], c[2]):
                    e.click()
                    has_expandable_rows = True
                    break

        # iterate through all of the ros to find a match
        last_val_of_col = {}
        for row_idx in range(1, 100):
            row_id = self._find_enq_row_id_by_index(row_idx)
            if row_id is None:
                break  # no more rows

            matches = True
            for c in enquiry_constraints_by_idx:
                val = self._get_text("css=#" + row_id + " > td:nth-child(" + str(c[0]) + ")")
                if has_expandable_rows:
                    if val is not None and len(val) > 0:
                        last_val_of_col[c[0]] = val
                    elif last_val_of_col.has_key(c[0]):
                        val = last_val_of_col[c[0]]

                if not self._evaluate_comparison(val, c[1], c[2]):   # .find_element_by_xpath("a/img[@alt='Expand group']")
                    matches = False
                    break

            if matches:
                return row_id

        return None

    def _find_enq_row_id_by_index(self, row_idx):
        row_id = "r" + str(row_idx)
        try:
            row = self.find_element("xpath=.//tr[@id='" + row_id + "' or starts-with(@id, '" + row_id + "_')]")
            row_id = row.get_attribute('id')
            return row_id
        except:
            None

    def _enumerate_enquiry_header(self):
        result = []
        for i in range(1, 200, 1):
            try:
                id = 'columnHeaderText' + str(i)
                xpath = "xpath=.//th[@id='" + id + "' or starts-with(@id,'" + id + "_')]"
                elem = self.find_element(xpath, False, 0)
                result.append((i, elem.text))
            except:
                break

        return result


class T24TransactionPage(T24Page):

    version = None
    transaction_id = None

    def __init__(self, version = None, transaction_id = None):
        T24Page.__init__(self)

        self.version = version
        self.transaction_id = transaction_id

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

    def validate_btn_enabled(self):
        try:
            btn = self.find_element("xpath=.//img[@title='Validate a deal']")
            return "_dis.gif" not in btn.get_attribute("src")
        except:
            return False


    def _is_AA(self):
        return self.version is not None and (self.version == "AA.ARRANGEMENT.ACTIVITY" or self.version.startswith("AA.ARRANGEMENT.ACTIVITY,"))

    def _split_AA_property_name(self, field_name):
        try:
            if self._is_AA():
                start_idx = field_name.index("[")
                if start_idx == 0:
                    end_idx = field_name.index("]")
                    if end_idx > 1 and end_idx < (len(field_name) - 1):
                        return field_name[start_idx + 1 : end_idx], field_name[end_idx + 1:]
        except:
            pass

        return None, field_name


class T24RecordSeePage(T24TransactionPage):
    """ Models the T24 Record See Page"""

    # Allows us to call by proper name
    name = "T24 Record Page"

    # Probably not necessary
    uri = "/BrowserWeb/servlet/BrowserServlet#1"

    def __init__(self, version = None, transaction_id = None):
        T24TransactionPage.__init__(self, version, transaction_id)

    # Gets a text value from the underlying T24 field name
    @robot_alias("get_T24_field_value")
    def get_T24_field_value(self, fieldName):
        if fieldName == "ID" or fieldName == "@ID":
            fieldValue = self._get_value("xpath=.//input[@id='transactionId' and preceding-sibling::span]")
        else:
            fieldValue = self._get_T24_field_value_among_many(fieldName)
        self.log("Retrieved value for field '" + fieldName + "' is '" + fieldValue + "'", "INFO", False)
        return fieldValue

    def _get_T24_field_value_among_many(self, fieldName):
        aaProperty, fieldName = self._split_AA_property_name(fieldName)

        parts = fieldName.rpartition(':')  # we expect AAA:1, AAA:2 for multivalues or just AAA for normal fields
        if parts[1] == ':':
            mainFieldName = parts[0]
            indexPart = parts[2]
        else:
            mainFieldName = fieldName
            indexPart = ''

        locator = self._get_get_T24_field_value_locator(aaProperty, mainFieldName)

        isSimpleField = not indexPart.isdigit()  # simple fields should have a single element matched in the HTML
        elements = self._element_find(locator, isSimpleField, True)
        if elements is None:
            raise ValueError("Could not find elements for field '" + mainFieldName + "'.")

        if isSimpleField:
            return elements.text
        else:
            index = int(indexPart) - 1
            if index < len(elements):
                return elements[index].text
            else:
                raise ValueError("Could not find element at index " + indexPart + " for field '" + mainFieldName + "'.")

    def _get_get_T24_field_value_locator(self, aaProperty, mainFieldName):
        is_ver_14_or_above = True   # Config.get_t24_version() >= 14

        locator_parent = ""
        if aaProperty is not None and len(aaProperty) > 0:
            locator_parent = "fieldset/a[@name='legend_" + aaProperty + "']/../div//"

        if is_ver_14_or_above:
            return "xpath=.//" + locator_parent + "*[@id='fieldCaption:" + mainFieldName + "']/../../..//*[3]//*"
        else:
            return "xpath=.//" + locator_parent + "*[@id='fieldCaption:" + mainFieldName + "']/../..//*[3]//*"

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

    currentTabName = ''

    _last_selected_property = None

    def __init__(self, version = None, transaction_id = None):
        T24TransactionPage.__init__(self, version, transaction_id)

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
        aaProperty, fieldName = self._split_AA_property_name(fieldName)
        self._select_AA_property_if_valid(aaProperty)

        fieldCtrl = self._get_field_ctrl(aaProperty, fieldName)
        if not fieldCtrl:
            raise exceptions.NoSuchElementException("Unable to find control for '" + fieldName + "' field name")

        self.log("Checking if the field is in another tab...", "DEBUG", False)
        fieldTabName = self._select_field_tab(aaProperty, fieldCtrl)
        if(fieldTabName != self.currentTabName):
            self.log("The current tab is '" + fieldTabName + "'.", "INFO", False)
            self.currentTabName = fieldTabName

        if fieldText.upper().startswith("?SELECT-FIRST"):
            fieldText = fieldCtrl.get_first_value()
        else:
            fieldText = self.evaluate_value(fieldText)

        self.log("Setting value '" + fieldText + "' to field '" + fieldName + "'", "INFO", False)

        fieldCtrl.set_text(fieldText)

        return self

    def _select_AA_property_if_valid(self, aaProperty):
        if aaProperty is not None and self._last_selected_property != aaProperty:
            if self._last_selected_property is None:
                self.click_validate_button()    # do validate before we start input properties
            propertyLine = self.find_element("xpath=.//a[@href='#legend_" + aaProperty + "']", False, 0)
            propertyLine.click()

        self._last_selected_property = aaProperty

    def _get_field_ctrl(self, aaProperty, fieldName):
        waitTimeBetweenRetries = 1
        maxRetries = 10

        while maxRetries > 0:
            maxRetries -= 1
            hiddenFieldTabName = None
            try:
                elements = self.find_elements(T24InputFieldCtrl.get_locator(aaProperty, fieldName), False, 0)
                if elements:
                    if len(elements) == 1:
                        element = elements[0]
                    else:
                        self.log(str(len(elements)) + " elements matching field '" + fieldName + "'!", "INFO", False)
                        element = elements[0]  # choose first, though maybe in the current tab is better (if any)

                if element and element.get_attribute("type") != u'hidden':
                    return T24InputFieldCtrl(self, aaProperty, fieldName, element)
                elif element.get_attribute("type") == u'hidden':
                    hiddenFieldTabName = element.get_attribute("tabname")
            except:
                pass

            try:
                element = self.find_elements(T24SelectFieldCtrl.get_locator(aaProperty, fieldName), False, 0)[0]
                if element:
                    return T24SelectFieldCtrl(self, aaProperty, fieldName, element)
            except:
                pass

            try:
                elements = self.find_elements(T24RadioFieldCtrl.get_locator(aaProperty, fieldName, hiddenFieldTabName), False, 0)
                if elements:
                    return T24RadioFieldCtrl(self, aaProperty, fieldName, elements, hiddenFieldTabName)
            except:
                pass

            try:
                elements = self.find_elements(T24TextAreaFieldCtrl.get_locator(aaProperty, fieldName), False, waitTimeBetweenRetries)
                if elements and len(elements) == 1:
                    return T24TextAreaFieldCtrl(self, aaProperty, fieldName, elements[0])
            except:
                pass

        return None

    def _select_field_tab(self, aaProperty, fieldCtrl):
        try:
            tabName = fieldCtrl.element.get_attribute("tabname")
            if tabName and tabName != self.currentTabName and tabName != "mainTab":
                if tabName != 'tab1' or self.currentTabName:  # assume we start in 'tab1' and only go back if necessary
                    onclickVal = "javascript:changetab('" + tabName + "')"

                    locator_parent = ""
                    if aaProperty is not None and len(aaProperty) > 0:
                        locator_parent = "fieldset/a[@name='legend_" + aaProperty + "']/../div//"

                    tabElement = self.find_element('xpath=.//' + locator_parent + 'a[@onclick="' + onclickVal + '"]')
                    if tabElement.get_attribute("class") == "nonactive-tab":
                        self.log("Activating tab '" + tabName + "'...", "INFO", False)
                        tabElement.click()
            return tabName
        except:
            pass  # not essential action
            return None

    # Clicks the Commit Button when dealing with T24 transactions
    def click_commit_button(self):
        self._take_page_screenshot("VERBOSE")
        self.wait_until_page_contains_element(self._get_commit_locator(), 3)
        self.click_element(self._get_commit_locator())
        return self

    def click_validate_button(self):
        self.wait_until_page_contains_element(self._get_validate_locator(), 3)
        self.click_element(self._get_validate_locator())
        self._take_page_screenshot("VERBOSE")
        return self

    def is_accept_overrides_displayed_no_wait(self):
        try:
            if self.find_element("xpath=.//*[contains(text(),'Accept Overrides')]", False, 0) is not None:
                return True
            return False
        except:
            return False

    # Clicks the Accept Overrides link (if available) when dealing with T24 transactions
    def click_accept_overrides(self):
        try:
            start = datetime.now()
            self.log("Waiting for Accept Overrides link to appear... ", "DEBUG", False)
            self.wait_until_page_contains_element("link=Accept Overrides", 10)
            self.log("Accept Overrides link found in " + str(int((datetime.now() - start).total_seconds())) +
                     " seconds", "DEBUG", False)

            self._take_page_screenshot("VERBOSE")

            self.click_link("link=Accept Overrides")

            # The fastest way to search for completing of operation is just to look in the page source
            # We could also use self.wait_until_page_does_not_contain or wait_until_page_does_not_contain_element,
            # but need to temporarily reduce 'selenium_implicit_wait' from 10 to something quite smaller (e.g. 0.1)
            start = datetime.now()
            self.log("Waiting for completion of accepting overrides...", "DEBUG", False)
            err = self._wait_until_page_source_does_not_contain("Accept Overrides", 10)
            if err is None:
                self.log("Completed processing of 'Accept Overrides' in " +
                         str(int((datetime.now() - start).total_seconds())) + " seconds", "DEBUG", False)
            else:
                self.log(err, "WARN", False)
        except:
            e = sys.exc_info()[1]
            self.log(str(e), "WARN", False)
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

    def is_receive_documents_pending_no_wait(self):
        try:
            if self.find_elements("xpath=//select[starts-with(@id,'warningChooser:Have you received')]", False, 0):
                return True
            return False
        except:
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

    def get_fields_with_errors_no_wait(self):
        fields = []
        for span in self.find_elements("xpath=.//*[@id='errors']/tbody/*/*/a/span", False, 0):
            fields.append(str(span.text))

        if fields:
            self.log("Fields with errors:" + str(fields), "INFO", True)

        return fields
	

    # Clicks the Authorize Button When Dealing with T24 Transactions
    def click_authorize_button(self):
        self.click_element(self._get_authorize_locator())
        return self


class T24FieldCtrl:
    def __init__(self, page, aaProperty, fieldName, element):
        self.page = page
        self.aaProperty = aaProperty
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
            # wait for a reload (necessary after setting hot fields)
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
            self.element.send_keys(Keys.TAB)

    @staticmethod
    def _get_aa_property_locator_parent(aaProperty):
        if aaProperty is None or len(aaProperty) == 0:
            return ""

        #'css=fieldset>a[name="legend_Account"]+legend+div input[name="fieldName:SHORT.TITLE"]'
        return 'fieldset>a[name="legend_' + aaProperty + '"]+legend+div '


class T24InputFieldCtrl(T24FieldCtrl):
    def __init__(self, page, aaProperty, fieldName, element):
        T24FieldCtrl.__init__(self, page, aaProperty, fieldName, element)

    @staticmethod
    def get_locator(aaProperty, fieldName):
        return "css=" + T24FieldCtrl._get_aa_property_locator_parent(aaProperty) + "input[name='fieldName:" + fieldName + "']"

    def set_control_text(self, fieldText):
        self.page.log("Setting a value to a text field...", "DEBUG", False)
        self.element.clear()
        self.element.send_keys(fieldText)

    def get_first_value(self):
        return ''  # TODO maybe it's good to return the text of the input field, although it would be empty

class T24TextAreaFieldCtrl(T24InputFieldCtrl):
    def __init__(self, page, aaProperty, fieldName, element):
        T24InputFieldCtrl.__init__(self, page, aaProperty, fieldName, element)

    @staticmethod
    def get_locator(aaProperty, fieldName):
        return "css=" + T24FieldCtrl._get_aa_property_locator_parent(aaProperty) + "textArea[name='fieldName:" + fieldName + "']"

class T24SelectFieldCtrl(T24FieldCtrl):
    def __init__(self, page, aaProperty, fieldName, element):
        T24FieldCtrl.__init__(self, page, aaProperty, fieldName, element)

    @staticmethod
    def get_locator(aaProperty, fieldName):
        return "css=" + T24FieldCtrl._get_aa_property_locator_parent(aaProperty) + "select[name='fieldName:" + fieldName + "']"

    def set_control_text(self, fieldText):
        self.page.log("Selecting a value from a list...", "DEBUG", False)
        self.page.select_from_list(self.get_locator(self.aaProperty, self.fieldName), fieldText)

    def get_first_value(self):
        locator = self.get_locator(self.aaProperty, self.fieldName) + " option"
        elements = self.page.find_elements(locator)
        if len(elements) > 0 and len(elements[0].get_attribute('value')):
            return elements[0].get_attribute('value')
        elif len(elements) > 1:
            return elements[1].get_attribute('value')

        return ''


class T24RadioFieldCtrl(T24FieldCtrl):
    def __init__(self, page, aaProperty, fieldName, elements, tabName):
        T24FieldCtrl.__init__(self, page, aaProperty, fieldName, elements[0])
        self.elements = elements
        self.tabName = tabName

    @staticmethod
    def get_locator(aaProperty, fieldName, tabName):
        return "css=" + T24FieldCtrl._get_aa_property_locator_parent(aaProperty) + "input[name='radio:" + tabName + ":" + fieldName + "']"

    def set_control_text(self, fieldText):
        self.page.log("Choosing a value via a radio button...", "DEBUG", False)
        for elem in self.elements:
            val = elem.get_attribute("value")
            if val == fieldText or self._get_radio_button_text(val) == fieldText:
                elem.click()

    def _get_radio_button_text(self, radioInputValue):
        try:
            locator = "css=" + T24FieldCtrl._get_aa_property_locator_parent(self.aaProperty) + "input[name='radio:" + self.tabName + ":" + self.fieldName + "'][value='" + radioInputValue + "'] + span"
            elem = self.page.find_element(locator)
            return elem.get_attribute("innerText")
        except:
            return ""

    def get_first_value(self):
        return self.elements[0].get_attribute("value")
