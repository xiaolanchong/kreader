# -*- coding: utf-8 -*-

import logging
import pprint

from twitter import TwitterAnalyzer


WORD_WHITESPACE = 1
WORD_IGNORED = 2
WORD_ANNOTATED = 3
WORD_PARAGRAPH = 4

class IgnoredToken:
    def __init__(self, text):
        self.text = text

    def jsonify(self):
        return  {'class' : WORD_IGNORED,
                 'text'  : self.text}

    def __repr__(self):
        return 'I({0})'.format(self.text)

class AnnotatedToken:
    def __init__(self, text, dictionary_form, definition):
        self.text = text
        self.dictionary_form = dictionary_form
        self.definition = definition if definition else ''

    def jsonify(self):
        return  {'class' : WORD_ANNOTATED,
                 'text'  : self.text,
                 'dict_form'  : self.dictionary_form,
                 'def'   : self.definition}

    def __repr__(self):
        if self.definition and len(self.definition):
            return "A({0}, {1}, '{2}')".format(self.text, self.dictionary_form, self.definition)
        else:
            return "A({0}, {1})".format(self.text, self.dictionary_form)

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

    def __init__(self, dict_lookup_func=None, parser=TWITTER, ):
        self.dict_lookup_func = dict_lookup_func

        if   parser == KTokenizer.TWITTER:
            self.parser = TwitterAnalyzer()
        elif parser == KTokenizer.MECAB:
            self.parser = MecabAnalyzer()
        else:
            RuntimeError('Unknown parser specified: ' + str(parser))

    def parse(self, text):
        tokens = self.parser.parse(text)
        out = []
        current_pos = 0
        for index, token in enumerate(tokens):
            skipped_chars = 0
            while text[current_pos][0] != token.word[0]:
               current_pos += 1
               skipped_chars += 1

            if skipped_chars:
                out.append(Whitespace()) # convert all ws symbols to a space

            if token.dictionary_form:
                if token.pos is None:
                    definition = self.dict_lookup_func(token.dictionary_form) if self.dict_lookup_func else None
                else:
                    definition = token.pos
                obj = AnnotatedToken(token.word, token.dictionary_form, definition)
            else:
                obj = IgnoredToken(token.word)

            current_pos += len(token.word)
            out.append(obj)
        return out

