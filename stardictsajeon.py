# -*- coding: utf-8 -*-

import os.path
from stardict import DictFileReader, IfoFileReader, IdxFileReader

def find_nth(haystack, needle, n):
      start = haystack.find(needle)
      while start >= 0 and n > 1:
         start = haystack.find(needle, start+len(needle))
         n -= 1
      return start

def get_full_dict_name(file_name):
      return os.path.join(os.path.dirname(__file__), r'..', '_kreader_files', file_name)

class StardictBaseSajeon:
    def __init__(self, dict_dir, dict_name):
        ifo_file = os.path.join(dict_dir, dict_name + ".ifo")
        idx_file = os.path.join(dict_dir, dict_name + ".idx")
        dict_file =os.path.join(dict_dir, dict_name + ".dict.dz")
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

        article = self.customize(article, add_examples)
        return article

    def customize(self, article, add_examples):
        return article

class StardictEnSajeon(StardictBaseSajeon):
    def __init__(self):
        dict_dir = get_full_dict_name(r'stardict-KoreanEnglishDic-2.4.2')
        dict_name = 'KoreanEnglishDic'
        super().__init__(dict_dir, dict_name)

    def customize(self, article, add_examples):
        example_delimiter ='ㆍ'
        if add_examples:
            res = article.replace(example_delimiter, '\n')
        else:
            pos = article.find(example_delimiter)
            res = article[:pos]
        return res

class StardictRuSajeon(StardictBaseSajeon):
    def __init__(self):
        dict_dir = get_full_dict_name(r'stardict-GNU_korean-russian-dict(v.0.5)')
        dict_name = 'GNU_krd-0.5'
        super().__init__(dict_dir, dict_name)

    def customize(self, article, add_examples):
      if add_examples:
        return article

      second_cr = find_nth(article, '\n', 2)
      return article[:second_cr]

def test_output_en():
    ss = StardictEnSajeon()

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

def test_output_ru():
    ss = StardictRuSajeon()

    article_with_sample = ss.get_definition('번지', True)
    print(article_with_sample)
    print('-' * 25)

    article_with_sample = ss.get_definition('늙다', False)
    print(article_with_sample)
    print('-' * 25)

    article_with_sample = ss.get_definition('늙다', True)
    print(article_with_sample)
    print('-' * 25)

if __name__ == '__main__':
    test_output_ru()