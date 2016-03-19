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

from ktokenizer import KTokenizer, Whitespace as WS, get_word_number
from morph_analyzer import IgnoredToken as IT, AnnotatedToken as AT, \
                           create_particle_token, create_ending_token

from morph_analyzer import POS_NOUN, POS_VERB, POS_ADJECTIVE, POS_SUFFIX

def to_str(tokens):
    return [repr(token) for token in tokens]

class TestTokenizer(unittest.TestCase):
    def setUp(self):
        self.tokenizer = KTokenizer(None, KTokenizer.TWITTER)
        self.tokenizer_mecab = KTokenizer(None, KTokenizer.MECAB)
        self.maxDiff = None

    def testTokenize(self):
        text = '프리벳가 4번지에'
        res = self.tokenizer.parse(text)
        expected = [AT(text='프리벳', dictionary_form='프리벳', pos=POS_NOUN),
                    create_particle_token('가', None),
                    WS(),
                    IT('4'),
                    AT(text='번지', dictionary_form='번지', pos=POS_NOUN),
                    create_particle_token('에', None)
                    ]
        self.assertEquals(to_str(expected), to_str(res))

    def testTokenizeMecab(self):
        text = '프리벳가 4번지에'
        res = self.tokenizer_mecab.parse(text)
        expected = [AT(text='프리', dictionary_form='프리', pos=POS_NOUN),
                    AT(text='벳', dictionary_form='벳', pos=POS_NOUN),
                    AT(text='가', dictionary_form='가', pos=POS_SUFFIX),
                    WS(),
                    IT('4'),
                    AT(text='번지', dictionary_form='번지', pos=POS_NOUN),
                    create_particle_token('에', None)
                    ]
        self.assertEquals(to_str(expected), to_str(res))

    def testNormalized(self):
        text = '살고 있는 더즐리'
        res = self.tokenizer.parse(text)
        expected = [AT(text='살', dictionary_form='살', definition='', pos=POS_NOUN),
                    create_particle_token('고', None),
                    WS(),
                    AT(text='있는', dictionary_form='있다', definition='', pos=POS_ADJECTIVE),
                    WS(),
                    AT(text='더즐리', dictionary_form='더즐리', definition='', pos=POS_NOUN)
                    ]
        self.assertEquals(to_str(expected), to_str(res))

    def testNormalized2(self):
        text = '제 1장 살아남은 아이'
        res = self.tokenizer.parse(text)
        expected = [AT(text='제', dictionary_form='제', pos=POS_NOUN),
                    WS(),
                    IT('1'),
                    AT(text='장', dictionary_form='장', pos=POS_NOUN),
                    WS(),
                    AT(text='살아남', dictionary_form='살아나다', pos=POS_VERB),
                    create_ending_token('은', None),
                    WS(),
                    AT(text='아이', dictionary_form='아이', pos=POS_NOUN)]
        self.assertEquals(to_str(expected), to_str(res))

    def testWordNumber(self):
        num = get_word_number('var part_of_speech_info = "터무니없는 것 은 ";')
        self.assertEqual(5, num)

        num = get_word_number(' = "";')
        self.assertEqual(0, num)

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestTokenizer)
    unittest.TextTestRunner(verbosity=2).run(suite)