# -*- coding: utf-8 -*-

import logging
from collections import Counter
import re

from morph_analyzer import IgnoredToken, AnnotatedToken, WORD_WHITESPACE, WORD_PARAGRAPH, \
    POS_ENDING, composable_pos_set


class Whitespace:
    def __init__(self):
        self.space_number = 1
        self.text = ' ' * self.space_number

    def jsonify(self):
        return {'class': WORD_WHITESPACE}

    def __repr__(self):
        return '_'


class Paragraph:
    def __init__(self):
        pass

    def jsonify(self):
        return {'class': WORD_PARAGRAPH}

    def __repr__(self):
        return '_P'


re_word_counter = re.compile(r"[\w']+", re.UNICODE)


def get_word_number(text):
    groups = re_word_counter.findall(text)
    return len(Counter(groups))


def is_composable(pos):
    return pos in composable_pos_set


class KTokenizer:
    TWITTER = 1
    MECAB = 2

    def __init__(self, tokenizer=TWITTER):
        self.debug_mode = False
        self.lookedup_words = {}

        if tokenizer == KTokenizer.TWITTER:
            from twitter import TwitterAnalyzer
            self.tokenizer = TwitterAnalyzer(lambda x: x)
        elif tokenizer == KTokenizer.MECAB:
            from mecab_analyzer import MecabAnalyzer
            self.tokenizer = MecabAnalyzer()
        else:
            RuntimeError('Unknown tokenizer specified: ' + str(tokenizer))

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
                out.append(Whitespace())  # convert all ws symbols to a space

            out.append(token)
            current_pos += len(token.text)

        return self.merge_tokens(out)

    def process_token(self, cur_token, prev_token, result_tokens):
        if isinstance(prev_token, AnnotatedToken) and prev_token.pos in composable_pos_set:
            if isinstance(cur_token, AnnotatedToken) and cur_token.pos == POS_ENDING:
                prev_token.add_decomposed(cur_token)
                return prev_token
            else:
                result_tokens.append(prev_token)
                return cur_token

        elif isinstance(prev_token, IgnoredToken):
            if isinstance(cur_token, IgnoredToken) or \
                    isinstance(cur_token, Whitespace):
                prev_token.text += cur_token.text
                return prev_token

            else:
                result_tokens.append(prev_token)
                return cur_token
        else:
            result_tokens.append(prev_token)
            return cur_token

    def merge_tokens(self, tokens):
        if len(tokens) == 0:
            return tokens
        result_tokens = []
        prev_token = tokens[0]
        for cur_token in tokens[1:]:
            prev_token = self.process_token(cur_token, prev_token, result_tokens)
        result_tokens.append(prev_token)
        return result_tokens


def tokenize(ktokenizer, line_generator):
    text_objs = []
    glossary = set()
    total_words = 0

    for line in line_generator():
        line_objs = ktokenizer.parse(line)
        #            lookedup_words = ktokenizer.get_lookedup_words()
        for obj in line_objs:
            if isinstance(obj, AnnotatedToken):
                glossary.add(obj.dictionary_form)
        total_words += get_word_number(line)

        text_objs.extend(line_objs)
        text_objs.append(Paragraph())

    if len(text_objs):
        text_objs.pop()

    unique_words = len(glossary)

    return [obj.jsonify() for obj in text_objs], glossary, total_words, unique_words


if __name__ == '__main__':
    pass
