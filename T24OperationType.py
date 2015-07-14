class T24OperationType:
    Login = "Login"
    SignOff = "SignOff"
    Enquiry = "Querying Records"
    StartInputNewRecord = "Inputting of a New Record"
    StertEditExitingRecord = "Record Editing"
    StartAuthorizingRecord = "Record Authorization"
    SeeRecord = "Record Data Fetching"

    def __init__(self):
        print 'T24OperationType enumeration initialized'
