# -*- coding: utf-8 -*-

import os.path
import unittest
import sys

sys.path.append(os.path.abspath('..'))

from ktokenizer import KTokenizer, Whitespace as WS, tokenize
from morph_analyzer import AnnotatedToken as AT, IgnoredToken as IT, DecomposedToken as D, \
    POS_NOUN, POS_VERB, POS_ADJECTIVE, POS_SUFFIX, POS_AUXILIARY, POS_ADVERB, POS_PARTICLE, POS_ENDING


def to_str(tokens):
    return [repr(token) for token in tokens]


class TestTokenizerWithDictionary(unittest.TestCase):
    def setUp(self):
        self.tokenizer = KTokenizer()
        self.tokenizer.debug_mode = True
        self.tokenizer_sd = KTokenizer()
        self.tokenizer_sd.debug_mode = True

        self.tokenizer_mecab = KTokenizer(KTokenizer.MECAB)
        self.tokenizer_mecab.debug_mode = True
        self.maxDiff = None

    def testTokenizeOneWord(self):
        text = '4번지에'  # '프리벳가 4번지에 살고'
        res = self.tokenizer.parse(text)
        expected = [IT('4'),
                    AT(text='번지', dictionary_form='번지', definition='', pos=POS_NOUN),
                    AT(text='에', dictionary_form='에', pos=POS_PARTICLE)
                    ]
        self.assertEqual(to_str(res), to_str(expected))

    def testTokenizeComplex(self):
        text = '살고 있는 더즐리 부부는 자신들.'
        res = self.tokenizer.parse(text)
        # pprint.pprint(res)
        expected = \
            [AT(text='살', dictionary_form='살', pos=POS_NOUN),
             AT(text='고', dictionary_form='고', pos=POS_PARTICLE),
             WS(),
             AT(text='있는', dictionary_form='있다', definition='', pos=POS_ADJECTIVE),
             WS(),
             AT(text='더즐리', dictionary_form='더즐리', definition='', pos=POS_NOUN),
             WS(),
             AT(text='부부', dictionary_form='부부', definition='', pos=POS_NOUN),
             AT(text='는', dictionary_form='는', pos=POS_PARTICLE),
             WS(),
             AT(text='자신', dictionary_form='자신', definition='', pos=POS_NOUN),
             AT(text='들', dictionary_form='들', definition='', pos=POS_SUFFIX),
             IT('.')]
        self.assertEqual(to_str(res), to_str(expected))

    def testSerialize2(self):
        token = AT(text='있는', dictionary_form='있다', definition='', pos=POS_AUXILIARY,
                   decomposed_tokens=[D(POS_ENDING, '는')])
        res = token.jsonify()
        expected = {'class': 3, 'pos': 'aux', 'text': '있는', 'dict_form': '있다', 'dec_tok': [('end', '는')]
                    }
        self.assertEqual(res, expected)

    def testSerialize(self):
        token = AT(text='보였', dictionary_form='보이다', pos=POS_VERB)
        res = token.jsonify()
        expected = {'class': 3, 'pos': 'v', 'text': '보였', 'dict_form': '보이다',
                    }
        self.assertEqual(res, expected)

    def testTokenizeKorEngDictionary(self):
        text = '살고 있는 더즐리 부부는 자신들.'
        res = self.tokenizer_sd.parse(text)
        # pprint.pprint(res)
        expected = \
            [AT(text='살', dictionary_form='살', definition='', pos=POS_NOUN),
             AT(text='고', dictionary_form='고', pos=POS_PARTICLE),
             WS(),
             AT(text='있는', dictionary_form='있다', definition='', pos=POS_ADJECTIVE),
             WS(),
             AT(text='더즐리', dictionary_form='더즐리', definition='', pos=POS_NOUN),
             WS(),
             AT(text='부부', dictionary_form='부부', definition='', pos=POS_NOUN),
             AT(text='는', dictionary_form='는', pos=POS_PARTICLE),
             WS(),
             AT(text='자신', dictionary_form='자신', definition='', pos=POS_NOUN),
             AT(text='들', dictionary_form='들', definition='', pos=POS_SUFFIX),
             IT('.')]

        self.assertEqual(to_str(res), to_str(expected))

    def testMekabTokenizer(self):
        text = '살고 있는 더즐리 부부는 자신들.'
        res = self.tokenizer_mecab.parse(text)
        # pprint.pprint(res)
        expected = \
            [AT(text='살고', dictionary_form='살다', definition='', pos=POS_VERB, decomposed_tokens=[D(POS_ENDING, '고')]),
             WS(),
             AT(text='있는', dictionary_form='있다', definition='', pos=POS_AUXILIARY,
                decomposed_tokens=[D(POS_ENDING, '는')]),
             WS(),
             AT(text='더', dictionary_form='더', pos=POS_ADVERB),
             AT(text='즐', dictionary_form='즐', pos=POS_NOUN),
             AT(text='리', dictionary_form='리', pos=POS_NOUN),
             WS(),
             AT(text='부부', dictionary_form='부부', definition='', pos=POS_NOUN),
             AT(text='는', dictionary_form='는', pos=POS_PARTICLE),
             WS(),
             AT(text='자신', dictionary_form='자신', definition='', pos=POS_NOUN),
             AT(text='들', dictionary_form='들', definition='', pos=POS_SUFFIX),
             IT('.')]

        self.assertEqual(to_str(res), to_str(expected))

    def testTokenizeFunc(self):
        text = '전혀 무관해 보였다\n그런데\n아들이 하나 있다'
        parsed_text, glossary, total_words, unique_words = \
            tokenize(self.tokenizer_mecab, lambda: text.split('\n'))
        self.assertEqual(len(parsed_text), 15)
        self.assertEqual(len(glossary), 9)


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestTokenizerWithDictionary)
    unittest.TextTestRunner(verbosity=2).run(suite)
