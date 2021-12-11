# -*- coding: utf-8 -*-

import os.path
import unittest
import sys
from pprint import pprint

sys.path.append(os.path.abspath('..'))

from compositedict import CompositeDictionary


class TestDictionary(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None
        self.dict = CompositeDictionary(True)

    def testSimple(self):
        res = self.dict.get_definitions('콧수염')
        pprint(res)


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestDictionary)
    unittest.TextTestRunner(verbosity=2).run(suite)
