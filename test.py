import unittest
from end_of_package import EndOfPackage
from camfis_utils import EOP


class TestEndOfPackage(unittest.TestCase):

    def testCreateEOP(self):
        eop = EndOfPackage()
        self.assertTrue(eop.is_valid())
    
    def testTranslateCorrectEOP(self):
        eop = EndOfPackage(eop=EOP)
        self.assertTrue(eop.is_valid())
    
    def testTranslateIncorrectEOP(self):
        eop = EndOfPackage(eop=b"\x01\x02")
        self.assertFalse(eop.is_valid())


if __name__ == "__main__":
    unittest.main(verbosity=2)
