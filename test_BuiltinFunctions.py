import unittest
import BuiltinFunctions as BF


class BuiltinFormulasTestCase(unittest.TestCase):

    def test_add_t24_days(self):
        self.assertEqual('20160627', BF.add_t24_days('20160625', 2))
        self.assertEqual('20160622', BF.add_t24_days('20160625', -3))