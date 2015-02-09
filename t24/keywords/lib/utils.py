import sys
import random
import datetime
import time

class utils:
 
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'
    __version__ = '0.1'
 
    def get_unique_new_customer_mnemonic(self):
    	return 'XYZ12345'
    
    def get_unique_date_string(self):
        now = datetime.datetime.now()
        return now.strftime("%m%d%H%M%S")
        
    def get_todays_date(self):
        now = datetime.datetime.now()
        return now.strftime("%m/%d/%Y")
    
    def get_id_from_transaction_confirmation_text(self, confirmTransactionText):
        return confirmTransactionText.replace('Txn Complete:', '').strip().split(' ', 1)[0]
