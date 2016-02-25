import sys
import random
import datetime
import time

class utils:
 
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'
    __version__ = '0.1'

    @staticmethod
    def num_to_short_alphanumeric(i):
        chars = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXY'
        length = len(chars)

        result = ''
        while i:
            result = chars[i % length] + result
            i = i // length
        if not result:
            result = chars[0]
        return result

    def get_unique_new_customer_mnemonic(self):
        base = datetime.datetime(2016, 2, 1, 00, 00)
        secondsPassed = int((datetime.datetime.now() - base).total_seconds())
        code = self.num_to_short_alphanumeric(secondsPassed)
        result = code.rjust(8, 'Z')
        return result

    def get_unique_date_string(self):
        now = datetime.datetime.now()
        return now.strftime("%m%d%H%M%S")
        
    def get_todays_date(self):
        now = datetime.datetime.now()
        return now.strftime("%m/%d/%Y")
    
    def get_id_from_transaction_confirmation_text(self, confirmTransactionText):
        return confirmTransactionText.replace('Txn Complete:', '').strip().split(' ', 1)[0]
