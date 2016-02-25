import unittest
import utils

class UtilsTestCase(unittest.TestCase):


    def test_customer_mnenomonic_generation(self):
        u = utils.utils()
        print u.get_unique_new_customer_mnemonic()
