import datetime

class BuiltinFunctions:
 
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
