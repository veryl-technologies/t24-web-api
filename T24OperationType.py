class T24OperationType:
    Login = "Login"
    SignOff = "SignOff"
    Enquiry = "Querying Records"
    StartInputNewRecord = "Inputting of a New Record"
    StertEditExitingRecord = "Record Editing"
    StartAuthorizingRecord = "Record Authorization"
    SeeRecord = "Record Data Fetching"
    Menu = "Menu Command"
    Tab = "Tab Command"

    def __init__(self):
        print 'T24OperationType enumeration initialized'
