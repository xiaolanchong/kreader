# -*- coding: utf-8 -*-

from collections import namedtuple

WORD_WHITESPACE = 1
WORD_IGNORED = 2
WORD_ANNOTATED = 3
WORD_PARAGRAPH = 4

POS_NOUN = 'n'
POS_VERB = 'v'
POS_ADJ = 'adj'
POS_ADV = 'adv'
POS_PARTICLE = 'prt'
POS_ENDING = 'end'
POS_AUX = 'aux'

#Token = namedtuple('Token', ['word', 'dictionary_form', 'pos']) # dictionary_form is None for word not to look up

"""
class Token:
    def __init__(self):
        pass

    def serialize(self, lookup_func):
        raise NotImplementedError()

"""

def create_service_token(token_type, text, pos_name, dict_lookup_func):
    if dict_lookup_func and len(text) > 1:
        definition = dict_lookup_func(text)
        if definition and len(definition):
            return token_type(text=text, definition=definition)

    definition = text + ' ' + pos_name
    return token_type(text=text, definition=definition)

def create_particle_token(text, dict_lookup_func):
    return create_service_token(ParticleToken, text, 'particle', dict_lookup_func)

def create_ending_token(text, dict_lookup_func):
    return create_service_token(EndingToken, text, 'ending', dict_lookup_func)

class IgnoredToken:
    def __init__(self, text):
        self.text = text

    def jsonify(self):
        return  {'class' : WORD_IGNORED,
                 'text'  : self.text}

    def __repr__(self):
        return 'IT({0})'.format(self.text)

class AnnotatedToken:
    def __init__(self, **kwargs):
        self.text = kwargs['text']
        self.dictionary_form = kwargs['dictionary_form']
        self.definition = kwargs.get('definition', '')
        self.pos = kwargs['pos']

    def jsonify(self):
        return  {'class' : WORD_ANNOTATED,
                 'text'  : self.text,
                 'dict_form'  : self.dictionary_form,
                 'def'   : self.definition,
                 'pos'   : self.pos}

    def __repr__(self):
        return "AT('{0}', '{1}', '{2}', '{3}')".format(self.text, self.dictionary_form, self.definition, self.pos)

class ParticleToken(AnnotatedToken):
    def __init__(self, **kwargs):
        text = kwargs['text']
        kwargs['dictionary_form'] = text
        #if 'definition' not in kwargs:
       #     kwargs['definition'] = get_particle_desc(text)
        kwargs['pos'] = POS_PARTICLE
        super().__init__(**kwargs)

class EndingToken(AnnotatedToken):
    def __init__(self, **kwargs):
        text = kwargs['text']
        kwargs['dictionary_form'] = text
       # kwargs['definition'] = get_ending_desc(text)
        kwargs['pos'] = POS_ENDING
        super().__init__(**kwargs)

class MorphAnalyzer:
    def parse(self, text):
        raise NotImplementedError('')