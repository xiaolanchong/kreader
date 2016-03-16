# -*- coding: utf-8 -*-

import re

from ktokenizer import KTokenizer
from ezsajeon import EzSajeon

ezsajeon = EzSajeon()
tokenizer = KTokenizer(ezsajeon.get_definition, KTokenizer.MECAB)

hanja_re = re.compile('^\((.+?)\)')

def main():
    card_tag = 'hp_stone_ch1'
    glossary = {}
    in_path = '..\_kreader_files\hp1_1.txt'
    out_path = '..\_kreader_files\hp1_1_words.txt'
    with open(in_path, encoding='utf8') as fin, \
         open(out_path, encoding='utf8', mode='w') as fout:
        for line in fin.readlines():
            line_objs = tokenizer.parse(line)
            lookedup_words = tokenizer.get_lookedup_words()
            for word, definition in lookedup_words.items():
               if len(word) and len(definition) and (word not in glossary):
                  hanja = ''
                  m = hanja_re.search(definition)
                  if m is not None:
                     hanja = m.group(1)

                  definition = definition.replace('\n', '; ')
                  normalized_line = line.strip().replace('\t', ' ')
                  out_line = '{0}\t{1}\t{2}\t{3}\t{4}\n'.format(
                                 word, definition.strip(), hanja, normalized_line, card_tag)
                  fout.write(out_line)
               elif len(definition) == 0:
                  print(word + ' : no definition')

            glossary.update(lookedup_words)

if __name__ == '__main__':
    main()
