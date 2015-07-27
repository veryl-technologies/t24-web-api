from Singleton import Singleton

@Singleton
class T24ExecutionContext:

    NewRecordsIds = []
    TypicalsOfNewRecords = []

    UpdatedRecordsIds = []
    TypicalsOfUpdatedRecords = []

    AuthorizedRecordsIds = []
    TypicalsOfAuthorizedRecords = []

    Operations = []

    CurrentPage = None

    def __init__(self):
        print 'Execution Context created'

    def clear(self):
        self.NewRecordsIds = []
        self.TypicalsOfNewRecords = []
        self.UpdatedRecordsIds = []
        self.TypicalsOfUpdatedRecords = []
        self.AuthorizedRecordsIds = []
        self.TypicalsOfAuthorizedRecords = []
        self.CurrentPage = None
        self.Operations = []

    def add_record_created(self, recordType, recordId):
        self.TypicalsOfNewRecords.append(recordType)
        self.NewRecordsIds.append(recordId)

    def add_record_updated(self, recordType, recordId):
        self.TypicalsOfNewRecords.append(recordType)
        self.NewRecordsIds.append(recordId)

    def add_record_authorized(self, recordType, recordId):
        self.TypicalsOfAuthorizedRecords.append(recordType)
        self.AuthorizedRecordsIds.append(recordId)

    def add_operation(self, operation):
        print 'Executing operation: ' + operation + " ..."
        self.Operations.append(operation)

    def set_current_page(self, page):
        print 'Current page is ' + type(page) + "."
        CurrentPage = page


