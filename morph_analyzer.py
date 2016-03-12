# -*- coding: utf-8 -*-

from collections import namedtuple

POS_NOUN = 1

Token = namedtuple('Token', ['word', 'dictionary_form', 'pos']) # dictionary_form is None for word not to look up

class MorphAnalyzer:
    def parse(self, text):
        raise NotImplementedError('')