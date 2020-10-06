# -*- coding: utf-8 -*-

import os.path
import unittest
import sys
from pprint import pprint

sys.path.append(os.path.abspath('..'))


class TestWordExtraction(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None

    def testSimple(self):
        pass



if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestWordExtraction)
    unittest.TextTestRunner(verbosity=2).run(suite)