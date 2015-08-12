from t24pageobjects import T24LoginPage, T24HomePage, T24EnquiryStartPage, T24EnquiryResultPage, T24RecordSeePage, T24RecordInputPage
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

    ### 'T24 Login'
    def t24_login(self, user_type="INPUTTER"):
        print "Trying to login as: " + user_type

        self.login_page = T24LoginPage()
        self.login_page.open()
        self.login_user_type = user_type

        if user_type == "INPUTTER":
            self.home_page = self.login_page.enter_T24_credentials("INPUTT", "123456")
        elif user_type == "AUTHORISER":
            self.home_page = self.login_page.enter_T24_credentials("AUTHOR", "123456")
        else:
            raise NotImplementedError('TODO t24_login')

    def _make_sure_is_logged_in(self, user_type="INPUTTER"):
        print "_make_sure_is_logged_in"
        if not self.login_page:
            self.t24_login(user_type)
        elif self.login_user_type != user_type:
                self.t24_logoff()
                self.t24_login(user_type)

    def t24_logoff(self):
        if self.home_page:
            self.home_page.sign_off()
            self.home_page = None

    ### 'Execute T24 Menu Command'
    def execute_t24_menu_command(self):
        self._make_sure_is_logged_in()
        print "execute_t24_menu_command"

    ### 'Create Or Amend T24 Record'
    def create_or_amend_t24_record(self, app_version, record_id, record_field_values, oveerrides_handling=None, error_handling=None, post_verification=None):
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

    ### 'Authorize T24 Record'
    def authorize_t24_record(self, app_version, record_id, extra_authorizations=0):
        self._make_sure_is_logged_in("AUTHORISER")
        authorize_page = self.home_page.open_authorize_page(app_version, record_id)
        authorize_page.click_authorize_button()
        self.last_authorize_id = authorize_page.get_id_from_completed_transaction()
        self.last_tx_id = self.last_authorize_id
        BuiltIn().set_test_variable("${TX_ID}", self.last_tx_id)
        authorize_page.close_window()

    ### 'Check T24 Record Exists'
    def check_t24_record_exists(self, app, record_id, validations):
        self._make_sure_is_logged_in()
        see_page = self.home_page.open_see_page(app, record_id)

        validation_fields = []
        validation_operators = []
        validation_values = []

        # parse the values
        for v in validations:
            fld, op, val = self._parse_validation_rule(v)
            validation_fields.append(fld)
            validation_operators.append(op)
            validation_values.append(val)

        # check for expected & actual result
        errors = []
        for idx, field in enumerate(validation_fields) :
            actual_value = see_page.get_T24_field_value(field)
            op = validation_operators[idx]
            expected_value = validation_values[idx]
            if op == "EQ" and expected_value != actual_value:
                errors.append("Field '" + field + "' has expected value '" + expected_value + "' but the actual value is '" + actual_value + "'")
            if op == "LK" and expected_value not in actual_value:
                errors.append("Field '" + field + "' has expected value '" + expected_value + "' that is not part of the actual value '" + actual_value + "'")

        if errors:
            BuiltIn().fail("\n".join(errors))

    def _parse_validation_rule(self, validation_rule):
        if " EQ " in validation_rule:
            return self._get_validation_rule_parts(validation_rule, " EQ ")

        if " LK " in validation_rule:
            return self._get_validation_rule_parts(validation_rule, " LK ")

        raise NotImplementedError('TODO _parse_validation_rule')

    def _get_validation_rule_parts(self, validation_rule, operator):
        items = validation_rule.split(operator, 1)
        return items[0], operator.trim(), items[1]

    ### 'Execute T24 Enquiry'
    def execute_T24_enquiry(self):
        self._make_sure_is_logged_in()
        raise NotImplementedError('TODO execute_T24_enquiry')
        print "check_t24_record_exists"

    ### 'Validate T24 Record'
    def validate_t24_record(self):
        self._make_sure_is_logged_in()
        raise NotImplementedError('TODO validate_t24_record')
        print "check_t24_record_exists"

    def close_browsers(self):
        if self.login_page:
            self.login_page.close_all_browsers()
