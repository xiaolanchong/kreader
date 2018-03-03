# -*- coding: utf-8 -*-

import os.path

# ezcorean dictionary
class EzSajeon:
    def __init__(self):
        self.dict = {}
        path = os.path.join(os.path.dirname(__file__), 'ezcorean_2cols.tsv')
        with open(path, encoding='utf8') as f:
            for line in f.readlines():
                word, definition = line.rstrip().split('\t')
                all_definitions = self.dict.get(word)
                if all_definitions:
                    all_definitions += '\n'
                    all_definitions += definition
                else:
                    all_definitions = definition
                self.dict[word] = all_definitions

    def get_definition(self, word):
        return self.dict.get(word, '')


def test_output():
    es = EzSajeon()

    article_with_sample = es.get_definition('살')
    print(article_with_sample)
    print('-' * 25)

    article_no_sample = es.get_definition('번지')
    print(article_no_sample)
    print('-' * 25)

    article_no_sample = es.get_definition('번번번번번지')
    print(article_no_sample)
    print('-' * 25)

    article_with_sample = es.get_definition('적')
    print(article_with_sample)


if __name__ == '__main__':
    test_output()