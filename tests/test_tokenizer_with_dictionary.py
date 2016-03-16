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

from ktokenizer import KTokenizer, Whitespace as WS
from morph_analyzer import AnnotatedToken as AT, IgnoredToken as IT, \
                           create_ending_token, create_particle_token, ParticleToken as PT, \
                           POS_NOUN, POS_VERB, POS_ADJECTIVE, POS_SUFFIX, POS_AUXILIARY, POS_ADVERB
from ezsajeon import EzSajeon
from stardictsajeon import StardictSajeon

KOR_ENG_DICT = False

def to_str(tokens):
    return [repr(token) for token in tokens]

class TestTokenizerWithDictionary(unittest.TestCase):
    def setUp(self):
        self.ezdict = EzSajeon()

        self.tokenizer = KTokenizer(self.ezdict.get_definition)
        self.tokenizer.debug_mode = True
        if KOR_ENG_DICT:
            self.stardict = StardictSajeon()
            self.tokenizer_sd = KTokenizer(self.stardict.get_definition)
            self.tokenizer_sd.debug_mode = True

        self.tokenizer_mecab = KTokenizer(self.ezdict.get_definition, KTokenizer.MECAB)
        self.maxDiff = None

    def testTokenizeOneWord(self):
        text = '4번지에'#'프리벳가 4번지에 살고'
        res = self.tokenizer.parse(text)
        expected = [IT('4'),
                    AT(text='번지', dictionary_form='번지', definition='', pos=POS_NOUN),
                    create_particle_token('에', None)
                    ]
        self.assertEqual(to_str(res), to_str(expected))

        lookedup_words = {
            '번지' : '(番地) Area of land',
        }

        self.assertEqual(lookedup_words, self.tokenizer.get_lookedup_words())

    def testTokenizeComplex(self):
        text = '살고 있는 더즐리 부부는 자신들.'
        res = self.tokenizer.parse(text)
        #pprint.pprint(res)
        expected = \
        [AT(text='살', dictionary_form='살', definition='', pos=POS_NOUN),
         create_particle_token('고', None),
         WS(),
         AT(text='있는', dictionary_form='있다', definition='', pos=POS_ADJECTIVE),
         WS(),
         AT(text='더즐리', dictionary_form='더즐리', definition='', pos=POS_NOUN),
         WS(),
         AT(text='부부', dictionary_form='부부', definition='', pos=POS_NOUN),
         create_particle_token('는', None),
         WS(),
         AT(text='자신', dictionary_form='자신', definition='', pos=POS_NOUN),
         AT(text='들', dictionary_form='들', definition='', pos=POS_SUFFIX),
         IT('.')]
        self.assertEqual(to_str(res), to_str(expected))

        lookedup_words = {
            '살' : 'tine\nflesh,muscle\nYears old',
            '있다' : 'keep\nlie\nTo be\nTo be',
            '부부' : 'man\n(夫婦) Man and wife',
            '자신' : '(自信) Self-confidence\n(自身) one’s own self, one`s own body',
            '들' : 'a field, plains, an opening\nand so on and so forth, etcaetera',
            '더즐리' : ''
        }

        self.assertEqual(lookedup_words, self.tokenizer.get_lookedup_words())

    def testDeconjugation(self):
        text = '무관해 보였다'
        res = self.tokenizer.parse(text)
        expected = \
            [AT(text='무관', dictionary_form='무관', definition='', pos=POS_NOUN),
             create_particle_token('해', None),
             WS(),
             AT(text='보였', dictionary_form='보이다', definition='', pos=POS_VERB),
             create_ending_token('다', None)
             ]
        self.assertEqual(to_str(res), to_str(expected))

        lookedup_words = {
            '무관' : '(武官) a military officer\n(無關) irrelevance',
            '보이다' : 'see,catch sight of\nshow,let see\nto appear as sth, like sth'
        }

        self.assertEqual(lookedup_words, self.tokenizer.get_lookedup_words())

    def testSerialize(self):
        token = AT(text='보였', dictionary_form='보이다', definition='to appear as sth, like sth', pos=POS_VERB)
        res = token.jsonify()
        expected =  {'class': 3, 'pos': 'v', 'text': '보였', 'dict_form': '보이다',
                     'def' : 'to appear as sth, like sth'}
        self.assertEqual(res, expected)

    def testTokenizeKorEngDictionary(self):
        if not KOR_ENG_DICT:
         return
        text = '살고 있는 더즐리 부부는 자신들.'
        res = self.tokenizer_sd.parse(text)
        #pprint.pprint(res)
        expected = \
        [AT(text='살', dictionary_form='살', definition='', pos=POS_NOUN),
         create_particle_token('고', None),
         WS(),
         AT(text='있는', dictionary_form='있다', definition='', pos=POS_ADJECTIVE),
         WS(),
         AT(text='더즐리', dictionary_form='더즐리', definition='', pos=POS_NOUN),
         WS(),
         AT(text='부부', dictionary_form='부부', definition='', pos=POS_NOUN),
         create_particle_token('는', None),
         WS(),
         AT(text='자신', dictionary_form='자신', definition='', pos=POS_NOUN),
         AT(text='들', dictionary_form='들', definition='', pos=POS_SUFFIX),
         IT('.')]

        self.assertEqual(to_str(res), to_str(expected))

        lookedup_words = {
            '살' : '살11 (뼈를 둘러싼) flesh.',
            '있다' : '있다1 [위치하다] be; be situated; <美> be located; stand(건물 등이); lie(도시 등이); run(산맥·강이).',
            '부부' : '부부 [夫婦] husband and wife; man and wife[woman]; a (married) couple; a (wedded) pair.',
            '들' : '들1 a field; [전답] the fields; [평야] a plain.',
            '자신' : '자신 [自身] (one\'s) self; oneself.',
            '더즐리': ''
        }

        self.assertEqual(lookedup_words, self.tokenizer_sd.get_lookedup_words())

    def testMekabTokenizer(self):
        text = '살고 있는 더즐리 부부는 자신들.'
        res = self.tokenizer_mecab.parse(text)
        #pprint.pprint(res)
        expected = \
        [AT(text='살', dictionary_form='살다', definition='', pos=POS_VERB),
         create_ending_token('고', None),
         WS(),
         AT(text='있', dictionary_form='있다', definition='', pos=POS_AUXILIARY),
         create_ending_token('는', None),
         WS(),
         AT(text='더', dictionary_form='더', pos=POS_ADVERB),
         AT(text='즐', dictionary_form='즐', pos=POS_NOUN),
         AT(text='리', dictionary_form='리', pos=POS_NOUN),
         WS(),
         AT(text='부부', dictionary_form='부부', definition='', pos=POS_NOUN),
         create_particle_token('는', None),
         WS(),
         AT(text='자신', dictionary_form='자신', definition='', pos=POS_NOUN),
         AT(text='들', dictionary_form='들', definition='', pos=POS_SUFFIX),
         IT('.')]

        self.assertEqual(to_str(res), to_str(expected))

        lookedup_words = {
          '살다': 'To live',
          '있다': 'keep\nlie\nTo be\nTo be',
          '더': 'More',
          '들': 'a field, plains, an opening\nand so on and so forth, etcaetera',
          '리': 'a reason for doing sth, good cause for sth',
          '부부': 'man\n(夫婦) Man and wife',
          '자신': '(自信) Self-confidence\n(自身) one’s own self, one`s own body',
          '즐': ''
        }
        self.assertEqual(lookedup_words, self.tokenizer_mecab.get_lookedup_words())


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestTokenizerWithDictionary)
    unittest.TextTestRunner(verbosity=2).run(suite)