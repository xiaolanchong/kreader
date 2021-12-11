# -*- coding: utf-8 -*-

import pprint
from morph_analyzer import *
from mecab import Mecab
import jamo


def convert_pos(pos):
    known_pos = {
        'NNG': POS_NOUN,
        'NNP': POS_NOUN,
        'NNB': POS_NOUN,
        'NNBC': POS_NOUN,
        'NR': POS_NUMBER,
        'NP': POS_NOUN,  # to POS_PRONOUN?
        'VV': POS_VERB,
        'VA': POS_ADJECTIVE,
        'VX': POS_AUXILIARY,  # or POS_VERB?
        'VCP': POS_ADJECTIVE,
        'VCN': POS_ADJECTIVE,
        'MM': POS_DETERMINER,
        'MAG': POS_ADVERB,
        'MAJ': POS_ADVERB,
        'IC': POS_INTERJECTION,
        'JKS': POS_PARTICLE,
        'JKC': POS_PARTICLE,
        'JKG': POS_PARTICLE,
        'JKO': POS_PARTICLE,
        'JKB': POS_PARTICLE,
        'JKV': POS_PARTICLE,
        'JKQ': POS_PARTICLE,
        'JC': POS_CONJUNCTIVE,
        'JX': POS_PARTICLE,
        'EP': POS_ENDING,
        'EF': POS_ENDING,
        'EC': POS_ENDING,
        'ETN': POS_ENDING,
        'ETM': POS_ENDING,
        'XPN': POS_NOUN,
        'XSN': POS_SUFFIX,
        'XSV': POS_SUFFIX,
        'XSA': POS_SUFFIX,
        'XR': POS_NOUN  # hada root
    }

    return known_pos.get(pos, pos)


'SF'
'SE'
'SSO'
'SSC'
'SC'
'SY'
'SH'
'SL'
'SN'


def recover_particle(word):
    I, V, F = jamo.decompose(word[-1])
    if F == 'ᆻ':
        return 'ᆻ'
    else:
        return word[-1]


def patch_dictionary_form(word, dictionary_form, pos):
    if pos[0] == 'V' and dictionary_form[-1] != '다':
        return dictionary_form + '다'
    if pos[0] == 'N':
        return word
    return dictionary_form


def decompose(pos_desc):
    parts = pos_desc.split('+')
    decomposed_tokens = []
    for dep_part in parts[1:]:
        dep_posdesc_word = dep_part.split('/')
        dep_pos = convert_pos(dep_posdesc_word[0])
        dep_word = dep_posdesc_word[1] if len(dep_posdesc_word) > 1 else dep_posdesc_word[0]
        decomposed_tokens.append(DecomposedToken(dep_pos, dep_word))  # TODO: restore 시-, -었

    return convert_pos(parts[0]), decomposed_tokens


class MecabAnalyzer(MorphAnalyzer):
    def __init__(self):
        self.parser = Mecab()

    def parse(self, text):
        out = []
        tokens = self.parser.parse(text)
        for word, dictionary_form, pos in tokens:
            dictionary_form = patch_dictionary_form(word, dictionary_form, pos)
            if pos[0] == 'S':
                obj = IgnoredToken(word)
            else:
                definition = ''
                main_pos, decomposed_tokens = decompose(pos)
                obj = AnnotatedToken(text=word,
                                     dictionary_form=dictionary_form,
                                     definition=definition,
                                     pos=main_pos,
                                     decomposed_tokens=decomposed_tokens
                                     )

            out.append(obj)
        return out


def test_output():
    # text = '그는 목이 거의 없을 정도로 살이 뒤룩뒤룩 찐 몸집이 큰 사내로, 코밑에는 커다란 콧수염을 기르고 있었다.'
    # text = '4번지에 살고 있는 더즐리 부부'
    text = '그들은 기이하거나 신비스런 일과는 전혀 무관해 보였다.'
    # text = '프리벳가 4번지에'

    parser = MecabAnalyzer()

    f = parser.parse(text)
    pprint.pprint(f)


if __name__ == '__main__':
    test_output()
