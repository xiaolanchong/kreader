# -*- coding: utf-8 -*-

import jamo
import konlpy
from morph_analyzer import *

productive_pos = frozenset(['VerbPrefix', 'Verb', 'Determiner', 'NounPrefix', 'Adjective', 'Noun', 'Adverb'])

non_productive_pos = frozenset(['Punctuation', 'Exclamation', 'KoreanParticle', 'Josa', 'Alpha', 'Conjunction',
                                'Number', 'Foreign'])

ignored_pos = ['Punctuation', 'Alpha', 'Number', 'Foreign']

pos_name = {
    'Verb':        POS_VERB,
    'VerbPrefix':  POS_VERB,
    'NounPrefix':  POS_NOUN,
    'Determiner':  POS_DETERMINER,
    'Adjective':   POS_ADJECTIVE,
    'Noun':        POS_NOUN,
    'Adverb':      POS_ADVERB,
    'Exclamation': POS_INTERJECTION,
    'KoreanParticle': POS_PARTICLE,
    'Josa ':          POS_PARTICLE,
    'Conjunction':  POS_CONJUNCTIVE,
    'Number':      POS_NUMBER,
    'Suffix':      POS_SUFFIX,
    'PreEomi':     POS_ENDING,
    'Eomi':        POS_ENDING,
}


def is_ignored(pos):
    return pos in ignored_pos


def do_words_suit(a, b):
    if a[0] == b[0]:
        return True

    a_letters = jamo.decompose(a[0])
    b_letters = jamo.decompose(b[0])
    # skip dummy initial
    if a_letters[0] == 'ᄋ' and b_letters[0] == 'ᄋ':
        return a_letters[1] == b_letters[1]
    else:
        return a_letters[0] == b_letters[0]


no_stem = ''


# The correct solution is dynamic programming matching
def get_word_to_stem_pairs(words, stems):
    index_stems = 0
    res = []
    for word in words:
        if index_stems < len(stems):
            stem = stems[index_stems]
        else:
            print('Stem index is out of range', index_stems, stems)
            res.append((word, no_stem))
            continue

        if do_words_suit(word, stem):
            res.append((word, stem))
            index_stems += 1
        else:
            res.append((word, no_stem))
    return res


class TwitterAnalyzer(MorphAnalyzer):
    def __init__(self, dict_lookup_func):
        self.parser = konlpy.tag.Twitter()
        self.dict_lookup_func = dict_lookup_func if dict_lookup_func else lambda x: ''

    def parse(self, text):
        tokens = self.parser.pos(text, norm=False, stem=False)
        stems = self.parser.pos(text, norm=True, stem=True)
        words_to_stems = get_word_to_stem_pairs([word for word, pos in tokens], [word for word, pos in stems])

        out = []
        current_pos = 0
        for index, token in enumerate(tokens):
            word, pos = token[0], token[1]
            if len(word) == 0:
                continue

            skipped_chars = 0
            while text[current_pos][0] != word[0]:
                current_pos += 1
                skipped_chars += 1

            dictionary_form = words_to_stems[index][1]

            if is_ignored(pos):
                obj = IgnoredToken(word)
            else:
                definition = self.get_definition(dictionary_form, pos)
                obj = AnnotatedToken(text=word,
                                     dictionary_form=dictionary_form,
                                     definition=definition,
                                     pos=pos_name.get(pos, pos))

            current_pos += len(word)
            out.append(obj)
        return out

    def get_definition(self, dictionary_form, pos):
        return self.dict_lookup_func(dictionary_form)


def test_twitter_output():
    # text = '4번지에 살고 있는 더즐리 부부'
    text = '그들은 기이하거나 신비스런 일과는 전혀 무관해 보였다.'

    parser = konlpy.tag.Twitter()

    f = parser.pos(text, norm=False, stem=False)
    print(' '.join([word for word, pos in f]))

    s = parser.pos(text, norm=True, stem=True)
    print(' '.join([word + '/' + pos for word, pos in s]))


if __name__ == '__main__':
    test_twitter_output()
