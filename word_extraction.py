# -*- coding: utf-8 -*-

import re

from ktokenizer import KTokenizer, tokenize
from morph_analyzer import AnnotatedToken
from ezsajeon import EzSajeon

ezsajeon = EzSajeon()
tokenizer = KTokenizer(KTokenizer.MECAB)

hanja_re = re.compile('^\((.+?)\)')

def get_text_from_file(path):
    with open(path, encoding='utf8') as f:
       for line in f.readlines():
           yield line

def main():
    card_tag = 'hp_stone_ch1'
    in_path = '..\_kreader_files\hp1_1.txt'
    out_path = '..\_kreader_files\hp1_1_words.txt'
    mash(in_path, out_path, card_tag)

def mash(in_path, out_path, card_tag):
    glossary = set()
    words_no_definition = set()

    with open(in_path, encoding='utf8') as fin, \
         open(out_path, encoding='utf8', mode='w') as fout:
        for line in fin.readlines():
            line_objs = tokenizer.parse(line)
            #lookedup_words = tokenizer.get_lookedup_words()
            for token in line_objs:
               if isinstance(token, AnnotatedToken) and (token.dictionary_form not in glossary):
                  word = token.dictionary_form
                  glossary.add(word)
                  definition = ezsajeon.get_definition(word)
                  hanja = ''
                  m = hanja_re.search(definition)
                  if m is not None:
                     hanja = m.group(1)

                  definition = definition.replace('\n', '; ')
                  normalized_line = line.strip().replace('\t', ' ')
                  out_line = '{0}\t{1}\t{2}\t{3}\t{4}\n'.format(
                                 word, definition.strip(), hanja, normalized_line, card_tag)
                  fout.write(out_line)
               elif len(definition) == 0 and word not in words_no_definition:
                  print(word + ' : no definition')
                  words_no_definition.add(word)

           # glossary.update(lookedup_words)

    print('Unique words: {0}'.format(len(glossary)))

if __name__ == '__main__':
    main()
