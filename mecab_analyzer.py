# -*- coding: utf-8 -*-

import pprint

from morph_analyzer import AnnotatedToken, IgnoredToken, \
                           create_particle_token, create_ending_token, \
                           MorphAnalyzer

from mecab import Mecab

class MecabAnalyzer(MorphAnalyzer):
    def __init__(self, dict_lookup_func):
        self.dict_lookup_func = dict_lookup_func if dict_lookup_func else lambda x: ''
        self.parser = Mecab()

    def parse(self, text):
        out = []
        tokens = self.parser.parse(text)
        for word, dictionary_form, pos in tokens:
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
                            pos=pos
                            )

            out.append(obj)
        return out

def test_output():
    #text = '그는 목이 거의 없을 정도로 살이 뒤룩뒤룩 찐 몸집이 큰 사내로, 코밑에는 커다란 콧수염을 기르고 있었다.'
    text = '4번지에 살고 있는 더즐리 부부'
    text = '그들은 기이하거나 신비스런 일과는 전혀 무관해 보였다.'
   # text = '프리벳가 4번지에'

    parser = MecabAnalyzer()

    f = parser.parse(text)
    pprint.pprint(f)

if __name__ == '__main__':
    test_output()