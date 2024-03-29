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
    return os.path.join(os.path.dirname(__file__), r'..', 'kreader_dicts', file_name)


class StardictBaseSajeon:
    TYPE_TEXT = 'm'
    TYPE_XDXF = 'x'
    TYPE_HTML = 'h'

    def __init__(self, dict_dir, dict_name):
        ifo_file = os.path.join(dict_dir, dict_name + ".ifo")
        idx_file = os.path.join(dict_dir, dict_name + ".idx")
        dict_file = os.path.join(dict_dir, dict_name + ".dict.dz")
        ifo_reader = IfoFileReader(ifo_file)
        idx_reader = IdxFileReader(idx_file)
        self.ifo_reader = ifo_reader
        self.dict_reader = DictFileReader(dict_file, ifo_reader, idx_reader, True)

    """
        sametypesequence
        'm' Word's pure text meaning. The data should be a utf-8 string ending with '\0'.
        'g' A utf-8 string which is marked up with the Pango text markup language.
        't' English phonetic string. The data should be a utf-8 string ending with '\0'.
        'x' A utf-8 string which is marked up with the xdxf language.
        'y' Chinese YinBiao or Japanese KANA. The data should be a utf-8 string ending with '\0'.
        'k' KingSoft PowerWord's data. The data is a utf-8 string ending with '\0'.
        'w' MediaWiki markup language.
        'h' Html codes.
        'n' WordNet data.
        'r' Resource file list.
        'X' this type identifier is reserved for experimental extensions.
    """
    def get_definition(self, word, add_examples=False):
        dicts = self.dict_reader.get_dict_by_word(word)
        if len(dicts) == 0:
            return ''

        if len(dicts) > 1:
            raise RuntimeError("Found {0} dictionaries for word '{1}', the only one expected".format(len(dicts), word))

        sametypesequence, data = next(iter(dicts[0].items()))
        assert sametypesequence in 'mgtxyk'
        article = data.decode('utf8')

        article = self.customize(article, add_examples)
        return article

    def get_all_words(self):
        return self.dict_reader.get_all_words()

    def get_type(self):
        return self.ifo_reader.get_ifo('sametypesequence')

    def customize(self, article, add_examples):
        return article


class StardictEnSajeon(StardictBaseSajeon):
    def __init__(self):
        dict_dir = get_full_dict_name(r'stardict-KoreanEnglishDic-2.4.2')
        dict_name = 'KoreanEnglishDic'
        super().__init__(dict_dir, dict_name)

    def customize(self, article, add_examples):
        example_delimiter = 'ㆍ'
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

    @staticmethod
    def get_definitions(article):
        for definition in article.split('\n\n'):
            second_cr = find_nth(definition, '\n', 2)
            subst = definition[:second_cr] if second_cr > 0 else definition
            subst = subst.rstrip()
            if len(subst):
                yield subst

    def customize(self, article, add_examples):
        if add_examples:
            return article.rstrip()

        return '\n'.join(StardictRuSajeon.get_definitions(article))


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

    article_with_sample = ss.get_definition('조정', True)
    print(article_with_sample)
    print('-' * 25)

    article_with_sample = ss.get_definition('늙다', False)
    print(article_with_sample)
    print('-' * 25)

    article_with_sample = ss.get_definition('늙다', True)
    print(article_with_sample)
    print('-' * 25)


def test_output_ru():
    ss = StardictRuSajeon()
    with open('GNU_krd_dump.txt', mode='w', encoding='utf8') as f:
        for word in ss.get_all_words():
            article_without_sample = ss.get_definition(word, False)
            f.write(article_without_sample)
            f.write('\n----------\n')


def test_hanja_dict():
    rel_dir_name = 'stardict-Hanja_KoreanHanzi_Dic-2.4.2'
    dict_name = 'Hanja_KoreanHanzi_Dic'
    dir_name = os.path.join(os.path.dirname(__file__), r'..', '_temp', rel_dir_name)
    hanja_dict = StardictBaseSajeon(dir_name, dict_name)
    import pprint
    with open('hanja_out.txt', mode='w', encoding='utf8') as f:
        f.write('\n'.join(list(hanja_dict.get_all_words())[:13000]))


if __name__ == '__main__':
    test_output_ru()
    #test_hanja_dict()
