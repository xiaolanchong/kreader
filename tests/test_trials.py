# -*- coding: utf-8 -*-

import os.path
import unittest
import sys
import pprint
sys.path.append(os.path.abspath('..'))

from ktokenizer import KTokenizer, tokenize
from ezsajeon import EzSajeon

def main():
    ezdict = EzSajeon()
    tokenizer_mecab = KTokenizer(KTokenizer.MECAB)

    file = open('../../_kreader_files/kbs sample.txt', encoding='utf8')
    parsed_text, glossary, total_words, unique_words = tokenize(tokenizer_mecab, lambda : file.readlines())
    print(total_words, unique_words)


if __name__ == '__main__':
    main()
