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
                           POS_NOUN, POS_VERB, POS_ADJECTIVE, POS_SUFFIX
from sajeon import Sajeon

def to_str(tokens):
    return [repr(token) for token in tokens]

class TestTokenizerWithDictionary(unittest.TestCase):
    def setUp(self):
        self.dict = Sajeon()
        self.tokenizer = KTokenizer(self.dict.get_definition)
        self.maxDiff = None

    def testTokenizeOneWord(self):
        text = '4번지에'#'프리벳가 4번지에 살고'
        res = self.tokenizer.parse(text)
        expected = [IT('4'),
                    AT(text='번지', dictionary_form='번지', definition='(番地) Area of land', pos=POS_NOUN),
                    create_particle_token('에', None)
                    ]
        self.assertEqual(to_str(res), to_str(expected))

    def testTokenizeComplex(self):
        text = '살고 있는 더즐리 부부는 자신들이 정상적이라는 것을 아주 자랑스럽게 여기는 사람들이었다.'
        res = self.tokenizer.parse(text)
        #pprint.pprint(res)
        expected = \
        [AT(text='살', dictionary_form='살', definition='Years old', pos=POS_NOUN),
         create_particle_token('고', None),
         WS(),
         AT(text='있는', dictionary_form='있다', definition='To be', pos=POS_ADJECTIVE),
         WS(),
         AT(text='더즐리', dictionary_form='더즐리', definition='', pos=POS_NOUN),
         WS(),
         AT(text='부부', dictionary_form='부부', definition='(夫婦) Man and wife', pos=POS_NOUN),
         create_particle_token('는', None),
         WS(),
         AT(text='자신', dictionary_form='자신', definition='(自身) one’s own self, one`s own body', pos=POS_NOUN),
         AT(text='들', dictionary_form='들', definition='and so on and so forth, etcaetera', pos=POS_SUFFIX),
         create_particle_token('이', None),
         WS(),
         AT(text='정상', dictionary_form='정상', definition='(頂上) The top, summit', pos=POS_NOUN),
         AT(text='적', dictionary_form='적', definition='The enemy', pos=POS_SUFFIX),
         PT(text='이라는', definition='that which'),
         WS(),
         AT(text='것', dictionary_form='것', definition='A thing or  an object', pos=POS_NOUN),
         create_particle_token('을', None),
         WS(),
         AT(text='아주', dictionary_form='아주', definition='Extremely', pos=POS_NOUN),
         WS(),
         AT(text='자랑', dictionary_form='자랑', definition='Pride', pos=POS_NOUN),
         create_particle_token('스럽게', None),
         WS(),
         AT(text='여기는', dictionary_form='여기다',
            definition='Think, consider as; to think, consider/estimate sth as sth else', pos=POS_VERB),
         WS(),
         AT(text='사람', dictionary_form='사람', definition='Person', pos=POS_NOUN),
         AT(text='들이었', dictionary_form='들이다', definition='spend (노력 따위를)', pos=POS_VERB),
         create_ending_token('다', None),
         IT('.')]
        self.assertEqual(to_str(res), to_str(expected))

    def testDeconjugation(self):
        text = '무관해 보였다'
        res = self.tokenizer.parse(text)
        expected = \
            [AT(text='무관', dictionary_form='무관', definition='(無關) irrelevance', pos=POS_NOUN),
             create_particle_token('해', None),
             WS(),
             AT(text='보였', dictionary_form='보이다', definition='to appear as sth, like sth', pos=POS_VERB),
             create_ending_token('다', None)
             ]
        self.assertEqual(to_str(res), to_str(expected))

    def testSerialize(self):
        token = AT(text='보였', dictionary_form='보이다', definition='to appear as sth, like sth', pos=POS_VERB)
        res = token.jsonify()
        self.assertEqual(res, '')


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestTokenizerWithDictionary)
    unittest.TextTestRunner(verbosity=2).run(suite)