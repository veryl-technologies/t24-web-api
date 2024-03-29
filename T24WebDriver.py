
from t24pageobjects import T24LoginPage
from T24ExecutionContext import T24ExecutionContext
from robot.libraries.BuiltIn import BuiltIn
from robot.libraries import Dialogs
from utils import VariablesExporter
from decimal import Decimal
import fnmatch


class T24WebDriver:
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'
    __version__ = '0.1'

    login_page = None
    login_user_type = None
    home_page = None
    last_tx_id = None
    last_input_id = None
    last_authorize_id = None

    def _log_info(self, message):
        BuiltIn().log(message, "INFO")

    def _log_debug(self, message):
        BuiltIn().log(message, "DEBUG")

    def t24_login(self, user_type="INPUTTER"):
        """
        Enters login credential in the T24 login page for the specified type of user.
        The default user type is INPUTTER
        """

        if self.login_user_type == user_type:
            self._log_info('Already logged in as ' + user_type)
            return

        self._log_info('Trying to login as ' + user_type)

        var_user_name = "${LOGIN_" + user_type + "}"
        user = BuiltIn().get_variable_value(var_user_name)
        if not user:
            BuiltIn().fail("Please specify a user name in a variable " + var_user_name)

        var_pass = "${PASSWORD_" + user_type + "}"
        password = BuiltIn().get_variable_value(var_pass)
        if not password:
            BuiltIn().fail("Please specify a password in a variable " + var_pass)

        self.t24_logoff()

        if not self.login_page:
            self.login_page = T24LoginPage()
            self.login_page.open()
            # For demos, sometimes it is nice to to start in maximized mode. Uncomment line below when necessary:
            # self.login_page.maximize_browser_window()

        self.home_page = self.login_page.enter_T24_credentials(user, password)
        self.login_user_type = user_type
        self.login_page = None  # After a successful login, the login page gets actually closed, so don't store it

    def _make_sure_is_logged_in(self, user_type=None):
        if not self.login_user_type:
            self.t24_login(user_type or "INPUTTER")
        elif user_type and self.login_user_type != user_type:
            self._log_debug('The current user ' + self.login_user_type + ' needs to be changed with ' + user_type)
            self.t24_login(user_type)

    def t24_logoff(self):
        """
        If there is a currently logged-in user in T24, clicks the 'Sign Off' button and reopens the T24 login page
        """
        if self.home_page:
            self.login_page = self.home_page.sign_off()
            self.home_page = None

    def execute_t24_menu_command(self, menu_items):
        """
        Clicks on a T24 menu item ('>' is used as the menu hierarchy delimiter)
        Example: 'User Menu > Customer > Individual Customer'
        Note that starting items can be omitted.
        For example: 'Customer > Individual Customer' or 'Individual Customer' will both navigate to the same target
        """

        self._make_sure_is_logged_in()

        self.home_page.run_t24_menu_command(menu_items)

    def execute_t24_tab_command(self, tab_items):
        """
        Clicks on a T24 tab ('>' is used as the tab hierarchy delimiter)
        Example: 'Till Admin > Exchange Rates'
        """

        self._make_sure_is_logged_in()

        self.home_page.run_t24_tab_command(tab_items)

    def create_or_amend_t24_record(self, app_version, record_id, record_field_values, overrides_handling=None, error_handling=None, post_verification=None):
        """
        Creates a T24 record with the specified fields if 'record_id' is not specified, otherwise amends an existing record
        """
        self._make_sure_is_logged_in()

        if record_id and not record_id.startswith(">>"):
            input_page = self.home_page.open_edit_page(app_version, record_id)
        else:
            input_page = self.home_page.open_input_page_new_record(app_version)

        for field_and_value in record_field_values:
            pair = field_and_value.split("=")
            input_page.set_T24_field_value(pair[0], pair[1])

        input_page.click_commit_button()

        try:
            if not self._validate_errors(input_page, error_handling):
                if overrides_handling != "Fail" and not input_page.is_txn_complete_displayed_no_wait():
                    if input_page.is_receive_documents_pending_no_wait():
                        input_page.receive_documents()
                    if input_page.is_accept_overrides_displayed_no_wait():
                        input_page.click_accept_overrides()
                    if not input_page.is_txn_complete_displayed_no_wait():
                        input_page.click_commit_button()

                self.last_input_id = input_page.get_id_from_completed_transaction()
                self.last_tx_id = self.last_input_id
                BuiltIn().set_test_variable("${TX_ID}", self.last_tx_id)
                if record_id.startswith(">>"):
                    self._set_variable(record_id[2:].strip(), self.last_tx_id)
        finally:
            input_page.close_window()
            self._make_home_page_default()

    def _set_variable(self, name, value):
        if name.lower().startswith("g_") or name.lower().startswith("global_"):
            BuiltIn().set_global_variable("${" + name + "}", value)
            VariablesExporter().add_global(name, value)
        elif name.lower().startswith("m_") or name.lower().startswith("module_"):
            BuiltIn().set_global_variable("${" + name + "}", value)
            VariablesExporter().add_module(name, value)
        else:
            BuiltIn().set_test_variable("${" + name + "}", value)

    def _make_home_page_default(self):
        T24ExecutionContext.Instance().set_current_page(self.home_page)

    def authorize_t24_record(self, app_version, record_id, extra_authorizations=0):
        """
        Authorizes a T24 record by logging in in T24 as AUTHORISER user
        """
        self._make_sure_is_logged_in("AUTHORISER")
        authorize_page = self.home_page.open_authorize_page(app_version, record_id)
        authorize_page.click_authorize_button()
        self.last_authorize_id = authorize_page.get_id_from_completed_transaction()
        self.last_tx_id = self.last_authorize_id
        BuiltIn().set_test_variable("${TX_ID}", self.last_tx_id)
        authorize_page.close_window()
        self._make_home_page_default()

    def check_t24_record(self, app, record_id, validations):
        """
        Retrieves the T24 record by its ID and verifies its field values against some predefined criteria
        """
        if not validations:
            self._log_info('No actions specified after records retrieval. Would try to read @ID...')
            validations = ['@ID >> dummy']  # empty SEE should probably check for record existence.
            # TODO optimize to check for 'RECORD NOT FOUND' instead of waiting for failed XPATH

        # parse the rules in 3 arrays
        validation_fields, validation_operators, validation_values = self._parse_validation_rules(validations)

        # Open the records page for retrieving values
        self._make_sure_is_logged_in()
        see_page = self.home_page.open_see_page(app, record_id)

        # check for expected & actual result
        errors = []
        for idx, field in enumerate(validation_fields):
            op = validation_operators[idx]
            expected_value = validation_values[idx]

            if field == '${TX_ID}':
                actual_value = self.last_tx_id
            else:
                actual_value = see_page.get_T24_field_value(field)

            if op == ">>":
                self._set_variable(expected_value.strip(), actual_value)
            else:
                self._validate_field_value(field, op, expected_value, actual_value, errors)

        # go back to home screen
        see_page.close_window()
        self._make_home_page_default()

        # fail if there are any validation errors
        if errors:
            BuiltIn().fail("\n".join(errors))

    @staticmethod
    def _get_operator_friendly_name(op):
        if op == "EQ":
            return "equals"
        elif op == "LK":
            return "matches"
        elif op == "CT":
            return "contains"
        elif op == "BW":
            return "begins with"
        elif op == "EW":
            return "ends with"
        else:
            return op

    def _parse_validation_rules(self, validations):
        validation_fields = []
        validation_operators = []
        validation_values = []

        # parse the values
        for v in validations:
            fld, op, val = self._parse_validation_rule(v)
            validation_fields.append(fld)
            validation_operators.append(op)
            validation_values.append(self._process_validation_value(val))

        return validation_fields, validation_operators, validation_values

    def _process_validation_value(self, val):
        if val.startswith("?"):
            val = self._evaluate_expression(val[1:])
        return val

    def _evaluate_expression(self, expr):
        # NOTE For a safer alternative to eval() see ast.literal_eval()
        # http://stackoverflow.com/questions/15197673/using-pythons-eval-vs-ast-literal-eval
        self._log_info("Evaluating expression '" + expr + "' ...")
        res = str(eval(expr))  # syntax for imports is eval("__import__('datetime').datetime.now()")
        self._log_info("The result of expression evaluation is '" + res + "'")
        return res

    def _parse_validation_rule(self, validation_rule):
        validation_rule = self._normalize_filter(validation_rule)

        for op in ["EQ", "LK", "CT", "BW", "EW", ">>"]:
            op_spaces = " " + op + " "
            if op_spaces in validation_rule:
                return self._get_validation_rule_parts(validation_rule, op_spaces)

        raise NotImplementedError("Unexpected text for filter/validation: '" + validation_rule + "'")

    def _normalize_filter(self, param):
        # Currently in RIDE we use filters like =EQ:= , but the logic expects just EQ
        if ":=" in param:
            return param.replace(":=", "", 1).replace(" :", " ", 1)
        return param

    def _get_validation_rule_parts(self, validation_rule, operator):
        items = validation_rule.split(operator, 1)
        return items[0], operator.strip(), items[1]

    def execute_T24_enquiry(self, enquiry, enquiry_constraints, action, action_parameters):
        """
        Executes a T24 enquiry with the specified criteria and processes the first found result
        either by fetching and optionally verifying its values (via action "Check Result")
        or by applying a custom like clicking on the corresponding link/button/menu item
        """

        # prepare the enquiry constraints
        if enquiry_constraints:
            for i, ec in enumerate(enquiry_constraints):
                enquiry_constraints[i] = self._normalize_filter(ec)

        # run the enquiry
        self._make_sure_is_logged_in()
        enq_res_page = self.home_page.open_t24_enquiry(enquiry, enquiry_constraints)

        if not action or not action.strip() or action == u"Check Result":
            # parse the rules in 3 arrays
            enq_res_columns, validation_operators, validation_values = self._parse_validation_rules(action_parameters)

            # read the data from the enquiry result
            values = enq_res_page.get_values_from_enquiry_result(enq_res_columns, enquiry_constraints)
            if not values:
                raise Exception('No matching enquiry rows found')

            # need to save data into RF variables
            for i, c in enumerate(enq_res_columns):
                if validation_operators[i] == ">>":
                    self._set_variable(validation_values[i].strip(), values[i])

            # verify the results
            errors = []
            for idx, column in enumerate(enq_res_columns):
                op = validation_operators[idx]
                if op != ">>":
                    self._validate_field_value(column, op, validation_values[idx], values[idx], errors)

            # fail if there are any validation errors
            if errors:
                BuiltIn().fail("\n".join(errors))

            # go back to home screen
            enq_res_page.close_window()
            self._make_home_page_default()

        else:
            is_success, err_msg = enq_res_page.execute_enquiry_action(enquiry_constraints, action)
            if not is_success:
                raise Exception(err_msg)

    def _validate_field_value(self, column, op, expected_value, actual_value, errors):
        if op == "EQ" and expected_value != actual_value and not self._are_equal_as_numbers(expected_value, actual_value):
            errors.append(
                "Field '" + column + "' has expected value '" + expected_value + "' but the actual value is '" + actual_value + "'")
        elif op == "LK" and not self._is_match_LK(actual_value, expected_value):
            errors.append(
                "Field '" + column + "' is expected to match pattern '" + expected_value + "' but the actual value '" + actual_value + "' is not a match")
        elif op == "CT" and expected_value not in actual_value:
            errors.append(
                "Field '" + column + "' is expected to contain value '" + expected_value + "' but it is not a part of the actual value '" + actual_value + "'")
        elif op == "BW" and not actual_value.startswith(expected_value):
            errors.append("Field '" + column + "' is expected to start with '" + expected_value + "' but the actual value is '" + actual_value + "'")
        elif op == "EW" and not actual_value.endswith(expected_value):
            errors.append("Field '" + column + "' is expected to end with '" + expected_value + "' but the actual value is '" + actual_value + "'")
        else:
            self._log_info("For field '" + column + "' verified that the actual value '" + actual_value + "' " +
                           self._get_operator_friendly_name(op) + " the expected value '" + expected_value + "'")

    @staticmethod
    def _are_equal_as_numbers(expected_value, actual_value):
        try:
            return T24WebDriver._str_to_decimal(expected_value) == T24WebDriver._str_to_decimal(actual_value)
        except:
            return False

    @staticmethod
    def _str_to_decimal(val):
        if "," in val and '.' in val:
            val = val.replace(",", "")

        if "," in val and '.' not in val:
            val = val.replace(",", ".")

        return Decimal(val)

    def _is_match_LK(self, value, pattern):
        return fnmatch.fnmatchcase(value, pattern.replace("...", "*"))

    def validate_t24_record(self, app_version, record_id, record_field_values, overrides_handling=None, error_handling=None):
        """
        Validates if a T24 record with the specified fields can be created or amended
        """
        self._make_sure_is_logged_in()

        if record_id and not record_id.startswith(">>"):
            input_page = self.home_page.open_edit_page(app_version, record_id)
        else:
            input_page = self.home_page.open_input_page_new_record(app_version)

        try:
            for field_and_value in record_field_values:
                pair = field_and_value.split("=")
                input_page.set_T24_field_value(pair[0], pair[1])

            input_page.click_validate_button()
            self._validate_errors(input_page, error_handling)
        finally:
            input_page.close_window()
            self._make_home_page_default()

    def _validate_errors(self, input_page, error_handling):
        problematic_fields = input_page.get_fields_with_errors_no_wait()

        if error_handling == "Fail" or not error_handling:
            if problematic_fields:
                BuiltIn().fail("Unexpected errors in fields: " + ", ".join(problematic_fields))
        else:
            if not problematic_fields:
                BuiltIn().fail("Expected errors, but encountered none")
            else:
                if error_handling.startswith("Expect Error for Field:"):
                    field = error_handling.replace("Expect Error for Field:", "", 1)
                    if not field in problematic_fields:
                        BuiltIn().fail("Expected error in field '" + field + "', but instead got errors in " + ", ".join(problematic_fields))
                    else:
                        BuiltIn().log("The encountered error in field '" + field + "' was expected")
                else: # expect any error
                    BuiltIn().log("The encountered error was expected")

        return problematic_fields

    def close_browsers(self):
        """
        Closes all browser windows (usually at the end of a test case)
        """
        self.login_user_type = None

        if self.home_page:
            self.home_page.close_all_browsers()
            self.home_page = None
        elif self.login_page:
            self.login_page.close_all_browsers()
            self.login_page = None

    def manual_step(self, message):
        Dialogs.execute_manual_step(message)

    def pause_step(self, message):
        Dialogs.pause_execution(message)
