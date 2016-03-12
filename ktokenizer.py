# -*- coding: utf-8 -*-

import logging
import pprint

from twitter import TwitterAnalyzer
from mecab_analyzer import MecabAnalyzer
from morph_analyzer import IgnoredToken, AnnotatedToken, WORD_WHITESPACE, WORD_PARAGRAPH

class Whitespace:
    def __init__(self):
        pass

    def jsonify(self):
        return {'class' : WORD_WHITESPACE}

    def __repr__(self):
        return ' '

class Paragraph:
    def __init__(self):
        pass

    def jsonify(self):
        return {'class' : WORD_PARAGRAPH}

    def __repr__(self):
        return ' P'

class KTokenizer:
    TWITTER = 1
    MECAB = 2

    def __init__(self, dict_lookup_func=None, parser=TWITTER):
        self.dict_lookup_func = dict_lookup_func

        if   parser == KTokenizer.TWITTER:
            self.parser = TwitterAnalyzer(self.dict_lookup_func)
        elif parser == KTokenizer.MECAB:
            self.parser = MecabAnalyzer(self.dict_lookup_func)
        else:
            RuntimeError('Unknown parser specified: ' + str(parser))

    def parse(self, text):
        try:
            tokens = self.parser.parse(text)
        except Exception as e:
            logging.exception(e)
            logging.error('Error on parsing text: ' + text)
            #raise
            return IgnoredToken(text)

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

