# -*- coding: utf-8 -*-

WORD_WHITESPACE = 1
WORD_IGNORED = 2
WORD_ANNOTATED = 3
WORD_PARAGRAPH = 4

POS_NOUN = 'n'
POS_VERB = 'v'
POS_ADJECTIVE = 'adj'
POS_ADVERB = 'adv'
POS_PARTICLE = 'prt'
POS_ENDING = 'end'   # adj -> adv, verb inflection
POS_AUXILIARY = 'aux'
POS_DETERMINER = 'det'  # prenoun, modifier
POS_INTERJECTION = 'int'
POS_CONJUNCTIVE = 'conj'
POS_NUMBER = 'num'
POS_SUFFIX = 'sfx'  # noun suffix: 적

composable_pos_set = frozenset([POS_NOUN, POS_VERB, POS_ADJECTIVE, POS_ADVERB, POS_AUXILIARY, POS_DETERMINER, POS_SUFFIX])

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

"""

class IgnoredToken:
    def __init__(self, text):
        self.text = text

    def jsonify(self):
        return  {'class' : WORD_IGNORED,
                 'text'  : self.text}

    def __repr__(self):
        return 'IT({0})'.format(self.text)

class DecomposedToken:
    def __init__(self, pos, word):
        self.pos   = pos
        self.word = word

    def jsonify(self):
        return  ( self.pos, self.word )

    def __repr__(self):
        return '({0}, {1})'.format(self.pos, self.word)

class AnnotatedToken:
    def __init__(self, **kwargs):
        self.text = kwargs['text']
        self.dictionary_form = kwargs['dictionary_form']
       # self.definition = kwargs.get('definition', '')
        self.pos = kwargs['pos']
        self.decomposed_tokens = kwargs.get('decomposed_tokens', [])

    def jsonify(self):
        out =  {'class' : WORD_ANNOTATED,
                 'text'  : self.text,
                 'dict_form'  : self.dictionary_form,
                 'pos'   : self.pos,
                 }
        if len(self.decomposed_tokens):
           out['dec_tok'] = [tok.jsonify() for tok in self.decomposed_tokens]
        return out

    def add_decomposed(self, next_token):
         self.text += next_token.text
         self.decomposed_tokens.append(DecomposedToken(next_token.pos,
               next_token.dictionary_form if next_token.dictionary_form else next_token.text ))

    def __repr__(self):
        if len(self.decomposed_tokens):
          return "AT('{0}', '{1}', '{2}', '{3}')".format(self.text, self.dictionary_form,
                                                     self.pos, repr(self.decomposed_tokens))
        else:
          return "AT('{0}', '{1}', '{2}')".format(self.text, self.dictionary_form, self.pos)

"""
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

"""

class MorphAnalyzer:
    def parse(self, text):
        raise NotImplementedError('')