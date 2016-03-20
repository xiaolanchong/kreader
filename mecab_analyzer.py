# -*- coding: utf-8 -*-

import pprint

from morph_analyzer import AnnotatedToken, IgnoredToken, \
                           create_particle_token, create_ending_token, \
                           MorphAnalyzer

from morph_analyzer import *

from mecab import Mecab

def convert_pos(pos):
    known_pos = {
    'NNG' : POS_NOUN,
    'NNP' : POS_NOUN,
    'NNB' : POS_NOUN,
    'NNBC' : POS_NOUN,
    'NR' : POS_NUMBER,
    'NP' : POS_NOUN,   # to POS_PRONOUN?
    'VV' : POS_VERB,
    'VA' : POS_ADJECTIVE,
    'VX' : POS_AUXILIARY, # or POS_VERB?
    'VCP' : POS_ADJECTIVE,
    'VCN' : POS_ADJECTIVE,
    'MM' : POS_DETERMINER,
    'MAG' : POS_ADVERB,
    'MAJ' : POS_ADVERB,
    'IC' : POS_INTERJECTION,
    'JKS' : POS_PARTICLE,
    'JKC' : POS_PARTICLE,
    'JKG' : POS_PARTICLE,
    'JKO' : POS_PARTICLE,
    'JKB' : POS_PARTICLE,
    'JKV' : POS_PARTICLE,
    'JKQ' : POS_PARTICLE,
    'JC' : POS_CONJUNCTIVE,
    'JX' : POS_PARTICLE,
    'EP' : POS_ENDING,
    'EF' : POS_ENDING,
    'EC' : POS_ENDING,
    'ETN' : POS_ENDING,
    'ETM' : POS_ENDING,
    'XPN' : POS_NOUN,
    'XSN' : POS_SUFFIX,
    'XSV' : POS_SUFFIX,
    'XSA' : POS_SUFFIX,
    }

    return known_pos.get(pos, pos)

'XR'
'SF'
'SE'
'SSO'
'SSC'
'SC'
'SY'
'SH'
'SL'
'SN'

def patch_dictionary_form(word, dictionary_form, pos):
    if pos[0] == 'V' and dictionary_form[-1] != '다':
        return dictionary_form + '다'
    if pos[0] == 'N':
        return word
    return dictionary_form

def crack_complex_pos(pos):
    return pos.split('+')[0]

class MecabAnalyzer(MorphAnalyzer):
    def __init__(self, dict_lookup_func):
        self.dict_lookup_func = dict_lookup_func if dict_lookup_func else lambda x: ''
        self.parser = Mecab()

    def parse(self, text):
        out = []
        tokens = self.parser.parse(text)
        for word, dictionary_form, pos in tokens:
            dictionary_form = patch_dictionary_form(word, dictionary_form, pos)
            if pos[0] == 'S':
                obj = IgnoredToken(word)
            elif pos[0] == 'J':
                obj = create_particle_token(word, self.dict_lookup_func)
            elif pos[0] == 'E':
                obj = create_ending_token(word, self.dict_lookup_func)
            else:
                definition = self.dict_lookup_func(dictionary_form)
                obj = AnnotatedToken(text=word,
                            dictionary_form=dictionary_form,
                            definition=definition,
                            pos=convert_pos(pos)
                            )

            out.append(obj)
        return out

def test_output():
    #text = '그는 목이 거의 없을 정도로 살이 뒤룩뒤룩 찐 몸집이 큰 사내로, 코밑에는 커다란 콧수염을 기르고 있었다.'
    #text = '4번지에 살고 있는 더즐리 부부'
    text = '그들은 기이하거나 신비스런 일과는 전혀 무관해 보였다.'
   # text = '프리벳가 4번지에'

    parser = MecabAnalyzer(None)

    f = parser.parse(text)
    pprint.pprint(f)

if __name__ == '__main__':
    test_output()