# -*- coding: utf-8 -*-

import os.path
import unittest
import sys
import pprint

sys.path.append(os.path.abspath('..'))

from mecab_analyzer import MecabAnalyzer
from morph_analyzer import AnnotatedToken as AT, IgnoredToken as IT, create_particle_token, create_ending_token
from morph_analyzer import *

def to_str(tokens):
    return [repr(token) for token in tokens]

class TestMecab(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None
        self.parser = MecabAnalyzer(None)

    def testParse(self):
        text = '프리벳가 4번지에 살고 있는 더즐리 부부는 보였다'
        res = self.parser.parse(text)
        expected = \
            [AT(text='프리', dictionary_form='프리', pos=POS_NOUN),
             AT(text='벳', dictionary_form='벳', pos=POS_NOUN),
             AT(text='가', dictionary_form='가', pos=POS_SUFFIX),
             IT('4'),
             AT(text='번지', dictionary_form='번지', pos=POS_NOUN),
             create_particle_token('에', None),
             AT(text='살', dictionary_form='살다', pos=POS_VERB),
             create_ending_token('고', None),
             AT(text='있', dictionary_form='있', pos=POS_AUXILIARY),
             create_ending_token('는', None),
             AT(text='더', dictionary_form='더', pos=POS_ADVERB),
             AT(text='즐', dictionary_form='즐', pos=POS_NOUN),
             AT(text='리', dictionary_form='리', pos=POS_NOUN),
             AT(text='부부', dictionary_form='부부', pos=POS_NOUN),
             create_particle_token('는', None),
             AT(text='보였', dictionary_form='보이다', pos='VV+EP'),
             create_ending_token('다', None)]
        self.assertEqual(to_str(res), to_str(expected))

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestMecab)
    unittest.TextTestRunner(verbosity=2).run(suite)