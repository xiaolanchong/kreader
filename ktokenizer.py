# -*- coding: utf-8 -*-

import logging
import pprint
from collections import Counter
import re

from morph_analyzer import IgnoredToken, AnnotatedToken, WORD_WHITESPACE, WORD_PARAGRAPH

class Whitespace:
    def __init__(self):
        pass

    def jsonify(self):
        return {'class' : WORD_WHITESPACE}

    def __repr__(self):
        return '_'

class Paragraph:
    def __init__(self):
        pass

    def jsonify(self):
        return {'class' : WORD_PARAGRAPH}

    def __repr__(self):
        return '_P'

re_word_counter = re.compile(r"[\w']+", re.UNICODE)

def get_word_number(text):
    re = re_word_counter.findall(text)
    return len(Counter(re))


class KTokenizer:
    TWITTER = 1
    MECAB = 2

    def __init__(self, dict_lookup_func=None, tokenizer=TWITTER):
        self.debug_mode = False
        self.dict_lookup_func = dict_lookup_func
        self.lookedup_words = {}

        if   tokenizer == KTokenizer.TWITTER:
            from twitter import TwitterAnalyzer
            self.tokenizer = TwitterAnalyzer(self.add_lookedup_word)
        elif tokenizer == KTokenizer.MECAB:
            from mecab_analyzer import MecabAnalyzer
            self.tokenizer = MecabAnalyzer(self.add_lookedup_word)
        else:
            RuntimeError('Unknown tokenizer specified: ' + str(parser))

    def parse(self, text):
        self.lookedup_words = {}
        try:
            tokens = self.tokenizer.parse(text)
        except Exception as e:
            logging.exception(e)
            logging.error('Error on parsing text: ' + text)
            if self.debug_mode:
                raise
            return [IgnoredToken(text)]

        out = []
        current_pos = 0
        for index, token in enumerate(tokens):
            skipped_chars = 0
            while text[current_pos][0] != token.text[0]:
               current_pos += 1
               skipped_chars += 1

            if skipped_chars:
                out.append(Whitespace()) # convert all ws symbols to a space

            out.append(token)
            current_pos += len(token.text)
        return out

    def get_lookedup_words(self):
        return self.lookedup_words

    def add_lookedup_word(self, word):
        if self.dict_lookup_func is not None and \
           word not in self.lookedup_words:
            definition = self.dict_lookup_func(word)
            self.lookedup_words[word] = definition
        return ''

def tokenize(ktokenizer, line_generator):
    text_objs = []
    glossary = {}
    total_words = 0

    for line in line_generator():
            line_objs = ktokenizer.parse(line)
            lookedup_words = ktokenizer.get_lookedup_words()
            glossary.update(lookedup_words)
            total_words += get_word_number(line)

            text_objs.extend(line_objs)
            text_objs.append(Paragraph())

    if len(text_objs):
        text_objs.pop()

    unique_words = len(glossary)

    return [obj.jsonify() for obj in text_objs], glossary, total_words, unique_words

if __name__ == '__main__':
    pass
