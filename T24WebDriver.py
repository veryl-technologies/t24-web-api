from t24pageobjects import T24LoginPage
from T24ExecutionContext import T24ExecutionContext
from robot.libraries.BuiltIn import BuiltIn

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
        Enters login credential in the T24 login page for the specified user type.
        The default user type is INPUTTER
        """

        self._log_info('Trying to login as ' + user_type)

        var_user_name = "${LOGIN_" + user_type + "}"
        user = BuiltIn().get_variable_value(var_user_name)
        if not user:
            BuiltIn().fail("Please specify a user name in a variable " + var_user_name)

        var_pass = "${PASSWORD_" + user_type + "}"
        password = BuiltIn().get_variable_value(var_pass)
        if not password:
            BuiltIn().fail("Please specify a password in a variable " + var_pass)

        # TODO disable Capture Screenshot as it currently doesn't work
        se2lib = BuiltIn().get_library_instance('Selenium2Library')
        se2lib.register_keyword_to_run_on_failure = None

        if not self.login_page:
            self.login_page = T24LoginPage()
            self.login_page.open()

        self.login_user_type = user_type
        self.home_page = self.login_page.enter_T24_credentials(user, password)

    def _make_sure_is_logged_in(self, user_type="INPUTTER"):
        self._log_debug('Checking whether the current user is ' + user_type)
        if not self.login_page:
            self.t24_login(user_type)
        elif self.login_user_type != user_type:
                self.t24_logoff()
                self.t24_login(user_type)

    def t24_logoff(self):
        """
        If there is a currently logged-in user in T24, a Sign Off would be get clicked to open the T24 login page
        """
        if self.home_page:
            self.home_page.sign_off()
            self.home_page = None

    def execute_t24_menu_command(self):
        self._make_sure_is_logged_in()
        raise NotImplementedError('TODO execute_t24_menu_command')

    def create_or_amend_t24_record(self, app_version, record_id, record_field_values, oveerrides_handling=None, error_handling=None, post_verification=None):
        """
        Creates a T24 record with the specified fields if 'record_id' is not specified, otherwise amends it
        """
        self._make_sure_is_logged_in()

        if record_id:
            input_page = self.home_page.open_edit_page(app_version, record_id)
        else:
            input_page = self.home_page.open_input_page_new_record(app_version)

        for field_and_value in record_field_values:
            pair = field_and_value.split("=")
            input_page.set_T24_field_value(pair[0], pair[1])

        input_page.click_commit_button()
        self.last_input_id = input_page.get_id_from_completed_transaction()
        self.last_tx_id = self.last_input_id
        BuiltIn().set_test_variable("${TX_ID}", self.last_tx_id)
        input_page.close_window()
        self._make_home_page_default()

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
        Retrieves the T24 record by its unique ID and verifies its fields against some predefined criteria
        """
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
                BuiltIn().set_test_variable("${" + expected_value.strip() + "}", actual_value)
            else:
                if op == "EQ" and expected_value != actual_value:
                    errors.append("Field '" + field + "' has expected value '" + expected_value + "' but the actual value is '" + actual_value + "'")
                elif op == "LK" and expected_value not in actual_value:
                    errors.append("Field '" + field + "' has expected value '" + expected_value + "' that is not part of the actual value '" + actual_value + "'")
                else:
                    self._log_info("For field '" + field + "' verified that the actual value '" + actual_value + "' " +
                                   self._get_operator_friendly_name(op) + " the expected value '" + expected_value + "'")

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
            return "contains"
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
            validation_values.append(val)

        return validation_fields, validation_operators, validation_values

    def _parse_validation_rule(self, validation_rule):
        validation_rule = self._normalize_filter(validation_rule)

        if " EQ " in validation_rule:
            return self._get_validation_rule_parts(validation_rule, " EQ ")

        if " LK " in validation_rule:
            return self._get_validation_rule_parts(validation_rule, " LK ")

        if " >> " in validation_rule:
            return self._get_validation_rule_parts(validation_rule, " >> ")

        raise NotImplementedError("Unexpected text for filter/validation: '" + validation_rule + "'")

    def _normalize_filter(self, param):
        # Currently in RIDE we use filters like =EQ:= , but the logic expects just EQ
        if ":=" in param:
            return param.replace(":=", "", 1).replace(":", "", 1)
        return param

    def _get_validation_rule_parts(self, validation_rule, operator):
        items = validation_rule.split(operator, 1)
        return items[0], operator.strip(), items[1]

    def execute_T24_enquiry(self, enquiry, enquiry_constraints, action, action_parameters):
        """
        Execute a T24 enquiry with the specified criteria and processes the first found result
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
            values = enq_res_page.get_values_from_enquiry_result(enq_res_columns)

            # need to save data into RF variables
            for i, c in enumerate(enq_res_columns):
                if validation_operators[i] == ">>":
                    BuiltIn().set_test_variable("${" + validation_values[i].strip() + "}", values[i])

            # verify the results
            errors = []
            for idx, column in enumerate(enq_res_columns):
                op = validation_operators[idx]
                if op == ">>":
                    continue

                actual_value = values[idx]
                expected_value = validation_values[idx]
                if op == "EQ" and expected_value != actual_value:
                    errors.append("Column '" + column + "' has expected value '" + expected_value + "' but the actual value is '" + actual_value + "'")
                elif op == "LK" and expected_value not in actual_value:
                    errors.append("Column '" + column + "' has expected value '" + expected_value + "' that is not part of the actual value '" + actual_value + "'")
                else:
                    self._log_info("For column '" + column + "' verified that the actual value '" + actual_value + "' " +
                                   self._get_operator_friendly_name(op) + " the expected value '" + expected_value + "'")

            # fail if there are any validation errors
            if errors:
                BuiltIn().fail("\n".join(errors))
        else:
            raise NotImplementedError("Not implemented execution actions on enquiry results. Can't apply action " + action)

        # go back to home screen
        enq_res_page.close_window()
        self._make_home_page_default()

    def validate_t24_record(self):
        self._make_sure_is_logged_in()
        raise NotImplementedError('TODO validate_t24_record')

    def close_browsers(self):
        """
        Closes all browser windows (usually at the end of a test case)
        """
        if self.login_page:
            self.login_page.close_all_browsers()
            self.login_page = None
