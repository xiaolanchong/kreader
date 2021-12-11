# -*- coding: utf-8 -*-

import os.path
import unittest
import sys
import pprint

sys.path.append(os.path.abspath('..'))

from twitter import do_words_suit, get_word_to_stem_pairs


class TestTwitter(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None

    def testDecompose(self):
        res = do_words_suit('찐', '찌다')
        self.assertTrue(res)

    def testDecomposeNeung(self):
        res = do_words_suit('은', '아')
        self.assertFalse(res)

    def testWordToStem(self):
        a = ['이', '거의', '없', '을', '정도', '로', '찐', '몸집', '이', '큰', '사내', '로', ',', '코밑', '커다란', '콧수염', '을', '기르', '고',
             '있었', '다', '.']
        b = ['이', '거의', '없다', '정도', '로', '찌다', '몸집', '이', '크다', '사내', '로', ',', '코밑', '커다랗다', '콧수염', '을', '기르다', '있다',
             '.']
        res = get_word_to_stem_pairs(a, b)
        expected = \
            [('이', '이'),
             ('거의', '거의'),
             ('없', '없다'),
             ('을', ''),
             ('정도', '정도'),
             ('로', '로'),
             ('찐', '찌다'),
             ('몸집', '몸집'),
             ('이', '이'),
             ('큰', '크다'),
             ('사내', '사내'),
             ('로', '로'),
             (',', ','),
             ('코밑', '코밑'),
             ('커다란', '커다랗다'),
             ('콧수염', '콧수염'),
             ('을', '을'),
             ('기르', '기르다'),
             ('고', ''),
             ('있었', '있다'),
             ('다', ''),
             ('.', '.')]
        self.assertEqual(res, expected)


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestTwitter)
    unittest.TextTestRunner(verbosity=2).run(suite)
