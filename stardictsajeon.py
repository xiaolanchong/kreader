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

    def get_definition(self, word):
        dicts = self.dict_reader.get_dict_by_word(word)
        if len(dicts) != 1:
            raise RuntimeError("{0} dictionaries for word '{1}' != 1".format(len(dicts), word))

        article = dicts[0].get('m', '')
        article = article.decode('utf8')
        line_delimiter ='ㆍ'
        res = article.replace(line_delimiter, '\n')
        return res


def test_output():
    ss = StardictSajeon()
    d = ss.get_definition('번지')
    print(d)

if __name__ == '__main__':
    test_output()