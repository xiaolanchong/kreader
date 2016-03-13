# -*- coding: utf-8 -*-

import os.path

# ezcorean dictionary
class EzSajeon:
    def __init__(self):
        self.dict = {}
        path = os.path.join(os.path.dirname(__file__),'ezcorean_2cols.tsv')
        with open(path, encoding='utf8') as f:
            for line in f.readlines():
                word, definition = line.rstrip().split('\t')
                self.dict[word] = definition

    def get_definition(self, word):
        return self.dict.get(word, '')