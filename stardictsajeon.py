# -*- coding: utf-8 -*-

import os.path
from stardict import DictFileReader, IfoFileReader, IdxFileReader

class StardictSajeon:
    def __init__(self):
        dict_dir = r'c:\tools\_lang\GoldenDict\content\stardict-KoreanEnglishDic-2.4.2'

        ifo_file = os.path.join(dict_dir, "KoreanEnglishDic.ifo")
        idx_file = os.path.join(dict_dir, "KoreanEnglishDic.idx")
        dict_file =os.path.join(dict_dir, "KoreanEnglishDic.dict.dz")
        ifo_reader = IfoFileReader(ifo_file)
        idx_reader = IdxFileReader(idx_file)
        self.dict_reader = DictFileReader(dict_file, ifo_reader, idx_reader, True)

    def get_definition(self, word, add_examples=False):
        dicts = self.dict_reader.get_dict_by_word(word)
        if len(dicts) == 0:
            return ''

        if len(dicts) > 1:
            raise RuntimeError("Found {0} dictionaries for word '{1}', the only one expected".format(len(dicts), word))

        article = dicts[0].get('m', '')
        article = article.decode('utf8')

        example_delimiter ='ㆍ'
        if add_examples:
            res = article.replace(example_delimiter, '\n')
        else:
            pos = article.find(example_delimiter)
            res = article[:pos]
        return res


def test_output():
    ss = StardictSajeon()

    article_with_sample = ss.get_definition('번지', True)
    print(article_with_sample)
    print('-' * 25)

    article_no_sample = ss.get_definition('번지', False)
    print(article_no_sample)
    print('-' * 25)

    article_no_sample = ss.get_definition('번번번번번지', False)
    print(article_no_sample)
    print('-' * 25)

    article_with_sample = ss.get_definition('적', True)
    print(article_with_sample)
    open('testzzzz.txt', mode='w', encoding='utf8').write(article_with_sample)


if __name__ == '__main__':
    test_output()