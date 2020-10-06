# -*- coding: utf-8 -*-

import re
import argparse
import sys
import contextlib

from ktokenizer import KTokenizer, tokenize
from morph_analyzer import AnnotatedToken
from ezsajeon import EzSajeon
from stardictsajeon import StardictRuSajeon
from extract_utils import strip_definition

ezsajeon = EzSajeon()
rusajeon = StardictRuSajeon()
tokenizer = KTokenizer(KTokenizer.MECAB)

hanja_re = re.compile('^\((.+?)\)')


@contextlib.contextmanager
def smart_open(filename=None):
    if filename and filename != '-':
        fh = open(filename, encoding='utf8', mode='w')
    else:
        fh = sys.stdout

    try:
        yield fh
    finally:
        if fh is not sys.stdout:
            fh.close()


def get_text_from_file(path):
    with open(path, encoding='utf8') as f:
       for line in f.readlines():
           yield line

def mash(in_path, out_path, card_tag):
    glossary = set()
    words_no_definition = set()

    with open(in_path, encoding='utf8') as fin, \
         smart_open(out_path) as fout:
        for line in fin.readlines():
            line_objs = tokenizer.parse(line)
            for token in line_objs:
               if isinstance(token, AnnotatedToken) and (token.dictionary_form not in glossary):
                  word = token.dictionary_form
                  glossary.add(word)
                  definition = rusajeon.get_definition(word, True)
                  hanja = ''
                  m = hanja_re.search(definition)
                  if m is not None:
                     hanja = m.group(1)

                  definition = definition.replace('\n', '; ')
                  normalized_line = line.strip().replace('\t', ' ')
                  out_line = '{0}\t{1}\t{2}\t{3}\t{4}\n'.format(
                                 word, definition.strip(), hanja, normalized_line, card_tag)
                  fout.write(out_line)

    print('Unique words: {0}'.format(len(glossary)))

def main():  
    parser = argparse.ArgumentParser(description='Extracts words with definitions from Korean texts. '
                                                 'Output format to import into Anki easily: word <TAB> definition <TAB> hanja <TAB> sentence <TAB> tag')
    parser.add_argument(dest='input', 
                        help='Korean text file')
    parser.add_argument(nargs='?', dest='output',
                        help='output file', default='')
    parser.add_argument('--tag', '-t', default='', dest='card_tag',
                        help='optional tag for Anki cards')	

    args = parser.parse_args()
    mash(args.input, args.output, args.card_tag)

if __name__ == '__main__':
    main()
