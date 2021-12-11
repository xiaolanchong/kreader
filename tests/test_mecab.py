# -*- coding: utf-8 -*-

import os.path
import unittest
import sys

sys.path.append(os.path.abspath('..'))

from mecab_analyzer import MecabAnalyzer
from morph_analyzer import AnnotatedToken as AT, IgnoredToken as IT, DecomposedToken as D
from morph_analyzer import *


def to_str(tokens):
    return [repr(token) for token in tokens]


class TestMecab(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None
        self.parser = MecabAnalyzer()

    def testParse(self):
        text = '프리벳가 4번지에 살고 있는 더즐리 부부는 보였다'
        res = self.parser.parse(text)
        expected = \
            [AT(text='프리', dictionary_form='프리', pos=POS_NOUN),
             AT(text='벳', dictionary_form='벳', pos=POS_NOUN),
             AT(text='가', dictionary_form='가', pos=POS_SUFFIX),
             IT('4'),
             AT(text='번지', dictionary_form='번지', pos=POS_NOUN),
             AT(text='에', dictionary_form='에', pos=POS_PARTICLE),
             AT(text='살', dictionary_form='살다', pos=POS_VERB),
             AT(text='고', dictionary_form='고', pos=POS_ENDING),
             AT(text='있', dictionary_form='있다', pos=POS_AUXILIARY),
             AT(text='는', dictionary_form='는', pos=POS_ENDING),
             AT(text='더', dictionary_form='더', pos=POS_ADVERB),
             AT(text='즐', dictionary_form='즐', pos=POS_NOUN),
             AT(text='리', dictionary_form='리', pos=POS_NOUN),
             AT(text='부부', dictionary_form='부부', pos=POS_NOUN),
             AT(text='는', dictionary_form='는', pos=POS_PARTICLE),
             AT(text='보였', dictionary_form='보이다', pos=POS_VERB, decomposed_tokens=[D(POS_ENDING, 'EP')]),
             AT(text='다', dictionary_form='다', pos=POS_ENDING)]
        self.assertEqual(to_str(res), to_str(expected))

    def testParseWord(self):
        text = '효과) 사무실. '
        res = self.parser.parse(text)
        expected = \
            [AT(text='효과', dictionary_form='효과', pos=POS_NOUN),
             IT(')'),
             AT(text='사무실', dictionary_form='사무실', pos=POS_NOUN),
             IT('.')
             ]
        self.assertEqual(to_str(res), to_str(expected))

    def testComposition(self):
        text = '배웠는지'
        # text = '알아보겠습니다'
        res = self.parser.parse(text)
        expected = \
            [AT(text='배웠', dictionary_form='배우다', pos=POS_VERB, decomposed_tokens=[D(POS_ENDING, 'EP')]),
             AT(text='는지', dictionary_form='는지', pos=POS_ENDING),
             ]
        self.assertEqual(to_str(res), to_str(expected))


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestMecab)
    unittest.TextTestRunner(verbosity=2).run(suite)
