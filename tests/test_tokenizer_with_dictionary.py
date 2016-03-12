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

from ktokenizer import KTokenizer, AnnotatedToken as AT, IgnoredToken as IT, Whitespace as WS
from sajeon import Sajeon

class TestTokenizerWithDictionary(unittest.TestCase):
    def setUp(self):
        self.dict = Sajeon()
        self.tokenizer = KTokenizer(self.dict.get_definition)
        self.maxDiff = None

    def testTokenizeOneWord(self):
        text = '4번지에'#'프리벳가 4번지에 살고'
        res = self.tokenizer.parse(text)
        expected = [IT('4'),
                    AT('번지', '번지', '(番地) Area of land'),
                    AT('에', '에', 'Josa')
                    ]
        self.assertEqual(repr(res), repr(expected))

    def testTokenizeComplex(self):
        text = '살고 있는 더즐리 부부는 자신들이 정상적이라는 것을 아주 자랑스럽게 여기는 사람들이었다.'
        res = self.tokenizer.parse(text)
        #pprint.pprint(res)
        expected = \
        [AT('살', '살', 'Years old'),
         AT('고', '고', 'Josa'),
         WS(),
         AT('있는', '있다', 'To be'),
         WS(),
         AT('더즐리', '더즐리', None),
         WS(),
         AT('부부', '부부', '(夫婦) Man and wife'),
         AT('는', '는', 'Josa'),
         WS(),
         AT('자신', '자신', '(自身) one’s own self, one`s own body'),
         AT('들', '들', 'and so on and so forth, etcaetera'),
         AT('이', '이', 'Josa'),
         WS(),
         AT('정상', '정상', '(頂上) The top, summit'),
         AT('적', '적', 'The enemy'),
         AT('이라는', '이라는', 'Josa'),
         WS(),
         AT('것', '것', 'A thing or  an object'),
         AT('을', '을', 'Josa'),
         WS(),
         AT('아주', '아주', 'Extremely'),
         WS(),
         AT('자랑', '자랑', 'Pride'),
         AT('스럽게', '스럽게', 'Josa'),
         WS(),
         AT('여기는', '여기다', 'Think, consider as; to think, consider/estimate sth as sth else'),
         WS(),
         AT('사람', '사람', 'Person'),
         AT('들이었', '들이다', 'spend (노력 따위를)'),
         IT('다'),
         IT('.')]
        self.assertEqual(repr(res), repr(expected))


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestTokenizerWithDictionary)
    unittest.TextTestRunner(verbosity=2).run(suite)