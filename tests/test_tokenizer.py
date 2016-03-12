# -*- coding: utf-8 -*-

import os.path
import unittest
import sys
import pprint
import time
import logging
import datetime
import time
import html.parser
sys.path.append(os.path.abspath('..'))

from ktokenizer import KTokenizer, IgnoredToken as IT, AnnotatedToken as AT, Whitespace as WS

class TestTokenizer(unittest.TestCase):
    def setUp(self):
        self.tokenizer = KTokenizer()
        self.maxDiff = None

    def testTokenize(self):
        text = '프리벳가 4번지에'
        res = self.tokenizer.parse(text)
        expected = [AT('프리벳', '프리벳', None),
                    AT('가', '가', 'Josa'),
                    WS(),
                    IT('4'),
                    AT('번지', '번지', None),
                    AT('에', '에', 'Josa')
                    ]
        self.assertEquals(repr(expected), repr(res))

    def testNormalized(self):
        text = '살고 있는 더즐리'
        res = self.tokenizer.parse(text)
        expected = [AT('살', '살', None),
                    AT('고', '고', 'Josa'),
                    WS(),
                    AT('있는', '있다', None),
                    WS(),
                    AT('더즐리', '더즐리', None)
                    ]
        self.assertEquals(repr(expected), repr(res))

    def testNormalized2(self):
        text = '제 1장 살아남은 아이'
        res = self.tokenizer.parse(text)
        expected = [AT('제', '제', None), WS(), IT('1'), AT('장', '장', None), WS(),
                    AT('살아남', '살아나다', None),
                    IT('은'), # must be AT('은', '은', 'Josa'), Twitter ignores it!
                    WS(),
                    AT('아이', '아이', None)]
        self.assertEquals(repr(expected), repr(res))

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestTokenizer)
    unittest.TextTestRunner(verbosity=2).run(suite)